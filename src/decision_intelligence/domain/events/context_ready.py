from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ContextReady:
    """
    Emitted the first time DecisionContext transitions to *ready* state.
    Signals that the context is now sufficient for a meaningful retrieval query.
    """

    session_id: str
    signal_count: int
    occurred_at: datetime
