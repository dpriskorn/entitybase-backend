"""Handler for user operations."""

from models.infrastructure.vitess_client import VitessClient
from models.rest_api.entitybase.response.user import (
    WatchlistToggleResponse,
    UserCreateResponse,
)
from models.validation.utils import raise_validation_error
from models.rest_api.entitybase.request.user import (
    UserCreateRequest,
    WatchlistToggleRequest,
)
from models.user import User


class UserHandler:
    """Handler for user-related operations."""

    def create_user(
        self, request: UserCreateRequest, vitess_client: VitessClient
    ) -> UserCreateResponse:
        """Create/register a user."""
        # Check if user already exists
        exists = vitess_client.user_repository.user_exists(request.user_id)
        if not exists:
            result = vitess_client.user_repository.create_user(request.user_id)
            if not result.success:
                raise_validation_error(
                    result.error or "Failed to create user", status_code=500
                )
            created = True
        else:
            created = False
        return UserCreateResponse(user_id=request.user_id, created=created)

    def get_user(self, user_id: int, vitess_client: VitessClient) -> User:
        """Get user by ID."""
        user = vitess_client.user_repository.get_user(user_id)
        if user is None:
            raise_validation_error("User not found", status_code=404)
        return user

    def toggle_watchlist(
        self, user_id: int, request: WatchlistToggleRequest, vitess_client: VitessClient
    ) -> WatchlistToggleResponse:
        """Enable or disable watchlist for user."""
        # Check if user exists
        if not vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        result = vitess_client.user_repository.set_watchlist_enabled(
            user_id, request.enabled
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to set watchlist", status_code=500
            )
        return WatchlistToggleResponse(user_id=user_id, enabled=request.enabled)

    def get_user_stats(self, vitess_client: VitessClient) -> dict:
        """Get user statistics from the daily stats table."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT stat_date, total_users, active_users FROM user_daily_stats ORDER BY stat_date DESC LIMIT 1"
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "date": row[0].isoformat(),
                        "total_users": row[1],
                        "active_users": row[2],
                    }
                else:
                    # Fallback to live computation if no data
                    from models.rest_api.entitybase.services.user_stats_service import UserStatsService
                    service = UserStatsService()
                    stats = service.compute_daily_stats(vitess_client)
                    return {
                        "date": "live",
                        "total_users": stats.total_users,
                        "active_users": stats.active_users,
                    }
