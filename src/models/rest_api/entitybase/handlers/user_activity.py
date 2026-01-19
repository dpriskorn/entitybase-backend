"""Handler for user activity operations."""

from models.infrastructure.vitess.vitess_client import VitessClient
from models.rest_api.entitybase.response.user_activity import UserActivityResponse
from models.rest_api.entitybase.request.enums import UserActivityType
from models.rest_api.utils import raise_validation_error


class UserActivityHandler:
    """Handler for user activity operations."""

    def get_user_activities(
        self,
        user_id: int,
        vitess_client: VitessClient,
        activity_type: str = "",
        hours: int = 24,
        limit: int = 50,
        offset: int = 0,
    ) -> UserActivityResponse:
        """Get user's activities."""
        # Check if user exists
        if not vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        # Validate activity_type if provided
        if activity_type and activity_type not in [t.value for t in UserActivityType]:
            raise_validation_error(
                f"Invalid activity type: {activity_type}", status_code=400
            )

        activity_type_param = (
            None if activity_type == "" else UserActivityType(activity_type)
        )
        result = vitess_client.user_repository.get_user_activities(
            user_id, activity_type_param, hours, limit, offset
        )

        if not result.success:
            raise_validation_error(
                result.error or "Failed to get user activities", status_code=500
            )

        return UserActivityResponse(user_id=user_id, activities=result.data)
