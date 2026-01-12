"""Entity response models."""

from pydantic import BaseModel
from typing import Any, Dict, List

from .revert import EntityRevertResponse


class Backlink(BaseModel):
    pass


class BacklinksResponse(BaseModel):
    pass


class EntityAliases(BaseModel):
    pass


class EntityDeleteResponse(BaseModel):
    pass


class EntityDescriptions(BaseModel):
    pass


class EntityJsonImportResponse(BaseModel):
    pass


class EntityLabels(BaseModel):
    pass


class EntityListResponse(BaseModel):
    pass


class EntityMetadata(BaseModel):
    pass


class EntityMetadataBatchResponse(BaseModel):
    pass


class EntityRedirectResponse(BaseModel):
    pass


class EntityResponse(BaseModel):
    pass


class EntityRevisionResponse(BaseModel):
    pass


class ProtectionInfo(BaseModel):
    pass


class WikibaseEntityResponse(BaseModel):
    pass


class EntityHistoryEntry(BaseModel):
    """Response model for a single entity history entry."""

    revision_id: int
    created_at: str | None
    created_by: str | None
    edit_summary: str | None
    editor: str | None
    edit_type: str | None
    is_mass_edit: bool
