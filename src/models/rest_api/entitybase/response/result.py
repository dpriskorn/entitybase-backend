"""Result response models."""

from typing import Optional

from pydantic import BaseModel, Field


class RevisionIdResult(BaseModel):
    """Model for operations that return a revision ID."""

    revision_id: int = Field(default=0, description="The revision ID of the created/updated entity, or 0 for idempotent operations")


class RevisionResult(BaseModel):
    """Result of revision processing."""
    success: bool
    revision_id: int = Field(default=0)
    error: str = Field(default="")