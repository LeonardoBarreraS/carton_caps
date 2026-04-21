from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from conversation_management.domain.models import SessionStatus
from conversation_management.domain.value_objects.intent import Intent
from conversation_management.domain.value_objects.assistant_response import AssistantResponse
from conversation_management.domain.events.session_started import SessionStarted
from conversation_management.domain.events.turn_processed import TurnProcessed
from conversation_management.domain.events.session_closed import SessionClosed


class InvalidSessionTransitionError(Exception):
    """Raised when a ConversationSession state transition violates INV-CS-2."""


@dataclass
class ConversationSession:
    """
    Aggregate root — Lifecycle owner of a multi-turn user conversation.

    Manages session state transitions from creation to closure.
    Enforces turn sequencing and session-level invariants.

    Invariants enforced:
      INV-CS-1 — status is always a valid SessionStatus
      INV-CS-2 — only allowed state transitions are executed
      INV-CS-6 — user_id must be provided (pre-resolved by external auth)
    """

    session_id: str
    user_id: str
    school_id: str
    status: SessionStatus
    turn_count: int
    created_at: datetime
    updated_at: datetime

    # Collect domain events raised during the lifetime of this instance.
    # The application layer drains this list after each operation.
    _events: list = field(default_factory=list, repr=False, compare=False)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(cls, user_id: str, school_id: str) -> ConversationSession:
        """
        Create a new session in the *created* state.

        INV-CS-6: user_id must be provided.
        """
        if not user_id:
            raise ValueError("user_id must be provided — identity is pre-resolved by external auth")
        if not school_id:
            raise ValueError("school_id must be provided")

        now = datetime.now(timezone.utc)
        return cls(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            school_id=school_id,
            status=SessionStatus.CREATED,
            turn_count=0,
            created_at=now,
            updated_at=now,
            _events=[],
        )

    # ------------------------------------------------------------------
    # Behaviour — guarded state transitions
    # ------------------------------------------------------------------

    def begin_initialization(self) -> None:
        """
        Transition: created → initializing.
        Called when session startup begins (loading user profile, school, history).
        """
        self._assert_status(SessionStatus.CREATED, "begin_initialization")
        self.status = SessionStatus.INITIALIZING
        self._touch()

    def complete_initialization(self) -> None:
        """
        Transition: initializing → idle.
        Called when all session data is loaded and DecisionContext is pre-seeded.
        Emits: SessionStarted
        """
        self._assert_status(SessionStatus.INITIALIZING, "complete_initialization")
        self.status = SessionStatus.IDLE
        self._touch()
        self._events.append(
            SessionStarted(
                session_id=self.session_id,
                user_id=self.user_id,
                school_id=self.school_id,
                occurred_at=self.updated_at,
            )
        )

    def receive_message(self) -> None:
        """
        Transition: idle → active.
        Called when a new user message arrives on an established session.
        """
        self._assert_status(SessionStatus.IDLE, "receive_message")
        self.status = SessionStatus.ACTIVE
        self._touch()

    def complete_turn(self, intent: Intent, response: AssistantResponse) -> None:
        """
        Transition: active → idle.
        Called when a conversation turn finishes and a response has been produced.
        Emits: TurnProcessed
        """
        self._assert_status(SessionStatus.ACTIVE, "complete_turn")
        self.turn_count += 1
        self.status = SessionStatus.IDLE
        self._touch()
        self._events.append(
            TurnProcessed(
                session_id=self.session_id,
                turn_count=self.turn_count,
                intent_value=intent.value.value,
                occurred_at=self.updated_at,
            )
        )

    def fail_turn(self) -> None:
        """
        Rollback: active → idle.
        Called when a turn fails mid-execution (e.g. uncaught exception in TurnGraph).
        Restores the session to idle so the user can retry without starting a new session.
        No domain events are emitted — a failed turn is not a completed turn.
        """
        self._assert_status(SessionStatus.ACTIVE, "fail_turn")
        self.status = SessionStatus.IDLE
        self._touch()

    def close(self) -> None:
        """
        Transition: idle → closed.
        Terminal state — no further turns will be processed.
        Emits: SessionClosed
        """
        self._assert_status(SessionStatus.IDLE, "close")
        self.status = SessionStatus.CLOSED
        self._touch()
        self._events.append(
            SessionClosed(
                session_id=self.session_id,
                user_id=self.user_id,
                occurred_at=self.updated_at,
            )
        )

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

    def _assert_status(self, expected: SessionStatus, operation: str) -> None:
        """Guard — raises InvalidSessionTransitionError if current status is wrong."""
        if self.status != expected:
            raise InvalidSessionTransitionError(
                f"Cannot call '{operation}' on session in '{self.status.value}' state "
                f"(expected '{expected.value}'). Session ID: {self.session_id}"
            )

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
