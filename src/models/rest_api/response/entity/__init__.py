"""Entity response models."""

from pydantic import BaseModel

from .misc import (
    Backlink,
    BacklinksResponse,
    EntityAliases,
    EntityDeleteResponse,
    EntityDescriptions,
    EntityHistoryEntry,
    EntityJsonImportResponse,
    EntityLabels,
    EntityListResponse,
    EntityMetadata,
    EntityMetadataBatchResponse,
    EntityRedirectResponse,
    EntityResponse,
    EntityRevisionResponse,
    ProtectionResponse,
    WikibaseEntityResponse,
)

from .revert import EntityRevertResponse
