from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ContextUpdated:
    """
    Emitted when a new PreferenceSignal is added to DecisionContext
    and its state may have changed.
    """

    session_id: str
    context_state: str
    signal_count: int
    occurred_at: datetime
