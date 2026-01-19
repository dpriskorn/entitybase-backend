import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.rest_api.entitybase.request.watchlist import (
    WatchlistAddRequest,
)
from models.rest_api.entitybase.response.watchlist import WatchlistResponse
from models.rest_api.entitybase.request.user import WatchlistRemoveRequest
from models.rest_api.entitybase.handlers.watchlist import WatchlistHandler


class TestWatchlistHandler:
    """Unit tests for WatchlistHandler"""

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock Vitess client"""
        client = MagicMock()
        client.user_repository = MagicMock()
        client.watchlist_repository = MagicMock()
        return client

    @pytest.fixture
    def handler(self) -> WatchlistHandler:
        """Create handler instance"""
        return WatchlistHandler()

    def test_add_watch_success(
        self, handler: WatchlistHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test adding a watch successfully"""
        request = WatchlistAddRequest(
            user_id=12345, entity_id="Q42", properties=["P31"]
        )
        mock_vitess_client.user_repository.user_exists.return_value = True

        result = handler.add_watch(request, mock_vitess_client)

        assert result.message == "Watch added"
        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.watchlist_repository.add_watch.assert_called_once_with(
            12345, "Q42", ["P31"]
        )

    def test_add_watch_user_not_found(
        self, handler: WatchlistHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test adding a watch for non-existent user"""
        request = WatchlistAddRequest(
            user_id=12345, entity_id="Q42", properties=["P31"]
        )
        mock_vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(ValueError, match="User not registered"):
            handler.add_watch(request, mock_vitess_client)

        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.watchlist_repository.add_watch.assert_not_called()

    def test_remove_watch(
        self, handler: WatchlistHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test removing a watch"""
        request = WatchlistRemoveRequest(
            user_id=12345, entity_id="Q42", properties=["P31"]
        )

        result = handler.remove_watch(request, mock_vitess_client)

        assert result.message == "Watch removed"
        mock_vitess_client.watchlist_repository.remove_watch.assert_called_once_with(
            12345, "Q42", ["P31"]
        )

    def test_get_watches_success(
        self, handler: WatchlistHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting watches successfully"""
        mock_vitess_client.user_repository.user_exists.return_value = True
        mock_vitess_client.watchlist_repository.get_watches_for_user.return_value = [
            {"entity_id": "Q42", "properties": ["P31"]}
        ]

        result = handler.get_watches(12345, mock_vitess_client)

        assert isinstance(result, WatchlistResponse)
        assert result.user_id == 12345
        assert result.watches == [{"entity_id": "Q42", "properties": ["P31"]}]
        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.watchlist_repository.get_watches_for_user.assert_called_once_with(
            12345
        )

    def test_get_watches_user_not_found(
        self, handler: WatchlistHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting watches for non-existent user"""
        mock_vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(ValueError, match="User not registered"):
            handler.get_watches(12345, mock_vitess_client)

        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.watchlist_repository.get_watches_for_user.assert_not_called()

    def test_get_notifications_success(
        self, handler: WatchlistHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting notifications successfully"""
        from models.rest_api.entitybase.response.user import NotificationResponse

        dt = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
        mock_vitess_client.user_repository.user_exists.return_value = True
        mock_vitess_client.watchlist_repository.get_user_notifications.return_value = [
            {
                "id": 1,
                "entity_id": "Q42",
                "revision_id": 123,
                "change_type": "edit",
                "changed_properties": ["P31"],
                "event_timestamp": "2023-01-01T12:00:00Z",
                "is_checked": False,
                "checked_at": None,
            }
        ]

        result = handler.get_notifications(
            12345, mock_vitess_client, limit=30, offset=0
        )

        assert isinstance(result, NotificationResponse)
        assert result.user_id == 12345
        expected = [
            {
                "id": 1,
                "entity_id": "Q42",
                "revision_id": 123,
                "change_type": "edit",
                "changed_properties": ["P31"],
                "event_timestamp": dt,
                "is_checked": False,
                "checked_at": None,
            }
        ]
        assert [n.model_dump() for n in result.notifications] == expected
        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.watchlist_repository.get_user_notifications.assert_called_once_with(
            12345, 24, 30, 0
        )

    def test_get_notifications_user_not_found(
        self, handler: WatchlistHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting notifications for non-existent user"""
        mock_vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(ValueError, match="User not registered"):
            handler.get_notifications(12345, mock_vitess_client)

        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.watchlist_repository.get_user_notifications.assert_not_called()

    def test_mark_checked(
        self, handler: WatchlistHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test marking notification as checked"""
        from models.rest_api.entitybase.request.watchlist import MarkCheckedRequest

        request = MarkCheckedRequest(notification_id=1)

        result = handler.mark_checked(12345, request, mock_vitess_client)

        assert result.message == "Notification marked as checked"
        mock_vitess_client.watchlist_repository.mark_notification_checked.assert_called_once_with(
            1, 12345
        )
