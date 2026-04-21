from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from conversation_management.domain.entities.conversation_session import ConversationSession


class IConversationSessionRepository(ABC):
    """Domain-layer repository contract for ConversationSession persistence."""

    @abstractmethod
    def save(self, session: ConversationSession) -> None:
        ...

    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[ConversationSession]:
        ...

    @abstractmethod
    def find_active_by_user_id(self, user_id: str) -> Optional[ConversationSession]:
        """Return the active or idle session for a user, or None."""
        ...
