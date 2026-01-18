"""Response models for user operations."""

from pydantic import BaseModel, Field

from models.watchlist import WatchlistResponse, NotificationResponse


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
