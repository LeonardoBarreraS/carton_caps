from __future__ import annotations

from openai import OpenAI

from .application.ingest_product_catalog import IngestProductCatalogUseCase
from .application.ingest_referral_rules import IngestReferralRulesUseCase
from .config import OPENAI_API_KEY, PDF_DOCS_DIR, QDRANT_API_KEY, QDRANT_URL, SQLITE_DB_PATH
from .infrastructure.sources.pdf_referral_source import PDFReferralSource
from .infrastructure.sources.sqlite_product_source import SQLiteProductSource
from .infrastructure.transformers.product_semantic_builder import ProductSemanticBuilder
from .infrastructure.transformers.referral_semantic_builder import ReferralSemanticBuilder
from .infrastructure.vector_store.qdrant_writer import QdrantVectorStoreWriter


def run() -> None:
    """Composition root and entry point for the ingestion pipeline.

    Wires all ports to their adapters and runs both pipelines sequentially.
    This function is the only place that knows about all infrastructure components.
    """
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    writer = QdrantVectorStoreWriter(
        qdrant_url=QDRANT_URL,
        openai_client=openai_client,
        qdrant_api_key=QDRANT_API_KEY,
    )

    # --- Pipeline 1: Product Catalog ---
    print("[1/2] Ingesting product catalog from SQLite...")
    product_report = IngestProductCatalogUseCase(
        source=SQLiteProductSource(SQLITE_DB_PATH),
        transformer=ProductSemanticBuilder(openai_client),
        writer=writer,
    ).execute()

    print(f"      Documents written : {product_report.documents_written}")
    if product_report.errors:
        print(f"      Errors           : {len(product_report.errors)}")
        for err in product_report.errors:
            print(f"        - {err}")

    # --- Pipeline 2: Referral Rules ---
    print("[2/2] Ingesting referral rules from PDF documents...")
    referral_report = IngestReferralRulesUseCase(
        source=PDFReferralSource(PDF_DOCS_DIR),
        transformer=ReferralSemanticBuilder(openai_client),
        writer=writer,
    ).execute()

    print(f"      Documents written : {referral_report.documents_written}")
    if referral_report.errors:
        print(f"      Errors           : {len(referral_report.errors)}")
        for err in referral_report.errors:
            print(f"        - {err}")

    print("\nIngestion complete.")
    print(f"  product_catalog       : {product_report.documents_written} documents")
    print(f"  referral_program_rules: {referral_report.documents_written} documents")

