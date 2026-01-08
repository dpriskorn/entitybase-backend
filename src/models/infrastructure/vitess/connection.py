import pymysql
from contextlib import contextmanager
from typing import Any, Generator

from models.vitess_models import VitessConfig


class ConnectionManager:
    def __init__(self, config: VitessConfig) -> None:
        self.config = config

    def connect(self) -> Any:
        # Create a new connection each time to avoid threading issues
        return pymysql.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            passwd=self.config.password,
            database=self.config.database,
            autocommit=True,
        )

    def we_have_a_connection(self) -> bool:
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
        """Context manager for database connection"""
        conn = self.connect()
        try:
            yield conn
        finally:
            conn.close()  # Close connection after use
