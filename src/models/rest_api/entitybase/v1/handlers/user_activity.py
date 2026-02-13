"""Handler for user activity operations."""

import logging

from fastapi import HTTPException, Query

from models.rest_api.entitybase.v1.handler import Handler

logger = logging.getLogger(__name__)
from models.data.rest_api.v1.entitybase.response import (
    UserActivityResponse,
    UserActivityItemResponse,
)
from models.data.rest_api.v1.entitybase.request.enums import UserActivityType
from models.rest_api.utils import raise_validation_error


class UserActivityHandler(Handler):
    """Handler for user activity operations."""

    def get_user_activity(
        self,
        user_id: int,
        activity_type: str | None = None,
        hours: int = 24,
        limit: int = 50,
        offset: int = 0,
    ) -> UserActivityResponse:
        """Get user's activity with filtering."""
        logger.debug(
            f"Getting user activity for user_id={user_id}, activity_type={activity_type}, hours={hours}, limit={limit}, offset={offset}"
        )
        logger.debug(f"Validating user existence for user_id={user_id}")
        # Validate user exists
        if not self.state.vitess_client.user_repository.user_exists(user_id):
            logger.warning(f"User {user_id} not found")
            raise_validation_error("User not registered", status_code=400)

        logger.debug(f"Validating activity_type={activity_type}")
        # Validate activity_type
        valid_types = {"ENTITY_CREATE", "ENTITY_EDIT", "ENTITY_DELETE"}
        if activity_type and activity_type not in valid_types:
            logger.warning(f"Invalid activity type: {activity_type}")
            raise_validation_error(
                f"Invalid activity type. Must be one of: {', '.join(valid_types)}",
                status_code=400,
            )

        logger.debug(f"Validating limit={limit}")
        # Validate limit
        valid_limits = {10, 25, 50, 100}
        if limit not in valid_limits:
            logger.warning(f"Invalid limit: {limit}")
            raise_validation_error(
                f"Limit must be one of: {', '.join(map(str, sorted(valid_limits)))}",
                status_code=400,
            )

        # Parse activity_type enum
        activity_type_enum = None
        if activity_type:
            logger.debug(f"Parsing activity_type enum: {activity_type}")
            try:
                activity_type_enum = UserActivityType(activity_type)
            except ValueError:
                logger.warning(f"Failed to parse activity_type enum: {activity_type}")
                raise_validation_error(
                    f"Invalid activity type: {activity_type}", status_code=400
                )

        logger.debug(f"Fetching user activities from repository")
        result = self.state.vitess_client.user_repository.get_user_activities(
            user_id=user_id,
            activity_type=activity_type_enum,
            hours=hours,
            limit=limit,
            offset=offset,
        )

        if not result.success:
            logger.error(f"Failed to get user activities: {result.error}")
            raise_validation_error(
                result.error or "Failed to get user activities", status_code=500
            )

        activities = result.data if result.data else []
        logger.debug(f"Found {len(activities)} user activities")
        return UserActivityResponse(user_id=user_id, activities=activities)
