"""Response models for user operations."""

from typing import List, Optional

from pydantic import BaseModel, Field
from datetime import datetime


class Notification(BaseModel):
    """Notification model."""

    id: int
    entity_id: str
    revision_id: int = Field(default=0)
    change_type: str
    changed_properties: Optional[List[str]]
    event_timestamp: datetime
    is_checked: bool
    checked_at: Optional[datetime]


class UserCreateResponse(BaseModel):
    """Response for user creation."""

    user_id: int = Field(description="User ID")
    created: bool = Field(
        description="Whether the user was newly created"
    )  # True if newly created, False if already existed


class WatchlistToggleResponse(BaseModel):
    """Response for watchlist toggle."""

    user_id: int = Field(description="User ID")
    enabled: bool = Field(description="Whether watchlist is enabled")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(description="Response message")


class TermsByType(BaseModel):
    """Response for terms count by type."""

    labels: int = Field(description="Number of labels")
    descriptions: int = Field(description="Number of descriptions")
    aliases: int = Field(description="Number of aliases")


class NotificationResponse(BaseModel):
    """Response for user notifications."""

    user_id: int
    notifications: List[Notification]
