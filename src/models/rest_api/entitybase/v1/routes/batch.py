"""Batch routes for v1."""

from typing import Any, Dict, List

from fastapi import HTTPException, Request

from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.endpoints import v1_router


@v1_router.get(
    "/entities/sitelinks/{hashes}", tags=["items"], response_model=Dict[str, str]
)
async def get_batch_sitelinks(hashes: str, req: Request) -> dict[str, str]:
    """Get batch sitelink titles by hashes."""
    state = req.app.state.state_handler
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            title = state.s3_client.load_sitelink_metadata(hash_value)
            if title:
                result[h] = title
        except ValueError:
            pass  # Skip invalid hashes
    return result


@v1_router.get(
    "/entities/labels/{hashes}", tags=["items"], response_model=Dict[str, str]
)
async def get_batch_labels(hashes: str, req: Request) -> dict[str, str]:
    """Get batch labels by hashes."""
    state = req.app.state.state_handler
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            label = state.s3_client.load_metadata("labels", hash_value)
            if label:
                result[h] = label.data
        except ValueError:
            pass
    return result


@v1_router.get(
    "/entities/descriptions/{hashes}",
    tags=["items"],
    response_model=Dict[str, str],
)
async def get_batch_descriptions(hashes: str, req: Request) -> dict[str, str]:
    """Get batch descriptions by hashes."""
    state = req.app.state.state_handler
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            desc = state.s3_client.load_metadata("descriptions", hash_value)
            if desc:
                result[h] = desc.data
        except ValueError:
            pass
    return result


@v1_router.get(
    "/entities/aliases/{hashes}",
    tags=["items"],
    response_model=Dict[str, List[str]],
)
async def get_batch_aliases(hashes: str, req: Request) -> dict[str, list[str]]:
    """Get batch aliases by hashes."""
    state = req.app.state.state_handler
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            aliases = state.s3_client.load_metadata("aliases", hash_value)
            if aliases:
                result[h] = aliases.data
        except ValueError:
            pass
    return result


@v1_router.get(
    "/statements/batch",
    tags=["statements"],
    response_model=Dict[str, Dict[str, List[Any]]],
)
async def get_batch_statements(
    req: Request, entity_ids: str, property_ids: str = ""
) -> dict[str, dict[str, list]]:
    """Get batch statements for entities and properties."""
    if req is None:
        raise HTTPException(status_code=500, detail="Request not provided")
    state = req.app.state.state_handler
    entity_list = entity_ids.split(",")
    property_list = property_ids.split(",") if property_ids else None
    if len(entity_list) > 20:
        raise HTTPException(status_code=400, detail="Too many entities (max 20)")
    result = {}
    for entity_id in entity_list:
        entity_id = entity_id.strip()
        try:
            # Get entity revision
            handler = EntityReadHandler(state=state)
            entity_response = handler.get_entity(entity_id)
            statements = entity_response.entity_data.get("statements", {})
            if property_list:
                filtered = {p: statements.get(p, []) for p in property_list}
                result[entity_id] = filtered
            else:
                result[entity_id] = statements
        except Exception:
            result[entity_id] = {}
    return result
