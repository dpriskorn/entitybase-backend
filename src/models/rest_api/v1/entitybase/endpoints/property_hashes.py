"""Property hashes routes."""

from fastapi import APIRouter, Request

from models.rest_api.clients import Clients
from models.rest_api.v1.entitybase.handlers.statement import StatementHandler
from models.rest_api.v1.entitybase.response import (
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
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = StatementHandler()
    return handler.get_entity_property_hashes(
        entity_id, property_list, clients.vitess, clients.s3
    )
