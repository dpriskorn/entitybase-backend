"""Request models for entity revert operations."""

from pydantic import BaseModel, Field


class EntityRevertRequest(BaseModel):
    """Request to revert an entity to a previous revision."""

    to_revision_id: int = Field(..., gt=0, description="Revision ID to revert to")
    reason: str = Field("", max_length=500, description="Reason for reversion")
    reverted_by_user_id: int = Field(
        ..., description="MediaWiki user ID performing the revert"
    )
    watchlist_context: dict | None = Field(
        None, description="Optional watchlist context"
    )
