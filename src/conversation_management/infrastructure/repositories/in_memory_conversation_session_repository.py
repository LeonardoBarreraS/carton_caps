from __future__ import annotations

from typing import Optional

from conversation_management.domain.entities.conversation_session import ConversationSession
from conversation_management.domain.models import SessionStatus
from conversation_management.domain.ports.i_conversation_session_repository import (
    IConversationSessionRepository,
)

_ACTIVE_STATUSES = {SessionStatus.ACTIVE, SessionStatus.IDLE}


class InMemoryConversationSessionRepository(IConversationSessionRepository):
    """
    In-memory implementation of IConversationSessionRepository.

    Stores ConversationSession aggregates in a dict keyed by session_id.
    find_active_by_user_id enforces the one-active-session-per-user invariant
    by scanning for sessions in ACTIVE or IDLE state.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ConversationSession] = {}

    def save(self, session: ConversationSession) -> None:
        self._sessions[session.session_id] = session

    def find_by_id(self, session_id: str) -> Optional[ConversationSession]:
        return self._sessions.get(session_id)

    def find_active_by_user_id(self, user_id: str) -> Optional[ConversationSession]:
        for session in self._sessions.values():
            if session.user_id == user_id and session.status in _ACTIVE_STATUSES:
                return session
        return None
