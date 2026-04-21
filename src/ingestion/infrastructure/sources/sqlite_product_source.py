from __future__ import annotations

import sqlite3
from pathlib import Path

from ...domain.models import RawRecord
from ...domain.ports import IKnowledgeSource


class SQLiteProductSource(IKnowledgeSource):
    """Reads all rows from the products table in the SQLite database.

    Returns one RawRecord per product. Only the fields relevant to
    semantic enrichment are loaded: id, name, description, price.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = Path(db_path)

    def load(self) -> list[RawRecord]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT id, name, description, price FROM products"
            )
            rows = cursor.fetchall()
            return [
                RawRecord(
                    id=str(row["id"]),
                    content={
                        "name": row["name"] or "",
                        "description": row["description"] or "",
                        "price": float(row["price"]) if row["price"] is not None else 0.0,
                    },
                )
                for row in rows
            ]
        finally:
            conn.close()
