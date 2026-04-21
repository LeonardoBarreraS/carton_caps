from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SessionStarted:
    """
    Emitted when a ConversationSession transitions from initializing → active.
    The session is ready to accept the first user message.
    """

    session_id: str
    user_id: str
    school_id: str
    occurred_at: datetime
