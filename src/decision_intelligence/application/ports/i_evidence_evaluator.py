from __future__ import annotations

from abc import ABC, abstractmethod

from decision_intelligence.domain.value_objects.retrieval_query import RetrievalQuery
from decision_intelligence.domain.value_objects.retrieved_evidence import RetrievedEvidence


class IEvidenceEvaluator(ABC):
    """
    Application-layer port for retrieval quality scoring.

    Computes context_recall_score and context_precision_score on RetrievedEvidence.
    Returns a new immutable RetrievedEvidence enriched with both scores.

    INV-RE-1: context_recall_score computed after retrieval, before injection.
    INV-RE-2: context_precision_score computed after retrieval, before injection.
    INV-WF-5: quality evaluation must occur after retrieval and before evidence injection.
    """

    @abstractmethod
    def evaluate(
        self,
        query: RetrievalQuery,
        evidence: RetrievedEvidence,
    ) -> RetrievedEvidence:
        ...
