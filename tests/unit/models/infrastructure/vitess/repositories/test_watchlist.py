"""Unit tests for WatchlistRepository."""

from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.watchlist import WatchlistRepository


class TestWatchlistRepository:
    """Unit tests for WatchlistRepository."""

    def test_get_entity_watch_count_success(self):
        """Test getting entity watch count."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchone.return_value = (5,)
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.get_entity_watch_count(123)

        assert result == 5
        mock_cursor.execute.assert_called_once()

    def test_get_entity_watch_count_zero(self):
        """Test getting zero entity watch count."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchone.return_value = (0,)
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.get_entity_watch_count(123)

        assert result == 0
        mock_cursor.execute.assert_called_once()

    def test_get_property_watch_count_success(self):
        """Test getting property watch count."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchone.return_value = (3,)
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.get_property_watch_count(123)

        assert result == 3

    def test_add_watch_success(self):
        """Test adding watch successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_id_resolver.resolve_id.return_value = 456
        mock_cursor.lastrowid = 789
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.add_watch(123, "Q1", ["P31", "P17"])

        assert result.success is True
        assert result.data == 789

    def test_add_watch_entity_not_found(self):
        """Test adding watch when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.add_watch(123, "Q999", ["P31"])

        assert result.success is False
        assert "Entity not found" in result.error

    def test_add_watch_invalid_user(self):
        """Test adding watch with invalid user ID."""
        mock_vitess_client = MagicMock()

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.add_watch(0, "Q1", ["P31"])

        assert result.success is False
        assert "Invalid user ID" in result.error

    def test_add_watch_no_entity_id(self):
        """Test adding watch without entity ID."""
        mock_vitess_client = MagicMock()

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.add_watch(123, "", ["P31"])

        assert result.success is False
        assert "Entity ID is required" in result.error

    def test_add_watch_database_error(self):
        """Test adding watch with database error."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_id_resolver.resolve_id.return_value = 456
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.add_watch(123, "Q1", ["P31"])

        assert result.success is False
        assert "DB error" in result.error

    def test_remove_watch_success(self):
        """Test removing watch successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 456
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        # Should not raise
        repo.remove_watch(123, "Q1", ["P31"])

    def test_remove_watch_by_id_success(self):
        """Test removing watch by ID successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_cursor.rowcount = 1
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.remove_watch_by_id(789)

        assert result.success is True

    def test_remove_watch_by_id_not_found(self):
        """Test removing watch by ID when not found."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_cursor.rowcount = 0
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.remove_watch_by_id(999)

        assert result.success is False
        assert "not found" in result.error

    def test_get_watches_for_user_success(self):
        """Test getting watches for user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchall.return_value = [(1, 456, "P31,P17"), (2, 789, "")]
        mock_id_resolver.resolve_entity_id.side_effect = ["Q1", "Q2"]
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.get_watches_for_user(123)

        assert len(result) == 2
        assert result[0]["entity_id"] == "Q1"
        assert result[0]["properties"] == ["P31", "P17"]
        assert result[1]["properties"] is None

    def test_get_watchers_for_entity_success(self):
        """Test getting watchers for entity."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_id_resolver.resolve_id.return_value = 456
        mock_cursor.fetchall.return_value = [(123, "P31,P17"), (124, "")]
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.get_watchers_for_entity("Q1")

        assert len(result) == 2
        assert result[0]["user_id"] == 123
        assert result[0]["properties"] == ["P31", "P17"]
        assert result[1]["properties"] is None

    def test_get_notification_count_success(self):
        """Test getting notification count."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchone.return_value = (7,)
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.get_notification_count(123)

        assert result == 7

    def test_get_user_notifications_success(self):
        """Test getting user notifications."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchall.return_value = [
            (1, "Q1", 5, "edit", '{"P31": "Q5"}', "2023-01-01", True, "2023-01-02")
        ]
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_notifications(123)

        assert len(result) == 1
        assert result[0]["entity_id"] == "Q1"
        assert result[0]["change_type"] == "edit"
        assert result[0]["is_checked"] is True

    def test_mark_notification_checked_success(self):
        """Test marking notification as checked."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_connection_manager.connect.return_value = mock_connection
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=None)
        mock_cursor.rowcount = 1
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = WatchlistRepository(vitess_client=mock_vitess_client)

        # Should not raise
        result = repo.mark_notification_checked(1, 123)

        assert result is True
