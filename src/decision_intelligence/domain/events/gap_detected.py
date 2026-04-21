from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GapDetected:
    """
    Emitted when gap evaluation finds the context insufficient for a recommendation.
    Triggers a clarification signal in the Conversation Management turn pipeline.
    """

    session_id: str
    gaps: tuple[str, ...]
    occurred_at: datetime

    def __init__(self, session_id: str, gaps: list[str], occurred_at: datetime) -> None:
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "gaps", tuple(gaps))
        object.__setattr__(self, "occurred_at", occurred_at)
