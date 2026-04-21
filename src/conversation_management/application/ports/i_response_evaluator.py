from __future__ import annotations

from abc import ABC, abstractmethod

from conversation_management.domain.value_objects.assistant_response import AssistantResponse
from conversation_management.domain.value_objects.intent import Intent


class IResponseEvaluator(ABC):
    """
    Application-layer port for response quality scoring.

    Computes groundedness_score (claim traceability to evidence)
    and relevance_score (reverse-question alignment).

    Returns a new immutable AssistantResponse enriched with both scores.

    INV-AR-1: groundedness_score must reach threshold.
    INV-AR-5: route to fallback if either score fails.
    INV-AR-6: relevance_score via reverse-question technique.
    """

    @abstractmethod
    def evaluate(
        self,
        response: AssistantResponse,
        intent: Intent,
        evidence: dict,
        conversation_history: list[dict],
    ) -> AssistantResponse:
        """
        evidence: serialised RetrievedEvidence (primitive dict form).
        conversation_history: full prior turns for conversational relevance scoring.
        Returns a new AssistantResponse with scores populated.
        """
        ...
