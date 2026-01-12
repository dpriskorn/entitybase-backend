"""Request models for user operations."""

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    """Request to create/register a user."""

    user_id: int = Field(..., description="MediaWiki user ID", gt=0)


class WatchlistToggleRequest(BaseModel):
    """Request to enable/disable watchlist for user."""

    enabled: bool
