from __future__ import annotations

from openai import OpenAI
from qdrant_client import QdrantClient

from knowledge_retrieval.domain.value_objects.product import Product
from knowledge_retrieval.domain.ports.i_product_repository import IProductRepository

_EMBEDDING_MODEL = "text-embedding-3-small"


class QdrantProductRepository(IProductRepository):
    """
    Implements IProductRepository via semantic search over the product_catalog
    Qdrant collection populated by QdrantVectorStoreWriter during ingestion.

    Uses the same embedding model as the write side to guarantee query-document
    vector space alignment (text-embedding-3-small).
    """

    def __init__(
        self,
        qdrant_url: str,
        openai_client: OpenAI,
        collection_name: str = "product_catalog",
        qdrant_api_key: str | None = None,
    ) -> None:
        self._qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        self._openai = openai_client
        self._collection = collection_name

    def search(self, query_text: str, top_k: int) -> list[Product]:
        embedding = self._embed(query_text)
        results = self._qdrant.query_points(
            collection_name=self._collection,
            query=embedding,
            limit=top_k,
            with_payload=True,
        ).points
        products: list[Product] = []
        for point in results:
            payload = point.payload or {}
            products.append(
                Product(
                    product_id=str(payload.get("product_id", payload.get("doc_id", str(point.id)))),
                    name=payload.get("name", ""),
                    category=payload.get("category", ""),
                    brand=payload.get("brand", ""),
                    description=payload.get("text", ""),
                    attributes={},
                )
            )
        return products

    def _embed(self, text: str) -> list[float]:
        response = self._openai.embeddings.create(model=_EMBEDDING_MODEL, input=[text])
        return response.data[0].embedding
