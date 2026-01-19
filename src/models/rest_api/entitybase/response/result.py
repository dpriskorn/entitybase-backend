"""Result response models."""

from pydantic import BaseModel, Field


class RevisionIdResult(BaseModel):
    """Model for operations that return a revision ID."""

    revision_id: int | None = Field(description="The revision ID of the created/updated entity, or None for idempotent operations")


class RevisionResult(BaseModel):
    """Result of revision processing."""
    success: bool
    revision_id: int = Field(default=0)
    error: str = Field(default="")