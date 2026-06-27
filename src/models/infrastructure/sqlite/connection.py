"""SQLite database connection management."""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from models.base import Base
from models.data.config.sqlite import SqliteConfig
from models.infrastructure.connection import ConnectionManager

logger = logging.getLogger(__name__)


class SqliteCursorWrapper(Base):
    """Wraps a sqlite3 cursor to translate MySQL-style %s params to SQLite ? style.

    This allows existing repository code using %s placeholders to work
    with SQLite without modifying every query.
    """

    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self._cursor = cursor
        super().__init__()

    def execute(self, sql: str, parameters: Any = None) -> "SqliteCursorWrapper":
        if parameters is not None:
            sql = sql.replace("%s", "?")
        if parameters is None:
            self._cursor.execute(sql)
        else:
            self._cursor.execute(sql, parameters)
        return self

    def executemany(self, sql: str, parameters: Any) -> "SqliteCursorWrapper":
        sql = sql.replace("%s", "?")
        self._cursor.executemany(sql, parameters)
        return self

    def fetchone(self) -> Any:
        return self._cursor.fetchone()

    def fetchall(self) -> list[Any]:
        return self._cursor.fetchall()

    def fetchmany(self, size: int | None = None) -> list[Any]:
        # None uses cursor's arraysize (default behavior); 0 returns empty list
        return self._cursor.fetchmany(size)

    def close(self) -> None:
        self._cursor.close()

    @property
    def description(self) -> Any:
        return self._cursor.description

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    @property
    def lastrowid(self) -> int | None:
        return self._cursor.lastrowid

    def __iter__(self) -> Any:
        return iter(self._cursor.fetchall())


class SqliteCursorContextManager(Base):
    """Context manager for SQLite cursors."""

    def __init__(self, connection_manager: "SqliteConnectionManager") -> None:
        self.connection_manager = connection_manager
        self.cursor: SqliteCursorWrapper | None = None
        super().__init__()

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


class SqliteConnectionWrapper(Base):
    """Wrapper for SQLite connection to provide MySQL-compatible interface.

    This wrapper provides a cursor() method that returns a SqliteCursorWrapper,
    allowing existing code using connection.cursor() to work with SQLite.
    """

    def __init__(self, connection_manager: "SqliteConnectionManager") -> None:
        self.connection_manager = connection_manager
        super().__init__()

    def cursor(self) -> SqliteCursorWrapper:
        """Create a cursor wrapper around the SQLite connection."""
        return self.connection_manager.cursor()


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

    def acquire(self) -> SqliteConnectionWrapper:
        """Acquire a connection wrapper for MySQL-compatible interface.

        Returns a SqliteConnectionWrapper that provides a cursor() method,
        allowing existing code using connection.cursor() to work with SQLite.
        """
        if self.conn is None:
            self.connect()
        return SqliteConnectionWrapper(connection_manager=self)

    def release(self, connection: Any = None) -> None:
        """Release a connection back to the pool.

        For SQLite, this is a no-op since there's no connection pool.
        The connection remains open for reuse.
        """
        pass

    def disconnect(self) -> None:
        """Close the SQLite connection."""
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception as e:
                logger.warning(f"Error closing SQLite connection: {e}")
            self.conn = None
            logger.info("SQLite connection closed")
