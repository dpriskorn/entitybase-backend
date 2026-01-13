"""Handler for user preference operations."""

from models.infrastructure.vitess_client import VitessClient
from models.validation.utils import raise_validation_error
from models.rest_api.request.user_preferences import UserPreferencesRequest
from models.rest_api.response.user_preferences import UserPreferencesResponse


class UserPreferencesHandler:
    """Handler for user preference operations."""

    def get_preferences(
        self, user_id: int, vitess_client: VitessClient
    ) -> UserPreferencesResponse:
        """Get user's notification preferences."""
        # Check if user exists
        if not vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        prefs = vitess_client.user_repository.get_user_preferences(user_id)
        if prefs is None:
            # Return defaults if no custom preferences set
            prefs = {"notification_limit": 50, "retention_hours": 24}

        return UserPreferencesResponse(
            user_id=user_id,
            notification_limit=prefs["notification_limit"],
            retention_hours=prefs["retention_hours"],
        )

    def update_preferences(
        self, user_id: int, request: UserPreferencesRequest, vitess_client: VitessClient
    ) -> UserPreferencesResponse:
        """Update user's notification preferences."""
        # Check if user exists
        if not vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        vitess_client.user_repository.update_user_preferences(
            user_id=user_id,
            notification_limit=request.notification_limit,
            retention_hours=request.retention_hours,
        )

        return UserPreferencesResponse(
            user_id=user_id,
            notification_limit=request.notification_limit,
            retention_hours=request.retention_hours,
        )
