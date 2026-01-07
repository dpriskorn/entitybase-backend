import pymysql
from typing import Any, Optional

from models.vitess_models import VitessConfig


class ConnectionManager:
    def __init__(self, config: VitessConfig) -> None:
        self.config = config
        self._connection: Optional[Any] = None

    def connect(self) -> Any:
        if self._connection:
            try:
                self._connection.ping(reconnect=True)
            except Exception:
                self._connection = None

        if not self._connection:
            self._connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                passwd=self.config.password,
                database=self.config.database,
                autocommit=True,
            )
        return self._connection

    def check_connection(self) -> bool:
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False
