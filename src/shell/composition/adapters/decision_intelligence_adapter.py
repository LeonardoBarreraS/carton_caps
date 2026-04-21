from __future__ import annotations

from conversation_management.application.ports.i_decision_intelligence_service import (
    IDecisionIntelligenceService,
    PreSeedContextDTO,
    TurnInputDTO,
    TurnIntelligenceResultDTO,
)
from decision_intelligence.application.use_cases.pre_seed_context_use_case import (
    PreSeedContextUseCase,
)
from decision_intelligence.application.use_cases.process_turn_intelligence_use_case import (
    ProcessTurnIntelligenceCommand,
    ProcessTurnIntelligenceUseCase,
)


class DecisionIntelligenceAdapter(IDecisionIntelligenceService):
    """
    Shell adapter — implements the BC-1 IDecisionIntelligenceService cross-context port
    by delegating to BC-2 application-layer use cases.

    This adapter lives in the shell layer so it can import from both BCs without
    violating the Clean Architecture dependency rule inside each bounded context.

    COMM-1 contract (context_communication.json):
      BC-1 calls pre_seed_context / process_turn
      → shell adapter translates DTO → BC-2 command → BC-2 result → DTO
    """

    def __init__(
        self,
        pre_seed_use_case: PreSeedContextUseCase,
        process_turn_use_case: ProcessTurnIntelligenceUseCase,
    ) -> None:
        self._pre_seed_use_case = pre_seed_use_case
        self._process_turn_use_case = process_turn_use_case

    def pre_seed_context(self, dto: PreSeedContextDTO) -> None:
        self._pre_seed_use_case.execute(
            session_id=dto.session_id,
            school_id=dto.school_id,
            school_name=dto.school_name,
            purchase_signals=dto.purchase_signals,
        )

    def process_turn(self, dto: TurnInputDTO) -> TurnIntelligenceResultDTO:
        command = ProcessTurnIntelligenceCommand(
            session_id=dto.session_id,
            intent=dto.intent,
            message=dto.message,
            turn_number=dto.turn_number,
            conversation_history=dto.conversation_history,
        )
        result = self._process_turn_use_case.execute(command)
        return TurnIntelligenceResultDTO(
            evidence_chunks=result.evidence_chunks,
            evidence_type=result.evidence_type,
            context_recall_score=result.context_recall_score,
            context_precision_score=result.context_precision_score,
            context_state=result.context_state,
            clarification_needed=result.clarification_needed,
            clarification_question=result.clarification_question,
            school_name=result.school_name,
        )
