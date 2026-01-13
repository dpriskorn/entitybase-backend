"""User models."""

from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    """User model.
    We intentionally don't have auth, nor store the usernames."""

    user_id: int
    created_at: datetime
    preferences: dict | None = Field(default=None)
