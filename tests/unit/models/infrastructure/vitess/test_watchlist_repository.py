from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

from models.infrastructure.vitess.repositories.watchlist import WatchlistRepository


class TestWatchlistRepository:
    def test_init(self) -> None:
        """Test WatchlistRepository initialization."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver)

        assert repo.connection_manager == mock_connection_manager
        assert repo.id_resolver == mock_id_resolver

    def test_get_entity_watch_count(self) -> None:
        """Test getting entity watch count."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver=None)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (5,)

        result = repo.get_entity_watch_count(123)

        assert result == 5

    def test_get_property_watch_count(self) -> None:
        """Test getting property watch count."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver=None)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (3,)

        result = repo.get_property_watch_count(123)

        assert result == 3

    def test_add_watch_success(self) -> None:
        """Test successful watch addition."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_id_resolver.resolve_id.return_value = 456
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.lastrowid = 789

        result = repo.add_watch(123, "Q42", ["P31"])

        assert result.success is True
        assert result.data == 789

    def test_add_watch_invalid_user(self) -> None:
        """Test add watch with invalid user ID."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver)

        result = repo.add_watch(0, "Q42", ["P31"])

        assert result.success is False
        assert "Invalid user ID" in result.error

    def test_add_watch_entity_not_found(self) -> None:
        """Test add watch when entity not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 0

        result = repo.add_watch(123, "Q42", ["P31"])

        assert result.success is False
        assert "Entity not found" in result.error

    def test_remove_watch(self) -> None:
        """Test removing a watch."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_id_resolver.resolve_id.return_value = 456
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repo.remove_watch(123, "Q42", ["P31"])

        mock_cursor.execute.assert_called_once()

    def test_remove_watch_by_id_success(self) -> None:
        """Test successful removal by ID."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver=None)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        result = repo.remove_watch_by_id(789)

        assert result.success is True

    def test_remove_watch_by_id_not_found(self) -> None:
        """Test removal by ID when not found."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver=None)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        result = repo.remove_watch_by_id(789)

        assert result.success is False
        assert "Watchlist entry not found" in result.error

    def test_get_watches_for_user(self) -> None:
        """Test getting watches for user."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 456, "P31,P279"),
            (2, 789, "")
        ]
        mock_id_resolver.resolve_entity_id.side_effect = ["Q42", "Q43"]

        result = repo.get_watches_for_user(123)

        assert len(result) == 2
        assert result[0]["entity_id"] == "Q42"
        assert result[0]["properties"] == ["P31", "P279"]
        assert result[1]["entity_id"] == "Q43"
        assert result[1]["properties"] is None

    def test_get_watchers_for_entity(self) -> None:
        """Test getting watchers for entity."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_id_resolver.resolve_id.return_value = 456
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (123, "P31,P279"),
            (456, "")
        ]

        result = repo.get_watchers_for_entity("Q42")

        assert len(result) == 2
        assert result[0]["user_id"] == 123
        assert result[0]["properties"] == ["P31", "P279"]
        assert result[1]["user_id"] == 456
        assert result[1]["properties"] is None

    def test_get_notification_count(self) -> None:
        """Test getting notification count."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver=None)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (7,)

        result = repo.get_notification_count(123)

        assert result == 7

    def test_get_user_notifications(self) -> None:
        """Test getting user notifications."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver=None)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "Q42", 123, "edit", '["P31"]', "2023-01-01", 0, None)
        ]

        result = repo.get_user_notifications(123, 24, 50, 0)

        assert len(result) == 1
        assert result[0]["entity_id"] == "Q42"
        assert result[0]["change_type"] == "edit"
        assert result[0]["changed_properties"] == ["P31"]

    def test_mark_notification_checked(self) -> None:
        """Test marking notification as checked."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = WatchlistRepository(mock_connection_manager, mock_id_resolver=None)
        mock_connection_manager.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repo.mark_notification_checked(456, 123)

        mock_cursor.execute.assert_called_once()