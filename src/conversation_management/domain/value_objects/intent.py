from __future__ import annotations

from dataclasses import dataclass

from conversation_management.domain.models import IntentType


@dataclass(frozen=True)
class Intent:
    """
    Classified purpose of a user message turn.

    Immutable once created. Drives routing through the turn pipeline
    and constrains retrieval source selection.
    """

    value: IntentType
