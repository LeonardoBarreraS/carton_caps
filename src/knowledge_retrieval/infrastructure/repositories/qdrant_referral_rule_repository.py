from __future__ import annotations

from openai import OpenAI
from qdrant_client import QdrantClient

from knowledge_retrieval.domain.value_objects.referral_rule import ReferralRule
from knowledge_retrieval.domain.models import RuleType
from knowledge_retrieval.domain.ports.i_referral_rule_repository import IReferralRuleRepository

_EMBEDDING_MODEL = "text-embedding-3-small"

_LABEL_TO_RULE_TYPE: dict[str, RuleType] = {
    "eligibility": RuleType.ELIGIBILITY,
    "bonus": RuleType.BONUS,
    "invitation": RuleType.INVITATION,
    "requirement": RuleType.REQUIREMENT,
}


class QdrantReferralRuleRepository(IReferralRuleRepository):
    """
    Implements IReferralRuleRepository via semantic search over the
    referral_program_rules Qdrant collection populated during ingestion.

    Uses the same embedding model as the write side (text-embedding-3-small).
    Point payload label field is mapped to RuleType; defaults to ELIGIBILITY
    when the label does not match a known RuleType value.
    """

    def __init__(
        self,
        qdrant_url: str,
        openai_client: OpenAI,
        collection_name: str = "referral_program_rules",
        qdrant_api_key: str | None = None,
    ) -> None:
        self._qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self._openai = openai_client
        self._collection = collection_name

    def search(self, query_text: str, top_k: int) -> list[ReferralRule]:
        embedding = self._embed(query_text)
        results = self._qdrant.query_points(
            collection_name=self._collection,
            query=embedding,
            limit=top_k,
            with_payload=True,
        ).points
        rules: list[ReferralRule] = []
        for point in results:
            payload = point.payload or {}
            label = (payload.get("label") or "").lower()
            rule_type = _LABEL_TO_RULE_TYPE.get(label, RuleType.ELIGIBILITY)
            rules.append(
                ReferralRule(
                    rule_id=str(payload.get("doc_id", str(point.id))),
                    title=payload.get("label", "rule"),
                    description=payload.get("text", ""),
                    rule_type=rule_type,
                )
            )
        return rules

    def _embed(self, text: str) -> list[float]:
        response = self._openai.embeddings.create(model=_EMBEDDING_MODEL, input=[text])
        return response.data[0].embedding
