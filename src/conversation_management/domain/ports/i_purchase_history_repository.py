from __future__ import annotations

from abc import ABC, abstractmethod


class IPurchaseHistoryRepository(ABC):
    """
    Domain-layer repository contract for reading PurchaseHistory records.

    Optional signal — returns an empty list gracefully when no records exist.
    Each record is a plain dict matching the Purchase_History DB schema.
    """

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[dict]:
        ...
