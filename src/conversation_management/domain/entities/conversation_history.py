from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from conversation_management.domain.models import SenderType


@dataclass
class ConversationHistory:
    """
    Persisted record of a single conversation message.

    Loaded at session init to restore prior context.
    Appended on each completed turn.
    Not part of the ConversationSession consistency boundary.
    """

    history_id: str
    user_id: str
    session_id: str
    message: str
    sender: SenderType
    timestamp: datetime

    @classmethod
    def create(
        cls,
        user_id: str,
        session_id: str,
        message: str,
        sender: SenderType,
    ) -> ConversationHistory:
        if not message:
            raise ValueError("message must not be empty")
        return cls(
            history_id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id,
            message=message,
            sender=sender,
            timestamp=datetime.now(timezone.utc),
        )
