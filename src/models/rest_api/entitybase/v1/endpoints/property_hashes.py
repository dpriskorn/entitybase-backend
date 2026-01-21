"""Property hashes routes."""

from fastapi import APIRouter, Request

from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.rest_api.entitybase.v1.handlers.statement import StatementHandler
from models.rest_api.entitybase.v1.response import (
    PropertyHashesResponse,
)
from models.rest_api.utils import raise_validation_error


property_hashes_router = APIRouter()


@property_hashes_router.get(
    "/entity/{entity_id}/properties/{property_list}",
    response_model=PropertyHashesResponse,
)
def get_entity_property_hashes(
    entity_id: str, property_list: str, req: Request
) -> PropertyHashesResponse:
    """Get statement hashes for specified properties in an entity."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = StatementHandler(state=state)
    return handler.get_entity_property_hashes(entity_id, property_list)
