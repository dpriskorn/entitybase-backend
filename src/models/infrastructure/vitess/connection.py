"""Vitess database connection management."""

import pymysql
from contextlib import contextmanager
from typing import Any, Generator

from models.infrastructure.connection import ConnectionManager
from models.infrastructure.vitess.config import VitessConfig


class VitessConnectionManager(ConnectionManager):
    """Vitess connection manager that ensures connections are properly opened and closed."""

    config: VitessConfig

    def connect(self) -> pymysql.Connection:
        """Create a new database connection."""
        return pymysql.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            passwd=self.config.password,
            database=self.config.database,
            autocommit=True,
        )

    @property
    def healthy_connection(self) -> bool:
        """Check if the database connection is healthy."""
        # noinspection PyBroadException
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False

    @contextmanager
    def get_connection(self) -> Generator[Any, None, None]:
        """Context manager for database connection."""
        conn = self.connect()
        try:
            yield conn
        finally:
            conn.close()  # Close connection after use
