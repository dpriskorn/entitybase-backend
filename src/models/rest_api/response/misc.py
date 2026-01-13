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


class JsonSchema(BaseModel):
    """Model for JSON schema data."""

    data: dict[str, Any] = Field(..., description="The JSON schema dictionary")


class AliasesDict(BaseModel):
    """Model for extracted aliases dictionary."""

    aliases: dict[str, list[str]] = Field(..., description="Aliases per language")


class LabelsResponse(BaseModel):
    """Response model for all entity labels."""

    labels: dict[str, str] = Field(..., description="Labels per language")


class DescriptionsResponse(BaseModel):
    """Response model for all entity descriptions."""

    descriptions: dict[str, str] = Field(..., description="Descriptions per language")


class SitelinksResponse(BaseModel):
    """Response model for all entity sitelinks."""

    sitelinks: dict[str, str] = Field(..., description="Sitelinks per site")


class PropertiesResponse(BaseModel):
    """Response model for entity properties."""

    properties: dict[str, Any] = Field(..., description="Entity properties")


class MetadataContent(BaseModel):
    """Model for metadata content."""

    ref_count: int = Field(..., description="Reference count")


class TopEntityByBacklinks(BaseModel):
    """Model for entity backlink ranking."""

    entity_id: str = Field(..., description="Entity ID")
    backlink_count: int = Field(..., description="Number of backlinks to this entity")


class BacklinkStatisticsData(BaseModel):
    """Container for computed backlink statistics."""

    total_backlinks: int = Field(
        ..., description="Total number of backlink relationships"
    )
    unique_entities_with_backlinks: int = Field(
        ..., description="Number of entities with at least one backlink"
    )
    top_entities_by_backlinks: list[TopEntityByBacklinks] = Field(
        ..., description="Top entities by backlink count"
    )


class BacklinkStatisticsResponse(BaseModel):
    """API response for backlink statistics."""

    date: str = Field(..., description="Date of statistics computation")
    total_backlinks: int = Field(
        ..., description="Total number of backlink relationships"
    )
    unique_entities_with_backlinks: int = Field(
        ..., description="Number of entities with at least one backlink"
    )
    top_entities_by_backlinks: list[TopEntityByBacklinks] = Field(
        ..., description="Top entities by backlink count"
    )


class RawRevisionResponse(BaseModel):
    """Response model for raw revision data."""

    data: dict[str, Any] = Field(..., description="Raw revision data from storage")
