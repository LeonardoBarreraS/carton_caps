from __future__ import annotations

from dataclasses import dataclass

from conversation_management.domain.entities.conversation_session import InvalidSessionTransitionError
from conversation_management.domain.ports.i_conversation_session_repository import IConversationSessionRepository
from conversation_management.application.ports.i_event_publisher import IEventPublisher


class SessionNotFoundError(LookupError):
    """Raised when the requested session does not exist."""


class AuthorizationError(PermissionError):
    """Raised when the requesting user does not own the session."""


@dataclass
class CloseSessionCommand:
    session_id: str
    user_id: str


@dataclass
class CloseSessionResponse:
    session_id: str
    status: str


class CloseSessionUseCase:
    """
    UC-3 — Transition a ConversationSession to the closed terminal state.

    INV-CS-2: only idle sessions can be closed. The domain's close() guard
    raises InvalidSessionTransitionError on any illegal transition — this use
    case does not re-implement that check.
    """

    def __init__(
        self,
        session_repository: IConversationSessionRepository,
        event_publisher: IEventPublisher,
    ) -> None:
        self._repository = session_repository
        self._event_publisher = event_publisher

    def execute(self, command: CloseSessionCommand) -> CloseSessionResponse:
        session = self._repository.find_by_id(command.session_id)
        if session is None:
            raise SessionNotFoundError(f"Session '{command.session_id}' not found.")

        if session.user_id != command.user_id:
            raise AuthorizationError(
                f"User '{command.user_id}' does not own session '{command.session_id}'."
            )

        session.close()  # domain guard enforces INV-CS-2
        self._repository.save(session)
        self._event_publisher.publish(session.collect_events())  # publish SessionClosed

        return CloseSessionResponse(session_id=session.session_id, status="closed")
