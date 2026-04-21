from __future__ import annotations

from abc import ABC, abstractmethod

from conversation_management.domain.entities.conversation_history import ConversationHistory


class IConversationHistoryRepository(ABC):
    """Domain-layer repository contract for ConversationHistory records."""

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[ConversationHistory]:
        ...

    @abstractmethod
    def append(self, entry: ConversationHistory) -> None:
        ...
