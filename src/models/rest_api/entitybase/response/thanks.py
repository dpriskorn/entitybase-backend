"""Response models for thanks operations."""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ThankResponse(BaseModel):
    """Response for sending a thank."""

    thank_id: int = Field(description="Thank ID")
    from_user_id: int = Field(description="User ID sending the thank")
    to_user_id: int = Field(description="User ID receiving the thank")
    entity_id: str = Field(description="Entity ID")
    revision_id: int = Field(description="Revision ID")
    created_at: str = Field(
        description="Creation timestamp"
    )  # ISO format datetime string


class ThanksListResponse(BaseModel):
    """Response for thanks list queries."""

    user_id: int = Field(description="User ID")
    thanks: List["ThankItemResponse"] = Field(description="List of thanks")
    total_count: int = Field(description="Total count of thanks")
    has_more: bool = Field(description="Whether there are more thanks available")


class ThankItemResponse(BaseModel):
    """Individual thank item."""

    id: int
    from_user_id: int
    to_user_id: int
    entity_id: str
    revision_id: int
    created_at: datetime
