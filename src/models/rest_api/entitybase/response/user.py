"""Response models for user operations."""

from pydantic import BaseModel


class UserCreateResponse(BaseModel):
    """Response for user creation."""

    user_id: int
    created: bool  # True if newly created, False if already existed


class WatchlistToggleResponse(BaseModel):
    """Response for watchlist toggle."""

    user_id: int
    enabled: bool


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
