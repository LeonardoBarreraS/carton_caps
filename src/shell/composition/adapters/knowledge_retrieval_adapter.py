from __future__ import annotations

from decision_intelligence.application.ports.i_knowledge_retrieval_service import (
    IKnowledgeRetrievalService,
)
from decision_intelligence.application.ports.dtos import RetrievalQueryDTO, RetrievedEvidenceDTO
from knowledge_retrieval.application.use_cases.execute_retrieval_use_case import (
    ExecuteRetrievalCommand,
    ExecuteRetrievalUseCase,
)


class KnowledgeRetrievalAdapter(IKnowledgeRetrievalService):
    """
    Shell adapter — implements the BC-2 IKnowledgeRetrievalService cross-context port
    by delegating to BC-3's ExecuteRetrievalUseCase.

    This adapter lives in the shell layer so it can import from both BCs without
    violating the Clean Architecture dependency rule inside each bounded context.

    COMM-2 contract (context_communication.json):
      BC-2 calls retrieve(RetrievalQueryDTO)
      → shell adapter translates DTO → BC-3 command → BC-3 result → DTO
    """

    def __init__(self, execute_retrieval_use_case: ExecuteRetrievalUseCase) -> None:
        self._execute_retrieval_use_case = execute_retrieval_use_case

    def retrieve(self, query: RetrievalQueryDTO) -> RetrievedEvidenceDTO:
        command = ExecuteRetrievalCommand(
            query_text=query.query_text,
            source_target=query.source_target,
            top_k=query.top_k,
        )
        result = self._execute_retrieval_use_case.execute(command)
        return RetrievedEvidenceDTO(
            chunks=result.chunks,
            evidence_type=result.evidence_type,
        )
