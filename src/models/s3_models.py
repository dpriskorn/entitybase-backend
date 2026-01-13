"""S3-related models and configurations."""

from typing import Any, Dict

from pydantic import BaseModel, field_validator

from models.infrastructure.config import Config
from models.rest_api.response.statement import StatementResponse


class EntityData(BaseModel):
    """Typed model for entity data in revisions."""
    id: str
    type: str
    labels: Dict[str, Any] | None = None
    descriptions: Dict[str, Any] | None = None
    aliases: Dict[str, Any] | None = None
    claims: Dict[str, Any] | None = None
    sitelinks: Dict[str, Any] | None = None


class S3Config(Config):
    """Configuration for S3 connections."""

    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str


class RevisionMetadata(BaseModel):
    """Metadata for stored revisions."""

    key: str


class RevisionData(BaseModel):
    """Model for revision JSON data structure."""

    schema_version: str
    entity: EntityData
    redirects_to: str | None = None


class RevisionReadResponse(BaseModel):
    """Response model for reading revisions."""

    entity_id: str
    revision_id: int
    data: RevisionData
    content: Dict[str, Any]
    created_at: str | None = None
    user_id: int | None = None
    edit_summary: str | None = None


class StoredStatement(StatementResponse):
    """Statement format for S3 storage.

    Subclass of StatementResponse to ensure compatibility with API responses.
    Adds no additional fields, maintains same structure.
    """

    pass
