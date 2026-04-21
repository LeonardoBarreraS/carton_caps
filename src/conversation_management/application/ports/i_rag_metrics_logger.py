from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TurnMetricsDTO:
    """
    Carries all RAG evaluation scores and contextual metadata for one conversation turn.
    Populated by ProcessTurnUseCase after TurnGraph completes.
    Persisted by IRAGMetricsLogger for operational observability.
    """

    session_id: str
    turn_number: int
    intent: str
    context_state: str
    context_recall_score: float
    context_precision_score: float
    groundedness_score: float
    relevance_score: float
    is_fallback: bool
    clarification_needed: bool
    evidence_chunk_count: int
    timestamp: str  # ISO 8601 UTC


class IRAGMetricsLogger(ABC):
    """
    Application-layer port for persisting per-turn RAG evaluation metrics.

    Called by ProcessTurnUseCase after TurnGraph completes.
    Implemented in infrastructure by SQLiteRAGMetricsLogger.
    """

    @abstractmethod
    def log_turn_metrics(self, metrics: TurnMetricsDTO) -> None:
        ...
