"""Response models for user activity operations."""

from typing import List

from pydantic import BaseModel

from models.user_activity import UserActivityItem


class UserActivityResponse(BaseModel):
    """Response for user activity query."""

    user_id: int
    activities: List[UserActivityItem]
