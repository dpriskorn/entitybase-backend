"""Statement endpoints for Entitybase v1 API."""

from fastapi import APIRouter, Request
from typing import cast

from ...handlers.statement import StatementHandler
from ...request import (
    CleanupOrphanedRequest,
    MostUsedStatementsRequest,
    StatementBatchRequest,
)
from ...response import (
    CleanupOrphanedResponse,
    MostUsedStatementsResponse,
    StatementBatchResponse,
    StatementResponse,
)
from ...clients import Clients

router = APIRouter()


@router.get("/statements/{content_hash}", response_model=StatementResponse)
def get_statement(content_hash: int, req: Request) -> StatementResponse:
    """Retrieve a single statement by its content hash."""
    clients = cast(Clients, req.app.state.clients)
    handler = StatementHandler()
    return handler.get_statement(content_hash, clients.s3)  # type: ignore[no-any-return]


@router.post("/statements/batch", response_model=StatementBatchResponse)
def get_statements_batch(  # type: ignore[no-any-return]
    request: StatementBatchRequest, req: Request
) -> StatementBatchResponse:
    """Retrieve multiple statements by their content hashes in a batch request."""
    clients = cast(Clients, req.app.state.clients)
    handler = StatementHandler()
    return handler.get_statements_batch(request, clients.s3)  # type: ignore[no-any-return]


@router.get("/statements/most_used", response_model=MostUsedStatementsResponse)
def get_most_used_statements(  # type: ignore[no-any-return]
    request: MostUsedStatementsRequest, req: Request
) -> MostUsedStatementsResponse:
    """Get the most used statements based on reference count."""
    clients = cast(Clients, req.app.state.clients)
    handler = StatementHandler()
    return handler.get_most_used_statements(
        clients.vitess, request.limit, request.min_ref_count
    )  # type: ignore[no-any-return]


@router.post("/statements/cleanup-orphaned", response_model=CleanupOrphanedResponse)
def cleanup_orphaned_statements(  # type: ignore[no-any-return]
    request: CleanupOrphanedRequest, req: Request
) -> CleanupOrphanedResponse:
    """Clean up orphaned statements that are no longer referenced."""
    clients = cast(Clients, req.app.state.clients)
    handler = StatementHandler()
    return handler.cleanup_orphaned_statements(request, clients.vitess, clients.s3)  # type: ignore[no-any-return]
