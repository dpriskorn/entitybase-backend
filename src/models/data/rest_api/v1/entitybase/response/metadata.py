"""Metadata response models."""

from typing import Any

from pydantic import BaseModel, Field


class RevisionMetadataResponse(BaseModel):
    """Metadata for entity revisions."""

    revision_id: int = Field(description="Revision ID")
    created_at: str = Field(description="Creation timestamp")
    user_id: int = Field(description="User ID")
    edit_summary: str = Field(description="Edit summary")


class MetadataContent(BaseModel):
    """Model for metadata content."""

    ref_count: int = Field(..., description="Reference count")


class MetadataData(BaseModel):
    """Model for metadata data content."""

    model_config = {"extra": "allow"}

    data: str | dict[str, Any] = Field(
        ..., description="Metadata content as text or structured data"
    )
