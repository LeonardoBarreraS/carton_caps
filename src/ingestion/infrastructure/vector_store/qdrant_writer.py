from __future__ import annotations

import uuid

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from ...domain.models import IngestionDocument
from ...domain.ports import IVectorStoreWriter

_EMBEDDING_MODEL = "text-embedding-3-small"
_OPENAI_BATCH_SIZE = 500
_VECTOR_SIZE = 1536


def _stable_point_id(doc_id: str) -> str:
    """Derive a deterministic UUID from the document string ID for use as Qdrant point ID."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))


class QdrantVectorStoreWriter(IVectorStoreWriter):
    """
    Writes ingestion documents to a Qdrant persistent vector store.

    Embeddings are generated via the OpenAI embeddings API and upserted as
    Qdrant points with the document text and metadata as payload.

    This is the write-side counterpart to QdrantProductRepository and
    QdrantReferralRuleRepository in COMP-3. Both sides share the same
    collections and use the same embedding model — no code dependency exists
    between ingestion and the runtime retrieval components.
    """

    def __init__(
        self,
        qdrant_url: str,
        openai_client: OpenAI,
        collection_vector_size: int = _VECTOR_SIZE,
        qdrant_api_key: str | None = None,
    ) -> None:
        self._qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self._openai = openai_client
        self._vector_size = collection_vector_size

    def write_batch(self, collection_name: str, documents: list[IngestionDocument]) -> None:
        if not documents:
            return

        for batch_start in range(0, len(documents), _OPENAI_BATCH_SIZE):
            batch = documents[batch_start : batch_start + _OPENAI_BATCH_SIZE]
            texts = [doc.text for doc in batch]
            embeddings = self._embed(texts)

            points = [
                PointStruct(
                    id=_stable_point_id(doc.id),
                    vector=embedding,
                    payload={"doc_id": doc.id, "text": doc.text, **doc.metadata},
                )
                for doc, embedding in zip(batch, embeddings)
            ]
            self._qdrant.upsert(collection_name=collection_name, points=points)

    def clear_collection(self, collection_name: str) -> None:
        try:
            self._qdrant.delete_collection(collection_name)
        except Exception:
            pass
        self._qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=self._vector_size, distance=Distance.COSINE),
        )

    def _embed(self, texts: list[str]) -> list[list[float]]:
        response = self._openai.embeddings.create(model=_EMBEDDING_MODEL, input=texts)
        return [item.embedding for item in response.data]
