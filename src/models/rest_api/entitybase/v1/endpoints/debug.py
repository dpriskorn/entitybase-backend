"""Debug routes for development/testing."""

import logging

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)


debug_router = APIRouter(tags=["debug"])


@debug_router.get("/debug/entity/{entity_id}")
async def debug_entity(entity_id: str, request: Request) -> dict:
    """Debug endpoint to check entity in database.

    This endpoint queries the entity_id_mapping table directly to verify
    if an entity exists and what its internal_id is.
    """
    state = request.app.state.state_handler

    with state.vitess_client.cursor as cursor:
        cursor.execute(
            "SELECT internal_id, entity_id FROM entity_id_mapping WHERE entity_id = %s",
            (entity_id,),
        )
        result = cursor.fetchone()

    if result:
        return {
            "entity_id": result[1],
            "internal_id": result[0],
            "found": True,
        }
    return {
        "entity_id": entity_id,
        "found": False,
        "error": "Entity not found in entity_id_mapping",
    }


@debug_router.get("/debug/entity_head/{entity_id}")
async def debug_entity_head(entity_id: str, request: Request) -> dict:
    """Debug endpoint to check entity_head table."""
    logger.info(f"Debug: Checking entity_head for entity_id={entity_id}")
    state = request.app.state.state_handler

    internal_id = state.vitess_client.resolve_id(entity_id)
    if not internal_id:
        return {
            "entity_id": entity_id,
            "found": False,
            "error": "Entity not found in entity_id_mapping",
        }

    with state.vitess_client.cursor as cursor:
        cursor.execute(
            """SELECT internal_id, head_revision_id, is_semi_protected, is_locked, 
                      is_archived, is_dangling, is_mass_edit_protected, is_deleted, is_redirect
               FROM entity_head WHERE internal_id = %s""",
            (internal_id,),
        )
        result = cursor.fetchone()

    if result:
        return {
            "entity_id": entity_id,
            "internal_id": internal_id,
            "head_revision_id": result[1],
            "is_semi_protected": bool(result[2]),
            "is_locked": bool(result[3]),
            "is_archived": bool(result[4]),
            "is_dangling": bool(result[5]),
            "is_mass_edit_protected": bool(result[6]),
            "is_deleted": bool(result[7]),
            "is_redirect": bool(result[8]),
            "found": True,
        }
    return {
        "entity_id": entity_id,
        "internal_id": internal_id,
        "found": False,
        "error": "Entity not found in entity_head",
    }
