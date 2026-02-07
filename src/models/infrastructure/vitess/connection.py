"""Vitess database connection management."""

import logging
import queue
import threading
import pymysql
from typing import Any
from pydantic import Field, BaseModel
from pymysql.connections import Connection

from models.data.config.vitess import VitessConfig

logger = logging.getLogger(__name__)


class VitessConnectionManager(BaseModel):
    """Vitess connection manager with connection pooling support."""

    config: VitessConfig
    connection: Connection | None = Field(default=None)
    pool: queue.Queue[Connection] | None = Field(default=None, exclude=True)
    pool_lock: threading.Lock = Field(default_factory=threading.Lock, exclude=True)
    model_config = {"arbitrary_types_allowed": True}

    def __del__(self) -> None:
        """Deconstructor that disconnect from the database"""
        self.disconnect()

    def model_post_init(self, context: Any) -> None:
        """Initialize the connection pool."""
        logger.debug(f"Creating VitessConnectionManager with config: host='{self.config.host}', port={self.config.port}, database='{self.config.database}', user='{self.config.user}', password_length={len(self.config.password)}")
        self.pool = queue.Queue(maxsize=self.config.pool_size + self.config.max_overflow)

    def _create_new_connection(self) -> Connection:
        """Create a new database connection."""
        logger.info(f"Attempting database connection to {self.config.host}:{self.config.port}...")
        try:
            connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                passwd=self.config.password,
                database=self.config.database,
                autocommit=True,
            )
            logger.info(f"Successfully connected to database at {self.config.host}:{self.config.port}")
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to database at {self.config.host}:{self.config.port}: {e}")
            raise

    def acquire(self) -> Connection:
        """Acquire a connection from the pool."""
        if self.pool is None:
            self.pool = queue.Queue(maxsize=self.config.pool_size + self.config.max_overflow)

        try:
            connection = self.pool.get(timeout=self.config.pool_timeout)
            if not connection.open:
                logger.warning("Acquired a closed connection, creating new one")
                connection.close()
                connection = self._create_new_connection()
            logger.debug(f"Acquired connection from pool, pool size: {self.pool.qsize()}")
            return connection
        except queue.Empty:
            with self.pool_lock:
                if self.pool.qsize() < self.config.pool_size + self.config.max_overflow:
                    connection = self._create_new_connection()
                    logger.debug(f"Created new overflow connection, total: {self.pool.qsize() + 1}")
                    return connection
            logger.error(f"Connection pool exhausted (timeout: {self.config.pool_timeout}s)")
            raise TimeoutError(f"Could not acquire database connection within {self.config.pool_timeout}s")

    def release(self, connection: Connection) -> None:
        """Release a connection back to the pool."""
        if self.pool is None:
            self.pool = queue.Queue(maxsize=self.config.pool_size + self.config.max_overflow)

        try:
            if connection and connection.open:
                self.pool.put_nowait(connection)
                logger.debug(f"Released connection to pool, pool size: {self.pool.qsize()}")
            else:
                logger.warning("Attempted to release a closed or None connection, discarding")
        except queue.Full:
            connection.close()
            logger.debug("Pool full, closed excess connection")

    @property
    def healthy_connection(self) -> bool:
        """Check if the database connection is healthy."""
        try:
            connection = self.acquire()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            self.release(connection)
            return True
        except Exception as e:
            logger.warning(f"Connection health check failed: {e}")
            return False

    def connect(self) -> Connection:
        """Establish a connection from the pool and store it."""
        logger.info("Acquiring connection from pool and storing in connection field")
        self.connection = self.acquire()
        return self.connection

    def disconnect(self) -> None:
        """Close all connections in the pool."""
        if self.connection is not None:
            try:
                if self.connection.open:
                    self.release(self.connection)
                self.connection = None
            except Exception as e:
                logger.warning(f"Error releasing connection: {e}")

        if self.pool is not None:
            while not self.pool.empty():
                try:
                    connection = self.pool.get_nowait()
                    if connection.open:
                        connection.close()
                except Exception as e:
                    logger.warning(f"Error closing pooled connection: {e}")
            self.pool = None
            logger.info("Disconnected all pooled connections")
