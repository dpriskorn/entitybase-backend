"""User models."""

from datetime import datetime

from pydantic import BaseModel, Field

from models.data.common.roles import UserRole


class UserResponse(BaseModel):
    """User model for API responses."""

    user_id: int = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Unique username")
    role: UserRole = Field(..., description="User role")
    created_at: datetime = Field(..., description="Timestamp when user was created")
    preferences: dict | None = Field(
        default=None, description="User preferences dictionary"
    )


class UserCreateResponse(BaseModel):
    """Response for user creation."""

    user_id: int = Field(..., description="Unique user identifier for the created user")
    created: bool = Field(..., description="Whether a new user was created")


class WatchlistToggleResponse(BaseModel):
    """Response for watchlist toggle."""

    user_id: int = Field(..., description="User ID whose watchlist was toggled")
    enabled: bool = Field(..., description="Whether watchlist is now enabled")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message text")


class NotificationResponse(BaseModel):
    """Response for user notifications."""

    user_id: int = Field(..., description="User ID who owns the notifications")
    notifications: list = Field(..., description="List of user notifications")
