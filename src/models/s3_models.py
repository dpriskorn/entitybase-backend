"""S3-related models and configurations."""
from datetime import timezone, datetime
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field
from pydantic.root_model import RootModel

from models.config.settings import settings
from models.infrastructure.config import Config
from models.infrastructure.s3.enums import CreatedBy, EditType, EntityType, EditData
from models.rest_api.entitybase.response import EntityState, PropertyCounts


class EntityData(BaseModel):
    """Typed model for entity data in revisions."""

    id: str
    type: str
    labels: Dict[str, Any] | None = Field(default=None)
    descriptions: Dict[str, Any] | None = Field(default=None)
    aliases: Dict[str, Any] | None = Field(default=None)
    claims: Dict[str, Any] | None = Field(default=None)
    sitelinks: Dict[str, Any] | None = Field(default=None)


class S3Config(Config):
    """Configuration for S3 connections."""

    endpoint_url: str
    access_key: str
    secret_key: str


class RevisionMetadata(BaseModel):
    """Metadata for stored revisions."""

    key: str


class LabelsHashes(RootModel[dict[str, int]]):
    """Hash map for entity labels by language."""


class DescriptionsHashes(RootModel[dict[str, int]]):
    """Hash map for entity descriptions by language."""


class AliasesHashes(RootModel[dict[str, list[int]]]):
    """Hash map for entity aliases by language."""


class SitelinksHashes(RootModel[dict[str, int]]):
    """Hash map for entity sitelinks by site."""


class StatementsHashes(RootModel[list[int]]):
    """Hash list for entity statements."""


class HashMaps(BaseModel):
    labels: LabelsHashes | None = Field(default=None)
    descriptions: DescriptionsHashes | None = Field(default=None)
    aliases: AliasesHashes | None = Field(default=None)
    sitelinks: SitelinksHashes | None = Field(default=None)
    statements: StatementsHashes | None = Field(default=None)


class RevisionData(BaseModel):
    """Model for immutable revision snapshots stored in S3.

    Contains minimal entity data with hash-based deduplication for terms,
    sitelinks, and statements. Used for persistent storage and retrieval.
    """

    revision_id: int
    entity_type: EntityType
    edit: EditData
    hashes: HashMaps
    schema_version: str = Field(default=settings.s3_schema_revision_version, description="Version of schema. E.g. 1.0.0")
    created_at: str = Field(default=datetime.now(timezone.utc).isoformat(), description="Timestamp when entity was created.")
    redirects_to: str = Field(default="", description="Entity ID this entity redirects to. E.g. Q1")
    state: EntityState = Field(default=EntityState())
    property_counts: PropertyCounts | None = Field(default=None)
    properties: list[str] = Field(default_factory=list)


class S3QualifierData(BaseModel):
    """Model for individual qualifier data stored in S3."""

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    qualifier: Dict[str, Any] = Field(
        description="Full qualifier JSON object. Example: {'property': 'P580', 'value': '2023-01-01'}."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the qualifier content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when qualifier was created. Example: '2023-01-01T12:00:00Z'."
    )


class S3ReferenceData(BaseModel):
    """Model for individual reference data stored in S3."""

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    reference: Dict[str, Any] = Field(
        description="Full reference JSON object. Example: {'snaks': {'P854': [{'value': 'https://example.com'}]}}."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the reference content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when reference was created. Example: '2023-01-01T12:00:00Z'."
    )


class RevisionReadResponse(BaseModel):
    """Response model for reading revisions."""

    entity_id: str
    revision_id: int
    data: RevisionData
    content: Dict[str, Any]
    schema_version: str = Field(default="")
    created_at: str = Field(default="")
    user_id: int = Field(default=0)
    edit_summary: str = Field(default="")
    redirects_to: str = Field(default="")


class StoredStatement(BaseModel):
    """Statement format for S3 storage.

    Compatible with StatementResponse for API responses.
    """

    model_config = ConfigDict(populate_by_name=True)

    schema_version: str = Field(alias="schema")
    content_hash: int = Field(alias="hash")
    statement: Dict[str, Any]
    created_at: str
