from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PreferenceSignal:
    """
    A single user preference or constraint extracted from one conversation turn.

    Immutable once created. Accumulated monotonically into DecisionContext —
    once added, never removed (INV-DC-5).
    """

    key: str
    value: str
    turn_number: int

    def __post_init__(self) -> None:
        if not self.key:
            raise ValueError("PreferenceSignal.key must not be empty")
        if not self.value:
            raise ValueError("PreferenceSignal.value must not be empty")
        if self.turn_number < 1:
            raise ValueError(
                f"PreferenceSignal.turn_number must be >= 1, got {self.turn_number}"
            )
