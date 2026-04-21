from __future__ import annotations

from dataclasses import dataclass

from decision_intelligence.domain.models import SourceTarget


@dataclass(frozen=True)
class EvidenceChunk:
    """
    A single retrieved content chunk from the knowledge store.
    Immutable.
    """

    chunk_id: str
    text: str
    source_id: str  # product_id or rule_id
    relevance_score: float


@dataclass(frozen=True)
class RetrievedEvidence:
    """
    Immutable result of a retrieval execution.

    Carries retrieved content chunks and context quality scores evaluated
    before evidence is injected into generation.

    INV-RE-1: context_recall_score computed after retrieval, before injection.
    INV-RE-2: context_precision_score computed after retrieval, before injection.
    INV-RE-3: if recall < threshold, retrieval must be retried.
    INV-RE-4: evidence with failed quality scores must not reach generation.
    """

    source_target: SourceTarget
    chunks: tuple[EvidenceChunk, ...]
    context_recall_score: float = 0.0
    context_precision_score: float = 0.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.context_recall_score <= 1.0):
            raise ValueError(
                f"context_recall_score must be in [0.0, 1.0], got {self.context_recall_score}"
            )
        if not (0.0 <= self.context_precision_score <= 1.0):
            raise ValueError(
                f"context_precision_score must be in [0.0, 1.0], got {self.context_precision_score}"
            )

    @classmethod
    def create(
        cls,
        source_target: SourceTarget,
        chunks: list[EvidenceChunk],
        context_recall_score: float = 0.0,
        context_precision_score: float = 0.0,
    ) -> RetrievedEvidence:
        if not chunks:
            raise ValueError("RetrievedEvidence must contain at least one chunk")
        return cls(
            source_target=source_target,
            chunks=tuple(chunks),
            context_recall_score=context_recall_score,
            context_precision_score=context_precision_score,
        )


