from typing import Any, Dict

from fastapi import Response
from pydantic import BaseModel, Field

from models.api_models import (
    CleanupOrphanedRequest,
    CleanupOrphanedResponse,
    DeleteType,
    EditType,
    EntityCreateRequest,
    EntityDeleteRequest,
    EntityDeleteResponse,
    EntityListResponse,
    EntityRedirectRequest,
    EntityRedirectResponse,
    EntityResponse,
    MostUsedStatementsRequest,
    MostUsedStatementsResponse,
    PropertyCountsResponse,
    PropertyHashesResponse,
    PropertyListResponse,
    RedirectRevertRequest,
    StatementBatchRequest,
    StatementBatchResponse,
    StatementResponse,
)

__all__ = [
    "EditType",
    "EntityCreateRequest",
    "EntityResponse",
    "DeleteType",
    "EntityDeleteRequest",
    "EntityDeleteResponse",
    "EntityRedirectRequest",
    "EntityRedirectResponse",
    "RedirectRevertRequest",
    "StatementResponse",
    "StatementBatchRequest",
    "StatementBatchResponse",
    "PropertyListResponse",
    "PropertyCountsResponse",
    "PropertyHashesResponse",
    "MostUsedStatementsRequest",
    "MostUsedStatementsResponse",
    "CleanupOrphanedRequest",
    "CleanupOrphanedResponse",
    "EntityListResponse",
    "StatementHashResult",
]


class RevisionMetadata(BaseModel):
    revision_id: int
    created_at: str


class HealthCheckResponse(BaseModel):
    status: str
    s3: str
    vitess: str


class TtlResponse(Response):
    def __init__(self, content: str):
        super().__init__(
            content=content,
            media_type="text/turtle",
        )


class StatementHashResult(BaseModel):
    statements: list[int] = Field(
        default_factory=list,
        description="List of statement hashes (rapidhash of each statement)",
    )
    properties: list[str] = Field(
        default_factory=list,
        description="Sorted list of unique property IDs",
    )
    property_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Dict mapping property ID -> count of statements",
    )
    full_statements: list[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of full statement dicts (parallel with hashes)",
    )
