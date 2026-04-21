from __future__ import annotations

from abc import ABC, abstractmethod

from decision_intelligence.domain.value_objects.preference_signal import PreferenceSignal


class ISignalExtractor(ABC):
    """
    Application-layer port for preference signal extraction.

    Implemented in infrastructure by an LLM adapter.
    Called by the extract_signals node in DecisionIntelligenceSubgraph.

    conversation_history: full prior conversation as a list of
    {"role": "user"|"assistant", "content": str} dicts, in chronological
    order, NOT including the current message. Enables the LLM to correctly
    interpret short answers (e.g. "yes please", "3 kids") against prior turns.
    """

    @abstractmethod
    def extract(
        self,
        message: str,
        turn_number: int,
        conversation_history: list[dict] | None = None,
    ) -> list[PreferenceSignal]:
        ...
