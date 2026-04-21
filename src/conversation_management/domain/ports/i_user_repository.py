from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from conversation_management.domain.value_objects.user import User


class IUserRepository(ABC):
    """
    Domain-layer repository contract for reading User identity.

    Returns external reference value objects, not managed entities.
    User identity is pre-resolved by an external Auth BC and loaded as immutable.
    This repository provides read-only access — no persistence operations.
    """

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        ...
