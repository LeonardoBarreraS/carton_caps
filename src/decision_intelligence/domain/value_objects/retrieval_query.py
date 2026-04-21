from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from decision_intelligence.domain.models import ContextStatus, SourceTarget


# Routing table: intent string → SourceTarget  (INV-RQ-2, INV-RQ-3)
_INTENT_TO_SOURCE: dict[str, SourceTarget] = {
    "product_inquiry": SourceTarget.PRODUCT_CATALOG,
    "referral_question": SourceTarget.REFERRAL_PROGRAM_RULES,
}

_RETRIEVAL_INTENTS = frozenset(_INTENT_TO_SOURCE)


class InvalidRetrievalQueryError(Exception):
    """Raised when a RetrievalQuery violates INV-RQ-2 or INV-RQ-3."""


@dataclass(frozen=True)
class RetrievalQuery:
    """
    Context-enriched query artifact built from DecisionContext + Intent.

    Drives knowledge source routing. Must never be constructed from
    the raw user message alone (INV-RQ-1).

    Invariants enforced:
      INV-RQ-1 — query_text is the enriched form; raw message is not accepted here
      INV-RQ-2 — source_target must be product_catalog or referral_program_rules
      INV-RQ-3 — source_target validated against originating_intent
    """

    query_id: str
    session_id: str
    query_text: str         # enriched, constructed text — never the raw user message
    source_target: SourceTarget
    originating_intent: str
    context_state_at_creation: ContextStatus
    created_at: datetime

    @classmethod
    def from_context(
        cls,
        session_id: str,
        query_text: str,
        intent: str,
        context_status: ContextStatus,
    ) -> RetrievalQuery:
        """
        Factory — the only correct way to construct a RetrievalQuery.

        intent must be 'product_inquiry' or 'referral_question' (INV-RQ-3).
        source_target is derived automatically from intent (INV-RQ-2).
        query_text is accepted as-is; the caller (application layer) is
        responsible for ensuring it is context-enriched, not raw (INV-RQ-1).
        """
        if not query_text:
            raise ValueError("query_text must not be empty")

        source_target = _INTENT_TO_SOURCE.get(intent)
        if source_target is None:
            raise InvalidRetrievalQueryError(
                f"Cannot construct RetrievalQuery for intent '{intent}'. "
                f"Only {sorted(_RETRIEVAL_INTENTS)} intents require retrieval — INV-RQ-3"
            )

        return cls(
            query_id=str(uuid.uuid4()),
            session_id=session_id,
            query_text=query_text,
            source_target=source_target,
            originating_intent=intent,
            context_state_at_creation=context_status,
            created_at=datetime.now(timezone.utc),
        )
