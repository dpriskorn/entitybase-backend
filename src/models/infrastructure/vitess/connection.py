"""Vitess database connection management."""

import logging
import pymysql
from typing import Any
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

    def model_post_init(self, context: Any) -> None:
        """Create a new database connection."""
        logger.debug(f"Creating VitessConnectionManager with config: host='{self.config.host}', port={self.config.port}, database='{self.config.database}', user='{self.config.user}', password_length={len(self.config.password)}")
        self.connect()

    def connect(self) -> None:
        if self.connection is None:
            logger.info(f"Attempting database connection to {self.config.host}:{self.config.port}...")
            try:
                self.connection = pymysql.connect(
                    host=self.config.host,
                    port=self.config.port,
                    user=self.config.user,
                    passwd=self.config.password,
                    database=self.config.database,
                    autocommit=True,
                )
                logger.info(f"Successfully connected to database at {self.config.host}:{self.config.port}")
            except Exception as e:
                logger.error(f"Failed to connect to database at {self.config.host}:{self.config.port}: {e}")
                raise

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
