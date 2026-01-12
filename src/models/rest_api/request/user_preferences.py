"""Request models for user preference operations."""

from pydantic import BaseModel, Field


class UserPreferencesRequest(BaseModel):
    """Request to update user preferences."""

    notification_limit: int = Field(
        50, ge=50, le=500, description="Max notifications (50-500)"
    )
    retention_hours: int = Field(
        24, ge=1, le=720, description="Retention hours (1-720)"
    )
