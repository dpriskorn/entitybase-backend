"""Unit tests for notification_cleanup."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

from models.workers.notification_cleanup.main import NotificationCleanupWorker


class TestNotificationCleanupWorker:
    """Unit tests for NotificationCleanupWorker class."""

    def test_worker_initialization(self):
        """Test worker initialization."""
        worker = NotificationCleanupWorker()
        assert worker.worker_id is not None
        assert worker.max_age_days == 30
        assert worker.max_per_user == 500
        assert worker.vitess_client is None

    def test_worker_initialization_custom_limits(self):
        """Test worker initialization with custom limits."""
        worker = NotificationCleanupWorker(max_age_days=7, max_per_user=100)
        assert worker.max_age_days == 7
        assert worker.max_per_user == 100

    @pytest.mark.asyncio
    async def test_run_cleanup_success(self):
        """Test successful cleanup cycle."""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 5

        mock_cursor.fetchall.return_value = []

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )
        mock_connection.cursor.return_value.__exit__ = MagicMock(return_value=False)

        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = mock_connection

        mock_vitess_client = MagicMock()
        mock_vitess_client.connection_manager = mock_connection_manager

        worker = NotificationCleanupWorker()
        worker.vitess_client = mock_vitess_client

        await worker.run_cleanup()

    @pytest.mark.asyncio
    async def test_run_cleanup_with_user_limits(self):
        """Test cleanup cycle with users exceeding limits."""
        mock_cursor = MagicMock()

        mock_cursor.fetchall.side_effect = [
            [(1, 600), (2, 550)],  # First call: users with excess
            [],  # Second call: delete old notifications result
        ]
        mock_cursor.rowcount = 5

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )
        mock_connection.cursor.return_value.__exit__ = MagicMock(return_value=False)

        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = mock_connection

        mock_vitess_client = MagicMock()
        mock_vitess_client.connection_manager = mock_connection_manager

        worker = NotificationCleanupWorker()
        worker.vitess_client = mock_vitess_client

        await worker.run_cleanup()

    def test_delete_old_notifications(self):
        """Test deleting old notifications."""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 10

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )
        mock_connection.cursor.return_value.__exit__ = MagicMock(return_value=False)

        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = mock_connection

        mock_vitess_client = MagicMock()
        mock_vitess_client.connection_manager = mock_connection_manager

        worker = NotificationCleanupWorker()
        worker.vitess_client = mock_vitess_client

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        deleted = worker._delete_old_notifications(cutoff_date)

        assert deleted == 10
        mock_cursor.execute.assert_called_once()

    def test_enforce_user_limits_no_excess(self):
        """Test enforcing user limits when no users exceed limits."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.rowcount = 0

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )
        mock_connection.cursor.return_value.__exit__ = MagicMock(return_value=False)

        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = mock_connection

        mock_vitess_client = MagicMock()
        mock_vitess_client.connection_manager = mock_connection_manager

        worker = NotificationCleanupWorker()
        worker.vitess_client = mock_vitess_client

        deleted = worker._enforce_user_limits()

        assert deleted == 0

    def test_enforce_user_limits_with_excess(self):
        """Test enforcing user limits when users exceed limits."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, 600)]  # User 1 has 600, limit is 500
        mock_cursor.rowcount = 100  # 100 deleted

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )
        mock_connection.cursor.return_value.__exit__ = MagicMock(return_value=False)

        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = mock_connection

        mock_vitess_client = MagicMock()
        mock_vitess_client.connection_manager = mock_connection_manager
        mock_vitess_client.cursor = mock_connection.cursor.return_value

        worker = NotificationCleanupWorker()
        worker.vitess_client = mock_vitess_client

        deleted = worker._enforce_user_limits()

        assert deleted == 100

    def test_enforce_user_limits_multiple_users(self):
        """Test enforcing user limits with multiple users."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, 600),
            (2, 700),
        ]  # Two users exceed limit
        mock_cursor.rowcount = 100

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__ = MagicMock(
            return_value=mock_cursor
        )
        mock_connection.cursor.return_value.__exit__ = MagicMock(return_value=False)

        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = mock_connection

        mock_vitess_client = MagicMock()
        mock_vitess_client.connection_manager = mock_connection_manager
        mock_vitess_client.cursor = mock_connection.cursor.return_value

        worker = NotificationCleanupWorker()
        worker.vitess_client = mock_vitess_client

        deleted = worker._enforce_user_limits()

        assert deleted == 200
