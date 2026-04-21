from __future__ import annotations

from typing import Optional

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from conversation_management.domain.entities.conversation_history import ConversationHistory
from conversation_management.domain.models import SenderType, IntentType
from conversation_management.domain.value_objects.intent import Intent
from conversation_management.domain.value_objects.assistant_response import AssistantResponse
from conversation_management.application.ports.i_intent_classifier import IIntentClassifier
from conversation_management.application.ports.i_response_generator import IResponseGenerator
from conversation_management.application.ports.i_response_evaluator import IResponseEvaluator
from conversation_management.application.ports.i_decision_intelligence_service import (
    IDecisionIntelligenceService,
    TurnInputDTO,
)
from conversation_management.domain.ports.i_conversation_history_repository import IConversationHistoryRepository


_CLARIFICATION_INTENTS = frozenset({"ambiguous"})

_LLM_HISTORY_WINDOW = 5


def _recent(history: list[dict]) -> list[dict]:
    """Return only the last _LLM_HISTORY_WINDOW messages for LLM context."""
    return history[-_LLM_HISTORY_WINDOW:]


class TurnGraphState(TypedDict):
    session_id: str
    user_id: str
    message: str
    turn_number: int
    conversation_history: list[dict]
    user_name: str
    school_name: str
    intent: Optional[str]
    evidence_chunks: list[str]
    evidence_type: Optional[str]
    context_recall_score: float
    context_precision_score: float
    context_state: Optional[str]
    clarification_needed: bool
    clarification_question: Optional[str]
    response_text: Optional[str]
    groundedness_score: float
    relevance_score: float
    is_fallback: bool


def build_turn_graph(
    intent_classifier: IIntentClassifier,
    decision_intelligence_service: IDecisionIntelligenceService,
    response_generator: IResponseGenerator,
    response_evaluator: IResponseEvaluator,
    history_repository: IConversationHistoryRepository,
    min_groundedness: float = 0.8,
    min_relevance: float = 0.75,
):
    """
    Assemble and return the compiled TurnGraph (WF-GRAPH-1).

    This graph is the COORD-2 ConversationTurnCoordinator — it calls BC-2 and
    indirectly BC-3 through the IDecisionIntelligenceService port.

    All ports are injected at graph construction time via closures.
    """

    # ------------------------------------------------------------------ #
    # Nodes                                                               #
    # ------------------------------------------------------------------ #

    def classify_intent(state: TurnGraphState) -> dict:
        """N1 — Classify user message intent via LLM adapter (INV-WF-1)."""
        intent: Intent = intent_classifier.classify(
            state["message"],
            _recent(state.get("conversation_history") or []),
        )
        return {"intent": intent.value.value}

    def process_decision_intelligence(state: TurnGraphState) -> dict:
        """N2 — Delegate to BC-2 via port. Cross-context boundary (COMM-1)."""
        dto = TurnInputDTO(
            session_id=state["session_id"],
            intent=state["intent"],
            message=state["message"],
            turn_number=state["turn_number"],
            conversation_history=_recent(state.get("conversation_history") or []),
        )
        result = decision_intelligence_service.process_turn(dto)
        return {
            "evidence_chunks": result.evidence_chunks,
            "evidence_type": result.evidence_type,
            "context_recall_score": result.context_recall_score,
            "context_precision_score": result.context_precision_score,
            "context_state": result.context_state,
            "clarification_needed": result.clarification_needed,
            "clarification_question": result.clarification_question,
            "school_name": result.school_name,
        }

    def generate_response(state: TurnGraphState) -> dict:
        """N3 — Generate a grounded response from retrieved evidence (INV-AR-2, INV-AR-3, INV-AR-4)."""
        evidence = {
            "chunks": state.get("evidence_chunks", []),
            "evidence_type": state.get("evidence_type", ""),
        }
        context_snapshot = {
            "context_state": state.get("context_state", ""),
            "clarification_needed": state.get("clarification_needed", False),
            "school_name": state.get("school_name") or "your school",
            "user_name": state.get("user_name") or "there",
        }
        response: AssistantResponse = response_generator.generate(
            message=state["message"],
            conversation_history=_recent(state.get("conversation_history") or []),
            evidence=evidence,
            context_snapshot=context_snapshot,
        )
        return {"response_text": response.text}

    def generate_clarification(state: TurnGraphState) -> dict:
        """N4 — Generate a clarification question response."""
        clarification_question = (
            state.get("clarification_question")
            or "Could you provide more details so I can help you better?"
        )
        user_context = {
            "user_name": state.get("user_name") or "there",
            "school_name": state.get("school_name") or "your school",
        }
        response: AssistantResponse = response_generator.generate_clarification(
            message=state["message"],
            conversation_history=_recent(state.get("conversation_history") or []),
            clarification_question=clarification_question,
            user_context=user_context,
        )
        return {"response_text": response.text}

    def evaluate_response(state: TurnGraphState) -> dict:
        """N5 — Score groundedness and relevance (INV-AR-1, INV-AR-5, INV-AR-6)."""
        intent_type = IntentType(state["intent"])
        response = AssistantResponse.create(
            text=state["response_text"],
            intent_answered=intent_type,
            groundedness_score=0.0,
            relevance_score=0.0,
            evidence_source_ids=[],
        )
        evidence = {
            "chunks": state.get("evidence_chunks", []),
            "evidence_type": state.get("evidence_type", ""),
        }
        intent_vo = Intent(value=intent_type)
        evaluated: AssistantResponse = response_evaluator.evaluate(
            response,
            intent_vo,
            evidence,
            _recent(state.get("conversation_history") or []),
        )
        return {
            "groundedness_score": evaluated.groundedness_score,
            "relevance_score": evaluated.relevance_score,
        }

    def persist_turn(state: TurnGraphState) -> dict:
        """N6 — Append user message and assistant response to ConversationHistory."""
        user_entry = ConversationHistory.create(
            user_id=state["user_id"],
            session_id=state["session_id"],
            message=state["message"],
            sender=SenderType.USER,
        )
        assistant_entry = ConversationHistory.create(
            user_id=state["user_id"],
            session_id=state["session_id"],
            message=state["response_text"],
            sender=SenderType.ASSISTANT,
        )
        history_repository.append(user_entry)
        history_repository.append(assistant_entry)
        return {}

    def generate_redirect(state: TurnGraphState) -> dict:
        """N7 — Unified context-aware redirect for no-knowledge-answer situations.

        Handles three cases via redirect_reason derived from state:
          - 'out_of_scope'     — intent classified as out_of_scope at N1: bypass DI entirely.
          - 'general_question' — intent is general_question: bypass DI, engage conversationally.
          - 'low_quality'      — RAG pipeline ran but evaluate_response scores fell below thresholds.

        In all three cases no knowledge-grounded answer is possible. A single LLM-powered,
        personalised response acknowledges the situation and steers the user toward the domain.
        """
        intent = state.get("intent", "")
        if intent == "out_of_scope":
            redirect_reason = "out_of_scope"
        elif intent == "general_question":
            redirect_reason = "general_question"
        else:
            # RAG intent (product_inquiry / referral_question / clarification_response)
            # that failed quality evaluation — pipeline ran but could not produce a reliable answer.
            redirect_reason = "low_quality"

        evidence = (
            {
                "chunks": state.get("evidence_chunks", []),
                "evidence_type": state.get("evidence_type", ""),
            }
            if redirect_reason == "low_quality"
            else None
        )
        response: AssistantResponse = response_generator.generate_redirect(
            message=state["message"],
            conversation_history=_recent(state.get("conversation_history") or []),
            user_context={
                "user_name": state.get("user_name") or "there",
                "school_name": state.get("school_name") or "your school",
            },
            redirect_reason=redirect_reason,
            evidence=evidence,
        )
        return {"response_text": response.text}

    # ------------------------------------------------------------------ #
    # Routing                                                             #
    # ------------------------------------------------------------------ #

    def route_after_intent(state: TurnGraphState) -> str:
        """Route after N1 based on classified intent.

        - out_of_scope     → generate_redirect (N7): bypass DI, polite domain redirect.
        - general_question → generate_redirect (N7): bypass DI, conversational engagement.
        - ambiguous        → generate_clarification (N4): ask user to clarify.
        - product_inquiry, referral_question, clarification_response
                           → process_decision_intelligence (N2): full RAG pipeline.
        """
        intent = state.get("intent", "")
        if intent in ("out_of_scope", "general_question"):
            return "generate_redirect"
        if intent in _CLARIFICATION_INTENTS:  # {"ambiguous"}
            return "generate_clarification"
        return "process_decision_intelligence"

    def route_after_decision_intelligence(state: TurnGraphState) -> str:
        if state.get("clarification_needed"):
            return "generate_clarification"
        return "generate_response"

    def route_after_evaluate(state: TurnGraphState) -> str:
        gs = state.get("groundedness_score", 0.0)
        rs = state.get("relevance_score", 0.0)
        if gs >= min_groundedness and rs >= min_relevance:
            return "persist_turn"
        return "generate_redirect"

    # ------------------------------------------------------------------ #
    # Graph assembly                                                      #
    # ------------------------------------------------------------------ #

    graph = StateGraph(TurnGraphState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("process_decision_intelligence", process_decision_intelligence)
    graph.add_node("generate_response", generate_response)
    graph.add_node("generate_clarification", generate_clarification)
    graph.add_node("evaluate_response", evaluate_response)
    graph.add_node("persist_turn", persist_turn)
    graph.add_node("generate_redirect", generate_redirect)

    graph.set_entry_point("classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "generate_redirect": "generate_redirect",
            "process_decision_intelligence": "process_decision_intelligence",
            "generate_clarification": "generate_clarification",
        },
    )

    graph.add_conditional_edges(
        "process_decision_intelligence",
        route_after_decision_intelligence,
        {
            "generate_response": "generate_response",
            "generate_clarification": "generate_clarification",
        },
    )

    # generate_response always feeds evaluate_response — general_question no longer reaches
    # this node (it exits at classify_intent via generate_redirect), so every path through
    # generate_response is a RAG intent where evaluation is meaningful.
    graph.add_edge("generate_response", "evaluate_response")
    graph.add_edge("generate_clarification", "persist_turn")

    graph.add_conditional_edges(
        "evaluate_response",
        route_after_evaluate,
        {"persist_turn": "persist_turn", "generate_redirect": "generate_redirect"},
    )

    graph.add_edge("generate_redirect", "persist_turn")
    graph.add_edge("persist_turn", END)

    return graph.compile()
