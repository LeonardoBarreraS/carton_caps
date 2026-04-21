from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SessionClosed:
    """
    Emitted when a ConversationSession reaches the closed (terminal) state.
    No further turns will be processed for this session.
    """

    session_id: str
    user_id: str
    occurred_at: datetime
