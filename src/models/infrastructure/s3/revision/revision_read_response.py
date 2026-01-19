"""Revision read response model."""

from typing import Any

from pydantic import BaseModel, Field

from .revision_data import RevisionData


class RevisionReadResponse(BaseModel):
    """Response model for reading revisions."""

    entity_id: str
    revision_id: int
    data: "RevisionData"
    content: dict[str, Any]
    schema_version: str = Field(default="")
    created_at: str = Field(default="")
    user_id: int = Field(default=0)
    edit_summary: str = Field(default="")
    redirects_to: str = Field(default="")