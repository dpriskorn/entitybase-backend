"""Authentication request models."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request model for user login."""

    model_config = {"extra": "forbid"}

    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class RegisterRequest(BaseModel):
    """Request model for user registration (admin only)."""

    model_config = {"extra": "forbid"}

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (3-50 characters)",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
    )
