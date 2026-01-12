"""REST API response models."""

# Response models

from .entity import (
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
    ProtectionInfo,
    WikibaseEntityResponse,
)
from models.vitess_models import BacklinkData
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
    "BacklinkData",
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
    "ProtectionInfo",
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
