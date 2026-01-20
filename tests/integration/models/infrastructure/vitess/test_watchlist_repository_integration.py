import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, "src")

from models.infrastructure.vitess.repositories.watchlist import WatchlistRepository


class TestWatchlistRepository:
    """Unit tests for WatchlistRepository"""

    @pytest.fixture
    def mock_connection_manager(self) -> MagicMock:
        """Mock connection manager"""
        return MagicMock()

    @pytest.fixture
    def mock_id_resolver(self) -> MagicMock:
        """Mock ID resolver"""
        return MagicMock()

    @pytest.fixture
    def repository(
        self, mock_connection_manager: MagicMock, mock_id_resolver: MagicMock
    ) -> WatchlistRepository:
        """Create repository instance"""
        return WatchlistRepository(mock_connection_manager, mock_id_resolver)

    def test_add_watch(
        self,
        repository: WatchlistRepository,
        mock_connection_manager: MagicMock,
        mock_id_resolver: MagicMock,
    ) -> None:
        """Test adding a watch"""
        mock_id_resolver.resolve_id.return_value = 1001
        mock_conn = MagicMock()

        mock_cursor = MagicMock()


        repository.add_watch(12345, "Q42", ["P31"])

        mock_id_resolver.resolve_id.assert_called_once_with(mock_conn, "Q42")
        mock_cursor.execute.assert_called_once_with(
            """
            INSERT INTO watchlist (user_id, internal_entity_id, watched_properties)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE watched_properties = VALUES(watched_properties)
            """,
            (12345, 1001, "P31"),
        )

    def test_remove_watch(
        self,
        repository: WatchlistRepository,
        mock_connection_manager: MagicMock,
        mock_id_resolver: MagicMock,
    ) -> None:
        """Test removing a watch"""
        mock_id_resolver.resolve_id.return_value = 1001
        mock_conn = MagicMock()

        mock_cursor = MagicMock()


        repository.remove_watch(12345, "Q42", ["P31"])

        mock_id_resolver.resolve_id.assert_called_once_with(mock_conn, "Q42")
        mock_cursor.execute.assert_called_once_with(
            """
            DELETE FROM watchlist
            WHERE user_id = %s AND internal_entity_id = %s AND watched_properties = %s
            """,
            (12345, 1001, "P31"),
        )

    def test_get_watches_for_user(
        self,
        repository: WatchlistRepository,
        mock_connection_manager: MagicMock,
        mock_id_resolver: MagicMock,
    ) -> None:
        """Test getting watches for user"""
        mock_conn = MagicMock()

        mock_cursor = MagicMock()

        mock_cursor.fetchall.return_value = [
            (1001, "P31"),
            (1002, ""),
        ]
        mock_id_resolver.resolve_entity_id.side_effect = (
            lambda conn, iid: "Q42" if iid == 1001 else "Q43"
        )

        result = repository.get_watches_for_user(12345)

        assert result == [
            {"entity_id": "Q42", "properties": ["P31"]},
            {"entity_id": "Q43", "properties": None},
        ]
        mock_cursor.execute.assert_called_once_with(
            """
            SELECT internal_entity_id, watched_properties
            FROM watchlist
            WHERE user_id = %s
            """,
            (12345,),
        )

    def test_get_watchers_for_entity(
        self,
        repository: WatchlistRepository,
        mock_connection_manager: MagicMock,
        mock_id_resolver: MagicMock,
    ) -> None:
        """Test getting watchers for entity"""
        mock_id_resolver.resolve_id.return_value = 1001
        mock_conn = MagicMock()

        mock_cursor = MagicMock()

        mock_cursor.fetchall.return_value = [
            (12345, "P31"),
            (67890, None),
        ]

        result = repository.get_watchers_for_entity("Q42")

        assert result == [
            {"user_id": 12345, "properties": ["P31"]},
            {"user_id": 67890, "properties": None},
        ]
        mock_id_resolver.resolve_id.assert_called_once_with(mock_conn, "Q42")

    def test_get_user_notifications(
        self, repository: WatchlistRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test getting user notifications"""
        mock_conn = MagicMock()

        mock_cursor = MagicMock()

        mock_cursor.fetchall.return_value = [
            (1, "Q42", 123, "edit", '["P31"]', "2023-01-01T12:00:00Z", False, None),
            (
                2,
                "Q43",
                124,
                "create",
                None,
                "2023-01-02T12:00:00Z",
                True,
                "2023-01-02T13:00:00Z",
            ),
        ]

        result = repository.get_user_notifications(12345, limit=30, offset=0)

        assert result == [
            {
                "id": 1,
                "entity_id": "Q42",
                "revision_id": 123,
                "change_type": "edit",
                "changed_properties": ["P31"],
                "event_timestamp": "2023-01-01T12:00:00Z",
                "is_checked": False,
                "checked_at": None,
            },
            {
                "id": 2,
                "entity_id": "Q43",
                "revision_id": 124,
                "change_type": "create",
                "changed_properties": None,
                "event_timestamp": "2023-01-02T12:00:00Z",
                "is_checked": True,
                "checked_at": "2023-01-02T13:00:00Z",
            },
        ]
        mock_cursor.execute.assert_called_once()

    def test_mark_notification_checked(
        self, repository: WatchlistRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test marking notification as checked"""
        mock_conn = MagicMock()

        mock_cursor = MagicMock()


        repository.mark_notification_checked(1, 12345)

        mock_cursor.execute.assert_called_once_with(
            """
            UPDATE user_notifications
            SET is_checked = TRUE, checked_at = NOW()
            WHERE id = %s AND user_id = %s
            """,
            (1, 12345),
        )

    def test_get_entity_watch_count(
        self, repository: WatchlistRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test getting entity watch count"""
        mock_conn = MagicMock()

        mock_cursor = MagicMock()

        mock_cursor.fetchone.return_value = (250,)

        result = repository.get_entity_watch_count(12345)

        assert result == 250
        mock_cursor.execute.assert_called_once_with(
            "SELECT COUNT(*) FROM watchlist WHERE user_id = %s AND watched_properties = ''",
            (12345,),
        )

    def test_get_property_watch_count(
        self, repository: WatchlistRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test getting property watch count"""
        mock_conn = MagicMock()

        mock_cursor = MagicMock()

        mock_cursor.fetchone.return_value = (150,)

        result = repository.get_property_watch_count(12345)

        assert result == 150
        mock_cursor.execute.assert_called_once_with(
            "SELECT COUNT(*) FROM watchlist WHERE user_id = %s AND watched_properties != ''",
            (12345,),
        )

    def test_add_watch_entity_limit_exceeded(
        self,
        repository: WatchlistRepository,
        mock_connection_manager: MagicMock,
        mock_id_resolver: MagicMock,
    ) -> None:
        """Test add_watch fails when entity watch limit exceeded"""
        mock_id_resolver.resolve_id.return_value = 1001

        # Mock count at limit
        with patch.object(
            repository, "get_entity_watch_count", return_value=500
        ) as mock_count:
            with pytest.raises(
                ValueError, match="Maximum 500 entity watches per user exceeded"
            ):
                repository.add_watch(12345, "Q42", None)

            mock_count.assert_called_once_with(12345)

    def test_add_watch_property_limit_exceeded(
        self,
        repository: WatchlistRepository,
        mock_connection_manager: MagicMock,
        mock_id_resolver: MagicMock,
    ) -> None:
        """Test add_watch fails when property watch limit exceeded"""
        mock_id_resolver.resolve_id.return_value = 1001

        # Mock count at limit
        with patch.object(
            repository, "get_property_watch_count", return_value=500
        ) as mock_count:
            with pytest.raises(
                ValueError,
                match="Maximum 500 entity-property watches per user exceeded",
            ):
                repository.add_watch(12345, "Q42", ["P31"])

            mock_count.assert_called_once_with(12345)
