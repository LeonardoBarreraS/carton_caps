from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from decision_intelligence.domain.entities.decision_context import DecisionContext


class IDecisionContextRepository(ABC):
    """
    Domain-layer repository contract for DecisionContext persistence.
    Scoped to session lifecycle — one context per session.
    """

    @abstractmethod
    def save(self, context: DecisionContext) -> None:
        ...

    @abstractmethod
    def find_by_session_id(self, session_id: str) -> Optional[DecisionContext]:
        ...
