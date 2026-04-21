from __future__ import annotations

from dataclasses import dataclass

from knowledge_retrieval.domain.models import RuleType


# INV-AR-3: A referral rule must have a non-empty title, description, and a valid rule_type.
@dataclass(frozen=True)
class ReferralRule:
    rule_id: str
    title: str
    description: str
    rule_type: RuleType

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("rule_id must not be empty")
        if not self.title.strip():
            raise ValueError("ReferralRule title must not be empty")
        if not self.description.strip():
            raise ValueError("ReferralRule description must not be empty")
