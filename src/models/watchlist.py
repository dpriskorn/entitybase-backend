"""Watchlist models."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class WatchlistEntry(BaseModel):
    """Watchlist entry for database."""

    user_id: int
    internal_entity_id: int
    watched_properties: List[str] | None = None


class WatchlistAddRequest(BaseModel):
    """Request to add a watchlist entry."""

    user_id: int = Field(..., description="MediaWiki user ID")
    entity_id: str = Field(..., description="Entity ID (e.g., Q42)")
    properties: List[str] | None = Field(
        None, description="Specific properties to watch, empty for whole entity"
    )


class WatchlistResponse(BaseModel):
    """Response for listing user's watchlist."""

    user_id: int
    watches: List[dict]  # List of {"entity_id": str, "properties": List[str] | None}


class WatchlistRemoveRequest(BaseModel):
    """Request to remove a watchlist entry."""

    user_id: int
    entity_id: str
    properties: List[str] | None = None


class Notification(BaseModel):
    """Notification model."""

    id: int
    entity_id: str
    revision_id: Optional[int]
    change_type: str
    changed_properties: Optional[List[str]]
    event_timestamp: datetime
    is_checked: bool
    checked_at: Optional[datetime]


class NotificationResponse(BaseModel):
    """Response for user notifications."""

    user_id: int
    notifications: List[Notification]


class MarkCheckedRequest(BaseModel):
    """Request to mark notification as checked."""

    notification_id: int
