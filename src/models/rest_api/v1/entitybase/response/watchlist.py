from typing import List

from pydantic import BaseModel, Field


class WatchlistEntryResponse(BaseModel):
    """Watchlist entry for database."""

    id: int = Field(default=0, description="Unique identifier for the watchlist entry")
    user_id: int = Field(description="User ID who owns the watchlist entry")
    internal_entity_id: int = Field(description="Internal entity ID being watched")
    watched_properties: List[str] | None = Field(
        default=None,
        description="List of specific properties being watched, null for all",
    )


class WatchlistResponse(BaseModel):
    """Response for listing user's watchlist."""

    user_id: int = Field(description="User ID for whom the watchlist is returned")
    watches: List[dict] = Field(
        description="List of watchlist entries with entity_id and properties"
    )  # List of {"entity_id": str, "properties": List[str] | None}
