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
    connection_semaphore: threading.Semaphore | None = Field(default=None, exclude=True)
    overflow_connections: set[Connection] = Field(default_factory=set, exclude=True)
    active_connections: set[Connection] = Field(default_factory=set, exclude=True)
    pool_slots_created: int = Field(default=0, exclude=True)
    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, context: Any) -> None:
        """Initialize the connection pool."""
        logger.debug(
            f"Creating VitessConnectionManager with config: host='{self.config.host}', port={self.config.port}, database='{self.config.database}', user='{self.config.user}', password_length={len(self.config.password)}"
        )
        self.pool = queue.Queue(maxsize=self.config.pool_size)
        self.connection_semaphore = threading.Semaphore(
            self.config.pool_size + self.config.max_overflow
        )

    def _create_new_connection(self) -> Connection:
        """Create a new database connection."""
        logger.info(
            f"Attempting database connection to {self.config.host}:{self.config.port}..."
        )
        logger.debug(
            f"Connection parameters: user='{self.config.user}', database='{self.config.database}'"
        )
        try:
            logger.debug("Calling pymysql.connect()...")
            connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                passwd=self.config.password,
                database=self.config.database,
                autocommit=True,
            )
            logger.info(
                f"Successfully connected to database at {self.config.host}:{self.config.port}"
            )
            return connection
        except Exception as e:
            logger.error(
                f"Failed to connect to database at {self.config.host}:{self.config.port}: {e}"
            )
            raise

    def acquire(self) -> Connection:
        """Acquire a connection from pool."""
        logger.debug("=== acquire() START ===")
        if self.pool is None:
            logger.debug("Creating new pool queue")
            self.pool = queue.Queue(maxsize=self.config.pool_size)

        if self.connection_semaphore is None:
            self.connection_semaphore = threading.Semaphore(
                self.config.pool_size + self.config.max_overflow
            )

        try:
            logger.debug(f"Acquiring semaphore (timeout={self.config.pool_timeout}s)")
            if not self.connection_semaphore.acquire(timeout=self.config.pool_timeout):
                logger.error(
                    f"Connection pool exhausted (timeout: {self.config.pool_timeout}s)"
                )
                raise TimeoutError(
                    f"Could not acquire database connection within {self.config.pool_timeout}s"
                )
        except ValueError:
            logger.error("Failed to acquire semaphore")
            raise TimeoutError(
                f"Could not acquire database connection within {self.config.pool_timeout}s"
            )

        is_overflow = False
        try:
            try:
                logger.debug(
                    f"Attempting to get connection from pool, pool size: {self.pool.qsize()}"
                )
                connection = self.pool.get_nowait()
                logger.debug(
                    f"Got connection from pool, checking if open: {connection.open}"
                )
                if not connection.open:
                    logger.warning("Acquired a closed connection, creating new one")
                    connection = self._create_new_connection()
            except queue.Empty:
                logger.debug("Pool empty, creating new connection")
                connection = self._create_new_connection()
                is_overflow = self.pool_slots_created >= self.config.pool_size
                if not is_overflow:
                    self.pool_slots_created += 1

            if is_overflow:
                self.overflow_connections.add(connection)

            self.active_connections.add(connection)
            logger.debug(
                f"Successfully acquired connection, active connections: {len(self.active_connections)}"
            )
            return connection
        except Exception:
            logger.debug("Exception during acquire, releasing semaphore")
            self.connection_semaphore.release()
            raise

    def release(self, connection: Connection) -> None:
        """Release a connection back to pool."""
        if self.pool is None:
            self.pool = queue.Queue(maxsize=self.config.pool_size)

        if not connection or not connection.open:
            logger.warning(
                "Attempted to release a closed or None connection, discarding"
            )
            self.active_connections.discard(connection)
            if self.connection_semaphore:
                try:
                    self.connection_semaphore.release()
                except ValueError:
                    pass
            return

        is_overflow = connection in self.overflow_connections

        if is_overflow:
            self.overflow_connections.discard(connection)
            connection.close()
            logger.debug("Closed overflow connection")
            self.active_connections.discard(connection)
            self._release_semaphore()
            return

        if self.pool.qsize() >= self.config.pool_size:
            connection.close()
            logger.debug("Pool at capacity, closed excess connection")
            self.active_connections.discard(connection)
            self._release_semaphore()
            return

        try:
            self.pool.put_nowait(connection)
            logger.debug(f"Released connection to pool, pool size: {self.pool.qsize()}")
        except queue.Full:
            connection.close()
            logger.debug("Pool full, closed excess connection")

        self.active_connections.discard(connection)
        self._release_semaphore()

    def _release_semaphore(self) -> None:
        """Release semaphore permit."""
        if self.connection_semaphore:
            try:
                self.connection_semaphore.release()
            except ValueError:
                pass

    @property
    def healthy_connection(self) -> bool:
        """Check if database connection is healthy."""
        logger.debug("=== healthy_connection() START ===")
        try:
            logger.debug("Acquiring connection for health check...")
            connection = self.acquire()
            logger.debug("Connection acquired, creating cursor...")
            cursor = connection.cursor()
            logger.debug("Executing SELECT 1 query...")
            cursor.execute("SELECT 1")
            logger.debug("Fetching result...")
            cursor.fetchone()
            logger.debug("Closing cursor...")
            cursor.close()
            logger.debug("Releasing connection...")
            self.release(connection)
            logger.debug("=== healthy_connection() SUCCESS ===")
            return True
        except Exception as e:
            logger.warning(f"Connection health check failed: {e}")
            logger.debug("=== healthy_connection() FAILED ===")
            return False

    def connect(self) -> Connection:
        """Establish a connection from pool and store it."""
        logger.info("=== connect() START ===")
        logger.info("Acquiring connection from pool and storing in connection field")
        self.connection = self.acquire()
        logger.info(f"Connection acquired and stored: {self.connection is not None}")
        logger.info("=== connect() END ===")
        return self.connection

    def disconnect(self) -> None:
        """Close all connections in pool."""
        if self.connection is not None:
            try:
                if self.connection.open:
                    self.connection.close()
                self.connection = None
            except Exception as e:
                logger.warning(f"Error closing stored connection: {e}")

        if self.pool is not None:
            while not self.pool.empty():
                try:
                    connection = self.pool.get_nowait()
                    if connection.open:
                        connection.close()
                except Exception as e:
                    logger.warning(f"Error closing pooled connection: {e}")
            self.pool = None

        for connection in list(self.overflow_connections):
            try:
                if connection.open:
                    connection.close()
            except Exception as e:
                logger.warning(f"Error closing overflow connection: {e}")
        self.overflow_connections.clear()

        for connection in list(self.active_connections):
            try:
                if connection.open:
                    connection.close()
            except Exception as e:
                logger.warning(f"Error closing active connection: {e}")
        self.active_connections.clear()

        self.connection_semaphore = None

        logger.info("Disconnected all pooled connections")


class CursorContextManager:
    """Context manager for database cursors that properly handles connection lifecycle."""

    def __init__(self, connection_manager: VitessConnectionManager):
        self.connection_manager = connection_manager
        self.connection: Connection | None = None
        self.cursor: Any | None = None

    def __enter__(self) -> Any:
        """Acquire connection from pool and create cursor."""
        self.connection = self.connection_manager.acquire()
        if self.connection is None:
            raise RuntimeError("Failed to acquire connection from pool")
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Close cursor and release connection back to pool."""
        try:
            if self.cursor:
                self.cursor.close()
        except Exception as e:
            logger.warning(f"Error closing cursor: {e}")

        try:
            if self.connection and self.connection.open:
                self.connection_manager.release(self.connection)
        except Exception as e:
            logger.warning(f"Error releasing connection: {e}")

        return False
