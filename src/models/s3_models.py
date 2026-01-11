"""S3-related models and configurations."""

from typing import Any, Dict

from pydantic import BaseModel

from models.rest_api.response.statement import StatementResponse
from models.infrastructure.config import Config


class S3Config(Config):
    """Configuration for S3 connections."""
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str


class RevisionMetadata(BaseModel):
    """Metadata for stored revisions."""
    key: str


class RevisionReadResponse(BaseModel):
    """Response model for reading revisions."""
    entity_id: str
    revision_id: int
    data: Dict[str, Any]


class StoredStatement(StatementResponse):
    """Statement format for S3 storage.

    Subclass of StatementResponse to ensure compatibility with API responses.
    Adds no additional fields, maintains same structure.
    """

    pass
