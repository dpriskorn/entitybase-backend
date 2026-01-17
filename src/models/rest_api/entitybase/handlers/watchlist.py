"""Handler for watchlist operations."""

from models.infrastructure.vitess_client import VitessClient
from models.rest_api.entitybase.response.misc import WatchCounts
from models.rest_api.entitybase.response.user import MessageResponse
from models.validation.utils import raise_validation_error
from models.watchlist import (
    WatchlistAddRequest,
    WatchlistRemoveRequest,
    WatchlistResponse,
    NotificationResponse,
    MarkCheckedRequest,
)


class WatchlistHandler:
    """Handler for watchlist-related operations."""

    def add_watch(
        self, request: WatchlistAddRequest, vitess_client: VitessClient
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
        vitess_client.user_repository.update_user_activity(request.user_id)
        return MessageResponse(message="Watch added")

    def remove_watch(
        self, request: WatchlistRemoveRequest, vitess_client: VitessClient
    ) -> MessageResponse:
        """Remove a watchlist entry."""
        vitess_client.watchlist_repository.remove_watch(
            request.user_id, request.entity_id, request.properties
        )
        return MessageResponse(message="Watch removed")

    def get_watches(
        self, user_id: int, vitess_client: VitessClient
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
        vitess_client.user_repository.update_user_activity(user_id)
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
        vitess_client.user_repository.update_user_activity(user_id)
        return NotificationResponse(user_id=user_id, notifications=notifications)

    def mark_checked(
        self, user_id: int, request: MarkCheckedRequest, vitess_client: VitessClient
    ) -> MessageResponse:
        """Mark a notification as checked."""
        vitess_client.watchlist_repository.mark_notification_checked(
            request.notification_id, user_id
        )
        return MessageResponse(message="Notification marked as checked")

    def get_watch_counts(
        self, user_id: int, vitess_client: VitessClient
    ) -> WatchCounts:
        """Get user's watch counts."""
        entity_count = vitess_client.watchlist_repository.get_entity_watch_count(
            user_id
        )
        property_count = vitess_client.watchlist_repository.get_property_watch_count(
            user_id
        )
        return WatchCounts(entity_count=entity_count, property_count=property_count)
