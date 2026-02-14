"""Integration tests for Vitess connection pool with real MySQL database."""

import logging
import time

import pytest

from models.config.settings import settings
from models.data.config.vitess import VitessConfig
from models.infrastructure.vitess.connection import VitessConnectionManager

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def test_timer():
    """Auto-apply timing to all tests."""
    import time as time_module

    logger.debug(f"=== TEST START: {time_module.time()} ===")
    yield
    logger.debug(f"=== TEST END: {time_module.time()} ===")


@pytest.fixture(scope="function")
def connection_manager() -> VitessConnectionManager:
    """Create a VitessConnectionManager for testing."""
    test_config = VitessConfig(
        host=settings.vitess_host,
        port=settings.vitess_port,
        database=settings.vitess_database,
        user=settings.vitess_user,
        password=settings.vitess_password,
        pool_size=20,
        max_overflow=20,
        pool_timeout=5,
    )
    manager = VitessConnectionManager(config=test_config)
    yield manager
    manager.disconnect()


def test_acquire_timeout_when_pool_exhausted(connection_manager):
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

        with pytest.raises(TimeoutError, match="Could not acquire database connection"):
            manager.acquire()
    finally:
        for conn in connections:
            manager.release(conn)


def test_release_closes_excess_connections(connection_manager):
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
        assert not conn_overflow.open, "Overflow connection should be closed"
        assert manager.pool.qsize() == 0, (
            "Pool should be empty after releasing overflow connection"
        )

        manager.release(connections[0])
        assert connections[0].open, "Pool connection should remain open"
        assert manager.pool.qsize() == 1, (
            "One connection should be in pool after releasing pool connection"
        )
    finally:
        for conn in connections:
            if conn and conn.open:
                conn.close()


def test_acquire_replaces_closed_connections(connection_manager):
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


def test_concurrent_acquire_release(connection_manager):
    """Test that concurrent acquire/release operations work correctly."""
    import threading

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


def test_healthy_connection_with_real_database(connection_manager):
    """Test that healthy_connection property works with real database."""
    manager = connection_manager

    assert manager.healthy_connection is True, "Connection should be healthy"


def test_multiple_acquire_and_release(connection_manager):
    """Test multiple acquire and release cycles."""
    manager = connection_manager
    config = manager.config

    max_connections = config.pool_size + config.max_overflow
    connections = []
    for _ in range(max_connections):
        conn = manager.acquire()
        connections.append(conn)
        assert conn.open

    for conn in connections:
        manager.release(conn)

    assert manager.pool is not None
    assert manager.pool.qsize() == config.pool_size


def test_disconnect_closes_all_connections(connection_manager):
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
