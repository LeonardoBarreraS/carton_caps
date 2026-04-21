from __future__ import annotations

import sqlite3
from typing import Optional

from conversation_management.domain.value_objects.school import School
from conversation_management.domain.ports.i_school_repository import ISchoolRepository


class SQLiteSchoolRepository(ISchoolRepository):
    """
    Read-only implementation of ISchoolRepository backed by the existing
    carton_caps_data.sqlite Schools and Users tables.

    Resolves the school for a user via a JOIN — provides the fundraising
    anchor seed for DecisionContext initialization (INV-CS-3).
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def find_by_user_id(self, user_id: str) -> Optional[School]:
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            return None

        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                """
                SELECT s.id, s.name, s.address
                FROM Schools s
                JOIN Users u ON u.school_id = s.id
                WHERE u.id = ?
                """,
                (uid,),
            ).fetchone()
            if row is None:
                return None
            return School(
                school_id=str(row["id"]),
                name=row["name"],
                address=row["address"],
            )
        finally:
            conn.close()
