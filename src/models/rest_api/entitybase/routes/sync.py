"""Sync routes."""

from fastapi import APIRouter, Request

from models.rest_api.clients import Clients
from models.rest_api.entitybase.handlers.statement import StatementHandler
from models.rest_api.entitybase.response import PropertyHashesResponse
from models.validation.utils import raise_validation_error


sync_router = APIRouter()


@sync_router.get(
    "/entity/{entity_id}/properties/{property_list}",
    response_model=PropertyHashesResponse,
)
def get_entity_property_hashes_sync(
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


def get_entity_property_counts(
    entity_id: str, req: Request
) -> None:  # PropertyCountsResponse
    """Get statement counts for each property in an entity."""
    clients = req.app.state.clients
    handler = StatementHandler()
    result = handler.get_entity_property_counts(entity_id, clients.vitess, clients.s3)
    # Not used as route, perhaps internal
    return result
