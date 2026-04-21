from __future__ import annotations

from abc import ABC, abstractmethod

from .models import IngestionDocument, RawRecord


class IKnowledgeSource(ABC):
    """Reads raw records from a knowledge source (SQLite, PDF, etc.)."""

    @abstractmethod
    def load(self) -> list[RawRecord]:
        ...


class IDocumentTransformer(ABC):
    """Transforms a raw record into one or more semantically labeled ingestion documents.

    A product record produces exactly one enriched document.
    A PDF record produces N documents — one per semantic unit (rule, FAQ entry, section).
    """

    @abstractmethod
    def transform(self, record: RawRecord) -> list[IngestionDocument]:
        ...


class IVectorStoreWriter(ABC):
    """Writes ingestion documents to a named collection in the vector store."""

    @abstractmethod
    def write_batch(self, collection_name: str, documents: list[IngestionDocument]) -> None:
        ...

    @abstractmethod
    def clear_collection(self, collection_name: str) -> None:
        """Removes the collection entirely so re-ingestion starts clean."""
        ...
