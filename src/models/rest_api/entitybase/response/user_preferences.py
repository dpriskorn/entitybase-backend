"""Response models for user preference operations."""

from pydantic import BaseModel, Field


class UserPreferencesResponse(BaseModel):
    """Response for user preferences query."""

    user_id: int = Field(description="User ID")
    notification_limit: int = Field(description="Notification limit")
    retention_hours: int = Field(description="Retention hours")
