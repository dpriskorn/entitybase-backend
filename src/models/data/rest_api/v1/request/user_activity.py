"""Request models for user activity operations."""

from pydantic import BaseModel


class UserActivityRequest(BaseModel):
    """Request to filter user activities."""

    pass  # Filtering done via query params
