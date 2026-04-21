from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import List

from conversation_management.domain.entities.conversation_history import ConversationHistory
from conversation_management.domain.models import SenderType
from conversation_management.domain.ports.i_conversation_history_repository import (
    IConversationHistoryRepository,
)

# ---------------------------------------------------------------------------
# DDL — ensure optional columns exist on the pre-existing table.
# These statements are safe to run repeatedly: SQLite raises OperationalError
# ("duplicate column name") if the column already exists; we catch and ignore.
# ---------------------------------------------------------------------------
_ALTER_ADD_HISTORY_ID = (
    "ALTER TABLE Conversation_History ADD COLUMN history_id TEXT NOT NULL DEFAULT ''"
)
_ALTER_ADD_SESSION_ID = (
    "ALTER TABLE Conversation_History ADD COLUMN session_id TEXT NOT NULL DEFAULT ''"
)

_INSERT = """
INSERT INTO Conversation_History (history_id, user_id, session_id, message, sender, timestamp)
VALUES (?, ?, ?, ?, ?, ?)
"""

_FIND_BY_USER = """
SELECT id, history_id, user_id, session_id, message, sender, timestamp
FROM Conversation_History
WHERE user_id = ?
ORDER BY timestamp ASC
"""

# Map legacy "bot" value stored in pre-existing rows to the domain enum.
_SENDER_MAP: dict[str, SenderType] = {
    "user": SenderType.USER,
    "assistant": SenderType.ASSISTANT,
    "bot": SenderType.ASSISTANT,  # legacy value present in seeded data
}

# Map domain enum values → DB-accepted values on write.
# The Conversation_History table CHECK constraint only allows ('user', 'bot');
# the domain uses 'assistant', so we translate on the write path.
_DB_SENDER_MAP: dict[str, str] = {
    "user": "user",
    "assistant": "bot",  # domain 'assistant' → legacy DB value 'bot'
}


class SQLiteConversationHistoryRepository(IConversationHistoryRepository):
    """
    Read/write implementation of IConversationHistoryRepository backed by the
    existing carton_caps_data.sqlite Conversation_History table.

    On first use the adapter adds two optional columns (history_id, session_id)
    via ALTER TABLE if they are not already present — existing rows keep their
    default empty-string values.

    Replaces InMemoryConversationHistoryRepository for durable message storage.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._migrate()

    # ------------------------------------------------------------------
    # Schema migration
    # ------------------------------------------------------------------

    def _migrate(self) -> None:
        """Add history_id and session_id columns if not present."""
        conn = sqlite3.connect(self._db_path)
        try:
            for statement in (_ALTER_ADD_HISTORY_ID, _ALTER_ADD_SESSION_ID):
                try:
                    conn.execute(statement)
                    conn.commit()
                except sqlite3.OperationalError:
                    # Column already exists — safe to ignore.
                    pass
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Port implementation
    # ------------------------------------------------------------------

    def find_by_user_id(self, user_id: str) -> List[ConversationHistory]:
        """Return all messages for a user ordered chronologically."""
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            return []

        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(_FIND_BY_USER, (uid,)).fetchall()
            return [self._row_to_entity(row) for row in rows]
        finally:
            conn.close()

    def append(self, entry: ConversationHistory) -> None:
        """Persist a single ConversationHistory record."""
        try:
            uid = int(entry.user_id)
        except (ValueError, TypeError):
            uid = entry.user_id  # fallback — keep as-is if not numeric

        db_sender = _DB_SENDER_MAP.get(entry.sender.value, entry.sender.value)

        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute(
                _INSERT,
                (
                    entry.history_id,
                    uid,
                    entry.session_id,
                    entry.message,
                    db_sender,
                    entry.timestamp.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Mapping
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_entity(row: sqlite3.Row) -> ConversationHistory:
        raw_sender = (row["sender"] or "").lower()
        sender = _SENDER_MAP.get(raw_sender, SenderType.USER)

        raw_ts = row["timestamp"] or ""
        try:
            ts = datetime.fromisoformat(raw_ts)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            ts = datetime.now(timezone.utc)

        # For legacy rows inserted before history_id column existed, derive
        # a stable pseudo-ID from the row's auto-increment integer id.
        history_id = row["history_id"] or f"legacy-{row['id']}"
        session_id = row["session_id"] or ""

        return ConversationHistory(
            history_id=history_id,
            user_id=str(row["user_id"]),
            session_id=session_id,
            message=row["message"] or "",
            sender=sender,
            timestamp=ts,
        )
