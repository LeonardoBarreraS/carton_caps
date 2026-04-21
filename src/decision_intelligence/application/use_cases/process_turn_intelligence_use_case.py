from __future__ import annotations

from dataclasses import dataclass, field

from decision_intelligence.domain.ports.i_decision_context_repository import IDecisionContextRepository
from decision_intelligence.application.ports.i_signal_extractor import ISignalExtractor
from decision_intelligence.application.ports.i_evidence_evaluator import IEvidenceEvaluator
from decision_intelligence.application.ports.i_knowledge_retrieval_service import IKnowledgeRetrievalService
from decision_intelligence.application.ports.i_event_publisher import IEventPublisher
from decision_intelligence.application.workflows.decision_intelligence_subgraph import (
    build_decision_intelligence_subgraph,
    DecisionGraphState,
)

from typing import Optional


class SessionContextNotFoundError(LookupError):
    """Raised when no DecisionContext exists for the given session_id."""


@dataclass
class ProcessTurnIntelligenceCommand:
    session_id: str
    intent: str
    message: str
    turn_number: int
    conversation_history: list[dict] = field(default_factory=list)


@dataclass
class ProcessTurnIntelligenceResult:
    evidence_chunks: list[str]
    evidence_type: str
    context_recall_score: float
    context_precision_score: float
    context_state: str
    clarification_needed: bool
    clarification_question: Optional[str]
    school_name: str = ""


class ProcessTurnIntelligenceUseCase:
    """
    UC-5 — Execute the full Decision Intelligence pipeline for one conversation turn.

    Loads the DecisionContext for the session, assembles and runs the
    DecisionIntelligenceSubgraph (LangGraph), persists the updated context,
    drains intra-component domain events, and returns the result to BC-1.

    Transaction boundary: load context → run subgraph → save context.

    INV-DC-4: retrieval only triggered when context is partial/ready/enriched.
    INV-DC-5: signals accumulate monotonically inside the subgraph.
    INV-RQ-1: retrieval query built from context snapshot, not raw message.
    INV-WF-2: context updated before query construction (enforced by graph edge order).
    INV-WF-4: subgraph always executes regardless of intent.
    """

    def __init__(
        self,
        decision_context_repository: IDecisionContextRepository,
        signal_extractor: ISignalExtractor,
        evidence_evaluator: IEvidenceEvaluator,
        knowledge_retrieval_service: IKnowledgeRetrievalService,
        event_publisher: IEventPublisher,
        min_recall_threshold: float = 0.6,
        max_retrieval_retries: int = 2,
    ) -> None:
        self._repository = decision_context_repository
        self._signal_extractor = signal_extractor
        self._evidence_evaluator = evidence_evaluator
        self._knowledge_retrieval_service = knowledge_retrieval_service
        self._event_publisher = event_publisher
        self._min_recall_threshold = min_recall_threshold
        self._max_retrieval_retries = max_retrieval_retries

    def execute(self, command: ProcessTurnIntelligenceCommand) -> ProcessTurnIntelligenceResult:
        context = self._repository.find_by_session_id(command.session_id)
        if context is None:
            raise SessionContextNotFoundError(
                f"No DecisionContext found for session '{command.session_id}'. "
                "Ensure StartSessionUseCase was called first."
            )

        subgraph = build_decision_intelligence_subgraph(
            context=context,
            signal_extractor=self._signal_extractor,
            evidence_evaluator=self._evidence_evaluator,
            knowledge_retrieval_service=self._knowledge_retrieval_service,
            min_recall_threshold=self._min_recall_threshold,
            max_retrieval_retries=self._max_retrieval_retries,
        )

        initial_state: DecisionGraphState = {
            "session_id": command.session_id,
            "intent": command.intent,
            "message": command.message,
            "turn_number": command.turn_number,
            "conversation_history": command.conversation_history,
            "context_snapshot": context.snapshot(),
            "extracted_signals": [],
            "gaps": [],
            "clarification_needed": False,
            "clarification_question": None,
            "retrieval_query_text": None,
            "source_target": None,
            "evidence_chunks": [],
            "evidence_type": None,
            "context_recall_score": 0.0,
            "context_precision_score": 0.0,
            "retrieval_attempts": 0,
            "context_state": context.status.value,
        }

        final_state = subgraph.invoke(initial_state)

        # Post-graph: persist updated DecisionContext and publish events
        self._repository.save(context)
        self._event_publisher.publish(context.collect_events())

        return ProcessTurnIntelligenceResult(
            evidence_chunks=final_state.get("evidence_chunks", []),
            evidence_type=final_state.get("evidence_type", ""),
            context_recall_score=final_state.get("context_recall_score", 0.0),
            context_precision_score=final_state.get("context_precision_score", 0.0),
            context_state=final_state.get("context_state", context.status.value),
            clarification_needed=final_state.get("clarification_needed", False),
            clarification_question=final_state.get("clarification_question"),
            school_name=context.school_anchor.school_name,
        )
