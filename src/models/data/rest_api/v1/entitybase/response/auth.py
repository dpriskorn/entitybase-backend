"""Authentication response models."""

from pydantic import BaseModel, Field

from models.data.rest_api.v1.entitybase.response.user import UserResponse


class LoginResponse(BaseModel):
    """Response model for successful login."""

    model_config = {"extra": "forbid"}

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry time in seconds")
    user: UserResponse = Field(..., description="User information")


class RegisterResponse(BaseModel):
    """Response model for successful user registration."""

    model_config = {"extra": "forbid"}

    user_id: int = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role")
