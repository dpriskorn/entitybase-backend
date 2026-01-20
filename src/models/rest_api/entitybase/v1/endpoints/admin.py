"""Admin routes."""

from fastapi import APIRouter, Query, Request

from models.rest_api.state import State
from models.rest_api.entitybase.v1.handlers.admin import AdminHandler
from models.rest_api.entitybase.v1.response.entity.entitybase import EntityListResponse
from models.rest_api.utils import raise_validation_error


admin_router = APIRouter()


@admin_router.get("/entities", response_model=EntityListResponse)
def list_entities(  # type: ignore[no-any-return]
    req: Request,
    entity_type: str = Query(
        "",
        description="Entity type to filter by (item, property, lexeme, entityschema). Leave empty for all types",
    ),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of entities to return"
    ),
    offset: int = Query(0, ge=0, description="Number of entities to skip"),
) -> EntityListResponse:
    """List entities based on type, limit, and offset."""
    clients = req.app.state.clients
    if not isinstance(clients, State):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = AdminHandler()
    result = handler.list_entities(
        vitess_client=clients.vitess_config,
        entity_type=entity_type,
        limit=limit,
        offset=offset,
    )
    if not isinstance(result, EntityListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result
