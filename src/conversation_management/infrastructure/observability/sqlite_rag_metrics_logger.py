from __future__ import annotations

import sqlite3
import sys

from conversation_management.application.ports.i_rag_metrics_logger import (
    IRAGMetricsLogger,
    TurnMetricsDTO,
)

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS rag_metrics (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id              TEXT    NOT NULL,
    turn_number             INTEGER NOT NULL,
    intent                  TEXT    NOT NULL,
    context_state           TEXT    NOT NULL,
    context_recall_score    REAL    NOT NULL,
    context_precision_score REAL    NOT NULL,
    groundedness_score      REAL    NOT NULL,
    relevance_score         REAL    NOT NULL,
    is_fallback             INTEGER NOT NULL,
    clarification_needed    INTEGER NOT NULL,
    evidence_chunk_count    INTEGER NOT NULL,
    timestamp               TEXT    NOT NULL
)
"""

_INSERT = """
INSERT INTO rag_metrics (
    session_id, turn_number, intent, context_state,
    context_recall_score, context_precision_score,
    groundedness_score, relevance_score,
    is_fallback, clarification_needed, evidence_chunk_count, timestamp
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


class SQLiteRAGMetricsLogger(IRAGMetricsLogger):
    """
    Persists RAG evaluation metrics for every conversation turn to rag_metrics.sqlite.

    Creates the rag_metrics table automatically on first run.
    Write failures are printed to stderr and never interrupt the turn pipeline.

    Useful queries:
        -- Average scores per session
        SELECT session_id, AVG(context_recall_score), AVG(groundedness_score)
        FROM rag_metrics GROUP BY session_id;

        -- Quality gate failures (fallback triggered)
        SELECT * FROM rag_metrics WHERE is_fallback = 1 ORDER BY timestamp DESC;

        -- Score breakdown by intent
        SELECT intent, COUNT(*), AVG(groundedness_score), AVG(relevance_score)
        FROM rag_metrics GROUP BY intent;

        -- Low-recall turns (retrieval quality signal)
        SELECT session_id, turn_number, intent, context_state, context_recall_score
        FROM rag_metrics WHERE context_recall_score < 0.6 ORDER BY context_recall_score;
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._ensure_table()

    def _ensure_table(self) -> None:
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute(_CREATE_TABLE)
            conn.commit()
        finally:
            conn.close()

    def log_turn_metrics(self, metrics: TurnMetricsDTO) -> None:
        try:
            conn = sqlite3.connect(self._db_path)
            try:
                conn.execute(
                    _INSERT,
                    (
                        metrics.session_id,
                        metrics.turn_number,
                        metrics.intent,
                        metrics.context_state,
                        metrics.context_recall_score,
                        metrics.context_precision_score,
                        metrics.groundedness_score,
                        metrics.relevance_score,
                        int(metrics.is_fallback),
                        int(metrics.clarification_needed),
                        metrics.evidence_chunk_count,
                        metrics.timestamp,
                    ),
                )
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error as exc:
            print(f"[RAGMetricsLogger] Failed to log metrics: {exc}", file=sys.stderr)
