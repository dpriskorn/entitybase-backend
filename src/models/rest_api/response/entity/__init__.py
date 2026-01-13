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
    EntityAliases,
    EntityDescriptions,
    EntityLabels,
    EntityMetadata,
    EntitySitelinks,
    EntityStatements,
    LabelValue,
    WikibaseEntityResponse,
)
