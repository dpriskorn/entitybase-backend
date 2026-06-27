"""Unit tests for watchlist handler."""

from unittest.mock import MagicMock

import pytest

from models.rest_api.entitybase.v1.handlers.watchlist import WatchlistHandler


class TestWatchlistHandler:
    """Unit tests for WatchlistHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.state = MagicMock()
        self.state.mysql_client.user_repository.user_exists.return_value = True
        self.state.mysql_client.user_repository.is_watchlist_enabled.return_value = True
        self.state.mysql_client.watchlist_repository.add_watch.return_value = MagicMock(
            success=True
        )
        self.state.mysql_client.watchlist_repository.remove_watch.return_value = (
            MagicMock(success=True)
        )
        self.state.mysql_client.watchlist_repository.remove_watch_by_id.return_value = (
            MagicMock(success=True)
        )
        self.state.mysql_client.watchlist_repository.get_user_watchlist.return_value = []
        self.state.mysql_client.watchlist_repository.get_watches_for_user.return_value = []
        self.state.mysql_client.watchlist_repository.get_user_notifications.return_value = []
        self.state.mysql_client.watchlist_repository.get_entity_watch_count.return_value = 10
        self.state.mysql_client.watchlist_repository.get_property_watch_count.return_value = 5
        self.state.mysql_client.user_repository.update_user_activity.return_value = (
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
        self.state.mysql_client.watchlist_repository.add_watch.assert_called_once()

    def test_add_watch_user_not_found(self):
        """Test add_watch when user not found."""
        from fastapi import HTTPException

        self.state.mysql_client.user_repository.user_exists.return_value = False

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

        self.state.mysql_client.user_repository.is_watchlist_enabled.return_value = (
            False
        )

        from models.data.rest_api.v1.entitybase.request.watchlist import (
            WatchlistAddRequest,
        )

        request = WatchlistAddRequest(entity_id="Q1", properties=["P31"])

        with pytest.raises(HTTPException) as exc_info:
            self.handler.add_watch(123, request)

        assert exc_info.value.status_code == 400

    def test_add_watch_failure(self):
        """Test add_watch when repository returns error."""
        from fastapi import HTTPException

        self.state.mysql_client.watchlist_repository.add_watch.return_value = MagicMock(
            success=False, error="Database error"
        )

        from models.data.rest_api.v1.entitybase.request.watchlist import (
            WatchlistAddRequest,
        )

        request = WatchlistAddRequest(entity_id="Q1", properties=["P31"])

        with pytest.raises(HTTPException) as exc_info:
            self.handler.add_watch(123, request)

        assert exc_info.value.status_code == 500

    def test_add_watch_activity_failure_logs_warning(self):
        """Test add_watch when activity update fails (logs warning but doesn't fail)."""
        from models.data.rest_api.v1.entitybase.request.watchlist import (
            WatchlistAddRequest,
        )

        self.state.mysql_client.user_repository.update_user_activity.return_value = (
            MagicMock(success=False, error="Activity error")
        )

        request = WatchlistAddRequest(entity_id="Q1", properties=["P31"])
        response = self.handler.add_watch(123, request)

        assert response.message == "Watch added"

    def test_remove_watch_success(self):
        """Test remove_watch success."""
        from models.data.rest_api.v1.entitybase.request.watchlist import (
            WatchlistRemoveRequest,
        )

        request = WatchlistRemoveRequest(entity_id="Q1")
        response = self.handler.remove_watch(123, request)

        assert response.message == "Watch removed"

    def test_remove_watch_by_id_success(self):
        """Test remove_watch_by_id success."""
        self.state.mysql_client.watchlist_repository.remove_watch_by_id.return_value = (
            MagicMock(success=True)
        )
        response = self.handler.remove_watch_by_id(123, 1)

        assert response.message == "Watch removed"

    def test_remove_watch_by_id_user_not_found(self):
        """Test remove_watch_by_id when user not found."""
        from fastapi import HTTPException

        self.state.mysql_client.user_repository.user_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            self.handler.remove_watch_by_id(123, 1)

        assert exc_info.value.status_code == 404

    def test_remove_watch_by_id_failure(self):
        """Test remove_watch_by_id when repository returns error."""
        from fastapi import HTTPException

        self.state.mysql_client.watchlist_repository.remove_watch_by_id.return_value = (
            MagicMock(success=False, error="Watch not found")
        )

        with pytest.raises(HTTPException) as exc_info:
            self.handler.remove_watch_by_id(123, 1)

        assert exc_info.value.status_code == 404

    def test_get_watches_success(self):
        """Test get_watches success."""
        self.state.mysql_client.watchlist_repository.get_watches_for_user.return_value = [
            {"entity_id": "Q1"}
        ]
        response = self.handler.get_watches(123)

        assert response.user_id == 123

    def test_get_watches_watchlist_disabled(self):
        """Test get_watches when watchlist is disabled."""
        from fastapi import HTTPException

        self.state.mysql_client.user_repository.is_watchlist_enabled.return_value = (
            False
        )

        with pytest.raises(HTTPException) as exc_info:
            self.handler.get_watches(123)

        assert exc_info.value.status_code == 400

    def test_get_notifications(self):
        """Test get_notifications."""
        self.state.mysql_client.watchlist_repository.get_user_notifications.return_value = [
            {"id": "notif1"}
        ]

        response = self.handler.get_notifications(123)

        assert response.user_id == 123

    def test_get_notifications_watchlist_disabled(self):
        """Test get_notifications when watchlist is disabled."""
        from fastapi import HTTPException

        self.state.mysql_client.user_repository.is_watchlist_enabled.return_value = (
            False
        )

        with pytest.raises(HTTPException) as exc_info:
            self.handler.get_notifications(123)

        assert exc_info.value.status_code == 400

    def test_mark_checked(self):
        """Test mark_checked."""
        from models.data.rest_api.v1.entitybase.request.watchlist import (
            MarkCheckedRequest,
        )

        request = MarkCheckedRequest(notification_id=1)
        response = self.handler.mark_checked(123, request)

        assert response.message == "Notification marked as checked"

    def test_get_watch_counts(self):
        """Test get_watch_counts."""
        response = self.handler.get_watch_counts(123)

        assert response.entity_count == 10
        assert response.property_count == 5

    def test_handler_has_state(self):
        """Test handler has state."""
        assert hasattr(self.handler, "state")
