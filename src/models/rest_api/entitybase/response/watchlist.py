from typing import List

from pydantic import BaseModel, Field


class WatchlistEntryResponse(BaseModel):
    """Watchlist entry for database."""

    id: int = Field(default=0)
    user_id: int
    internal_entity_id: int
    watched_properties: List[str] | None = Field(default=None)


class WatchlistResponse(BaseModel):
    """Response for listing user's watchlist."""

    user_id: int
    watches: List[dict]  # List of {"entity_id": str, "properties": List[str] | None}
