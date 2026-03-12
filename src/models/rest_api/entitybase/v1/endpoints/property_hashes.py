"""Property hashes routes."""

from fastapi import APIRouter, Request

from models.rest_api.entitybase.v1.handlers.statement import StatementHandler
from models.data.rest_api.v1.entitybase.response import (
    PropertyHashesResponse,
)
from models.rest_api.utils import raise_validation_error, validate_state_clients


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
    validate_state_clients(state)

    handler = StatementHandler(state=state)
    return handler.get_entity_property_hashes(entity_id, property_list)
