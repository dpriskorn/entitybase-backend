"""Watchlist models."""

from typing import List

from pydantic import BaseModel, Field


class WatchlistAddRequest(BaseModel):
    """Request to add a watchlist entry."""

    user_id: int = Field(..., description="MediaWiki user ID")
    entity_id: str = Field(..., description="Entity ID (e.g., Q42)")
    properties: List[str] | None = Field(
        None, description="Specific properties to watch, empty for whole entity"
    )


class WatchlistRemoveRequest(BaseModel):
    """Request to remove a watchlist entry by ID."""

    watch_id: int = Field(..., description="Watchlist entry ID to remove")


class MarkCheckedRequest(BaseModel):
    """Request to mark notification as checked."""

    notification_id: int
