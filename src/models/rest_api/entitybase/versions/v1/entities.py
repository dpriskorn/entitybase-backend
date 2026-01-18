"""General entity endpoints for Entitybase v1 API."""

from typing import Any, Dict

from fastapi import APIRouter, Query, Request, Response

from models.rest_api.clients import Clients
from models.rest_api.entitybase.handlers.admin import AdminHandler
from models.rest_api.entitybase.handlers.entity.delete import EntityDeleteHandler
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.handlers.export import ExportHandler
from models.rest_api.entitybase.handlers.statement import StatementHandler
from models.rest_api.entitybase.request.entity import EntityDeleteRequest
from models.rest_api.entitybase.response import (
    EntityResponse,
    EntityListResponse,
    EntityRevisionResponse,
)
from models.rest_api.entitybase.response import TurtleResponse
from models.rest_api.entitybase.response.misc import RawRevisionResponse
from models.rest_api.entitybase.response import (
    PropertyHashesResponse,
    PropertyListResponse,
)
from models.rest_api.entitybase.response.entity.entitybase import EntityHistoryEntry
from models.rest_api.entitybase.response.entity.entitybase import EntityDeleteResponse
from models.validation.utils import raise_validation_error

router = APIRouter()


@router.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str, req: Request) -> EntityResponse:
    """Retrieve a single entity by its ID."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    return handler.get_entity(  # type: ignore[no-any-return]
        entity_id, clients.vitess, clients.s3
    )


@router.get("/entities/{entity_id}/history", response_model=list[EntityHistoryEntry])
def get_entity_history(
    entity_id: str,
    req: Request,
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of revisions to return"
    ),
    offset: int = Query(0, ge=0, description="Number of revisions to skip"),
) -> list[EntityHistoryEntry]:
    """Get the revision history for an entity."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    return handler.get_entity_history(  # type: ignore[no-any-return]
        entity_id, clients.vitess, clients.s3, limit, offset
    )


@router.get(
    "/entities/{entity_id}/revision/{revision_id}",
    response_model=EntityRevisionResponse,
)
def get_entity_revision(
    entity_id: str, revision_id: int, req: Request
) -> EntityRevisionResponse:
    """Get a specific revision of an entity."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    return handler.get_entity_revision(entity_id, revision_id, clients.s3)  # type: ignore


@router.get("/entities/{entity_id}/revision/{revision_id}/ttl")
async def get_entity_ttl_revision(
    req: Request,
    entity_id: str,
    revision_id: int,
    format_: str = Query(
        "turtle", alias="format", enum=["turtle", "rdfxml", "ntriples"]
    ),
) -> Response:
    """Get Turtle (TTL) representation of a specific entity revision."""
    from models.workers.entity_diff_worker import RDFSerializer

    clients = req.app.state.clients
    revision_data = clients.s3.read_revision(entity_id, revision_id)

    serializer = RDFSerializer()
    rdf_content = serializer.entity_data_to_rdf(revision_data.data, format_)

    content_type = {
        "turtle": "text/turtle",
        "rdfxml": "application/rdf+xml",
        "ntriples": "application/n-triples",
    }.get(format_, "text/turtle")

    return Response(content=rdf_content, media_type=content_type)


@router.get("/entities/{entity_id}/revision/{revision_id}/json", response_model=Dict[str, Any])
async def get_entity_json_revision(  # type: ignore[return]
    entity_id: str,
    revision_id: int,
    req: Request,
) -> dict:
    """Get JSON representation of a specific entity revision."""
    clients = req.app.state.clients
    revision_data = clients.s3.read_revision(entity_id, revision_id)

    return revision_data.data  # type: ignore[no-any-return]


@router.get("/entities/{entity_id}.ttl")
async def get_entity_data_turtle(entity_id: str, req: Request) -> TurtleResponse:
    """Get entity data in Turtle format."""
    clients = req.app.state.clients
    handler = ExportHandler()
    result = handler.get_entity_data_turtle(
        entity_id, clients.vitess, clients.s3, clients.property_registry
    )
    if not isinstance(result, TurtleResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@router.get("/entities/{entity_id}.json", response_model=Dict[str, Any])
async def get_entity_data_json(entity_id: str, req: Request) -> dict[str, Any]:
    """Get entity data in JSON format."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    entity_response = handler.get_entity(entity_id, clients.vitess, clients.s3)
    if not isinstance(entity_response.entity_data, dict):
        raise_validation_error("Invalid response type", status_code=500)
    return entity_response.entity_data


@router.delete("/entities/{entity_id}", response_model=EntityDeleteResponse)
async def delete_entity(  # type: ignore[no-any-return]
    entity_id: str, request: EntityDeleteRequest, req: Request
) -> EntityDeleteResponse:
    """Delete an entity."""
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


@router.get(
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


@router.get("/entities/{entity_id}/properties", response_model=PropertyListResponse)
async def get_entity_properties(entity_id: str, req: Request) -> PropertyListResponse:
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = StatementHandler()
    return handler.get_entity_properties(entity_id, clients.vitess, clients.s3)


@router.get(
    "/entities/{entity_id}/properties/{property_list}",
    response_model=PropertyHashesResponse,
)
async def get_entity_property_hashes(
    entity_id: str, property_list: str, req: Request
) -> PropertyHashesResponse:
    """Get entity property hashes for specified properties."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = StatementHandler()
    return handler.get_entity_property_hashes(
        entity_id, property_list, clients.vitess, clients.s3
    )
