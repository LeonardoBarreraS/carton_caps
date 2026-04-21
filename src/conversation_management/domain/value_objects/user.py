from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """
    Identity reference for the interacting user.

    Pre-resolved by the external auth API before any request reaches this service.
    Loaded from DB at session init. Never authenticated here.

    This is an external reference value object — an immutable reference to a User entity
    managed by an external Auth BC. It is never created or mutated within this bounded context.

    INV-CS-6: identity is pre-resolved; this service never authenticates.
    """

    user_id: str
    school_id: str
    name: str = ""
