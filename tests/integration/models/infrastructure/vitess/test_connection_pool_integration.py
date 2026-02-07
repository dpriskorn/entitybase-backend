"""Integration tests for Vitess connection pool with real MySQL database."""

import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def test_timer():
    """Auto-apply timing to all tests."""
    import time as time_module

    logger.debug(f"=== TEST START: {time_module.time()} ===")
    yield
    logger.debug(f"=== TEST END: {time_module.time()} ===")


@pytest.mark.integration
class TestVitessConnectionPoolIntegration:
    """Integration tests for VitessConnectionManager connection pooling against real database."""

    def test_acquire_timeout_when_pool_exhausted(self, connection_manager):
        """Test that acquire raises TimeoutError when pool is exhausted."""
        manager = connection_manager
        config = manager.config

        max_connections = config.pool_size + config.max_overflow
        connections = []

        try:
            for _ in range(max_connections):
                conn = manager.acquire()
                connections.append(conn)
                assert conn.open, "Connection should be open"

            with pytest.raises(
                TimeoutError, match="Could not acquire database connection"
            ):
                manager.acquire()
        finally:
            for conn in connections:
                manager.release(conn)

    def test_release_closes_excess_connections(self, connection_manager):
        """Test that release closes excess connections when pool is full."""
        manager = connection_manager
        config = manager.config

        connections = []
        try:
            for _ in range(config.pool_size):
                conn = manager.acquire()
                connections.append(conn)

            conn_overflow = manager.acquire()
            connections.append(conn_overflow)

            assert manager.pool is not None
            assert manager.pool.qsize() == 0, "All connections should be checked out"

            manager.release(conn_overflow)
            assert conn_overflow.open, "Overflow connection should remain open"
            assert manager.pool.qsize() == 1, "One connection should be in pool"

            manager.release(connections[0])
            assert connections[0].open, "Pool connection should remain open"
            assert manager.pool.qsize() == 1, "Still one connection in pool"
        finally:
            for conn in connections:
                if conn and conn.open:
                    conn.close()

    def test_acquire_replaces_closed_connections(self, connection_manager):
        """Test that acquire creates new connection if pooled connection is closed."""
        manager = connection_manager

        conn1 = None
        conn2 = None
        try:
            conn1 = manager.acquire()
            manager.release(conn1)

            assert conn1.open, "First connection should be open"

            conn1.close()

            assert not conn1.open, "First connection should be closed"

            conn2 = manager.acquire()

            assert conn2 is not conn1, "Should get a new connection object"
            assert conn2.open, "New connection should be open"
        finally:
            if conn1 and conn1.open:
                conn1.close()
            if conn2 and conn2.open:
                conn2.close()

    def test_concurrent_acquire_release(self, connection_manager):
        """Test that concurrent acquire/release operations work correctly."""
        import threading
        import time

        manager = connection_manager
        config = manager.config

        max_connections = config.pool_size + config.max_overflow
        num_threads = 10
        num_iterations = 5
        errors = []
        success_count = [0]

        def worker():
            try:
                for _ in range(num_iterations):
                    conn = manager.acquire()
                    time.sleep(0.01)
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
        assert success_count[0] == num_threads * num_iterations, (
            f"Expected {num_threads * num_iterations} successful operations"
        )

    def test_healthy_connection_with_real_database(self, connection_manager):
        """Test that healthy_connection property works with real database."""
        manager = connection_manager

        assert manager.healthy_connection is True, "Connection should be healthy"

    def test_multiple_acquire_and_release(self, connection_manager):
        """Test multiple acquire and release cycles."""
        manager = connection_manager

        connections = []
        for _ in range(5):
            conn = manager.acquire()
            connections.append(conn)
            assert conn.open

        for conn in connections:
            manager.release(conn)

        assert manager.pool is not None
        assert manager.pool.qsize() == len(connections)

    def test_disconnect_closes_all_connections(self, connection_manager):
        """Test that disconnect closes all pooled connections."""
        manager = connection_manager

        connections = []
        for _ in range(manager.config.pool_size):
            conn = manager.acquire()
            connections.append(conn)

        manager.disconnect()

        assert manager.pool is None

        for conn in connections:
            assert not conn.open, f"Connection {conn} should be closed after disconnect"
