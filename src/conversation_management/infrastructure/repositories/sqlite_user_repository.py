from __future__ import annotations

import sqlite3
from typing import Optional

from conversation_management.domain.value_objects.user import User
from conversation_management.domain.ports.i_user_repository import IUserRepository


class SQLiteUserRepository(IUserRepository):
    """
    Read-only implementation of IUserRepository backed by the existing
    carton_caps_data.sqlite Users table.

    Identity is pre-resolved by external auth — this adapter never mutates.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def find_by_id(self, user_id: str) -> Optional[User]:
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            return None

        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT id, school_id, name FROM Users WHERE id = ?", (uid,)
            ).fetchone()
            if row is None:
                return None
            return User(
                user_id=str(row["id"]),
                school_id=str(row["school_id"]),
                name=str(row["name"]) if row["name"] else "",
            )
        finally:
            conn.close()
