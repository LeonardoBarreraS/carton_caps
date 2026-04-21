from __future__ import annotations

import uuid

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from decision_intelligence.domain.entities.decision_context import DecisionContext
from decision_intelligence.domain.value_objects.retrieval_query import RetrievalQuery
from decision_intelligence.domain.models import ContextStatus, SourceTarget
from decision_intelligence.domain.value_objects.preference_signal import PreferenceSignal
from decision_intelligence.domain.value_objects.retrieved_evidence import RetrievedEvidence, EvidenceChunk
from decision_intelligence.application.ports.i_signal_extractor import ISignalExtractor
from decision_intelligence.application.ports.i_evidence_evaluator import IEvidenceEvaluator
from decision_intelligence.application.ports.i_knowledge_retrieval_service import IKnowledgeRetrievalService
from decision_intelligence.application.ports.dtos import RetrievalQueryDTO


_RETRIEVAL_INTENTS = frozenset({"product_inquiry", "referral_question"})

# Intents for which the user's question itself is the retrieval signal.
# No preference signals are required — the intent + message fully drives the query.
# The context readiness gate (EMPTY/PARTIAL/READY) must NOT block these intents.
_INTENT_SUFFICIENT_RETRIEVAL = frozenset({"referral_question"})

_INTENT_TO_SOURCE_TARGET = {
    "product_inquiry": SourceTarget.PRODUCT_CATALOG,
    "referral_question": SourceTarget.REFERRAL_PROGRAM_RULES,
}

# Signal keys whose values map directly to vocabulary present in the enriched
# product documents stored in the vector store. A product_inquiry context is
# considered retrieval-ready as soon as it contains at least one of these keys.
_RETRIEVAL_USEFUL_SIGNAL_KEYS = frozenset({
    "product_category",    # matches product type labels (cereal, snacks, oatmeal, …)
    "meal_occasion",       # matches meal-occasion labels (breakfast, school_lunch, …)
    "dietary_restriction", # matches allergen / dietary markers in enriched text
    "health_goal",         # matches dietary profile keywords (whole_grain, healthy, …)
    "budget_tier",         # matches budget tier text (budget-friendly, premium, …)
})

_LLM_HISTORY_WINDOW = 5


def _recent(history: list[dict]) -> list[dict]:
    """Return only the last _LLM_HISTORY_WINDOW messages for LLM context."""
    return history[-_LLM_HISTORY_WINDOW:]


_BASE_TOP_K = 5          # documents retrieved on the first attempt
_TOP_K_INCREMENT = 3     # additional documents added on each retry

# Minimum number of words the assembled query content (message + signal values)
# must contain before the domain anchor is appended. If the content falls below
# this threshold the current message is an anaphorical reference ("ok", "tell me
# more", "and that?") that lacks retrieval vocabulary. A substantive prior user
# message is then injected from conversation_history to resolve the implicit
# reference without an extra LLM call.
_MIN_QUERY_CONTENT_WORDS = 4


class DecisionGraphState(TypedDict):
    session_id: str
    intent: str
    message: str
    turn_number: int
    conversation_history: list[dict]
    context_snapshot: dict
    extracted_signals: list[dict]       # serialised {key, value, turn_number}
    gaps: list[str]
    clarification_needed: bool
    clarification_question: str | None
    retrieval_query_text: str | None
    source_target: str | None
    top_k: int                          # escalates on each retry attempt
    evidence_chunks: list[str]
    evidence_type: str | None
    context_recall_score: float
    context_precision_score: float
    retrieval_attempts: int
    context_state: str


def _detect_gaps(intent: str, signal_keys: set[str]) -> list[str]:
    """
    Application-layer gap detection.

    For product_inquiry: a gap exists only when the context contains NONE of the
    retrieval-useful signal keys. Any single key from _RETRIEVAL_USEFUL_SIGNAL_KEYS
    is sufficient to produce a meaningful vector-search query because each key's
    values appear verbatim in the enriched product documents stored in Qdrant.

    This avoids the prior bottleneck where the absence of "product_category"
    alone would block retrieval even though other strong signals (e.g.
    meal_occasion=breakfast, health_goal=healthy) were already present.

    For referral_question: school anchor alone is sufficient — no gap flagged.
    """
    if intent == "product_inquiry":
        if not signal_keys & _RETRIEVAL_USEFUL_SIGNAL_KEYS:
            return list(_RETRIEVAL_USEFUL_SIGNAL_KEYS)
    return []

def _build_clarification_question(gaps: list[str]) -> str:
    # When the full set of retrieval-useful keys is returned as gaps, it means
    # the context has no useful signal at all — ask an open-ended question instead
    # of listing raw key names to the user.
    if set(gaps) == _RETRIEVAL_USEFUL_SIGNAL_KEYS:
        return (
            "I'd love to help you find the right product! "
            "Could you tell me what kind of item you're looking for — "
            "for example, a breakfast food, a snack, something healthy, "
            "or a specific budget?"
        )
    gap_labels = ", ".join(gaps)
    return (
        f"To give you a better recommendation, could you tell me more about: {gap_labels}?"
    )


def build_decision_intelligence_subgraph(
    context: DecisionContext,
    signal_extractor: ISignalExtractor,
    evidence_evaluator: IEvidenceEvaluator,
    knowledge_retrieval_service: IKnowledgeRetrievalService,
    min_recall_threshold: float = 0.6,
    max_retrieval_retries: int = 2,
):
    """
    Assemble and return the compiled DecisionIntelligenceSubgraph (WF-GRAPH-2).

    DecisionContext is injected as a closure — it is NOT placed in graph state.
    This preserves Clean Architecture: domain objects never enter LangGraph's
    serialisation boundary.

    All port implementations are also injected as closures at graph construction time.
    """

    # ------------------------------------------------------------------ #
    # Nodes                                                               #
    # ------------------------------------------------------------------ #

    def extract_signals(state: DecisionGraphState) -> dict:
        """N1 — Extract PreferenceSignals from the user message via LLM adapter."""
        signals = signal_extractor.extract(
            state["message"],
            state["turn_number"],
            conversation_history=_recent(state.get("conversation_history") or []),
        )
        return {
            "extracted_signals": [
                {"key": s.key, "value": s.value, "turn_number": s.turn_number}
                for s in signals
            ]
        }

    def update_decision_context(state: DecisionGraphState) -> dict:
        """N2 — Accumulate extracted signals into DecisionContext (monotonic, INV-DC-5)."""
        for sig_dict in state["extracted_signals"]:
            signal = PreferenceSignal(
                key=sig_dict["key"],
                value=sig_dict["value"],
                turn_number=sig_dict["turn_number"],
            )
            context.add_signal(signal)
        snapshot = context.snapshot()
        return {"context_snapshot": snapshot, "context_state": snapshot["context_status"]}

    def evaluate_context_readiness(state: DecisionGraphState) -> dict:
        """N3 — Determine whether context is ready for retrieval, needs clarification, or neither."""
        intent = state["intent"]

        # clarification_response: resume the original retrieval intent if one was saved
        if intent == "clarification_response":
            pending_intent = context.pending_retrieval_intent
            if not pending_intent:
                # User answered a clarification but there is no pending retrieval to resume
                return {
                    "gaps": [],
                    "clarification_needed": False,
                    "clarification_question": None,
                    "context_state": context.status.value,
                }
            # Context already reached readiness (signals accumulated across turns)
            if context.is_ready_for_retrieval():
                context.clear_pending_retrieval_intent()
                return {
                    "intent": pending_intent,
                    "gaps": [],
                    "clarification_needed": False,
                    "clarification_question": None,
                    "context_state": context.status.value,
                }
            # Context is still partial — re-evaluate gaps using the original intent
            snapshot = state["context_snapshot"]
            signal_keys = {s["key"] for s in snapshot.get("signals", [])}
            gaps = _detect_gaps(pending_intent, signal_keys)
            if gaps:
                context.record_gap_evaluation(gaps)
                return {
                    "intent": pending_intent,
                    "gaps": gaps,
                    "clarification_needed": True,
                    "clarification_question": _build_clarification_question(gaps),
                    "context_state": context.status.value,
                }
            # No blocking gaps and we have signals: mark ready and proceed to retrieval
            if context.signals:
                context.mark_ready()
                context.clear_pending_retrieval_intent()
            return {
                "intent": pending_intent,
                "gaps": [],
                "clarification_needed": False,
                "clarification_question": None,
                "context_state": context.status.value,
            }

        # Intents that never require retrieval: exit with empty evidence
        if intent not in _RETRIEVAL_INTENTS:
            return {
                "gaps": [],
                "clarification_needed": False,
                "clarification_question": None,
                "context_state": context.status.value,
            }

        # Intent-sufficient intents (e.g. referral_question): the user's message IS
        # the retrieval query. No preference signals are needed — skip the context
        # readiness gate entirely and proceed straight to retrieval.
        if intent in _INTENT_SUFFICIENT_RETRIEVAL:
            return {
                "gaps": [],
                "clarification_needed": False,
                "clarification_question": None,
                "context_state": context.status.value,
            }

        # Context already ready or enriched: skip gap evaluation, proceed to retrieval
        if context.is_ready_for_retrieval():
            return {
                "gaps": [],
                "clarification_needed": False,
                "clarification_question": None,
                "context_state": context.status.value,
            }

        # Context is PARTIAL: detect gaps and decide
        snapshot = state["context_snapshot"]
        signal_keys = {s["key"] for s in snapshot.get("signals", [])}
        gaps = _detect_gaps(intent, signal_keys)

        if gaps:
            context.record_gap_evaluation(gaps)
            context.set_pending_retrieval_intent(intent)
            return {
                "gaps": gaps,
                "clarification_needed": True,
                "clarification_question": _build_clarification_question(gaps),
                "context_state": context.status.value,
            }

        # No blocking gaps and we have signals: transition context to ready
        if context.signals:
            context.mark_ready()

        return {
            "gaps": [],
            "clarification_needed": False,
            "clarification_question": None,
            "context_state": context.status.value,
        }

    def construct_retrieval_query(state: DecisionGraphState) -> dict:
        """
        N4 — Build an enriched retrieval query from message + accumulated signals (INV-RQ-1).

        Query construction strategy:
        - For fresh intents (product_inquiry, referral_question): the user's message is
          the primary semantic source. Signal values are appended as reinforcement.
          School name is excluded — it does not appear in product or referral chunks.
        - For clarification_response (intent was overridden to the original retrieval
          intent by N3, so this branch is actually unreachable here, but signal-only
          assembly is the correct fallback when the message is a vague answer).
        - top_k escalates on each retry: _BASE_TOP_K + retrieval_attempts * _TOP_K_INCREMENT.
          This makes every retry genuinely broader than the previous attempt.
        """
        snapshot = state["context_snapshot"]
        signals = snapshot.get("signals", [])
        intent = state["intent"]
        attempts = state.get("retrieval_attempts", 0)

        # Primary query content: user's raw message carries the exact retrieval vocabulary
        # (e.g. "eligibility", "how to refer", "healthy breakfast cereal").
        # Signal values reinforce it; for clarification turns the message is vague so
        # we fall back to signals only.
        message = state.get("message", "").strip()
        original_intent = snapshot.get("pending_retrieval_intent") or intent
        is_clarification_resume = original_intent != state.get("intent") or not message

        parts: list[str] = []
        if message and not is_clarification_resume:
            parts.append(message)
        for sig in signals:
            parts.append(sig["value"])

        # Vague-message backstop: if the assembled content (message + signal values)
        # is thin (<  _MIN_QUERY_CONTENT_WORDS words), the current message is an
        # anaphorical reference ("ok", "tell me more", "and what about that?") that
        # carries no retrieval vocabulary. Inject the most recent substantive prior
        # user message from conversation_history to resolve the implicit reference.
        # This keeps query construction deterministic and zero-cost (no LLM call).
        content_words = len(" ".join(parts).split())
        if content_words < _MIN_QUERY_CONTENT_WORDS:
            history = _recent(state.get("conversation_history") or [])
            for entry in reversed(history):
                if entry.get("role") == "user":
                    prior = entry.get("content", "").strip()
                    # Skip: same as current message, or itself vague
                    if prior and prior != message and len(prior.split()) >= _MIN_QUERY_CONTENT_WORDS:
                        parts.append(prior)
                        break

        # Append a minimal domain anchor so the query sits in the right semantic neighbourhood
        if intent == "product_inquiry":
            parts.append("fundraising product")
        elif intent == "referral_question":
            parts.append("referral program")

        query_text = " ".join(filter(None, parts))

        # top_k grows with each retry — genuinely broader result set each time
        top_k = _BASE_TOP_K + attempts * _TOP_K_INCREMENT

        # Validate via domain factory — enforces INV-RQ-2 and INV-RQ-3
        RetrievalQuery.from_context(
            session_id=state["session_id"],
            query_text=query_text,
            intent=intent,
            context_status=context.status,
        )

        source_target = (
            "product_catalog" if intent == "product_inquiry" else "referral_program_rules"
        )
        return {"retrieval_query_text": query_text, "source_target": source_target, "top_k": top_k}

    def execute_retrieval(state: DecisionGraphState) -> dict:
        """N5 — Execute retrieval via BC-3 through the IKnowledgeRetrievalService port (COMM-2)."""
        dto = RetrievalQueryDTO(
            query_text=state["retrieval_query_text"],
            source_target=state["source_target"],
            top_k=state.get("top_k", _BASE_TOP_K),
        )
        result = knowledge_retrieval_service.retrieve(dto)
        return {
            "evidence_chunks": result.chunks,
            "evidence_type": result.evidence_type,
            "retrieval_attempts": state.get("retrieval_attempts", 0) + 1,
        }

    def evaluate_evidence_quality(state: DecisionGraphState) -> dict:
        """N6 — Score evidence recall and precision via IEvidenceEvaluator (INV-RE-1, INV-RE-2)."""
        chunks = state.get("evidence_chunks", [])
        if not chunks:
            return {"context_recall_score": 0.0, "context_precision_score": 0.0}

        query = RetrievalQuery.from_context(
            session_id=state["session_id"],
            query_text=state["retrieval_query_text"],
            intent=state["intent"],
            context_status=context.status,
        )

        source_target_enum = _INTENT_TO_SOURCE_TARGET[state["intent"]]
        evidence_chunks_obj = [
            EvidenceChunk(
                chunk_id=str(uuid.uuid4()),
                text=chunk,
                source_id="",
                relevance_score=0.0,
            )
            for chunk in chunks
        ]
        evidence = RetrievedEvidence.create(
            source_target=source_target_enum,
            chunks=evidence_chunks_obj,
        )
        evaluated = evidence_evaluator.evaluate(query, evidence)
        return {
            "context_recall_score": evaluated.context_recall_score,
            "context_precision_score": evaluated.context_precision_score,
        }

    # ------------------------------------------------------------------ #
    # Routing                                                             #
    # ------------------------------------------------------------------ #

    def route_after_readiness(state: DecisionGraphState) -> str:
        if state.get("clarification_needed"):
            return "end"
        if state["intent"] not in _RETRIEVAL_INTENTS:
            return "end"
        if context.is_ready_for_retrieval():
            return "construct_retrieval_query"
        # Intent-sufficient intents bypass the context readiness gate —
        # the user's message is the query; signals are not required.
        if state["intent"] in _INTENT_SUFFICIENT_RETRIEVAL:
            return "construct_retrieval_query"
        return "end"

    def route_after_evidence_quality(state: DecisionGraphState) -> str:
        recall = state.get("context_recall_score", 0.0)
        attempts = state.get("retrieval_attempts", 0)
        if recall >= min_recall_threshold:
            return "end"
        if attempts < max_retrieval_retries:
            return "construct_retrieval_query"
        return "end"

    # ------------------------------------------------------------------ #
    # Graph assembly                                                      #
    # ------------------------------------------------------------------ #

    graph = StateGraph(DecisionGraphState)

    graph.add_node("extract_signals", extract_signals)
    graph.add_node("update_decision_context", update_decision_context)
    graph.add_node("evaluate_context_readiness", evaluate_context_readiness)
    graph.add_node("construct_retrieval_query", construct_retrieval_query)
    graph.add_node("execute_retrieval", execute_retrieval)
    graph.add_node("evaluate_evidence_quality", evaluate_evidence_quality)

    graph.set_entry_point("extract_signals")
    graph.add_edge("extract_signals", "update_decision_context")
    graph.add_edge("update_decision_context", "evaluate_context_readiness")
    graph.add_conditional_edges(
        "evaluate_context_readiness",
        route_after_readiness,
        {"construct_retrieval_query": "construct_retrieval_query", "end": END},
    )
    graph.add_edge("construct_retrieval_query", "execute_retrieval")
    graph.add_edge("execute_retrieval", "evaluate_evidence_quality")
    graph.add_conditional_edges(
        "evaluate_evidence_quality",
        route_after_evidence_quality,
        {"construct_retrieval_query": "construct_retrieval_query", "end": END},
    )

    return graph.compile()

