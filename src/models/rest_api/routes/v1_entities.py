"""Additional v1 entity routes."""

from fastapi import Request

from models.rest_api.clients import Clients
from models.rest_api.entitybase.handlers.admin import AdminHandler
from models.rest_api.entitybase.handlers.entity.delete import EntityDeleteHandler
from models.rest_api.entitybase.handlers.export import ExportHandler
from models.rest_api.entitybase.handlers.statement import StatementHandler
from models.rest_api.entitybase.request.entity import EntityDeleteRequest
from models.rest_api.entitybase.response import TtlResponse
from models.rest_api.entitybase.response.misc import RawRevisionResponse
from models.rest_api.entitybase.response import (
    PropertyHashesResponse,
    PropertyListResponse,
)
from models.rest_api.entitybase.response.entity.entitybase import EntityDeleteResponse
from models.rest_api.entitybase.v1 import v1_router
from models.validation.utils import raise_validation_error


@v1_router.get("/entities/{entity_id}.ttl")
async def get_entity_data_turtle(entity_id: str, req: Request) -> TtlResponse:
    clients = req.app.state.clients
    handler = ExportHandler()
    result = handler.get_entity_data_turtle(
        entity_id, clients.vitess, clients.s3, clients.property_registry
    )
    if not isinstance(result, TtlResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@v1_router.delete("/entities/{entity_id}", response_model=EntityDeleteResponse)
async def delete_entity(  # type: ignore[no-any-return]
    entity_id: str, request: EntityDeleteRequest, req: Request
) -> EntityDeleteResponse:
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EntityDeleteHandler()
    result = await handler.delete_entity(
        entity_id, request, clients.vitess, clients.s3, clients.stream_producer
    )
    if not isinstance(result, EntityDeleteResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@v1_router.get(
    "/entities/{entity_id}/revisions/raw/{revision_id}",
    response_model=RawRevisionResponse,
)
def get_raw_revision(
    entity_id: str, revision_id: int, req: Request
) -> RawRevisionResponse:
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = AdminHandler()
    result = handler.get_raw_revision(
        entity_id, revision_id, clients.vitess, clients.s3
    )  # type: ignore
    if not isinstance(result, RawRevisionResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, RawRevisionResponse)
    return result


@v1_router.get("/entities/{entity_id}/properties", response_model=PropertyListResponse)
async def get_entity_properties(entity_id: str, req: Request) -> PropertyListResponse:
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = StatementHandler()
    return handler.get_entity_properties(entity_id, clients.vitess, clients.s3)


@v1_router.get(
    "/entities/{entity_id}/properties/{property_list}",
    response_model=PropertyHashesResponse,
)
async def get_entity_property_hashes(
    entity_id: str, property_list: str, req: Request
) -> PropertyHashesResponse:
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = StatementHandler()
    return handler.get_entity_property_hashes(
        entity_id, property_list, clients.vitess, clients.s3
    )
