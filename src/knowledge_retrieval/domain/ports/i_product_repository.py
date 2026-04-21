from __future__ import annotations

from abc import ABC, abstractmethod

from knowledge_retrieval.domain.value_objects.product import Product


class IProductRepository(ABC):
    @abstractmethod
    def search(self, query_text: str, top_k: int) -> list[Product]:
        """Return the top_k most relevant products for the given query_text."""
        ...
