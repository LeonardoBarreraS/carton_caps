from __future__ import annotations

from typing import Optional

from decision_intelligence.domain.entities.decision_context import DecisionContext
from decision_intelligence.domain.ports.i_decision_context_repository import (
    IDecisionContextRepository,
)


class InMemoryDecisionContextRepository(IDecisionContextRepository):
    """
    In-memory implementation of IDecisionContextRepository.

    Stores one DecisionContext per session_id. Adequate for the prototype —
    context accumulates signals in memory across all turns of an active session.
    """

    def __init__(self) -> None:
        self._contexts: dict[str, DecisionContext] = {}

    def save(self, context: DecisionContext) -> None:
        self._contexts[context.session_id] = context

    def find_by_session_id(self, session_id: str) -> Optional[DecisionContext]:
        return self._contexts.get(session_id)
