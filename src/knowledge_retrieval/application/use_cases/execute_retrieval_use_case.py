from __future__ import annotations

from dataclasses import dataclass, field

from knowledge_retrieval.domain.ports.i_product_repository import IProductRepository
from knowledge_retrieval.domain.ports.i_referral_rule_repository import IReferralRuleRepository

_SOURCE_PRODUCT_CATALOG = "product_catalog"
_SOURCE_REFERRAL_RULES = "referral_program_rules"


class UnknownSourceTargetError(ValueError):
    """Raised when source_target is not a recognised knowledge source (INV-AR-2, INV-AR-3)."""


@dataclass
class ExecuteRetrievalCommand:
    query_text: str
    source_target: str  # product_catalog | referral_program_rules
    top_k: int = field(default=5)


@dataclass
class ExecuteRetrievalResponse:
    chunks: list[str]
    evidence_type: str  # product_evidence | referral_rule_evidence


class ExecuteRetrievalUseCase:
    """
    UC-6 — Route a retrieval query to the correct knowledge source and return
    the top-matching content chunks.

    Delegates to IProductRepository or IReferralRuleRepository based on
    source_target. Returns raw retrieved content — never invents or rewrites
    any content.

    INV-AR-2: product recommendations cite only retrieved products.
    INV-AR-3: referral guidance derived exclusively from retrieved rules.
    INV-AR-4: content returned as-is; no rewriting occurs here.
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        referral_rule_repository: IReferralRuleRepository,
    ) -> None:
        self._product_repository = product_repository
        self._referral_rule_repository = referral_rule_repository

    def execute(self, command: ExecuteRetrievalCommand) -> ExecuteRetrievalResponse:
        if command.source_target == _SOURCE_PRODUCT_CATALOG:
            products = self._product_repository.search(command.query_text, command.top_k)
            chunks = [
                f"{p.name} — {p.description} (Category: {p.category}, Brand: {p.brand})"
                for p in products
            ]
            return ExecuteRetrievalResponse(chunks=chunks, evidence_type="product_evidence")

        if command.source_target == _SOURCE_REFERRAL_RULES:
            rules = self._referral_rule_repository.search(command.query_text, command.top_k)
            chunks = [f"{r.title}: {r.description}" for r in rules]
            return ExecuteRetrievalResponse(chunks=chunks, evidence_type="referral_rule_evidence")

        raise UnknownSourceTargetError(
            f"source_target '{command.source_target}' is not a recognised knowledge source. "
            f"Expected '{_SOURCE_PRODUCT_CATALOG}' or '{_SOURCE_REFERRAL_RULES}'."
        )
