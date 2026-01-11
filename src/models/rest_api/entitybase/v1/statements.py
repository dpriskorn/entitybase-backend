"""Statement endpoints for Entitybase v1 API."""

from fastapi import APIRouter, Request

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

router = APIRouter()


@router.get("/statements/{content_hash}", response_model=StatementResponse)
def get_statement(content_hash: int, req: Request) -> StatementResponse:
    """Retrieve a single statement by its content hash."""
    clients = req.app.state.clients
    handler = StatementHandler()
    return handler.get_statement(content_hash, clients.s3)


@router.post("/statements/batch", response_model=StatementBatchResponse)
def get_statements_batch(
    request: StatementBatchRequest, req: Request
) -> StatementBatchResponse:
    """Retrieve multiple statements by their content hashes in a batch request."""
    clients = req.app.state.clients
    handler = StatementHandler()
    return handler.get_statements_batch(request, clients.s3)


@router.get("/statements/most_used", response_model=MostUsedStatementsResponse)
def get_most_used_statements(
    request: MostUsedStatementsRequest, req: Request
) -> MostUsedStatementsResponse:
    """Get the most used statements based on reference count."""
    clients = req.app.state.clients
    handler = StatementHandler()
    return handler.get_most_used_statements(
        clients.vitess, request.limit, request.min_ref_count
    )


@router.post("/statements/cleanup-orphaned", response_model=CleanupOrphanedResponse)
def cleanup_orphaned_statements(
    request: CleanupOrphanedRequest, req: Request
) -> CleanupOrphanedResponse:
    """Clean up orphaned statements that are no longer referenced."""
    clients = req.app.state.clients
    handler = StatementHandler()
    return handler.cleanup_orphaned_statements(request, clients.vitess, clients.s3)
