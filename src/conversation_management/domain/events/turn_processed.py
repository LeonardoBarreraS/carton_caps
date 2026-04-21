from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TurnProcessed:
    """
    Emitted when a ConversationSession transitions from active → idle.
    A complete turn (message → response) has been processed.
    """

    session_id: str
    turn_count: int
    intent_value: str
    occurred_at: datetime
