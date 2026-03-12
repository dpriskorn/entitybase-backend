"""Unit tests for watchlist handler."""

from unittest.mock import MagicMock

import pytest

from models.rest_api.entitybase.v1.handlers.watchlist import WatchlistHandler


class TestWatchlistHandler:
    """Unit tests for WatchlistHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.state = MagicMock()
        self.state.vitess_client.user_repository.user_exists.return_value = True
        self.state.vitess_client.user_repository.is_watchlist_enabled.return_value = (
            True
        )
        self.state.vitess_client.watchlist_repository.add_watch.return_value = (
            MagicMock(success=True)
        )
        self.state.vitess_client.watchlist_repository.remove_watch.return_value = (
            MagicMock(success=True)
        )
        self.state.vitess_client.watchlist_repository.get_user_watchlist.return_value = []
        self.state.vitess_client.watchlist_repository.get_user_notifications.return_value = []
        self.state.vitess_client.watchlist_repository.get_entity_watch_count.return_value = 10
        self.state.vitess_client.watchlist_repository.get_property_watch_count.return_value = 5
        self.state.vitess_client.user_repository.update_user_activity.return_value = (
            MagicMock(success=True)
        )

        self.handler = WatchlistHandler(state=self.state)

    def test_add_watch_success(self):
        """Test add_watch success."""
        from models.data.rest_api.v1.entitybase.request.watchlist import (
            WatchlistAddRequest,
        )

        request = WatchlistAddRequest(entity_id="Q1", properties=["P31"])
        response = self.handler.add_watch(123, request)

        assert response.message == "Watch added"
        self.state.vitess_client.watchlist_repository.add_watch.assert_called_once()

    def test_add_watch_user_not_found(self):
        """Test add_watch when user not found."""
        from fastapi import HTTPException

        self.state.vitess_client.user_repository.user_exists.return_value = False

        from models.data.rest_api.v1.entitybase.request.watchlist import (
            WatchlistAddRequest,
        )

        request = WatchlistAddRequest(entity_id="Q1", properties=["P31"])

        with pytest.raises(HTTPException) as exc_info:
            self.handler.add_watch(123, request)

        assert exc_info.value.status_code == 404

    def test_add_watch_watchlist_disabled(self):
        """Test add_watch when watchlist is disabled."""
        from fastapi import HTTPException

        self.state.vitess_client.user_repository.is_watchlist_enabled.return_value = (
            False
        )

        from models.data.rest_api.v1.entitybase.request.watchlist import (
            WatchlistAddRequest,
        )

        request = WatchlistAddRequest(entity_id="Q1", properties=["P31"])

        with pytest.raises(HTTPException) as exc_info:
            self.handler.add_watch(123, request)

        assert exc_info.value.status_code == 400

    def test_remove_watch_success(self):
        """Test remove_watch success."""
        from models.data.rest_api.v1.entitybase.request.watchlist import (
            WatchlistRemoveRequest,
        )

        request = WatchlistRemoveRequest(entity_id="Q1")
        response = self.handler.remove_watch(123, request)

        assert response.message == "Watch removed"

    def test_handler_has_state(self):
        """Test handler has state."""
        assert hasattr(self.handler, "state")

    def test_get_notifications(self):
        """Test get_notifications."""
        self.state.vitess_client.watchlist_repository.get_user_notifications.return_value = [
            {"id": "notif1"}
        ]

        response = self.handler.get_notifications(123)

        assert response.user_id == 123

    def test_get_watch_counts(self):
        """Test get_watch_counts."""
        response = self.handler.get_watch_counts(123)

        assert response.entity_count == 10
        assert response.property_count == 5

    def test_mark_checked(self):
        """Test mark_checked."""
        from models.data.rest_api.v1.entitybase.request.watchlist import (
            MarkCheckedRequest,
        )

        request = MarkCheckedRequest(notification_id=1)
        response = self.handler.mark_checked(123, request)

        assert response.message == "Notification marked as checked"
