from __future__ import annotations

import chromadb
from chromadb import Settings
from openai import OpenAI

from ...domain.models import IngestionDocument
from ...domain.ports import IVectorStoreWriter

_EMBEDDING_MODEL = "text-embedding-3-small"
_OPENAI_BATCH_SIZE = 500  # embeddings API limit is 2048; 500 is a safe batch size


class ChromaVectorStoreWriter(IVectorStoreWriter):
    """Writes ingestion documents to a ChromaDB persistent vector store.

    Embeddings are generated via the OpenAI embeddings API and stored alongside
    the document text and metadata. This is the write-side counterpart to the
    ProductVectorStoreRepository and ReferralRuleVectorStoreRepository in COMP-3.

    Both components share the vector store as a storage contract — there is no
    code dependency between ingestion and the runtime retrieval components.
    """

    def __init__(self, persist_directory: str, openai_client: OpenAI) -> None:
        self._chroma = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )
        self._openai = openai_client

    def write_batch(self, collection_name: str, documents: list[IngestionDocument]) -> None:
        if not documents:
            return

        collection = self._chroma.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # Process in batches to stay within API limits
        for batch_start in range(0, len(documents), _OPENAI_BATCH_SIZE):
            batch = documents[batch_start : batch_start + _OPENAI_BATCH_SIZE]
            texts = [doc.text for doc in batch]
            embeddings = self._embed(texts)

            collection.add(
                ids=[doc.id for doc in batch],
                embeddings=embeddings,
                documents=texts,
                metadatas=[doc.metadata for doc in batch],
            )

    def clear_collection(self, collection_name: str) -> None:
        try:
            self._chroma.delete_collection(collection_name)
        except Exception:
            pass  # No-op if collection does not exist yet

    def _embed(self, texts: list[str]) -> list[list[float]]:
        response = self._openai.embeddings.create(
            model=_EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]
