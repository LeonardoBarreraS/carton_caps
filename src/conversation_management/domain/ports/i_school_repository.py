from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from conversation_management.domain.value_objects.school import School


class ISchoolRepository(ABC):
    """
    Domain-layer repository contract for loading School by user association.

    Returns external reference value objects, not managed entities.
    School identity is pre-resolved by an external Master Data BC and loaded as immutable.
    This repository provides read-only access — no persistence operations.
    """

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Optional[School]:
        ...
