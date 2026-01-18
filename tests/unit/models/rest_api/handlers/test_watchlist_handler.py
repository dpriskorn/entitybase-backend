"""Unit tests for WatchlistHandler."""

import pytest
from unittest.mock import Mock

from models.rest_api.entitybase.handlers.watchlist import WatchlistHandler
from models.watchlist import (
    WatchlistAddRequest,
    WatchlistRemoveRequest,
    MarkCheckedRequest,
)


class TestWatchlistHandler:
    """Test cases for WatchlistHandler."""

    def test_add_watch_success(self):
        """Test successful watch addition."""
        vitess_client = Mock()
        vitess_client.user_repository.user_exists.return_value = True
        vitess_client.user_repository.is_watchlist_enabled.return_value = True
        vitess_client.watchlist_repository.add_watch.return_value.success = True
        vitess_client.user_repository.update_user_activity.return_value.success = True

        handler = WatchlistHandler()
        request = WatchlistAddRequest(user_id=123, entity_id="Q42", properties=["P31"])
        result = handler.add_watch(request, vitess_client)

        assert result.message == "Watch added"
        vitess_client.watchlist_repository.add_watch.assert_called_once_with(
            123, "Q42", ["P31"]
        )
        vitess_client.user_repository.update_user_activity.assert_called_once_with(123)

    def test_add_watch_user_not_exists(self):
        """Test add watch for non-existent user."""
        vitess_client = Mock()
        vitess_client.user_repository.user_exists.return_value = False

        handler = WatchlistHandler()
        request = WatchlistAddRequest(user_id=123, entity_id="Q42")

        with pytest.raises(ValueError, match="User not registered"):
            handler.add_watch(request, vitess_client)

    def test_add_watch_disabled(self):
        """Test add watch when watchlist disabled."""
        vitess_client = Mock()
        vitess_client.user_repository.user_exists.return_value = True
        vitess_client.user_repository.is_watchlist_enabled.return_value = False

        handler = WatchlistHandler()
        request = WatchlistAddRequest(user_id=123, entity_id="Q42")

        with pytest.raises(ValueError, match="Watchlist is disabled"):
            handler.add_watch(request, vitess_client)

    def test_remove_watch_success(self):
        """Test successful watch removal."""
        vitess_client = Mock()

        handler = WatchlistHandler()
        request = WatchlistRemoveRequest(
            user_id=123, entity_id="Q42", properties=["P31"]
        )
        result = handler.remove_watch(request, vitess_client)

        assert result.message == "Watch removed"
        vitess_client.watchlist_repository.remove_watch.assert_called_once_with(
            123, "Q42", ["P31"]
        )

    def test_get_watches_success(self):
        """Test successful watch retrieval."""
        vitess_client = Mock()
        vitess_client.user_repository.user_exists.return_value = True
        vitess_client.user_repository.is_watchlist_enabled.return_value = True
        vitess_client.watchlist_repository.get_watches_for_user.return_value = [
            {"entity_id": "Q42", "properties": ["P31"]}
        ]
        vitess_client.user_repository.update_user_activity.return_value = None

        handler = WatchlistHandler()
        result = handler.get_watches(123, vitess_client)

        assert result.user_id == 123
        assert result.watches == [{"entity_id": "Q42", "properties": ["P31"]}]
        vitess_client.watchlist_repository.get_watches_for_user.assert_called_once_with(
            123
        )
        vitess_client.user_repository.update_user_activity.assert_called_once_with(123)

    def test_get_notifications_success(self):
        """Test successful notification retrieval."""
        vitess_client = Mock()
        vitess_client.user_repository.user_exists.return_value = True
        vitess_client.user_repository.is_watchlist_enabled.return_value = True
        vitess_client.watchlist_repository.get_user_notifications.return_value = []
        vitess_client.user_repository.update_user_activity.return_value = None

        handler = WatchlistHandler()
        result = handler.get_notifications(123, vitess_client, 24, 50, 0)

        assert result.user_id == 123
        assert result.notifications == []
        vitess_client.watchlist_repository.get_user_notifications.assert_called_once_with(
            123, 24, 50, 0
        )

    def test_mark_checked_success(self):
        """Test successful notification marking."""
        vitess_client = Mock()

        handler = WatchlistHandler()
        request = MarkCheckedRequest(notification_id=456)
        result = handler.mark_checked(123, request, vitess_client)

        assert result.message == "Notification marked as checked"
        vitess_client.watchlist_repository.mark_notification_checked.assert_called_once_with(
            456, 123
        )

    def test_get_watch_counts_success(self):
        """Test successful watch counts retrieval."""
        vitess_client = Mock()
        vitess_client.watchlist_repository.get_entity_watch_count.return_value = 10
        vitess_client.watchlist_repository.get_property_watch_count.return_value = 5

        handler = WatchlistHandler()
        result = handler.get_watch_counts(123, vitess_client)

        assert result.entity_count == 10
        assert result.property_count == 5
