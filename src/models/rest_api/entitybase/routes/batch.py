"""Batch routes for v1."""

from fastapi import HTTPException, Request

from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.versions.v1 import v1_router


@v1_router.get("/sitelinks/{hashes}")
async def get_batch_sitelinks(hashes: str, req: Request) -> dict[str, str]:
    """Get batch sitelink titles by hashes."""
    clients = req.app.state.clients
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            title = clients.s3.load_sitelink_metadata(hash_value)
            if title:
                result[h] = title
        except ValueError:
            pass  # Skip invalid hashes
    return result


@v1_router.get("/labels/{hashes}")
async def get_batch_labels(hashes: str, req: Request) -> dict[str, str]:
    """Get batch labels by hashes."""
    clients = req.app.state.clients
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            label = clients.s3.load_metadata("labels", hash_value)
            if label:
                result[h] = label
        except ValueError:
            pass
    return result


@v1_router.get("/descriptions/{hashes}")
async def get_batch_descriptions(hashes: str, req: Request) -> dict[str, str]:
    """Get batch descriptions by hashes."""
    clients = req.app.state.clients
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            desc = clients.s3.load_metadata("descriptions", hash_value)
            if desc:
                result[h] = desc
        except ValueError:
            pass
    return result


@v1_router.get("/aliases/{hashes}")
async def get_batch_aliases(hashes: str, req: Request) -> dict[str, list[str]]:
    """Get batch aliases by hashes."""
    clients = req.app.state.clients
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            aliases = clients.s3.load_metadata("aliases", hash_value)
            if aliases:
                result[h] = aliases
        except ValueError:
            pass
    return result


@v1_router.get("/statements/batch")
async def get_batch_statements(
    req: Request, entity_ids: str, property_ids: str = ""
) -> dict[str, dict[str, list]]:
    """Get batch statements for entities and properties."""
    if req is None:
        raise HTTPException(status_code=500, detail="Request not provided")
    clients = req.app.state.clients
    entity_list = entity_ids.split(",")
    property_list = property_ids.split(",") if property_ids else None
    if len(entity_list) > 20:
        raise HTTPException(status_code=400, detail="Too many entities (max 20)")
    result = {}
    for entity_id in entity_list:
        entity_id = entity_id.strip()
        try:
            # Get entity revision
            handler = EntityReadHandler()
            entity_response = handler.get_entity(entity_id, clients.vitess, clients.s3)
            statements = entity_response.entity_data.get("statements", {})
            if property_list:
                filtered = {p: statements.get(p, []) for p in property_list}
                result[entity_id] = filtered
            else:
                result[entity_id] = statements
        except Exception:
            result[entity_id] = {}
    return result
