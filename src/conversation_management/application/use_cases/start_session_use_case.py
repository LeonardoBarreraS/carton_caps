from __future__ import annotations

from dataclasses import dataclass, field

from conversation_management.domain.entities.conversation_session import ConversationSession
from conversation_management.domain.ports.i_conversation_session_repository import IConversationSessionRepository
from conversation_management.domain.ports.i_conversation_history_repository import IConversationHistoryRepository
from conversation_management.domain.ports.i_user_repository import IUserRepository
from conversation_management.domain.ports.i_school_repository import ISchoolRepository
from conversation_management.domain.ports.i_purchase_history_repository import IPurchaseHistoryRepository
from conversation_management.application.ports.i_decision_intelligence_service import (
    IDecisionIntelligenceService,
    PreSeedContextDTO,
)
from conversation_management.application.ports.i_event_publisher import IEventPublisher


class UserNotFoundError(LookupError):
    """Raised when the user_id does not resolve to an existing user."""


class SchoolNotFoundError(LookupError):
    """Raised when no school is associated with the user."""


class SessionConflictError(Exception):
    """Raised when the user already has an active or idle session (INV-CS-7)."""


@dataclass
class StartSessionCommand:
    user_id: str


@dataclass
class StartSessionResponse:
    session_id: str
    status: str


class StartSessionUseCase:
    """
    UC-1 — Create and fully initialise a ConversationSession for a user.
    Also acts as COORD-1: coordinates session creation (BC-1) with
    DecisionContext initialisation (BC-2).

    Execution order:
      1. Guard: one active/idle session per user (INV-CS-7)
      2. Resolve User and School from repositories
      3. Load ConversationHistory + PurchaseHistory
      4. Create ConversationSession → begin_initialization()
      5. Pre-seed BC-2 DecisionContext via IDecisionIntelligenceService port
      6. complete_initialization() → session becomes idle
      7. Persist session, drain events, return response

    INV-CS-3: school pre-seeded into DecisionContext before session becomes active.
    INV-CS-5: DecisionContext exists before session enters active state.
    INV-CS-6: user_id must resolve to an existing user.
    INV-CS-7: one active/idle session per user.
    """

    def __init__(
        self,
        session_repository: IConversationSessionRepository,
        history_repository: IConversationHistoryRepository,
        user_repository: IUserRepository,
        school_repository: ISchoolRepository,
        purchase_history_repository: IPurchaseHistoryRepository,
        decision_intelligence_service: IDecisionIntelligenceService,
        event_publisher: IEventPublisher,
    ) -> None:
        self._session_repository = session_repository
        self._history_repository = history_repository
        self._user_repository = user_repository
        self._school_repository = school_repository
        self._purchase_history_repository = purchase_history_repository
        self._decision_intelligence_service = decision_intelligence_service
        self._event_publisher = event_publisher

    def execute(self, command: StartSessionCommand) -> StartSessionResponse:
        if not command.user_id:
            raise ValueError("user_id must not be empty.")

        # INV-CS-7: reject if user already has an open session
        existing = self._session_repository.find_active_by_user_id(command.user_id)
        if existing is not None:
            raise SessionConflictError(
                f"User '{command.user_id}' already has an active or idle session "
                f"('{existing.session_id}'). Close it before starting a new one."
            )

        # INV-CS-6: resolve user identity
        user = self._user_repository.find_by_id(command.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{command.user_id}' not found.")

        # INV-CS-3: school must be resolvable
        school = self._school_repository.find_by_user_id(command.user_id)
        if school is None:
            raise SchoolNotFoundError(
                f"No school found for user '{command.user_id}'. "
                "A school affiliation is required to start a session."
            )

        # Load optional context data (both gracefully return empty lists)
        _history = self._history_repository.find_by_user_id(command.user_id)#---> THIS IS NOT BEING USED. 
        purchase_records = self._purchase_history_repository.find_by_user_id(command.user_id)

        # Extract raw signal strings from purchase history records
        purchase_signals: list[str] = [
            record.get("product_name", "")
            for record in purchase_records
            if record.get("product_name")
        ]

        # Create session and begin initialization
        session = ConversationSession.create(
            user_id=command.user_id,
            school_id=school.school_id,
        )
        session.begin_initialization()

        # Pre-seed BC-2 DecisionContext — COORD-1 cross-context call (COMM-1)
        # INV-CS-3, INV-CS-5: context must exist before session becomes active
        dto = PreSeedContextDTO(
            session_id=session.session_id,
            school_id=school.school_id,
            school_name=school.name,
            purchase_signals=purchase_signals,
        )
        self._decision_intelligence_service.pre_seed_context(dto)

        # Complete initialization — session transitions initializing → idle
        session.complete_initialization()
        self._session_repository.save(session)
        self._event_publisher.publish(session.collect_events())  # publish SessionStarted

        return StartSessionResponse(session_id=session.session_id, status="idle")
