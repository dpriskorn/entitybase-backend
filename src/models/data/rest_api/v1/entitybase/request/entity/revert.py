"""Request models for entity revert operations."""

from pydantic import BaseModel, Field


class EntityRevertRequest(BaseModel):
    """Request to revert an entity to a previous revision."""

    to_revision_id: int = Field(..., gt=0, description="Revision ID to revert to")
    reason: str = Field("", max_length=500, description="Reason for reversion")
    watchlist_context: dict | None = Field(
        None, description="Optional watchlist context"
    )


class RedirectRevertRequest(BaseModel):
    revert_to_revision_id: int = Field(
        ..., description="Revision ID to revert to (e.g., 12340)."
    )
    revert_reason: str = Field(..., description="Reason for reverting redirect")
    created_by: str = Field(default="rest-api")
