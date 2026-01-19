"""Response models for user activity operations."""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from models.rest_api.entitybase.request.enums import UserActivityType


class UserActivityItemResponse(BaseModel):
    """Individual user activity item."""

    id: int = Field(description="Unique identifier for the activity")
    user_id: int = Field(description="User ID who performed the activity")
    activity_type: UserActivityType = Field(description="Type of activity performed")
    entity_id: str = Field(default="", description="Entity ID associated with the activity")
    revision_id: int = Field(default=0, description="Revision ID associated with the activity")
    created_at: datetime = Field(description="Timestamp when the activity occurred")


class UserActivityResponse(BaseModel):
    """Response for user activity query."""

    user_id: int = Field(description="User ID")
    activities: List[UserActivityItemResponse] = Field(description="List of user activities")

