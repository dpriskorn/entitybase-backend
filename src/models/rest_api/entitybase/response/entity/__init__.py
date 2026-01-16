"""Entity response models."""

from .backlinks import Backlink, BacklinksResponse
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
)
from .revert import EntityRevertResponse
from .wikibase import (
    AliasValue,
    DescriptionValue,
    EntityAliasesResponse,
    EntityDescriptionsResponse,
    EntityLabelsResponse,
    EntityMetadataResponse,
    EntitySitelinksResponse,
    EntityStatementsResponse,
    LabelValue,
    WikibaseEntityResponse,
)

__all__ = [
    "AliasValue",
    "Backlink",
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
    "LabelValue",
    "ProtectionResponse",
    "WikibaseEntityResponse",
]
