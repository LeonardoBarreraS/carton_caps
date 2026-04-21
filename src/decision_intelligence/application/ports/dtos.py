from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetrievalQueryDTO:
    """
    Data transferred from BC-2 to BC-3 for retrieval execution.
    Contains the enriched query text, the target knowledge source, and the
    number of documents to retrieve. top_k defaults to 5 and escalates on
    each retry attempt (construct_retrieval_query node).

    Defined in BC-2 ports layer — BC-2 owns this contract (COMM-2).
    """

    query_text: str
    source_target: str  # product_catalog | referral_program_rules
    top_k: int = 5


@dataclass
class RetrievedEvidenceDTO:
    """
    Data returned by BC-3 to BC-2 after retrieval execution.
    Contains raw retrieved content chunks and the evidence type.

    Defined in BC-2 ports layer — quality scoring (recall/precision)
    is applied by IEvidenceEvaluator inside BC-2 after this DTO is received.
    """

    chunks: list[str]
    evidence_type: str  # product_evidence | referral_rule_evidence
