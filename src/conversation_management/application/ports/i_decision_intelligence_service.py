from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PreSeedContextDTO:
    """
    Data transferred from BC-1 to BC-2 at session initialization.
    Carries the minimum data needed to create a DecisionContext anchored to a school.
    """

    session_id: str
    school_id: str
    school_name: str
    purchase_signals: list[str] = field(default_factory=list)


@dataclass
class TurnInputDTO:
    """
    Data transferred from BC-1 to BC-2 on every conversation turn.
    Intent is passed as its string value — not as the domain Intent value object.
    conversation_history is the full prior conversation in OpenAI message format.
    """

    session_id: str
    intent: str
    message: str
    turn_number: int
    conversation_history: list[dict] = field(default_factory=list)


@dataclass
class TurnIntelligenceResultDTO:
    """
    Data returned by BC-2 to BC-1 after processing a turn.
    All fields are primitives — no BC-2 domain objects cross the boundary.
    """

    evidence_chunks: list[str]
    evidence_type: str
    context_recall_score: float
    context_precision_score: float
    context_state: str  # empty | partial | ready | enriched
    clarification_needed: bool
    clarification_question: Optional[str]
    school_name: str = ""


class IDecisionIntelligenceService(ABC):
    """
    Application-layer cross-context port to COMP-2 (Decision Intelligence).

    Defined in BC-1 — BC-1 owns this contract; it defines what it needs,
    not how COMP-2 works internally.

    Implemented in the shell layer as a thin adapter that calls
    COMP-2 use cases (PreSeedContextUseCase, ProcessTurnIntelligenceUseCase).
    """

    @abstractmethod
    def pre_seed_context(self, dto: PreSeedContextDTO) -> None:
        """
        Called once per session during StartSessionUseCase.
        Creates the DecisionContext pre-seeded with school anchor
        and any available purchase history signals.

        INV-CS-3: school must be resolved before the first turn.
        """
        ...

    @abstractmethod
    def process_turn(self, dto: TurnInputDTO) -> TurnIntelligenceResultDTO:
        """
        Called on every turn by TurnGraph.process_decision_intelligence node.

        Returns TurnIntelligenceResultDTO with evidence or clarification signal.

        INV-WF-2: DecisionContext must be updated before RetrievalQuery is constructed.
        INV-WF-4: executes on every turn — cannot be skipped.
        """
        ...
