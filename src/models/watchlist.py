"""Watchlist models."""

from typing import List

from pydantic import BaseModel, Field


class WatchlistEntry(BaseModel):
    """Watchlist entry for database."""

    id: int | None = None
    user_id: int
    internal_entity_id: int
    watched_properties: List[str] | None = Field(default=None)


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
    """Request to remove a watchlist entry by ID."""

    watch_id: int = Field(..., description="Watchlist entry ID to remove")


class MarkCheckedRequest(BaseModel):
    """Request to mark notification as checked."""

    notification_id: int
