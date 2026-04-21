from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from conversation_management.domain.entities.conversation_session import (
    ConversationSession,
    InvalidSessionTransitionError,
)
from conversation_management.domain.models import SessionStatus, IntentType, SenderType
from conversation_management.domain.value_objects.intent import Intent
from conversation_management.domain.value_objects.assistant_response import AssistantResponse
from conversation_management.domain.ports.i_conversation_session_repository import (
    IConversationSessionRepository,
)
from conversation_management.domain.ports.i_user_repository import IUserRepository
from conversation_management.domain.ports.i_school_repository import ISchoolRepository
from conversation_management.application.ports.i_intent_classifier import IIntentClassifier
from conversation_management.application.ports.i_response_generator import IResponseGenerator
from conversation_management.application.ports.i_response_evaluator import IResponseEvaluator
from conversation_management.application.ports.i_decision_intelligence_service import (
    IDecisionIntelligenceService,
)
from conversation_management.domain.ports.i_conversation_history_repository import (
    IConversationHistoryRepository,
)
from conversation_management.application.ports.i_event_publisher import IEventPublisher
from conversation_management.application.ports.i_rag_metrics_logger import (
    IRAGMetricsLogger,
    TurnMetricsDTO,
)
from conversation_management.application.workflows.turn_graph import build_turn_graph


@dataclass(frozen=True)
class ProcessTurnCommand:
    session_id: str
    user_id: str
    message: str


@dataclass(frozen=True)
class ProcessTurnResponse:
    session_id: str
    response_text: str
    intent: str
    is_fallback: bool
    groundedness_score: float
    context_precision_score: float
    context_recall_score: float
    relevance_score: float


class SessionNotFoundError(Exception):
    pass


class SessionOwnershipError(Exception):
    pass


class InvalidTurnStateError(Exception):
    pass


class ProcessTurnUseCase:
    """
    UC-2 — Process a conversational turn within an active session.

    Orchestrates the full turn lifecycle:
      1. Guard domain invariants (INV-CS-4, INV-CS-5).
      2. Transition session: idle → active.
      3. Invoke the TurnGraph (WF-GRAPH-1, COORD-2).
      4. Reconstruct AssistantResponse from graph result.
      5. Transition session: active → idle.
      6. Drain domain events.
    """

    def __init__(
        self,
        session_repository: IConversationSessionRepository,
        intent_classifier: IIntentClassifier,
        decision_intelligence_service: IDecisionIntelligenceService,
        response_generator: IResponseGenerator,
        response_evaluator: IResponseEvaluator,
        history_repository: IConversationHistoryRepository,
        event_publisher: IEventPublisher,
        rag_metrics_logger: IRAGMetricsLogger,
        user_repository: IUserRepository,
        school_repository: ISchoolRepository,
        min_groundedness: float = 0.8,
        min_relevance: float = 0.75,
    ) -> None:
        self._session_repository = session_repository
        self._intent_classifier = intent_classifier
        self._decision_intelligence_service = decision_intelligence_service
        self._response_generator = response_generator
        self._response_evaluator = response_evaluator
        self._history_repository = history_repository
        self._event_publisher = event_publisher
        self._rag_metrics_logger = rag_metrics_logger
        self._user_repository = user_repository
        self._school_repository = school_repository
        self._min_groundedness = min_groundedness
        self._min_relevance = min_relevance

    def execute(self, command: ProcessTurnCommand) -> ProcessTurnResponse:
        # --- Guard: session exists ---
        session: ConversationSession | None = self._session_repository.find_by_id(
            command.session_id
        )
        if session is None:
            raise SessionNotFoundError(f"Session '{command.session_id}' not found.")

        # --- Guard: ownership (INV-CS-5) ---
        if session.user_id != command.user_id:
            raise SessionOwnershipError(
                f"User '{command.user_id}' does not own session '{command.session_id}'."
            )

        # --- Guard: session must be IDLE to accept a new turn (INV-CS-4) ---
        if session.status != SessionStatus.IDLE: 
            raise InvalidTurnStateError(
                f"Session '{command.session_id}' is not idle (current: {session.status.value}). "
                "Cannot start a new turn."
            )

        # --- Load full conversation history for LLM context ---
        history_entries = self._history_repository.find_by_user_id(command.user_id)
        conversation_history = [
            {
                "role": "user" if entry.sender == SenderType.USER else "assistant",
                "content": entry.message,
            }
            for entry in history_entries
        ]

        # --- Pre-load user name and school name for LLM personalization ---
        user = self._user_repository.find_by_id(command.user_id)
        user_name = user.name if user else ""
        school = self._school_repository.find_by_user_id(command.user_id)
        school_name = school.name if school else ""

        # --- Transition: idle → active ---
        session.receive_message()

        try:
            # --- Build and invoke TurnGraph (WF-GRAPH-1) ---
            turn_graph = build_turn_graph(
                intent_classifier=self._intent_classifier,
                decision_intelligence_service=self._decision_intelligence_service,
                response_generator=self._response_generator,
                response_evaluator=self._response_evaluator,
                history_repository=self._history_repository,
                min_groundedness=self._min_groundedness,
                min_relevance=self._min_relevance,
            )

            initial_state = {
                "session_id": command.session_id,
                "user_id": command.user_id,
                "message": command.message,
                "turn_number": session.turn_count + 1,
                "conversation_history": conversation_history,
                "user_name": user_name,
                "school_name": school_name,
                "intent": None,
                "evidence_chunks": [],
                "evidence_type": None,
                "context_recall_score": 0.0,
                "context_precision_score": 0.0,
                "context_state": None,
                "clarification_needed": False,
                "clarification_question": None,
                "response_text": None,
                "groundedness_score": 0.0,
                "relevance_score": 0.0,
                "is_fallback": False,
            }

            final_state = turn_graph.invoke(initial_state)

            # --- Log RAG metrics (observability, never interrupts the pipeline) ---
            try:
                self._rag_metrics_logger.log_turn_metrics(TurnMetricsDTO(
                    session_id=command.session_id,
                    turn_number=initial_state["turn_number"],
                    intent=final_state.get("intent") or "",
                    context_state=final_state.get("context_state") or "",
                    context_recall_score=final_state.get("context_recall_score", 0.0),
                    context_precision_score=final_state.get("context_precision_score", 0.0),
                    groundedness_score=final_state.get("groundedness_score", 0.0),
                    relevance_score=final_state.get("relevance_score", 0.0),
                    is_fallback=final_state.get("is_fallback", False),
                    clarification_needed=final_state.get("clarification_needed", False),
                    evidence_chunk_count=len(final_state.get("evidence_chunks") or []),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                ))
            except Exception:  # noqa: BLE001
                pass

            # --- Reconstruct AssistantResponse for domain method ---
            intent_type = IntentType(final_state["intent"])
            response_vo = AssistantResponse.create(
                text=final_state["response_text"],
                intent_answered=intent_type,
                groundedness_score=final_state["groundedness_score"],
                relevance_score=final_state["relevance_score"],
                evidence_source_ids=[],
            )

            # --- Transition: active → idle and record turn metadata ---
            session.complete_turn(intent=Intent(value=intent_type), response=response_vo)

        except Exception:
            # --- Rollback: active → idle so the user can retry the turn ---
            session.fail_turn()
            self._session_repository.save(session)
            raise

        # --- Persist updated session ---
        self._session_repository.save(session)

        # --- Publish domain events ---
        self._event_publisher.publish(session.collect_events())

        return ProcessTurnResponse(
            session_id=command.session_id,
            response_text=final_state["response_text"],
            intent=final_state["intent"],
            is_fallback=final_state.get("is_fallback", False),
            groundedness_score=final_state.get("groundedness_score", 0.0),
            context_precision_score=final_state.get("context_precision_score", 0.0),
            context_recall_score=final_state.get("context_recall_score", 0.0),
            relevance_score=final_state.get("relevance_score", 0.0),
        )
