"""Handler for watchlist operations."""

import logging

from models.rest_api.entitybase.v1.handler import Handler

from models.data.rest_api.v1.request import WatchlistRemoveRequest
from models.data.rest_api.v1.response import WatchCounts
from models.data.rest_api.v1.response import (
    MessageResponse,
    NotificationResponse,
)
from models.rest_api.utils import raise_validation_error
from models.data.rest_api.v1.request import (
    WatchlistAddRequest,
    MarkCheckedRequest,
)
from models.data.rest_api.v1.response import WatchlistResponse

logger = logging.getLogger(__name__)


class WatchlistHandler(Handler):
    """Handler for watchlist-related operations."""

    def add_watch(self, request: WatchlistAddRequest) -> MessageResponse:
        """Add a watchlist entry."""
        # Check if user exists
        if not self.state.vitess_client.user_repository.user_exists(request.user_id):
            raise_validation_error("User not registered", status_code=400)

        # Check if watchlist is enabled
        if not self.state.vitess_client.user_repository.is_watchlist_enabled(
            request.user_id
        ):
            raise_validation_error(
                "Watchlist is disabled for this user", status_code=400
            )

        result = self.state.vitess_client.watchlist_repository.add_watch(
            request.user_id, request.entity_id, request.properties
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to add watch", status_code=500
            )

        # Update activity
        activity_result = self.state.vitess_client.user_repository.update_user_activity(
            request.user_id
        )
        if not activity_result.success:
            # Log error but don't fail the watch add
            logger.warning(f"Failed to update user activity: {activity_result.error}")
        return MessageResponse(message="Watch added")

    def remove_watch(self, request: WatchlistRemoveRequest) -> MessageResponse:
        """Remove a watchlist entry."""
        self.state.vitess_client.watchlist_repository.remove_watch(
            request.user_id, request.entity_id, request.properties
        )
        return MessageResponse(message="Watch removed")

    def remove_watch_by_id(self, watch_id: int) -> MessageResponse:
        """Remove a watchlist entry by ID."""
        result = self.state.vitess_client.watchlist_repository.remove_watch_by_id(
            watch_id
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to remove watch", status_code=404
            )
        return MessageResponse(message="Watch removed")

    def get_watches(self, user_id: int) -> WatchlistResponse:
        """Get user's watchlist."""
        # Check if user exists
        if not self.state.vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        # Check if watchlist is enabled
        if not self.state.vitess_client.user_repository.is_watchlist_enabled(user_id):
            raise_validation_error(
                "Watchlist is disabled for this user", status_code=400
            )

        watches = self.state.vitess_client.watchlist_repository.get_watches_for_user(
            user_id
        )
        # Update activity
        self.state.vitess_client.user_repository.update_user_activity(user_id)
        return WatchlistResponse(user_id=user_id, watches=watches)

    def get_notifications(
        self,
        user_id: int,
        hours: int = 24,
        limit: int = 50,
        offset: int = 0,
    ) -> NotificationResponse:
        """Get user's recent notifications within time span."""
        # Check if user exists
        if not self.state.vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        # Check if watchlist is enabled
        if not self.state.vitess_client.user_repository.is_watchlist_enabled(user_id):
            raise_validation_error(
                "Watchlist is disabled for this user", status_code=400
            )

        notifications = (
            self.state.vitess_client.watchlist_repository.get_user_notifications(
                user_id, hours, limit, offset
            )
        )
        # Update activity
        self.state.vitess_client.user_repository.update_user_activity(user_id)
        return NotificationResponse(user_id=user_id, notifications=notifications)

    def mark_checked(
        self, user_id: int, request: MarkCheckedRequest
    ) -> MessageResponse:
        """Mark a notification as checked."""
        self.state.vitess_client.watchlist_repository.mark_notification_checked(
            request.notification_id, user_id
        )
        return MessageResponse(message="Notification marked as checked")

    def get_watch_counts(self, user_id: int) -> WatchCounts:
        """Get user's watch counts."""
        entity_count = (
            self.state.vitess_client.watchlist_repository.get_entity_watch_count(
                user_id
            )
        )
        property_count = (
            self.state.vitess_client.watchlist_repository.get_property_watch_count(
                user_id
            )
        )
        return WatchCounts(entity_count=entity_count, property_count=property_count)
