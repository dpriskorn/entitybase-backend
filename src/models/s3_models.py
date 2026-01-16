"""S3-related models and configurations."""

from typing import Any, Dict

from pydantic import BaseModel, Field
from pydantic.root_model import RootModel

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


class LabelsHashes(RootModel[dict[str, int]]):
    """Hash map for entity labels by language."""


class DescriptionsHashes(RootModel[dict[str, int]]):
    """Hash map for entity descriptions by language."""


class AliasesHashes(RootModel[dict[str, list[int]]]):
    """Hash map for entity aliases by language."""


class SitelinksHashes(RootModel[dict[str, int]]):
    """Hash map for entity sitelinks by site."""


class StatementsHashes(RootModel[dict[str, list[int]]]):
    """Hash map for entity statements by property."""


class RevisionCreateData(BaseModel):
    """Model for revision data used during creation."""

    schema_version: str
    revision_id: int
    created_at: str
    created_by: str
    entity_type: str
    entity: dict[str, Any]
    statements: list[int]
    properties: list[str]
    property_counts: dict[str, int]
    sitelinks_hashes: dict[str, int] | None
    content_hash: int
    edit_summary: str | None
    editor: str | None
    is_mass_edit: bool
    edit_type: str
    is_semi_protected: bool | None
    is_locked: bool | None
    is_archived: bool | None
    is_dangling: bool | None
    is_mass_edit_protected: bool | None
    is_deleted: bool
    is_redirect: bool


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
