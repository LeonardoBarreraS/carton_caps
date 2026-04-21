from __future__ import annotations

from dataclasses import dataclass


# INV-AR-2: A product must have a non-empty name.
@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    category: str
    brand: str
    description: str
    attributes: dict[str, str]

    def __post_init__(self) -> None:
        if not self.product_id.strip():
            raise ValueError("product_id must not be empty")
        if not self.name.strip():
            raise ValueError("Product name must not be empty")
