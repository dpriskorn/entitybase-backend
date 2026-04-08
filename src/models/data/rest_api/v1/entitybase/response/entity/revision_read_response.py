"""Revision read response model."""

from typing import Any

from pydantic import BaseModel, Field

from models.infrastructure.s3.revision.revision_data import RevisionData


class RevisionReadResponse(BaseModel):
    """Response model for reading revisions."""

    entity_id: str = Field(..., description="Entity ID")
    revision_id: int = Field(..., description="Revision ID")
    data: RevisionData = Field(..., description="Revision data object")
    content: dict[str, Any] = Field(..., description="Raw revision content")
    schema_version: str = Field(default="", description="Schema version")
    created_at: str = Field(default="", description="Timestamp when revision was created")
    user_id: int = Field(default=0, description="User ID who made the revision")
    edit_summary: str = Field(default="", description="Edit summary text")
    redirects_to: str = Field(default="", description="Redirect target if entity was redirected")
