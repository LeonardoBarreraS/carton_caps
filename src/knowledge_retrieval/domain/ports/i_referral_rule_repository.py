from __future__ import annotations

from abc import ABC, abstractmethod

from knowledge_retrieval.domain.value_objects.referral_rule import ReferralRule


class IReferralRuleRepository(ABC):
    @abstractmethod
    def search(self, query_text: str, top_k: int) -> list[ReferralRule]:
        """Return the top_k most relevant referral rules for the given query_text."""
        ...
