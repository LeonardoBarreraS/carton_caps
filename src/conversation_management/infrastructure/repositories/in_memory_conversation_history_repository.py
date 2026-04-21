from __future__ import annotations

from collections import defaultdict

from conversation_management.domain.entities.conversation_history import ConversationHistory
from conversation_management.domain.ports.i_conversation_history_repository import (
    IConversationHistoryRepository,
)


class InMemoryConversationHistoryRepository(IConversationHistoryRepository):
    """
    In-memory implementation of IConversationHistoryRepository.

    Groups ConversationHistory records by user_id in a defaultdict(list).
    Records are returned in insertion order (chronological).
    """

    def __init__(self) -> None:
        self._records: dict[str, list[ConversationHistory]] = defaultdict(list)

    def append(self, entry: ConversationHistory) -> None:
        self._records[entry.user_id].append(entry)

    def find_by_user_id(self, user_id: str) -> list[ConversationHistory]:
        return list(self._records.get(user_id, []))
