"""Handler for user preference operations."""

from datetime import datetime, timezone

from models.config.settings import settings
from models.data.infrastructure.stream.change_type import ChangeType
from models.infrastructure.stream.event import UserChangeEvent
from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.request.user_preferences import (
    UserPreferencesRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    UserPreferencesResponse,
)
from models.rest_api.utils import raise_validation_error


class UserPreferencesHandler(Handler):
    """Handler for user preference operations."""

    def get_preferences(self, user_id: int) -> UserPreferencesResponse:
        """Get user's notification preferences."""
        if not self.state.vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=404)

        result = self.state.vitess_client.user_repository.get_user_preferences(user_id)  # type: ignore[union-attr]
        if not result.success:
            if "User preferences not found" in (result.error or ""):
                prefs = {"notification_limit": 50, "retention_hours": 24}
            else:
                raise_validation_error(
                    result.error or "Failed to get user preferences", status_code=500
                )
        elif result.data is None or not isinstance(result.data, dict):
            prefs = {"notification_limit": 50, "retention_hours": 24}
        else:
            prefs = result.data

        return UserPreferencesResponse(
            user_id=user_id,
            notification_limit=prefs["notification_limit"],
            retention_hours=prefs["retention_hours"],
        )

    async def update_preferences(
        self, user_id: int, request: UserPreferencesRequest
    ) -> UserPreferencesResponse:
        """Update user's notification preferences."""
        if not self.state.vitess_client.user_repository.user_exists(user_id):  # type: ignore[union-attr]
            raise_validation_error("User not registered", status_code=404)

        result = self.state.vitess_client.user_repository.update_user_preferences(  # type: ignore[union-attr]
            user_id=user_id,
            notification_limit=request.notification_limit,
            retention_hours=request.retention_hours,
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to update user preferences", status_code=500
            )

        await self._publish_user_change_event(str(user_id))
        return UserPreferencesResponse(
            user_id=user_id,
            notification_limit=request.notification_limit,
            retention_hours=request.retention_hours,
        )

    async def _publish_user_change_event(self, user_id: str) -> None:
        """Publish user preferences updated event to stream."""
        if settings.streaming_enabled and self.state.user_change_stream_producer:
            event = UserChangeEvent(
                user=user_id,
                type=ChangeType.PREFERENCES_UPDATED,
                ts=datetime.now(timezone.utc),
            )
            await self.state.user_change_stream_producer.publish(event)
