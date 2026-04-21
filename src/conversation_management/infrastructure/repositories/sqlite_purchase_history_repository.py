from __future__ import annotations

import sqlite3

from conversation_management.domain.ports.i_purchase_history_repository import (
    IPurchaseHistoryRepository,
)


class SQLitePurchaseHistoryRepository(IPurchaseHistoryRepository):
    """
    Read-only implementation of IPurchaseHistoryRepository backed by the
    existing carton_caps_data.sqlite Purchase_History table joined with Products.

    Returns raw dicts as specified by the port contract (list[dict]).
    Used by StartSessionUseCase to forward purchase signals to DecisionContext
    pre-seeding via PreSeedContextDTO.purchase_signals.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def find_by_user_id(self, user_id: str) -> list[dict]:
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            return []

        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT ph.id, ph.product_id, p.name AS product_name,
                       ph.quantity, ph.purchased_at
                FROM Purchase_History ph
                JOIN Products p ON p.id = ph.product_id
                WHERE ph.user_id = ?
                ORDER BY ph.purchased_at DESC
                """,
                (uid,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
