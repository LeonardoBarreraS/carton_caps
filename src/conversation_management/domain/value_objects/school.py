from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class School:
    """
    The school the user supports through their purchases.

    Loaded from DB at session init. Provides the fundraising anchor
    passed to DecisionContext as a SchoolAnchor.

    This is an external reference value object — an immutable reference to a School entity
    managed by an external Master Data BC. It is never created or mutated within this bounded context.

    INV-CS-3: school must be resolved and pre-seeded before the first turn.
    """

    school_id: str
    name: str
    address: str
