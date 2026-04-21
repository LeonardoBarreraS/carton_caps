from __future__ import annotations

from enum import Enum


class SessionStatus(str, Enum):
    """Lifecycle states of a ConversationSession (INV-CS-1)."""
    CREATED = "created"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    CLOSED = "closed"


class SenderType(str, Enum):
    """Identifies the author of a ConversationHistory record."""
    USER = "user"
    ASSISTANT = "assistant"


class IntentType(str, Enum):
    """Classified purpose of a user message turn."""
    PRODUCT_INQUIRY = "product_inquiry"
    REFERRAL_QUESTION = "referral_question"
    GENERAL_QUESTION = "general_question"
    CLARIFICATION_RESPONSE = "clarification_response"
    AMBIGUOUS = "ambiguous"
    OUT_OF_SCOPE = "out_of_scope"
