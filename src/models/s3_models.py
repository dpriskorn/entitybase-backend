"""S3-related models and configurations."""

from typing import Any, Dict

from pydantic import BaseModel, field_validator

from models.infrastructure.config import Config
from models.rest_api.response.statement import StatementResponse


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

    ALLOWED_ENTITY_KEYS = frozenset([
        "id",
        "type",
        "labels",
        "descriptions",
        "aliases",
        "claims",
        "sitelinks",
    ])

    schema_version: str
    entity: Dict[str, Any]
    redirects_to: str | None = None

    @field_validator("entity")
    @classmethod
    def validate_entity_keys(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that entity dict only contains allowed keys."""
        if not isinstance(v, dict):
            from models.validation.utils import raise_validation_error
            raise_validation_error("Entity must be a dictionary", status_code=400)
        invalid_keys = set(v.keys()) - cls.ALLOWED_ENTITY_KEYS
        if invalid_keys:
            from models.validation.utils import raise_validation_error
            raise_validation_error(
                f"Invalid keys in entity data: {sorted(invalid_keys)}. Allowed: {sorted(cls.ALLOWED_ENTITY_KEYS)}",
                status_code=400,
            )
        return v


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
