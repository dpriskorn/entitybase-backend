"""Request models for user operations."""

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    """Request to create/register a user."""

    user_id: int = Field(..., description="MediaWiki user ID", gt=0)


class WatchlistToggleRequest(BaseModel):
    """Request to enable/disable watchlist for user."""

    enabled: bool


class WatchlistAddRequest(BaseModel):
    """Request to add a watchlist entry."""

    user_id: int = Field(..., description="User ID", gt=0)
    entity_id: str = Field(..., description="Entity ID to watch")
    properties: list[str] | None = Field(
        None, description="Specific properties to watch, or None for all"
    )


class WatchlistRemoveRequest(BaseModel):
    """Request to remove a watchlist entry."""

    user_id: int = Field(..., description="User ID", gt=0)
    entity_id: str = Field(..., description="Entity ID to unwatch")
    properties: list[str] | None = Field(
        None, description="Specific properties to unwatch, or None for all"
    )


class MarkCheckedRequest(BaseModel):
    """Request to mark a notification as checked."""

    notification_id: int = Field(..., description="Notification ID", gt=0)
