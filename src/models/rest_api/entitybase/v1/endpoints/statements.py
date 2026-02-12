"""Statement endpoints for Entitybase v1 API."""

from fastapi import APIRouter, HTTPException, Query, Request

from models.rest_api.entitybase.v1.handlers.statement import StatementHandler
from models.data.rest_api.v1.entitybase.request import (
    CleanupOrphanedRequest,
    StatementBatchRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    CleanupOrphanedResponse,
    MostUsedStatementsResponse,
    StatementBatchResponse,
    StatementResponse,
)
from models.rest_api.utils import raise_validation_error
from models.rest_api.entitybase.v1.handlers.state import StateHandler

router = APIRouter()


@router.get("/statements/most_used", response_model=MostUsedStatementsResponse)
def get_most_used_statements(
    req: Request,
    limit: int = Query(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of statements to return (1-10000, default 100)",
    ),
    min_ref_count: int = Query(
        default=1,
        ge=0,
        description="Minimum ref_count threshold (default 1)",
    ),
) -> MostUsedStatementsResponse:  # type: ignore[no-any-return]
    """Get most used statements based on reference count."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler(state=state)
    result = handler.get_most_used_statements(limit, min_ref_count)
    if not isinstance(result, MostUsedStatementsResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result  # type: ignore[no-any-return]


@router.get("/statements/{content_hash}", response_model=StatementResponse)
def get_statement(content_hash: int, req: Request) -> StatementResponse:
    """Retrieve a single statement by its content hash."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler(state=state)
    return handler.get_statement(content_hash)  # type: ignore[no-any-return]


@router.post("/statements/batch", response_model=StatementBatchResponse)
def get_statements_batch(  # type: ignore[no-any-return]
    request: StatementBatchRequest, req: Request
) -> StatementBatchResponse:
    """Retrieve multiple statements by their content hashes in a batch request."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler(state=state)
    return handler.get_statements_batch(request)  # type: ignore[no-any-return]


# todo convert this into a worker instead
@router.post("/statements/cleanup-orphaned", response_model=CleanupOrphanedResponse)
def cleanup_orphaned_statements(  # type: ignore[no-any-return]
    request: CleanupOrphanedRequest, req: Request
) -> CleanupOrphanedResponse:
    """Clean up orphaned statements that are no longer referenced."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler(state=state)
    return handler.cleanup_orphaned_statements(request)  # type: ignore[no-any-return]
