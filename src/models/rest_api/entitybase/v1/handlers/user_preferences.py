"""Handler for user preference operations."""

from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.request.user_preferences import (
    UserPreferencesRequest,
)
from models.data.rest_api.v1.response import (
    UserPreferencesResponse,
)
from models.rest_api.utils import raise_validation_error


class UserPreferencesHandler(Handler):
    """Handler for user preference operations."""

    def get_preferences(self, user_id: int) -> UserPreferencesResponse:
        """Get user's notification preferences."""
        # Check if user exists
        if not self.state.vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        result = self.state.vitess_client.user_repository.get_user_preferences(user_id)  # type: ignore[union-attr]
        if not result.success:
            if "User preferences not found" in (result.error or ""):
                # Return defaults if no custom preferences set
                prefs = {"notification_limit": 50, "retention_hours": 24}
            else:
                raise_validation_error(
                    result.error or "Failed to get user preferences", status_code=500
                )
        elif result.data is None or not isinstance(result.data, dict):
            # Return defaults if no custom preferences set or invalid data
            prefs = {"notification_limit": 50, "retention_hours": 24}
        else:
            prefs = result.data

        return UserPreferencesResponse(
            user_id=user_id,
            notification_limit=prefs["notification_limit"],
            retention_hours=prefs["retention_hours"],
        )

    def update_preferences(
        self, user_id: int, request: UserPreferencesRequest
    ) -> UserPreferencesResponse:
        """Update user's notification preferences."""
        # Check if user exists
        if not self.state.vitess_client.user_repository.user_exists(user_id):  # type: ignore[union-attr]
            raise_validation_error("User not registered", status_code=400)

        result = self.state.vitess_client.user_repository.update_user_preferences(  # type: ignore[union-attr]
            user_id=user_id,
            notification_limit=request.notification_limit,
            retention_hours=request.retention_hours,
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to update user preferences", status_code=500
            )

        return UserPreferencesResponse(
            user_id=user_id,
            notification_limit=request.notification_limit,
            retention_hours=request.retention_hours,
        )
