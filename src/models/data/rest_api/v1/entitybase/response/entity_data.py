"""Entity response models."""

from typing import Any

from pydantic import BaseModel, Field


class PropertiesResponse(BaseModel):
    """Response model for entity properties."""

    properties: dict[str, Any] = Field(..., description="Entity properties")


class EntitiesResponse(BaseModel):
    """Response model for entities search."""

    entities: dict[str, Any] = Field(..., description="Entities data")


class EntityJsonResponse(BaseModel):
    """Response model for JSON format entity data."""

    data: dict[str, Any] = Field(..., description="Entity data in JSON format")


class TurtleResponse(BaseModel):
    """Response model for Turtle format entity data."""

    turtle: str = Field(..., description="Entity data in Turtle format")


class TopEntityByBacklinks(BaseModel):
    """Model for entity backlink ranking."""

    entity_id: str = Field(..., description="Entity ID")
    backlink_count: int = Field(..., description="Number of backlinks to this entity")


class ElasticsearchDocumentResponse(BaseModel):
    """Response model for Elasticsearch document preview."""

    document: dict[str, Any] = Field(..., description="Elasticsearch document")
