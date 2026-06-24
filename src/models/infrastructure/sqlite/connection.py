"""SQLite database connection management."""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from models.data.config.sqlite import SqliteConfig
from models.infrastructure.connection import ConnectionManager

logger = logging.getLogger(__name__)


class SqliteCursorWrapper:
    """Wraps a sqlite3 cursor to translate MySQL-style %s params to SQLite ? style.

    This allows existing repository code using %s placeholders to work
    with SQLite without modifying every query.
    """

    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self._cursor = cursor

    def execute(
        self, sql: str, parameters: Any = None
    ) -> "SqliteCursorWrapper":
        if parameters is not None:
            sql = sql.replace("%s", "?")
        if parameters is None:
            self._cursor.execute(sql)
        else:
            self._cursor.execute(sql, parameters)
        return self

    def executemany(
        self, sql: str, parameters: Any
    ) -> "SqliteCursorWrapper":
        sql = sql.replace("%s", "?")
        self._cursor.executemany(sql, parameters)
        return self

    def fetchone(self) -> Any:
        return self._cursor.fetchone()

    def fetchall(self) -> list[Any]:
        return self._cursor.fetchall()

    def fetchmany(self, size: int | None = None) -> list[Any]:
        return self._cursor.fetchmany(size)

    def close(self) -> None:
        self._cursor.close()

    @property
    def description(self) -> Any:
        return self._cursor.description

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    def __iter__(self) -> Any:
        return iter(self._cursor.fetchall())


class SqliteCursorContextManager:
    """Context manager for SQLite cursors."""

    def __init__(
        self, connection_manager: "SqliteConnectionManager"
    ) -> None:
        self.connection_manager = connection_manager
        self.cursor: SqliteCursorWrapper | None = None

    def __enter__(self) -> SqliteCursorWrapper:
        self.cursor = self.connection_manager.cursor()
        return self.cursor

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> Literal[False]:
        if self.cursor:
            try:
                self.cursor.close()
            except Exception as e:
                logger.warning(f"Error closing SQLite cursor: {e}")
        return False


class SqliteConnectionManager(ConnectionManager):
    """SQLite connection manager.

    Manages a single SQLite connection with WAL mode for concurrent access.
    The cursor wrapper transparently handles %s to ? parameter translation.
    """

    config: SqliteConfig
    conn: sqlite3.Connection | None = Field(default=None)

    def model_post_init(self, context: Any) -> None:
        """Ensure the data directory exists."""
        self.config.datadir.mkdir(parents=True, exist_ok=True)

    def _get_db_path(self) -> str:
        return str(self.config.datadir / "entitybase.db")

    def connect(self) -> sqlite3.Connection:
        """Create a new SQLite connection with WAL mode."""
        db_path = self._get_db_path()
        logger.info(f"Opening SQLite database: {db_path}")
        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False,
        )
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        return self.conn

    @property
    def healthy_connection(self) -> bool:
        """Check if the SQLite connection is healthy."""
        if self.conn is None:
            return False
        try:
            self.conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    def cursor(self) -> SqliteCursorWrapper:
        """Create a cursor wrapper around a new sqlite3 cursor."""
        if self.conn is None:
            self.connect()
        if self.conn is None:
            raise RuntimeError("Failed to establish SQLite connection")
        return SqliteCursorWrapper(self.conn.cursor())

    def disconnect(self) -> None:
        """Close the SQLite connection."""
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception as e:
                logger.warning(f"Error closing SQLite connection: {e}")
            self.conn = None
            logger.info("SQLite connection closed")
