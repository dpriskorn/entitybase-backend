"""REST API response models."""

# Response models

from .entity.backlinks import BacklinksResponse, Backlink
from .entity.entitybase import (
    ProtectionResponse,
    EntityRevisionResponse,
    EntityResponse,
    EntityRedirectResponse,
    EntityMetadataBatchResponse,
    EntityListResponse,
    EntityJsonImportResponse,
    EntityDeleteResponse,
)
from .entity import WikibaseEntityResponse
from .entity.wikibase import (
    EntityMetadata,
    EntityLabels,
    EntityDescriptions,
    EntityAliases,
)
from .statement import (
    MostUsedStatementsResponse,
    PropertyCounts,
    PropertyCountsResponse,
    PropertyHashesResponse,
    PropertyListResponse,
    StatementBatchResponse,
    StatementHashResult,
    StatementResponse,
)
from .health import HealthCheckResponse, HealthResponse, WorkerHealthCheck
from .misc import CleanupOrphanedResponse, RevisionMetadataResponse, TtlResponse
from .rdf import (
    DeduplicationStats,
    FullRevisionData,
    MetadataLoadResponse,
    RedirectBatchResponse,
    WikibasePredicates,
)

__all__ = [
    "Backlink",
    "BacklinksResponse",
    "CleanupOrphanedResponse",
    "DeduplicationStats",
    "EntityAliases",
    "EntityDeleteResponse",
    "EntityDescriptions",
    "EntityJsonImportResponse",
    "EntityLabels",
    "EntityListResponse",
    "EntityMetadata",
    "EntityMetadataBatchResponse",
    "EntityRedirectResponse",
    "EntityResponse",
    "EntityRevisionResponse",
    "FullRevisionData",
    "HealthCheckResponse",
    "HealthResponse",
    "MetadataLoadResponse",
    "MostUsedStatementsResponse",
    "PropertyCounts",
    "PropertyCountsResponse",
    "PropertyHashesResponse",
    "PropertyListResponse",
    "ProtectionResponse",
    "RedirectBatchResponse",
    "RevisionMetadataResponse",
    "StatementBatchResponse",
    "StatementHashResult",
    "StatementResponse",
    "TtlResponse",
    "WikibaseEntityResponse",
    "WikibasePredicates",
    "WorkerHealthCheck",
]
