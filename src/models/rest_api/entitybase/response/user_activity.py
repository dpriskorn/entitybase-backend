"""Response models for user activity operations."""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from models.rest_api.entitybase.request.enums import UserActivityType


class UserActivityItemResponse(BaseModel):
    """Individual user activity item."""

    id: int
    user_id: int
    activity_type: UserActivityType
    entity_id: str = Field(default="")
    revision_id: int = Field(default=0)
    created_at: datetime


class UserActivityResponse(BaseModel):
    """Response for user activity query."""

    user_id: int = Field(description="User ID")
    activities: List[UserActivityItemResponse] = Field(description="List of user activities")

