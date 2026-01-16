"""S3-related models and configurations."""

from typing import Any, Dict

from pydantic import BaseModel, Field

from models.infrastructure.config import Config
from models.rest_api.entitybase.response import StatementResponse


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
    bucket: str


class RevisionMetadata(BaseModel):
    """Metadata for stored revisions."""

    key: str


class LabelsHashes(BaseModel):
    """Hash map for entity labels by language."""

    __root__: dict[str, int]  # language -> hash


class DescriptionsHashes(BaseModel):
    """Hash map for entity descriptions by language."""

    __root__: dict[str, int]  # language -> hash


class AliasesHashes(BaseModel):
    """Hash map for entity aliases by language."""

    __root__: dict[str, list[int]]  # language -> list of hashes


class SitelinksHashes(BaseModel):
    """Hash map for entity sitelinks by site."""

    __root__: dict[str, int]  # site -> hash


class StatementsHashes(BaseModel):
    """Hash map for entity statements by property."""

    __root__: dict[str, list[int]]  # property -> list of hashes


class RevisionData(BaseModel):
    """Model for revision JSON data structure."""

    schema_version: str
    revision_id: int | None = Field(default=None)
    created_at: str = Field(default="")
    created_by: str = Field(default="")
    entity_type: str = Field(default="")
    entity: EntityData
    redirects_to: str = Field(default="")
    labels_hashes: LabelsHashes | None = Field(default=None)
    descriptions_hashes: DescriptionsHashes | None = Field(default=None)
    aliases_hashes: AliasesHashes | None = Field(default=None)
    sitelinks_hashes: SitelinksHashes | None = Field(default=None)
    statements_hashes: StatementsHashes | None = Field(default=None)


class RevisionReadResponse(BaseModel):
    """Response model for reading revisions."""

    entity_id: str
    revision_id: int
    data: RevisionData
    content: Dict[str, Any]
    created_at: str = Field(default="")
    user_id: int | None = Field(default=None)
    edit_summary: str = Field(default="")


class StoredStatement(StatementResponse):
    """Statement format for S3 storage.

    Subclass of StatementResponse to ensure compatibility with API responses.
    Adds no additional fields, maintains same structure.
    """

    pass
