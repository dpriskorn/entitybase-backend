"""Entity response models."""

from .backlinks import BacklinkResponse, BacklinksResponse
from .entitybase import (
    EntityDeleteResponse,
    EntityHistoryEntry,
    EntityJsonImportResponse,
    EntityListResponse,
    EntityMetadataBatchResponse,
    EntityRedirectResponse,
    EntityResponse,
    EntityRevisionResponse,
    ProtectionResponse,
    EntityMetadataResponse,
    EntityLabelsResponse,
    EntityDescriptionsResponse,
    EntityAliasesResponse,
    EntityStatementsResponse,
    EntitySitelinksResponse,
)
from .revert import EntityRevertResponse
from .change import EntityChange
from .wikibase import (
    AliasValue,
    DescriptionValue,
    LabelValue,
)

__all__ = [
    "AliasValue",
    "BacklinkResponse",
    "BacklinksResponse",
    "DescriptionValue",
    "EntityAliasesResponse",
    "EntityDeleteResponse",
    "EntityDescriptionsResponse",
    "EntityHistoryEntry",
    "EntityJsonImportResponse",
    "EntityLabelsResponse",
    "EntityListResponse",
    "EntityMetadataResponse",
    "EntityMetadataBatchResponse",
    "EntityRedirectResponse",
    "EntityResponse",
    "EntityRevertResponse",
    "EntityRevisionResponse",
    "EntitySitelinksResponse",
    "EntityStatementsResponse",
    "EntityChange",
    "LabelValue",
    "ProtectionResponse",
]
