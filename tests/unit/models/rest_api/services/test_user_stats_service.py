"""Unit tests for UserStatsService."""

import pytest
from unittest.mock import Mock

from models.rest_api.entitybase.services.user_stats_service import UserStatsService


class TestUserStatsService:
    """Test cases for UserStatsService."""

    def test_compute_daily_stats(self):
        """Test computing daily stats."""
        # Mock vitess client
        vitess_client = Mock()

        # Mock connection and cursor
        conn = Mock()
        cursor = Mock()
        vitess_client.connection_manager.get_connection.return_value.__enter__ = Mock(return_value=conn)
        vitess_client.connection_manager.get_connection.return_value.__exit__ = Mock(return_value=None)
        conn.cursor.return_value.__enter__ = Mock(return_value=cursor)
        conn.cursor.return_value.__exit__ = Mock(return_value=None)

        # Mock query results
        cursor.fetchone.side_effect = [(100,), (50,)]  # total_users=100, active_users=50

        service = UserStatsService()
        stats = service.compute_daily_stats(vitess_client)

        assert stats.total_users == 100
        assert stats.active_users == 50

        # Verify queries
        assert cursor.execute.call_count == 2
        cursor.execute.assert_any_call("SELECT COUNT(*) FROM users")
        cursor.execute.assert_any_call(
            "SELECT COUNT(*) FROM users WHERE last_activity >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
        )

    def test_get_total_users_zero(self):
        """Test getting total users when none exist."""
        vitess_client = Mock()
        conn = Mock()
        cursor = Mock()
        vitess_client.connection_manager.get_connection.return_value.__enter__ = Mock(return_value=conn)
        vitess_client.connection_manager.get_connection.return_value.__exit__ = Mock(return_value=None)
        conn.cursor.return_value.__enter__ = Mock(return_value=cursor)
        conn.cursor.return_value.__exit__ = Mock(return_value=None)

        cursor.fetchone.return_value = (0,)

        service = UserStatsService()
        total = service.get_total_users(vitess_client)

        assert total == 0

    def test_get_active_users_none(self):
        """Test getting active users when none exist."""
        vitess_client = Mock()
        conn = Mock()
        cursor = Mock()
        vitess_client.connection_manager.get_connection.return_value.__enter__ = Mock(return_value=conn)
        vitess_client.connection_manager.get_connection.return_value.__exit__ = Mock(return_value=None)
        conn.cursor.return_value.__enter__ = Mock(return_value=cursor)
        conn.cursor.return_value.__exit__ = Mock(return_value=None)

        cursor.fetchone.return_value = (0,)

        service = UserStatsService()
        active = service.get_active_users(vitess_client)

        assert active == 0