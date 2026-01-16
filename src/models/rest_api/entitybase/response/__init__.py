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
    EntityMetadataResponse,
    EntityLabelsResponse,
    EntityDescriptionsResponse,
    EntityAliasesResponse,
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
from .health import HealthCheckResponse, HealthResponse, WorkerHealthCheckResponse
from .misc import CleanupOrphanedResponse, RevisionMetadataResponse, TtlResponse
from .rdf import (
    DeduplicationStatsResponse,
    FullRevisionResponse,
    MetadataLoadResponse,
    RedirectBatchResponse,
    WikibasePredicatesResponse,
)

__all__ = [
    "Backlink",
    "BacklinksResponse",
    "CleanupOrphanedResponse",
    "DeduplicationStatsResponse",
    "EntityAliasesResponse",
    "EntityDeleteResponse",
    "EntityDescriptionsResponse",
    "EntityJsonImportResponse",
    "EntityLabelsResponse",
    "EntityListResponse",
    "EntityMetadataResponse",
    "EntityMetadataBatchResponse",
    "EntityRedirectResponse",
    "EntityResponse",
    "EntityRevisionResponse",
    "FullRevisionResponse",
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
    "WikibasePredicatesResponse",
    "WorkerHealthCheckResponse",
]
