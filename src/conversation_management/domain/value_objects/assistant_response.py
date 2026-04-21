from __future__ import annotations

from dataclasses import dataclass, field

from conversation_management.domain.models import IntentType


@dataclass(frozen=True)
class AssistantResponse:
    """
    Grounded response returned to the caller.

    Immutable once generated. Must be backed by retrieved evidence.
    Carries groundedness_score and relevance_score.

    A response that fails score thresholds must not be delivered —
    use AssistantResponse.fallback() instead.

    INV-AR-1: every response grounded in evidence
    INV-AR-5: response not returned if either score is below threshold
    INV-AR-6: relevance_score via reverse-question; grounded-but-wrong is still a failure
    """

    text: str
    intent_answered: IntentType
    groundedness_score: float
    relevance_score: float
    evidence_source_ids: tuple[str, ...]
    is_fallback: bool = False

    def __post_init__(self) -> None:
        if not self.is_fallback:
            if not self.text:
                raise ValueError("AssistantResponse.text must not be empty")
            if not (0.0 <= self.groundedness_score <= 1.0):
                raise ValueError(
                    f"groundedness_score must be in [0.0, 1.0], got {self.groundedness_score}"
                )
            if not (0.0 <= self.relevance_score <= 1.0):
                raise ValueError(
                    f"relevance_score must be in [0.0, 1.0], got {self.relevance_score}"
                )

    @classmethod
    def create(
        cls,
        text: str,
        intent_answered: IntentType,
        groundedness_score: float,
        relevance_score: float,
        evidence_source_ids: list[str],
    ) -> AssistantResponse:
        return cls(
            text=text,
            intent_answered=intent_answered,
            groundedness_score=groundedness_score,
            relevance_score=relevance_score,
            evidence_source_ids=tuple(evidence_source_ids),
            is_fallback=False,
        )


