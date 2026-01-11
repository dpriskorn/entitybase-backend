"""Miscellaneous response models."""

from typing import Any

from fastapi import Response

from pydantic import BaseModel, Field


class TtlResponse(Response):
    def __init__(self, content: str):
        super().__init__(
            content=content,
            media_type="text/turtle",
        )


class CleanupOrphanedResponse(BaseModel):
    cleaned_count: int = Field(
        ...,
        description="Number of statements cleaned up from S3 and Vitess",
    )
    failed_count: int = Field(
        default=0,
        description="Number of statements that failed to clean up",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="List of error messages for failed cleanups",
    )


class RevisionMetadataResponse(BaseModel):
    """Metadata for entity revisions."""

    revision_id: int
    created_at: str


class LabelResponse(BaseModel):
    """Response model for entity labels."""

    value: str = Field(..., description="The label text for the specified language")


class DescriptionResponse(BaseModel):
    """Response model for entity descriptions."""

    value: str = Field(
        ..., description="The description text for the specified language"
    )


class AliasesResponse(BaseModel):
    """Response model for entity aliases."""

    aliases: list[str] = Field(
        ..., description="List of alias texts for the specified language"
    )


class RawRevisionResponse(BaseModel):
    """Response model for raw revision data."""

    data: dict[str, Any] = Field(..., description="Raw revision data from storage")
