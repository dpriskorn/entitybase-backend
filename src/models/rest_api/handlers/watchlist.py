"""Handler for watchlist operations."""

from models.validation.utils import raise_validation_error
from models.watchlist import (
    WatchlistAddRequest,
    WatchlistRemoveRequest,
    WatchlistResponse,
    NotificationResponse,
    MarkCheckedRequest,
)
from models.rest_api.response.user import MessageResponse


class WatchlistHandler:
    """Handler for watchlist-related operations."""

    def add_watch(self, request: WatchlistAddRequest, vitess_client) -> dict:
        """Add a watchlist entry."""
        # Check if user exists
        if not vitess_client.user_repository.user_exists(request.user_id):
            raise_validation_error("User not registered", status_code=400)

        # Check if watchlist is enabled
        if not vitess_client.user_repository.is_watchlist_enabled(request.user_id):
            raise_validation_error(
                "Watchlist is disabled for this user", status_code=400
            )

        vitess_client.watchlist_repository.add_watch(
            request.user_id, request.entity_id, request.properties
        )
        # Update activity
        vitess_client.user_repository.update_user_activity(request.user_id)
        return {"message": "Watch added"}

    def remove_watch(self, request: WatchlistRemoveRequest, vitess_client) -> dict:
        """Remove a watchlist entry."""
        vitess_client.watchlist_repository.remove_watch(
            request.user_id, request.entity_id, request.properties
        )
        return {"message": "Watch removed"}

    def get_watches(self, user_id: int, vitess_client) -> WatchlistResponse:
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
        vitess_client,
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
        self, user_id: int, request: MarkCheckedRequest, vitess_client
    ) -> MessageResponse:
        """Mark a notification as checked."""
        vitess_client.watchlist_repository.mark_notification_checked(
            request.notification_id, user_id
        )
        return MessageResponse(message="Notification marked as checked")
