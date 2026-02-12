"""Manage import state using SQLite database."""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from contextlib import contextmanager

DB_PATH = "import_state.db"


@dataclass
class EntityRecord:
    entity_id: str
    entity_type: str
    status: str
    line_number: int
    run_id: int
    last_attempt: str
    retry_count: int
    error_message: Optional[str] = None


@dataclass
class ImportRun:
    run_id: int
    start_time: str
    end_time: Optional[str]
    jsonl_file: str
    total_entities: int
    success_count: int
    fail_count: int
    skip_count: int
    concurrency: int
    api_url: str


class ImportStateManager:
    """Manage import state with SQLite database."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS import_runs (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    jsonl_file TEXT NOT NULL,
                    total_entities INTEGER NOT NULL,
                    success_count INTEGER DEFAULT 0,
                    fail_count INTEGER DEFAULT 0,
                    skip_count INTEGER DEFAULT 0,
                    concurrency INTEGER,
                    api_url TEXT
                );

                CREATE TABLE IF NOT EXISTS entities (
                    entity_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    line_number INTEGER,
                    run_id INTEGER,
                    last_attempt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    retry_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    PRIMARY KEY (entity_id, run_id),
                    FOREIGN KEY (run_id) REFERENCES import_runs(run_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_entities_status ON entities(status);
                CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
                CREATE INDEX IF NOT EXISTS idx_entities_run_id ON entities(run_id);
                CREATE INDEX IF NOT EXISTS idx_entities_last_attempt ON entities(last_attempt);
            """)

    def create_run(self, jsonl_file: str, total_entities: int,
                  concurrency: int, api_url: str) -> int:
        """Create a new import run record."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO import_runs
                (jsonl_file, total_entities, concurrency, api_url)
                VALUES (?, ?, ?, ?)
            """, (jsonl_file, total_entities, concurrency, api_url))
            run_id = cursor.lastrowid
            conn.commit()
            return run_id

    def finish_run(self, run_id: int, success_count: int,
                  fail_count: int, skip_count: int):
        """Mark run as complete."""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE import_runs
                SET end_time = CURRENT_TIMESTAMP,
                    success_count = ?,
                    fail_count = ?,
                    skip_count = ?
                WHERE run_id = ?
            """, (success_count, fail_count, skip_count, run_id))
            conn.commit()

    def add_entities(self, run_id: int, entities: List[Dict[str, Any]]):
        """Bulk add entities in pending state."""
        with self._get_connection() as conn:
            conn.executemany("""
                INSERT OR REPLACE INTO entities
                (entity_id, entity_type, status, line_number, run_id)
                VALUES (?, ?, 'pending', ?, ?)
            """, [
                (e['id'], e.get('type', 'item'), line_num, run_id)
                for line_num, e in enumerate(entities, 1)
            ])
            conn.commit()

    def get_next_batch(self, run_id: int, limit: int = 10) -> List[EntityRecord]:
        """Get next batch of pending entities."""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE entities
                SET status = 'processing', last_attempt = CURRENT_TIMESTAMP
                WHERE rowid IN (
                    SELECT rowid FROM entities
                    WHERE run_id = ? AND status = 'pending'
                    LIMIT ?
                )
            """, (run_id, limit))
            conn.commit()

            cursor = conn.execute("""
                SELECT entity_id, entity_type, status, line_number, run_id,
                       last_attempt, retry_count, error_message
                FROM entities
                WHERE run_id = ? AND status = 'processing'
                LIMIT ?
            """, (run_id, limit))
            return [EntityRecord(**row) for row in cursor.fetchall()]

    def mark_success(self, entity_id: str, run_id: int):
        """Mark entity as successfully imported."""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE entities
                SET status = 'success', last_attempt = CURRENT_TIMESTAMP
                WHERE entity_id = ? AND run_id = ?
            """, (entity_id, run_id))
            conn.commit()

    def mark_failed(self, entity_id: str, run_id: int, error: str):
        """Mark entity as failed."""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE entities
                SET status = 'failed',
                    last_attempt = CURRENT_TIMESTAMP,
                    retry_count = retry_count + 1,
                    error_message = ?
                WHERE entity_id = ? AND run_id = ?
            """, (error, entity_id, run_id))
            conn.commit()

    def mark_skipped(self, entity_id: str, run_id: int):
        """Mark entity as skipped (already exists)."""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE entities
                SET status = 'skipped', last_attempt = CURRENT_TIMESTAMP
                WHERE entity_id = ? AND run_id = ?
            """, (entity_id, run_id))
            conn.commit()

    def get_run_stats(self, run_id: int) -> Optional[ImportRun]:
        """Get statistics for a run."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM import_runs WHERE run_id = ?
            """, (run_id,))
            row = cursor.fetchone()
            return ImportRun(**row) if row else None

    def get_failed_entities(self, run_id: int, limit: int = 100) -> List[EntityRecord]:
        """Get failed entities for a run."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM entities
                WHERE run_id = ? AND status = 'failed'
                ORDER BY last_attempt DESC
                LIMIT ?
            """, (run_id, limit))
            return [EntityRecord(**row) for row in cursor.fetchall()]

    def get_stats_summary(self) -> Dict[str, Any]:
        """Get overall statistics across all runs."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(DISTINCT run_id) as total_runs,
                    SUM(total_entities) as total_entities,
                    SUM(success_count) as total_success,
                    SUM(fail_count) as total_failed,
                    SUM(skip_count) as total_skipped
                FROM import_runs
            """)
            row = cursor.fetchone()
            return dict(row)

    def reset_run(self, run_id: int):
        """Reset a run (delete all its records)."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM entities WHERE run_id = ?", (run_id,))
            conn.execute("DELETE FROM import_runs WHERE run_id = ?", (run_id,))
            conn.commit()

    def reset_all(self):
        """Reset all data."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM entities")
            conn.execute("DELETE FROM import_runs")
            conn.commit()
