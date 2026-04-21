from __future__ import annotations

from decision_intelligence.domain.entities.decision_context import DecisionContext
from decision_intelligence.domain.value_objects.school_anchor import SchoolAnchor
from decision_intelligence.domain.value_objects.preference_signal import PreferenceSignal
from decision_intelligence.domain.ports.i_decision_context_repository import IDecisionContextRepository


class PreSeedContextUseCase:
    """
    UC-4 — Create and pre-seed a DecisionContext for a new session.

    Called once per session during session initialization, invoked indirectly
    via IDecisionIntelligenceService.pre_seed_context → DecisionIntelligenceAdapter
    → this use case.

    Creates a DecisionContext anchored to the school. Optionally converts
    purchase history strings into early PreferenceSignals.

    INV-DC-2: DecisionContext created with school anchor, never blank.
    INV-CS-3: school anchor pre-seeded before any conversation turn begins.
    """

    def __init__(self, decision_context_repository: IDecisionContextRepository) -> None:#------->> OJO ACÁ REVISAR COMO ESTE REPOSITORIO. 
        self._repository = decision_context_repository

    def execute(
        self,
        session_id: str,
        school_id: str,
        school_name: str,
        purchase_signals: list[str],
    ) -> None:
        school_anchor = SchoolAnchor(school_id=school_id, school_name=school_name)
        context = DecisionContext.create(session_id=session_id, school_anchor=school_anchor)

        # Seed purchase history as early preference signals.
        # turn_number=1 — these are available from the first turn.
        for signal_text in purchase_signals:
            if signal_text and signal_text.strip():
                signal = PreferenceSignal(
                    key="purchase_history",
                    value=signal_text.strip(),
                    turn_number=1,
                )
                context.add_signal(signal)

        self._repository.save(context)
