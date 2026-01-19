"""General entity endpoints for Entitybase v1 API."""

from typing import Any, Dict

from fastapi import APIRouter, Header, Query, Request, Response

from models.common import OperationResult
from models.rest_api.clients import Clients
from models.rest_api.entitybase.handlers.entity.handler import EntityHandler
from models.rest_api.entitybase.handlers.entity.delete import EntityDeleteHandler
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.handlers.export import ExportHandler
from models.rest_api.entitybase.handlers.statement import StatementHandler
from models.rest_api.entitybase.request.entity import EntityDeleteRequest
from models.rest_api.entitybase.request.entity import EntityUpdateRequest
from models.rest_api.entitybase.request.entity.add_property import AddPropertyRequest
from models.rest_api.entitybase.request.entity.patch_statement import (
    PatchStatementRequest,
)
from models.rest_api.entitybase.request.entity.remove_statement import (
    RemoveStatementRequest,
)
from models.rest_api.entitybase.request.entity.sitelink import SitelinkData
from models.rest_api.entitybase.response import (
    EntityResponse,
    EntityRevisionResponse,
    EntityJsonResponse,
)
from models.rest_api.entitybase.response import (
    PropertyHashesResponse,
    PropertyListResponse,
)
from models.rest_api.entitybase.response import TurtleResponse
from models.rest_api.entitybase.response.entity.entitybase import EntityDeleteResponse
from models.rest_api.entitybase.response.entity.entitybase import EntityHistoryEntry
from models.rest_api.entitybase.response.result import RevisionIdResult
from models.rest_api.utils import raise_validation_error

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


@router.get(
    "/entities/{entity_id}/revision/{revision_id}/json", response_model=Dict[str, Any]
)
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


@router.get("/entities/{entity_id}.json", response_model=EntityJsonResponse)
async def get_entity_data_json(entity_id: str, req: Request) -> EntityJsonResponse:
    """Get entity data in JSON format."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    entity_response = handler.get_entity(entity_id, clients.vitess, clients.s3)
    if not isinstance(entity_response.entity_data, dict):
        raise_validation_error("Invalid response type", status_code=500)
    return EntityJsonResponse(data=entity_response.entity_data)


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


# @router.get(
#     "/entities/{entity_id}/revision/raw/{revision_id}",
#     response_model=RawRevisionResponse,
# )
# def get_raw_revision(
#     entity_id: str, revision_id: int, req: Request
# ) -> RawRevisionResponse:
#     clients = req.app.state.clients
#     if not isinstance(clients, Clients):
#         raise_validation_error("Invalid clients type", status_code=500)
#     handler = AdminHandler()
#     result = handler.get_raw_revision(
#         entity_id, revision_id, clients.vitess, clients.s3
#     )  # type: ignore
#     if not isinstance(result, RawRevisionResponse):
#         raise_validation_error("Invalid response type", status_code=500)
#     assert isinstance(result, RawRevisionResponse)
#     return result


@router.get("/entities/{entity_id}/properties", response_model=PropertyListResponse)
async def get_entity_properties(entity_id: str, req: Request) -> PropertyListResponse:
    """Get list of unique property IDs for an entity's head revision.

    Returns sorted list of properties used in entity statements.
    """
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


@router.post(
    "/entities/{entity_id}/properties/{property_id}",
    response_model=OperationResult[RevisionIdResult],
)
async def add_entity_property(
    entity_id: str, property_id: str, request: AddPropertyRequest, req: Request
) -> OperationResult[RevisionIdResult]:
    """Add claims for a single property to an entity."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EntityHandler()
    result = handler.add_property(
        entity_id, property_id, request, clients.vitess, clients.s3, clients.validator
    )
    if not isinstance(result, OperationResult):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@router.delete(
    "/entities/{entity_id}/statements/{statement_hash}",
    response_model=OperationResult[RevisionIdResult],
)
async def remove_entity_statement(
    entity_id: str, statement_hash: str, request: RemoveStatementRequest, req: Request
) -> OperationResult[RevisionIdResult]:
    """Remove a statement by hash from an entity."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EntityHandler()
    result = handler.remove_statement(
        entity_id,
        statement_hash,
        request.edit_summary,
        clients.vitess,
        clients.s3,
        clients.validator,
    )
    if not isinstance(result, OperationResult):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@router.patch(
    "/entities/{entity_id}/statements/{statement_hash}",
    response_model=OperationResult[RevisionIdResult],
)
async def patch_entity_statement(
    entity_id: str, statement_hash: str, request: PatchStatementRequest, req: Request
) -> OperationResult[RevisionIdResult]:
    """Replace a statement by hash with new claim data."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EntityHandler()
    result = handler.patch_statement(
        entity_id,
        statement_hash,
        request,
        clients.vitess,
        clients.s3,
        clients.validator,
    )
    if not isinstance(result, OperationResult):
        raise_validation_error("Invalid response type", status_code=500)
    return result




@router.get("/entities/{entity_id}/sitelinks/{site}", response_model=SitelinkData)
async def get_entity_sitelink(entity_id: str, site: str, req: Request) -> SitelinkData:
    """Get a single sitelink for an entity."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EntityReadHandler()
    entity_response = handler.get_entity(entity_id, clients.vitess, clients.s3)

    sitelinks = entity_response.entity_data.get("sitelinks", {})
    if site not in sitelinks:
        raise_validation_error(f"Sitelink for site {site} not found", status_code=404)

    sitelink_data = sitelinks[site]
    return SitelinkData(title=sitelink_data.get("title", ""), badges=sitelink_data.get("badges", []))


@router.post("/entities/{entity_id}/sitelinks/{site}", response_model=OperationResult[RevisionIdResult])
async def post_entity_sitelink(
    entity_id: str, site: str, sitelink_data: SitelinkData, req: Request, x_user_id: int = Header(..., alias="X-User-ID")
) -> OperationResult[RevisionIdResult]:
    """Add a new sitelink for an entity."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(entity_id, clients.vitess, clients.s3)

    # Check if sitelink already exists
    sitelinks = current_entity.entity_data.get("sitelinks", {})
    if site in sitelinks:
        raise_validation_error(f"Sitelink for site {site} already exists", status_code=409)

    # Add sitelink
    if "sitelinks" not in current_entity.entity_data:
        current_entity.entity_data["sitelinks"] = {}
    current_entity.entity_data["sitelinks"][site] = {"title": sitelink_data.title, "badges": sitelink_data.badges}

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(type=entity_type, **current_entity.entity_data)

    result = await update_handler.update_entity(
        entity_id,
        update_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        clients.validator,
        user_id=x_user_id,
    )

    return OperationResult(success=True, data=RevisionIdResult(revision_id=result.revision_id))


@router.put("/entities/{entity_id}/sitelinks/{site}", response_model=OperationResult[RevisionIdResult])
async def put_entity_sitelink(
    entity_id: str, site: str, sitelink_data: SitelinkData, req: Request, x_user_id: int = Header(..., alias="X-User-ID")
) -> OperationResult[RevisionIdResult]:
    """Update an existing sitelink for an entity."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(entity_id, clients.vitess, clients.s3)

    # Check if sitelink exists
    sitelinks = current_entity.entity_data.get("sitelinks", {})
    if site not in sitelinks:
        raise_validation_error(f"Sitelink for site {site} not found", status_code=404)

    # Update sitelink
    current_entity.entity_data["sitelinks"][site] = {"title": sitelink_data.title, "badges": sitelink_data.badges}

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(type=entity_type, **current_entity.entity_data)

    result = await update_handler.update_entity(
        entity_id,
        update_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        clients.validator,
        user_id=x_user_id,
    )

    return OperationResult(success=True, data=RevisionIdResult(revision_id=result.revision_id))


@router.delete("/entities/{entity_id}/sitelinks/{site}", response_model=OperationResult[RevisionIdResult])
async def delete_entity_sitelink(
    entity_id: str, site: str, req: Request, x_user_id: int = Header(..., alias="X-User-ID")
) -> OperationResult[RevisionIdResult]:
    """Delete a sitelink from an entity."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)

    # Get current entity
    handler = EntityReadHandler()
    current_entity = handler.get_entity(entity_id, clients.vitess, clients.s3)

    # Check if sitelink exists
    sitelinks = current_entity.entity_data.get("sitelinks", {})
    if site not in sitelinks:
        # Idempotent - return success if not found
        return OperationResult(success=True, data=RevisionIdResult(revision_id=None))

    # Remove sitelink
    del current_entity.entity_data["sitelinks"][site]

    # Create new revision
    update_handler = EntityUpdateHandler()
    entity_type = current_entity.entity_data.get("type") or "item"
    update_request = EntityUpdateRequest(type=entity_type, **current_entity.entity_data)

    result = await update_handler.update_entity(
        entity_id,
        update_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        clients.validator,
        user_id=x_user_id,
    )

    return OperationResult(success=True, data=RevisionIdResult(revision_id=result.revision_id))