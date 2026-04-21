from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SchoolAnchor:
    """
    Immutable value object carrying the school identity pre-seeded into
    DecisionContext at session init.

    The fundraising anchor — always present, never changes (INV-DC-2).
    """

    school_id: str
    school_name: str

    def __post_init__(self) -> None:
        if not self.school_id:
            raise ValueError("SchoolAnchor.school_id must not be empty")
        if not self.school_name:
            raise ValueError("SchoolAnchor.school_name must not be empty")
