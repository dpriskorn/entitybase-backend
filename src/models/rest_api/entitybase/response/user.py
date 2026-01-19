"""Response models for user operations."""

from typing import List, Optional

from pydantic import BaseModel, Field
from datetime import datetime


class Notification(BaseModel):
    """Notification model."""

    id: int = Field(description="Unique identifier for the notification")
    entity_id: str = Field(description="Entity ID associated with the notification")
    revision_id: int = Field(default=0, description="Revision ID associated with the notification")
    change_type: str = Field(description="Type of change that triggered the notification")
    changed_properties: Optional[List[str]] = Field(description="List of properties that changed")
    event_timestamp: datetime = Field(description="Timestamp when the event occurred")
    is_checked: bool = Field(description="Whether the notification has been checked")
    checked_at: Optional[datetime] = Field(description="Timestamp when the notification was checked")


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

    user_id: int = Field(description="User ID for whom notifications are returned")
    notifications: List[Notification] = Field(description="List of notifications for the user")
