"""Revision data model."""

from datetime import timezone, datetime

from pydantic import BaseModel, Field

from models.config.settings import settings
from models.infrastructure.s3.revision.entity_state import EntityState
from models.infrastructure.s3.hashes.hash_maps import HashMaps
from models.infrastructure.s3.enums import EntityType, EditData
from models.property_counts import PropertyCounts


class RevisionData(BaseModel):
    """Model for immutable revision snapshots stored in S3.

    Contains minimal entity data with hash-based deduplication for terms,
    sitelinks, and statements. Used for persistent storage and retrieval.
    """

    revision_id: int
    entity_type: EntityType
    edit: EditData
    hashes: HashMaps
    schema_version: str = Field(
        default=settings.s3_schema_revision_version,
        description="Version of schema. E.g. 1.0.0",
    )
    created_at: str = Field(
        default=datetime.now(timezone.utc).isoformat(),
        description="Timestamp when entity was created.",
    )
    redirects_to: str = Field(
        default="", description="Entity ID this entity redirects to. E.g. Q1"
    )
    state: EntityState = Field(default=EntityState())
    property_counts: PropertyCounts | None = Field(default=None)
    properties: list[str] = Field(default_factory=list)