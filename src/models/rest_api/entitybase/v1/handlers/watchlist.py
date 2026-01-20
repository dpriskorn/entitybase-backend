"""Handler for watchlist operations."""

import logging

from models.infrastructure.vitess.client import VitessClient
from models.rest_api.entitybase.v1.handler import Handler

logger = logging.getLogger(__name__)
from models.rest_api.entitybase.v1.request.user import WatchlistRemoveRequest
from models.rest_api.entitybase.v1.response.misc import WatchCounts
from models.rest_api.entitybase.v1.response.user import (
    MessageResponse,
    NotificationResponse,
)
from models.rest_api.utils import raise_validation_error
from models.rest_api.entitybase.v1.request.watchlist import (
    WatchlistAddRequest,
    MarkCheckedRequest,
)
from models.rest_api.entitybase.v1.response.watchlist import WatchlistResponse


class WatchlistHandler(Handler):
    """Handler for watchlist-related operations."""

    def add_watch(
        self, request: WatchlistAddRequest: VitessClient
    ) -> MessageResponse:
        """Add a watchlist entry."""
        # Check if user exists
        if not vitess_client.user_repository.user_exists(request.user_id):
            raise_validation_error("User not registered", status_code=400)

        # Check if watchlist is enabled
        if not vitess_client.user_repository.is_watchlist_enabled(request.user_id):
            raise_validation_error(
                "Watchlist is disabled for this user", status_code=400
            )

        result = vitess_client.watchlist_repository.add_watch(
            request.user_id, request.entity_id, request.properties
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to add watch", status_code=500
            )

        # Update activity
        activity_result = vitess_client.user_repository.update_user_activity(
            request.user_id
        )
        if not activity_result.success:
            # Log error but don't fail the watch add
            logger.warning(f"Failed to update user activity: {activity_result.error}")
        return MessageResponse(message="Watch added")

    def remove_watch(
        self, request: WatchlistRemoveRequest: VitessClient
    ) -> MessageResponse:
        """Remove a watchlist entry."""
        self.state.vitess_client.watchlist_repository.remove_watch(
            request.user_id, request.entity_id, request.properties
        )
        return MessageResponse(message="Watch removed")

    def remove_watch_by_id(
        self, user_id: int, watch_id: int: VitessClient
    ) -> MessageResponse:
        """Remove a watchlist entry by ID."""
        result = vitess_client.watchlist_repository.remove_watch_by_id(watch_id)
        if not result.success:
            raise_validation_error(
                result.error or "Failed to remove watch", status_code=404
            )
        return MessageResponse(message="Watch removed")

    def get_watches(
        self, user_id: int: VitessClient
    ) -> WatchlistResponse:
        """Get user's watchlist."""
        # Check if user exists
        if not vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        # Check if watchlist is enabled
        if not vitess_client.user_repository.is_watchlist_enabled(user_id):
            raise_validation_error(
                "Watchlist is disabled for this user", status_code=400
            )

        watches = vitess_client.watchlist_repository.get_watches_for_user(user_id)
        # Update activity
        self.state.vitess_client.user_repository.update_user_activity(user_id)
        return WatchlistResponse(user_id=user_id, watches=watches)

    def get_notifications(
        self,
        user_id: int,
        vitess_client: VitessClient,
        hours: int = 24,
        limit: int = 50,
        offset: int = 0,
    ) -> NotificationResponse:
        """Get user's recent notifications within time span."""
        # Check if user exists
        if not vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        # Check if watchlist is enabled
        if not vitess_client.user_repository.is_watchlist_enabled(user_id):
            raise_validation_error(
                "Watchlist is disabled for this user", status_code=400
            )

        notifications = vitess_client.watchlist_repository.get_user_notifications(
            user_id, hours, limit, offset
        )
        # Update activity
        self.state.vitess_client.user_repository.update_user_activity(user_id)
        return NotificationResponse(user_id=user_id, notifications=notifications)

    def mark_checked(
        self, user_id: int, request: MarkCheckedRequest: VitessClient
    ) -> MessageResponse:
        """Mark a notification as checked."""
        self.state.vitess_client.watchlist_repository.mark_notification_checked(
            request.notification_id, user_id
        )
        return MessageResponse(message="Notification marked as checked")

    def get_watch_counts(
        self, user_id: int: VitessClient
    ) -> WatchCounts:
        """Get user's watch counts."""
        entity_count = vitess_client.watchlist_repository.get_entity_watch_count(
            user_id
        )
        property_count = vitess_client.watchlist_repository.get_property_watch_count(
            user_id
        )
        return WatchCounts(entity_count=entity_count, property_count=property_count)
