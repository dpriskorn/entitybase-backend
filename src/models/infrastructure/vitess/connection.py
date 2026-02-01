"""Vitess database connection management."""

import logging
import pymysql
from pydantic import Field, BaseModel
from pymysql.connections import Connection

from models.data.config.vitess import VitessConfig

logger = logging.getLogger(__name__)


class VitessConnectionManager(BaseModel):
    """Vitess connection manager that ensures connections are properly opened and closed."""

    config: VitessConfig
    connection: Connection | None = Field(default=None)
    model_config = {"arbitrary_types_allowed": True}

    def __del__(self) -> None:
        """Deconstructor that disconnect from the database"""
        self.disconnect()

    def model_post_init(self, context) -> None:
        """Create a new database connection."""
        self.connect()

    def connect(self) -> None:
        if self.connection is None:
            self.connection = pymysql.connect(
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
        if self.connection is None:
            self.connect()
        # noinspection PyBroadException
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False

    def disconnect(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
