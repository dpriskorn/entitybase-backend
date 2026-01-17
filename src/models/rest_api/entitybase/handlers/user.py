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

        vitess_client.user_repository.set_watchlist_enabled(user_id, request.enabled)
        return WatchlistToggleResponse(user_id=user_id, enabled=request.enabled)
