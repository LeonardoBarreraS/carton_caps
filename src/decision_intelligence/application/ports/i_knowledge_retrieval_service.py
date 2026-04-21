from __future__ import annotations

from abc import ABC, abstractmethod

from decision_intelligence.application.ports.dtos import RetrievalQueryDTO, RetrievedEvidenceDTO


class IKnowledgeRetrievalService(ABC):
    """
    Application-layer cross-context port to COMP-3 (Knowledge Retrieval).

    Defined in BC-2 — BC-2 owns this contract.
    Implemented in the shell layer as a thin adapter that calls
    COMP-3's ExecuteRetrievalUseCase.

    Returns raw RetrievedEvidenceDTO (scores assigned by IEvidenceEvaluator after this call).
    """

    @abstractmethod
    def retrieve(self, query: RetrievalQueryDTO) -> RetrievedEvidenceDTO:
        ...
