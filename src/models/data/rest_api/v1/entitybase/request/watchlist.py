"""Watchlist models."""

from typing import List

from pydantic import BaseModel, Field


class WatchlistAddRequest(BaseModel):
    """Request to add a watchlist entry."""

    entity_id: str = Field(..., description="Entity ID (e.g., Q42)")
    properties: List[str] | None = Field(
        None, description="Specific properties to watch, empty for whole entity"
    )


class WatchlistRemoveRequest(BaseModel):
    """Request to remove a watchlist entry."""

    entity_id: str = Field(..., description="Entity ID to remove from watchlist")
    properties: List[str] | None = Field(
        None, description="Specific properties to stop watching"
    )


class MarkCheckedRequest(BaseModel):
    """Request to mark notification as checked."""

    notification_id: int
