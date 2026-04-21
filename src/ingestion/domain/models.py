from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RawRecord:
    """A raw record loaded from a knowledge source before any transformation."""
    id: str
    content: dict[str, Any]


@dataclass(frozen=True)
class IngestionDocument:
    """A semantically labeled, embedding-ready document to be written to the vector store."""
    id: str
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class IngestionReport:
    """Summary produced at the end of a single ingestion pipeline execution."""
    collection: str
    documents_written: int
    errors: list[str] = field(default_factory=list)
