"""User models."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """User model.
    We intentionally don't have auth, nor store the usernames."""

    user_id: int
    created_at: datetime
    preferences: dict | None = Field(default=None)


class UserCreateResponse(BaseModel):
    """Response for user creation."""

    user_id: int
    created: bool


class WatchlistToggleResponse(BaseModel):
    """Response for watchlist toggle."""

    user_id: int
    enabled: bool


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class NotificationResponse(BaseModel):
    """Response for user notifications."""

    user_id: int
    notifications: list
