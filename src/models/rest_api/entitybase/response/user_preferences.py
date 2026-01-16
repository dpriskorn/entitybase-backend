"""Response models for user preference operations."""

from pydantic import BaseModel


class UserPreferencesResponse(BaseModel):
    """Response for user preferences query."""

    user_id: int
    notification_limit: int
    retention_hours: int
