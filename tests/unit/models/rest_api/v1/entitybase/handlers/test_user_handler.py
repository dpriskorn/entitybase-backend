"""Unit tests for UserHandler."""

from datetime import date
from unittest.mock import Mock

from models.rest_api.v1.entitybase.handlers.user import UserHandler


class TestUserHandler:
    """Test cases for UserHandler."""

    def test_get_user_stats_with_data(self) -> None:
        """Test getting user stats when data exists."""
        vitess_client = Mock()
        conn = Mock()
        cursor = Mock()
        vitess_client.connection_manager.get_connection.return_value.__enter__ = Mock(
            return_value=conn
        )
        vitess_client.connection_manager.get_connection.return_value.__exit__ = Mock(
            return_value=None
        )
        conn.cursor.return_value.__enter__ = Mock(return_value=cursor)
        conn.cursor.return_value.__exit__ = Mock(return_value=None)

        # Mock latest stats
        cursor.fetchone.return_value = ("2023-01-01", 1000, 500)

        handler = UserHandler()
        stats = handler.get_user_stats(vitess_client)

        expected = {
            "date": "2023-01-01",
            "total_users": 1000,
            "active_users": 500,
        }
        assert stats.model_dump(mode="json") == expected

    def test_get_user_stats_no_data_fallback(self) -> None:
        """Test getting user stats when no stored data, falls back to live computation."""
        vitess_client = Mock()

        # Mock no stored data
        conn1 = Mock()
        cursor1 = Mock()
        mock_cm1 = Mock()
        mock_cm1.__enter__ = Mock(return_value=conn1)
        mock_cm1.__exit__ = Mock(return_value=None)
        conn1.cursor.return_value.__enter__ = Mock(return_value=cursor1)
        conn1.cursor.return_value.__exit__ = Mock(return_value=None)
        cursor1.fetchone.return_value = None  # No stored stats

        # Mock live computation
        conn2 = Mock()
        cursor2 = Mock()
        mock_cm2 = Mock()
        mock_cm2.__enter__ = Mock(return_value=conn2)
        mock_cm2.__exit__ = Mock(return_value=None)
        conn2.cursor.return_value.__enter__ = Mock(return_value=cursor2)
        conn2.cursor.return_value.__exit__ = Mock(return_value=None)
        cursor2.fetchone.side_effect = [(150,), (75,)]  # Live: total=150, active=75

        vitess_client.connection_manager.get_connection.side_effect = [
            mock_cm1,
            mock_cm2,
        ]

        handler = UserHandler()
        stats = handler.get_user_stats(vitess_client)

        expected = {
            "date": "live",
            "total_users": 150,
            "active_users": 75,
        }
        assert stats.model_dump(mode="json") == expected

    def test_get_general_stats_with_data(self) -> None:
        """Test getting general stats when data exists."""
        vitess_client = Mock()
        conn = Mock()
        cursor = Mock()
        vitess_client.connection_manager.get_connection.return_value.__enter__ = Mock(
            return_value=conn
        )
        vitess_client.connection_manager.get_connection.return_value.__exit__ = Mock(
            return_value=None
        )
        conn.cursor.return_value.__enter__ = Mock(return_value=cursor)
        conn.cursor.return_value.__exit__ = Mock(return_value=None)

        # Mock latest stats
        cursor.fetchone.return_value = (
            date(2023, 1, 1),
            1000,
            500,
            200,
            800,
            50,
            100,
            1500,
            3000,
            '{"en": 2000, "de": 500}',
            '{"labels": 1500, "descriptions": 1000, "aliases": 500}',
        )

        handler = UserHandler()
        stats = handler.get_general_stats(vitess_client)

        expected = {
            "date": "2023-01-01",
            "total_statements": 1000,
            "total_qualifiers": 500,
            "total_references": 200,
            "total_items": 800,
            "total_lexemes": 50,
            "total_properties": 100,
            "total_sitelinks": 1500,
            "total_terms": 3000,
            "terms_per_language": {"en": 2000, "de": 500},
            "terms_by_type": {"labels": 1500, "descriptions": 1000, "aliases": 500},
        }
        assert stats.model_dump(mode="json") == expected
