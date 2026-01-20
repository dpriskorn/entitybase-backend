"""Vitess database connection management."""

import pymysql
from pydantic import Field

from models.infrastructure.connection import ConnectionManager
from models.infrastructure.vitess.vitess_config import VitessConfig


class VitessConnectionManager(ConnectionManager):
    """Vitess connection manager that ensures connections are properly opened and closed."""

    config: VitessConfig
    conn: pymysql.Connection = Field(default=None)

    def __enter__(self) -> None:
        """Create a new database connection."""
        if self.conn is None:
            self.conn = pymysql.connect(
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

    # @contextmanager
    # def get_connection(self) -> Generator[Any, None, None]:
    #     """Context manager for database connection."""
    #     conn = self.connect()
    #     try:
    #         yield conn
    #     finally:
    #         conn.close()  # Close connection after use

    def __exit__(self):
        self.conn.close()