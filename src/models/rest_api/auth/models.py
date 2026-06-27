"""Authentication models for Entitybase API."""

from pydantic import BaseModel, Field

from models.data.common.roles import UserRole


class User(BaseModel):
    """User model for authentication (internal, not exposed via API)."""

    model_config = {"extra": "forbid"}

    user_id: int = Field(..., description="Database user ID")
    username: str = Field(..., description="Unique username")
    role: UserRole = Field(..., description="User role")


class AuthenticatedRequest(BaseModel):
    """Returned by verify_auth dependency - contains authenticated user and edit summary."""

    model_config = {"extra": "forbid"}

    user: User
    edit_summary: str = Field(..., min_length=1, max_length=200)
    base_revision_id: int = Field(default=0, description="Base revision ID for optimistic locking")
