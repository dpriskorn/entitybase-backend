"""Response models for user activity operations."""

from typing import List

from pydantic import BaseModel, Field

from models.user_activity import UserActivityItem


class UserActivityResponse(BaseModel):
    """Response for user activity query."""

    user_id: int = Field(description="User ID")
    activities: List[UserActivityItem] = Field(description="List of user activities")
