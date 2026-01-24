"""Handler for user activity operations."""

from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.request import UserActivityType
from models.data.rest_api.v1.entitybase.response import UserActivityResponse
from models.rest_api.utils import raise_validation_error


class UserActivityHandler(Handler):
    """Handler for user activity operations."""

    def get_user_activities(
        self,
        user_id: int,
        activity_type: str = "",
        hours: int = 24,
        limit: int = 50,
        offset: int = 0,
    ) -> UserActivityResponse:
        """Get user's activities."""
        # Check if user exists
        if not self.state.vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        # Validate activity_type if provided
        if activity_type and activity_type not in [t.value for t in UserActivityType]:
            raise_validation_error(
                f"Invalid activity type: {activity_type}", status_code=400
            )

        activity_type_param = (
            None if activity_type == "" else UserActivityType(activity_type)
        )
        result = self.state.vitess_client.user_repository.get_user_activities(
            user_id, activity_type_param, hours, limit, offset
        )

        if not result.success:
            raise_validation_error(
                result.error or "Failed to get user activities", status_code=500
            )

        return UserActivityResponse(user_id=user_id, activities=result.data)
