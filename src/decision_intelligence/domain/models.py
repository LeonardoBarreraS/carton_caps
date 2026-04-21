from __future__ import annotations

from enum import Enum


class ContextStatus(str, Enum):
    """Lifecycle states of a DecisionContext (INV-DC-1)."""
    EMPTY = "empty"
    PARTIAL = "partial"
    READY = "ready"
    ENRICHED = "enriched"


class SourceTarget(str, Enum):
    """Knowledge source that a RetrievalQuery should be routed to (INV-RQ-2)."""
    PRODUCT_CATALOG = "product_catalog"
    REFERRAL_PROGRAM_RULES = "referral_program_rules"
