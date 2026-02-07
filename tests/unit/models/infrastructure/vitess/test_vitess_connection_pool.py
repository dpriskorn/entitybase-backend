"""Unit tests for Vitess connection pool."""

import queue
import threading
import time
from unittest.mock import MagicMock, patch

import pytest
from pymysql.connections import Connection

from models.data.config.vitess import VitessConfig
from models.infrastructure.vitess.connection import VitessConnectionManager


class TestVitessConnectionPool:
    """Unit tests for VitessConnectionManager connection pooling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = VitessConfig(
            host="localhost",
            port=15309,
            database="test_db",
            user="test_user",
            password="test_password",
            pool_size=2,
            max_overflow=1,
            pool_timeout=1,
        )

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_model_post_init_creates_pool(self, mock_connect):
        """Test that model_post_init creates connection pool."""
        manager = VitessConnectionManager(config=self.config)
        assert manager.pool is not None
        assert manager.pool.maxsize == 3  # pool_size + max_overflow

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_acquire_creates_new_connection_when_pool_empty(self, mock_connect):
        """Test that acquire creates a new connection when pool is empty."""
        mock_connection = MagicMock(spec=Connection)
        mock_connection.open = True
        mock_connect.return_value = mock_connection

        manager = VitessConnectionManager(config=self.config)
        connection = manager.acquire()

        assert connection == mock_connection
        mock_connect.assert_called_once()

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_acquire_reuses_pooled_connection(self, mock_connect):
        """Test that acquire reuses a connection from the pool."""
        mock_connection = MagicMock(spec=Connection)
        mock_connection.open = True
        mock_connect.return_value = mock_connection

        manager = VitessConnectionManager(config=self.config)

        # Acquire and release a connection
        connection1 = manager.acquire()
        manager.release(connection1)

        # Acquire again - should get the same connection
        connection2 = manager.acquire()

        # Only one connection should be created
        assert mock_connect.call_count == 1
        assert connection1 == connection2

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_acquire_creates_overflow_connection_when_pool_full(self, mock_connect):
        """Test that acquire creates overflow connection when pool is full."""
        mock_connection1 = MagicMock(spec=Connection)
        mock_connection1.open = True
        mock_connection2 = MagicMock(spec=Connection)
        mock_connection2.open = True
        mock_connection3 = MagicMock(spec=Connection)
        mock_connection3.open = True
        mock_connect.side_effect = [mock_connection1, mock_connection2, mock_connection3]

        manager = VitessConnectionManager(config=self.config)

        # Acquire pool_size connections (2)
        conn1 = manager.acquire()
        conn2 = manager.acquire()

        # Acquire overflow connection (1)
        conn3 = manager.acquire()

        assert mock_connect.call_count == 3
        assert manager.pool.qsize() == 0  # All connections checked out

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_acquire_timeout_when_pool_exhausted(self, mock_connect):
        """Test that acquire raises TimeoutError when pool is exhausted."""
        mock_connection1 = MagicMock(spec=Connection)
        mock_connection1.open = True
        mock_connection2 = MagicMock(spec=Connection)
        mock_connection2.open = True
        mock_connection3 = MagicMock(spec=Connection)
        mock_connection3.open = True
        mock_connect.side_effect = [mock_connection1, mock_connection2, mock_connection3]

        manager = VitessConnectionManager(config=self.config)

        # Acquire all connections (2 pool + 1 overflow)
        conn1 = manager.acquire()
        conn2 = manager.acquire()
        conn3 = manager.acquire()

        # Try to acquire one more - should timeout
        with pytest.raises(TimeoutError, match="Could not acquire database connection"):
            manager.acquire()

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_release_returns_connection_to_pool(self, mock_connect):
        """Test that release returns connection to pool."""
        mock_connection = MagicMock(spec=Connection)
        mock_connection.open = True
        mock_connect.return_value = mock_connection

        manager = VitessConnectionManager(config=self.config)
        connection = manager.acquire()

        assert manager.pool.qsize() == 0

        manager.release(connection)

        assert manager.pool.qsize() == 1

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_release_closes_excess_connections(self, mock_connect):
        """Test that release closes excess connections when pool is full."""
        mock_connection1 = MagicMock(spec=Connection)
        mock_connection1.open = True
        mock_connection2 = MagicMock(spec=Connection)
        mock_connection2.open = True
        mock_connection3 = MagicMock(spec=Connection)
        mock_connection3.open = True
        mock_connect.side_effect = [mock_connection1, mock_connection2, mock_connection3]

        manager = VitessConnectionManager(config=self.config)

        # Fill the pool
        conn1 = manager.acquire()
        conn2 = manager.acquire()

        # Acquire overflow connection
        conn3 = manager.acquire()

        # Release overflow connection back to full pool - should close it
        manager.release(conn3)
        conn3.close.assert_called_once()

        # Release pool connection - should keep it
        manager.release(conn1)
        assert conn1.close.call_count == 0
        assert manager.pool.qsize() == 1

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_acquire_replaces_closed_connections(self, mock_connect):
        """Test that acquire creates new connection if pooled connection is closed."""
        mock_connection1 = MagicMock(spec=Connection)
        mock_connection1.open = True
        mock_connection2 = MagicMock(spec=Connection)
        mock_connection2.open = False
        mock_connection3 = MagicMock(spec=Connection)
        mock_connection3.open = True
        mock_connect.side_effect = [mock_connection1, mock_connection2, mock_connection3]

        manager = VitessConnectionManager(config=self.config)

        # Acquire and release connection
        conn1 = manager.acquire()
        manager.release(conn1)

        # Mark connection as closed
        conn1.open = False

        # Acquire should replace closed connection
        conn2 = manager.acquire()

        assert mock_connect.call_count == 2  # Initial + replacement
        assert conn2.open

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_healthy_connection_checks_connection(self, mock_connect):
        """Test that healthy_connection property checks connection health."""
        mock_connection = MagicMock(spec=Connection)
        mock_connection.open = True
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1,)]
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        manager = VitessConnectionManager(config=self.config)

        result = manager.healthy_connection

        assert result is True
        mock_cursor.execute.assert_called_once_with("SELECT 1")

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_healthy_connection_returns_false_on_error(self, mock_connect):
        """Test that healthy_connection returns False on error."""
        mock_connection = MagicMock(spec=Connection)
        mock_connection.open = True
        mock_connection.cursor.side_effect = Exception("Database error")
        mock_connect.return_value = mock_connection

        manager = VitessConnectionManager(config=self.config)

        result = manager.healthy_connection

        assert result is False

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_disconnect_closes_all_pooled_connections(self, mock_connect):
        """Test that disconnect closes all pooled connections."""
        mock_connection1 = MagicMock(spec=Connection)
        mock_connection1.open = True
        mock_connection2 = MagicMock(spec=Connection)
        mock_connection2.open = True
        mock_connect.side_effect = [mock_connection1, mock_connection2]

        manager = VitessConnectionManager(config=self.config)

        # Acquire and release connections
        conn1 = manager.acquire()
        conn2 = manager.acquire()
        manager.release(conn1)
        manager.release(conn2)

        # Disconnect
        manager.disconnect()

        assert manager.pool is None
        mock_connection1.close.assert_called_once()
        mock_connection2.close.assert_called_once()

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_disconnect_handles_single_connection(self, mock_connect):
        """Test that disconnect handles old-style single connection."""
        mock_connection = MagicMock(spec=Connection)
        mock_connection.open = True
        mock_connect.return_value = mock_connection

        manager = VitessConnectionManager(config=self.config)
        manager.connection = mock_connection

        manager.disconnect()

        assert manager.connection is None
        mock_connection.close.assert_called_once()

    @patch("models.infrastructure.vitess.connection.pymysql.connect")
    def test_concurrent_acquire_release(self, mock_connect):
        """Test that concurrent acquire/release operations work correctly."""
        num_threads = 10
        num_iterations = 5

        mock_connections = []
        for _ in range(num_threads * num_iterations):
            conn = MagicMock(spec=Connection)
            conn.open = True
            mock_connections.append(conn)
        mock_connect.side_effect = mock_connections

        manager = VitessConnectionManager(config=self.config)

        errors = []
        success_count = [0]

        def worker():
            try:
                for _ in range(num_iterations):
                    conn = manager.acquire()
                    time.sleep(0.001)  # Simulate work
                    manager.release(conn)
                    success_count[0] += 1
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert success_count[0] == num_threads * num_iterations
