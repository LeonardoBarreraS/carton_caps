from __future__ import annotations

from ..domain.models import IngestionReport
from ..domain.ports import IDocumentTransformer, IKnowledgeSource, IVectorStoreWriter

COLLECTION_NAME = "referral_program_rules"


class IngestReferralRulesUseCase:
    """Reads referral rule documents from the source, splits each PDF into
    self-contained semantic chunks, and writes them to the referral_program_rules
    vector store collection.

    Clears the collection before writing so re-ingestion is always idempotent.
    """

    def __init__(
        self,
        source: IKnowledgeSource,
        transformer: IDocumentTransformer,
        writer: IVectorStoreWriter,
    ) -> None:
        self._source = source
        self._transformer = transformer
        self._writer = writer

    def execute(self) -> IngestionReport:
        records = self._source.load()
        documents = []
        errors: list[str] = []

        for record in records:
            try:
                docs = self._transformer.transform(record)
                documents.extend(docs)
            except Exception as exc:
                errors.append(f"Record {record.id}: {exc}")

        self._writer.clear_collection(COLLECTION_NAME)
        self._writer.write_batch(COLLECTION_NAME, documents)

        return IngestionReport(
            collection=COLLECTION_NAME,
            documents_written=len(documents),
            errors=errors,
        )
