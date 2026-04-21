from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from decision_intelligence.domain.models import ContextStatus
from decision_intelligence.domain.value_objects.school_anchor import SchoolAnchor
from decision_intelligence.domain.value_objects.preference_signal import PreferenceSignal
from decision_intelligence.domain.events.context_updated import ContextUpdated
from decision_intelligence.domain.events.gap_detected import GapDetected
from decision_intelligence.domain.events.context_ready import ContextReady


class InvalidContextTransitionError(Exception):
    """Raised when a DecisionContext state transition violates INV-DC-3."""


# States from which context has already reached readiness — cannot regress.
_NO_REGRESSION_STATES = {ContextStatus.READY, ContextStatus.ENRICHED}


@dataclass
class DecisionContext:
    """
    Aggregate root — The core intelligence asset of the system.

    Progressively accumulates user preference signals across turns.
    Signals are never removed — accumulation is strictly monotonic.
    School anchor is always present and never changes.
    State drives retrieval readiness for the RAG pipeline.

    Invariants enforced:
      INV-DC-1 — status is always a valid ContextStatus
      INV-DC-2 — school_anchor always present and never null
      INV-DC-3 — state never regresses; transition guards enforced
      INV-DC-5 — signals accumulate monotonically; add_signal never removes
      INV-DC-6 — ready/enriched requires at least one signal beyond school anchor
    """

    context_id: str            # equals session_id — 1:1 with ConversationSession
    session_id: str
    school_anchor: SchoolAnchor
    status: ContextStatus
    created_at: datetime
    updated_at: datetime

    _signals: list[PreferenceSignal] = field(default_factory=list, repr=False, compare=False)
    _identified_gaps: list[str] = field(default_factory=list, repr=False, compare=False)
    _events: list = field(default_factory=list, repr=False, compare=False)
    _pending_retrieval_intent: Optional[str] = field(default=None, repr=False, compare=False)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(cls, session_id: str, school_anchor: SchoolAnchor) -> DecisionContext:
        """
        Create a new DecisionContext in *empty* state, pre-seeded with school anchor.

        INV-DC-2: school_anchor must not be null.
        context_id equals session_id (1:1 relationship).
        """
        if school_anchor is None:
            raise ValueError(
                "school_anchor must not be null — INV-DC-2: school is always present"
            )
        now = datetime.now(timezone.utc)
        return cls(
            context_id=session_id,
            session_id=session_id,
            school_anchor=school_anchor,
            status=ContextStatus.EMPTY,
            created_at=now,
            updated_at=now,
            _signals=[],
            _identified_gaps=[],
            _events=[],
            _pending_retrieval_intent=None,
        )

    # ------------------------------------------------------------------
    # Behaviour
    # ------------------------------------------------------------------

    def add_signal(self, signal: PreferenceSignal) -> None:
        """
        Accumulate a new preference signal.

        Idempotent — signals with an identical key+value pair are not duplicated.
        Monotonic — signals are only ever appended, never removed (INV-DC-5).

        State transitions driven by this method:
          empty    → partial   (first signal added)
          partial  → partial   (subsequent signals, gaps may remain)
          ready    → enriched  (signal added after context reached readiness)
          enriched → enriched  (further refinement)
        """
        # Idempotency: skip exact duplicates
        if any(s.key == signal.key and s.value == signal.value for s in self._signals):
            return

        self._signals.append(signal)
        self._touch()

        if self.status == ContextStatus.EMPTY:
            self.status = ContextStatus.PARTIAL
        elif self.status == ContextStatus.READY:
            self.status = ContextStatus.ENRICHED

        self._events.append(
            ContextUpdated(
                session_id=self.session_id,
                context_state=self.status.value,
                signal_count=len(self._signals),
                occurred_at=self.updated_at,
            )
        )

    def record_gap_evaluation(self, gaps: list[str]) -> None:
        """
        Record gaps identified by the application-layer gap evaluation step.

        May only be called when context is in *partial* state.
        Emits GapDetected if gaps are non-empty.
        """
        if self.status != ContextStatus.PARTIAL:
            raise InvalidContextTransitionError(
                f"record_gap_evaluation may only be called in 'partial' state, "
                f"current state: '{self.status.value}'"
            )
        self._identified_gaps = list(gaps)
        self._touch()
        if gaps:
            self._events.append(
                GapDetected(
                    session_id=self.session_id,
                    gaps=list(gaps),
                    occurred_at=self.updated_at,
                )
            )

    def mark_ready(self) -> None:
        """
        Transition partial → ready.

        Called by the application layer when gap evaluation passes and
        sufficient signals exist for a meaningful retrieval query.

        INV-DC-6: at least one signal beyond school anchor must be present.
        """
        if self.status != ContextStatus.PARTIAL:
            raise InvalidContextTransitionError(
                f"mark_ready requires 'partial' state, current: '{self.status.value}'"
            )
        if not self._signals:
            raise InvalidContextTransitionError(
                "mark_ready requires at least one PreferenceSignal — INV-DC-6"
            )
        self.status = ContextStatus.READY
        self._touch()
        self._events.append(
            ContextReady(
                session_id=self.session_id,
                signal_count=len(self._signals),
                occurred_at=self.updated_at,
            )
        )

    # ------------------------------------------------------------------
    # Query methods (read-only)
    # ------------------------------------------------------------------

    def is_ready_for_retrieval(self) -> bool:
        """True when context is ready or enriched — retrieval can proceed (INV-DC-4)."""
        return self.status in _NO_REGRESSION_STATES

    def has_gap(self) -> bool:
        """True when context is partial and identified gaps are non-empty."""
        return self.status == ContextStatus.PARTIAL and bool(self._identified_gaps)

    @property
    def pending_retrieval_intent(self) -> Optional[str]:
        """The original retrieval intent saved when a clarification was requested."""
        return self._pending_retrieval_intent

    def set_pending_retrieval_intent(self, intent: str) -> None:
        """
        Save the original retrieval intent when a clarification gap is detected.

        Called by evaluate_context_readiness when clarification is needed,
        so the intent can be resumed once the user answers.
        """
        self._pending_retrieval_intent = intent
        self._touch()

    def clear_pending_retrieval_intent(self) -> None:
        """Clear the saved retrieval intent once it has been resumed."""
        self._pending_retrieval_intent = None
        self._touch()

    @property
    def signals(self) -> list[PreferenceSignal]:
        """Read-only view of accumulated signals."""
        return list(self._signals)

    @property
    def identified_gaps(self) -> list[str]:
        """Read-only view of identified gaps."""
        return list(self._identified_gaps)

    def snapshot(self) -> dict:
        """
        Return a read-only primitive snapshot of the current context state.

        Used by the application layer for retrieval query construction
        and response generation context. Exposes no mutable internals.
        """
        return {
            "session_id": self.session_id,
            "school_id": self.school_anchor.school_id,
            "school_name": self.school_anchor.school_name,
            "context_status": self.status.value,
            "signals": [
                {"key": s.key, "value": s.value, "turn_number": s.turn_number}
                for s in self._signals
            ],
            "identified_gaps": list(self._identified_gaps),
            "pending_retrieval_intent": self._pending_retrieval_intent,
        }

    # ------------------------------------------------------------------
    # Event collection helpers
    # ------------------------------------------------------------------

    def collect_events(self) -> list:
        """Drain and return all pending domain events."""
        events = list(self._events)
        self._events.clear()
        return events

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
