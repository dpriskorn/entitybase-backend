"""Statement endpoints for Entitybase v1 API."""

from fastapi import APIRouter, HTTPException, Request

from models.rest_api.entitybase.handlers.statement import StatementHandler
from models.rest_api.entitybase.request import (
    CleanupOrphanedRequest,
    MostUsedStatementsRequest,
    StatementBatchRequest,
)
from models.rest_api.entitybase.response import (
    CleanupOrphanedResponse,
    MostUsedStatementsResponse,
    StatementBatchResponse,
    StatementResponse,
)
from models.validation.utils import raise_validation_error
from models.rest_api.clients import Clients

router = APIRouter()


@router.get("/statements/{content_hash}", response_model=StatementResponse)
def get_statement(content_hash: int, req: Request) -> StatementResponse:
    """Retrieve a single statement by its content hash."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler()
    return handler.get_statement(content_hash, clients.s3)  # type: ignore[no-any-return]


@router.post("/statements/batch", response_model=StatementBatchResponse)
def get_statements_batch(  # type: ignore[no-any-return]
    request: StatementBatchRequest, req: Request
) -> StatementBatchResponse:
    """Retrieve multiple statements by their content hashes in a batch request."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler()
    return handler.get_statements_batch(request, clients.s3)  # type: ignore[no-any-return]


@router.get("/statements/most_used", response_model=MostUsedStatementsResponse)
def get_most_used_statements(  # type: ignore[no-any-return]
    request: MostUsedStatementsRequest, req: Request
) -> MostUsedStatementsResponse:
    """Get the most used statements based on reference count."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler()
    result = handler.get_most_used_statements(
        clients.vitess, request.limit, request.min_ref_count
    )
    if not isinstance(result, MostUsedStatementsResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result  # type: ignore[no-any-return]


@router.post("/statements/cleanup-orphaned", response_model=CleanupOrphanedResponse)
def cleanup_orphaned_statements(  # type: ignore[no-any-return]
    request: CleanupOrphanedRequest, req: Request
) -> CleanupOrphanedResponse:
    """Clean up orphaned statements that are no longer referenced."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler()
    return handler.cleanup_orphaned_statements(request, clients.vitess, clients.s3)  # type: ignore[no-any-return]
