from __future__ import annotations

from abc import ABC, abstractmethod

from conversation_management.domain.value_objects.intent import Intent


class IIntentClassifier(ABC):
    """
    Application-layer port for intent classification.

    Implemented in infrastructure by an LLM adapter.
    Called by the classify_intent node in TurnGraph.

    conversation_history: full prior conversation as a list of
    {"role": "user"|"assistant", "content": str} dicts, in chronological
    order, NOT including the current message.
    """

    @abstractmethod
    def classify(self, message: str, conversation_history: list[dict]) -> Intent:
        ...
