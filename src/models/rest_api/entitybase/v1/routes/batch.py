"""Batch routes for v1."""

from typing import Any, Dict, List

from fastapi import HTTPException, Request

from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.endpoints import v1_router


@v1_router.get(
    "/statements/batch",
    tags=["statements"],
    response_model=Dict[str, Dict[str, List[Any]]],
)
async def get_batch_statements(
    req: Request, entity_ids: str, property_ids: str = ""
) -> dict[str, dict[str, list]]:
    """Get statement hashes for multiple entities.

    Query params:
    - entity_ids: Comma-separated entity IDs (e.g., Q1,Q2,Q3). Max 20.
    - property_ids: Optional comma-separated property IDs to filter (e.g., P31,P279).

    Returns dict mapping entity_id → property_id → list of statement hashes.
    Entities not found return empty dict for that entity_id.

    Example: GET /statements/batch?entity_ids=Q1,Q2&property_ids=P31
    Returns: {"Q1": {"P31": [123, 456]}, "Q2": {"P31": [789]}}
    """
    if req is None:
        raise HTTPException(status_code=500, detail="Request not provided")
    state = req.app.state.state_handler
    entity_list = entity_ids.split(",")
    property_list = property_ids.split(",") if property_ids else None
    if len(entity_list) > 20:
        raise HTTPException(status_code=400, detail="Too many entities (max 20)")
    result = {}
    for raw_entity_id in entity_list:
        entity_id = raw_entity_id.strip()
        try:
            # Get entity revision
            handler = EntityReadHandler(state=state)
            entity_response = handler.get_entity(entity_id)
            statements = entity_response.entity_data.get("statements", {})
            if property_list:
                filtered = {p: statements.get(p, []) for p in property_list}
                result[raw_entity_id] = filtered
            else:
                result[raw_entity_id] = statements
        except Exception:
            result[raw_entity_id] = {}
    return result
