"""Statement endpoints for Entitybase v1 API."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

logger = logging.getLogger(__name__)
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.data.rest_api.v1.entitybase.request import CleanupOrphanedRequest
from models.data.rest_api.v1.entitybase.response import (
    BatchStatementsResponse,
    CleanupOrphanedResponse,
    MostUsedStatementsResponse,
    StatementResponse,
)
from models.rest_api.utils import raise_validation_error

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
) -> MostUsedStatementsResponse:
    """Get most used statements based on reference count."""
    state = req.app.state.state_handler
    if not (hasattr(state, "vitess_client") and hasattr(state, "s3_client")):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler(state=state)
    result = handler.get_most_used_statements(limit, min_ref_count)
    if not isinstance(result, MostUsedStatementsResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@router.get(
    "/statements/batch", tags=["statements"], response_model=BatchStatementsResponse
)
async def get_batch_statements(
    req: Request, entity_ids: str, property_ids: str = ""
) -> BatchStatementsResponse:
    """Get statement hashes for multiple entities.

    Query params:
    - entity_ids: Comma-separated entity IDs (e.g., Q1,Q2,Q3). Max 20.
    - property_ids: Optional comma-separated property IDs to filter (e.g., P31,P279).

    Returns dict mapping entity_id → property_id → list of statement hashes.
    Entities not found return empty dict for that entity_id.

    Example: GET /statements/batch?entity_ids=Q1,Q2&property_ids=P31
    Returns: {"Q1": {"P31": [123, 456]}, "Q2": {"P31": [789]}}
    """
    logger.debug(
        f"Getting batch statements for entity_ids={entity_ids}, property_ids={property_ids}"
    )
    if req is None:
        logger.error("Request not provided")
        raise HTTPException(status_code=500, detail="Request not provided")
    state = req.app.state.state_handler
    entity_list = entity_ids.split(",")
    property_list = property_ids.split(",") if property_ids else None
    logger.debug(f"Parsed entity_list={entity_list}, property_list={property_list}")
    if len(entity_list) > 20:
        logger.warning(f"Too many entities requested: {len(entity_list)}")
        raise HTTPException(status_code=400, detail="Too many entities (max 20)")
    result: dict[str, dict[str, list]] = {}
    for raw_entity_id in entity_list:
        entity_id = raw_entity_id.strip()
        logger.debug(f"Fetching statements for entity {entity_id}")
        try:
            handler = EntityReadHandler(state=state)
            entity_response = handler.get_entity(entity_id)
            statements = entity_response.entity_data.get("statements", {})
            logger.debug(f"Found statements for {entity_id}: {list(statements.keys())}")
            if property_list:
                filtered = {p: statements.get(p, []) for p in property_list}
                result[raw_entity_id] = filtered
            else:
                result[raw_entity_id] = statements
        except Exception:
            result[raw_entity_id] = {}
    return BatchStatementsResponse(statements=result)


@router.get("/statements/{content_hash}", response_model=StatementResponse)
def get_statement(content_hash: int, req: Request) -> StatementResponse:
    """Retrieve a single statement by its content hash."""
    state = req.app.state.state_handler
    if not (hasattr(state, "vitess_client") and hasattr(state, "s3_client")):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler(state=state)
    return handler.get_statement(content_hash)


@router.post("/statements/cleanup-orphaned", response_model=CleanupOrphanedResponse)
def cleanup_orphaned_statements(
    request: CleanupOrphanedRequest, req: Request
) -> CleanupOrphanedResponse:
    """Clean up orphaned statements that are no longer referenced."""
    state = req.app.state.state_handler
    if not (hasattr(state, "vitess_client") and hasattr(state, "s3_client")):
        raise HTTPException(status_code=500, detail="Invalid clients type")
    handler = StatementHandler(state=state)
    return handler.cleanup_orphaned_statements(request)
