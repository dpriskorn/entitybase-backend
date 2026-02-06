"""General entity endpoints for Entitybase v1 API."""

import logging

from fastapi import APIRouter, Query, Request, Response

from models.data.common import OperationResult
from models.data.rest_api.v1.entitybase.request import AddPropertyRequest
from models.data.rest_api.v1.entitybase.request import EntityDeleteRequest
from models.data.rest_api.v1.entitybase.request import (
    PatchStatementRequest,
)
from models.data.rest_api.v1.entitybase.request import (
    RemoveStatementRequest,
)
from models.data.rest_api.v1.entitybase.request.entity.context import SitelinkUpdateContext
from models.data.rest_api.v1.entitybase.request.entity.sitelink import SitelinkData
from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.response import (
    EntityDeleteResponse,
)
from models.data.rest_api.v1.entitybase.response import EntityHistoryEntry
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
    EntityJsonResponse,
)
from models.data.rest_api.v1.entitybase.response import (
    PropertyHashesResponse,
    PropertyListResponse,
)
from models.data.rest_api.v1.entitybase.response import RevisionIdResult
from models.data.rest_api.v1.entitybase.response import TurtleResponse
from models.rest_api.entitybase.v1.handlers.entity.delete import EntityDeleteHandler
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.handlers.export import ExportHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.rest_api.entitybase.v1.handlers.statement import StatementHandler
from models.rest_api.entitybase.v1.services.entity_statement_service import EntityStatementService
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str, req: Request) -> EntityResponse:
    """Retrieve a single entity by its ID."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    return handler.get_entity(  # type: ignore[no-any-return]
        entity_id
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
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    return handler.get_entity_history(  # type: ignore[no-any-return]
        entity_id, limit, offset
    )


@router.get(
    "/entities/{entity_id}/revision/{revision_id}",
    response_model=EntityResponse,
)
def get_entity_revision(
    entity_id: str, revision_id: int, req: Request
) -> EntityResponse:
    """Get a specific revision of an entity."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    return handler.get_entity_revision(entity_id, revision_id)  # type: ignore


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
    from models.workers.entity_diff.rdf_serializer import RDFSerializer

    state = req.app.state.state_handler
    revision_data = state.s3_client.read_revision(entity_id, revision_id)

    serializer = RDFSerializer()
    rdf_content = serializer.entity_data_to_rdf(revision_data.data, format_)

    content_type = {
        "turtle": "text/turtle",
        "rdfxml": "application/rdf+xml",
        "ntriples": "application/n-triples",
    }.get(format_, "text/turtle")

    return Response(content=rdf_content, media_type=content_type)


@router.get(
    "/entities/{entity_id}/revision/{revision_id}/json", response_model=EntityJsonResponse
)
async def get_entity_json_revision(
    entity_id: str,
    revision_id: int,
    req: Request,
) -> EntityJsonResponse:
    """Get JSON representation of a specific entity revision."""
    state = req.app.state.state_handler
    revision_data = state.s3_client.read_revision(entity_id, revision_id)

    return EntityJsonResponse(data=revision_data.data)


@router.get("/entities/{entity_id}.ttl")
async def get_entity_data_turtle(entity_id: str, req: Request) -> TurtleResponse:
    """Get entity data in Turtle format."""
    state = req.app.state.state_handler
    handler = ExportHandler(state=state)
    result = handler.get_entity_data_turtle(entity_id)
    if not isinstance(result, TurtleResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@router.get("/entities/{entity_id}.json", response_model=EntityJsonResponse)
async def get_entity_data_json(entity_id: str, req: Request) -> EntityJsonResponse:
    """Get entity data in JSON format."""
    state = req.app.state.state_handler
    handler = EntityReadHandler(state=state)
    entity_response = handler.get_entity(entity_id)
    if not isinstance(entity_response.entity_data, dict):
        raise_validation_error("Invalid response type", status_code=500)
    return EntityJsonResponse(data=entity_response.entity_data)


@router.delete("/entities/{entity_id}", response_model=EntityDeleteResponse)
async def delete_entity(  # type: ignore[no-any-return]
    entity_id: str,
    request: EntityDeleteRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityDeleteResponse:
    """Delete an entity."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    # todo pass clients to the handler here
    handler = EntityDeleteHandler(state=state)
    result = await handler.delete_entity(entity_id, request, edit_headers=headers)
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
#     state = req.app.state.state_handler
#     if not isinstance(clients, Clients):
#         raise_validation_error("Invalid clients type", status_code=500)
#     handler = AdminHandler(state=state)
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
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    # todo pass clients to the handler here
    handler = StatementHandler(state=state)
    return handler.get_entity_properties(entity_id)


@router.get(
    "/entities/{entity_id}/properties/{property_list}",
    response_model=PropertyHashesResponse,
)
async def get_entity_property_hashes(
    entity_id: str, property_list: str, req: Request
) -> PropertyHashesResponse:
    """Get entity property hashes for specified properties."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    # todo pass clients to the handler here
    handler = StatementHandler(state=state)
    return handler.get_entity_property_hashes(entity_id, property_list)


@router.post(
    "/entities/{entity_id}/properties/{property_id}",
    response_model=OperationResult[RevisionIdResult],
)
async def add_entity_property(
    entity_id: str,
    property_id: str,
    request: AddPropertyRequest,
    req: Request,
    headers: EditHeadersType,
) -> OperationResult[RevisionIdResult]:
    """Add claims for a single property to an entity."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    # todo pass clients to the handler here
    handler = EntityStatementService(state=state)
    result = await handler.add_property(
        entity_id, property_id, request, edit_headers=headers
    )
    if not isinstance(result, OperationResult):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@router.delete(
    "/entities/{entity_id}/statements/{statement_hash}",
    response_model=OperationResult[RevisionIdResult],
)
async def remove_entity_statement(
    entity_id: str,
    statement_hash: str,
    request: RemoveStatementRequest,
    req: Request,
    headers: EditHeadersType,
) -> OperationResult[RevisionIdResult]:
    """Remove a statement by hash from an entity."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    # todo pass clients to the handler here
    handler = EntityStatementService(state=state)
    result = await handler.remove_statement(
        entity_id,
        statement_hash,
        headers,
    )
    if not isinstance(result, OperationResult):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@router.patch(
    "/entities/{entity_id}/statements/{statement_hash}",
    response_model=OperationResult[RevisionIdResult],
)
async def patch_entity_statement(
    entity_id: str,
    statement_hash: str,
    request: PatchStatementRequest,
    req: Request,
    headers: EditHeadersType,
) -> OperationResult[RevisionIdResult]:
    """Replace a statement by hash with new claim data."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EntityStatementService(state=state)
    result = await handler.patch_statement(
        entity_id,
        statement_hash,
        request,
        headers,
    )
    if not isinstance(result, OperationResult):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@router.get("/entities/{entity_id}/sitelinks/{site}", response_model=SitelinkData)
async def get_entity_sitelink(entity_id: str, site: str, req: Request) -> SitelinkData:
    """Get a single sitelink for an entity."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    # todo pass clients to the handler here
    handler = EntityReadHandler(state=state)
    entity_response = handler.get_entity(entity_id)

    sitelinks = entity_response.entity_data.get("sitelinks", {})
    if site not in sitelinks:
        raise_validation_error(f"Sitelink for site {site} not found", status_code=404)

    sitelink_data = sitelinks[site]
    return SitelinkData(
        title=sitelink_data.get("title", ""), badges=sitelink_data.get("badges", [])
    )


@router.post(
    "/entities/{entity_id}/sitelinks/{site}",
    response_model=OperationResult[RevisionIdResult],
)
async def post_entity_sitelink(
    entity_id: str,
    site: str,
    sitelink_data: SitelinkData,
    req: Request,
    headers: EditHeadersType,
) -> OperationResult[RevisionIdResult]:
    """Add a new sitelink for an entity."""
    logger.debug(
        f"Starting post_entity_sitelink for entity_id: {entity_id}, site: {site}"
    )
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(entity_id)

    # Check if sitelink already exists
    sitelinks = current_entity.entity_data.get("sitelinks", {})
    if site in sitelinks:
        raise_validation_error(
            f"Sitelink for site {site} already exists", status_code=409
        )

    # Create new revision using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    ctx = SitelinkUpdateContext(
        entity_id=entity_id,
        site=site,
        title=sitelink_data.title,
        badges=sitelink_data.badges,
    )
    result = await update_handler.update_sitelink(
        ctx,
        headers,
        state.validator,
    )

    return OperationResult(
        success=True, data=RevisionIdResult(revision_id=result.revision_id)
    )


@router.put(
    "/entities/{entity_id}/sitelinks/{site}",
    response_model=OperationResult[RevisionIdResult],
)
async def put_entity_sitelink(
    entity_id: str,
    site: str,
    sitelink_data: SitelinkData,
    req: Request,
    headers: EditHeadersType,
) -> OperationResult[RevisionIdResult]:
    """Update an existing sitelink for an entity."""
    logger.debug(
        f"Starting put_entity_sitelink for entity_id: {entity_id}, site: {site}"
    )
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)

    # Get current entity
    handler = EntityReadHandler(state=state)
    current_entity = handler.get_entity(entity_id)

    # Update sitelink using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    ctx = SitelinkUpdateContext(
        entity_id=entity_id,
        site=site,
        title=sitelink_data.title,
        badges=sitelink_data.badges,
    )
    result = await update_handler.update_sitelink(
        ctx,
        headers,
        state.validator,
    )

    return OperationResult(
        success=True, data=RevisionIdResult(revision_id=result.revision_id)
    )


@router.delete(
    "/entities/{entity_id}/sitelinks/{site}",
    response_model=OperationResult[RevisionIdResult],
)
async def delete_entity_sitelink(
    entity_id: str,
    site: str,
    req: Request,
    headers: EditHeadersType,
) -> OperationResult[RevisionIdResult]:
    """Delete a sitelink from an entity."""
    logger.debug(
        f"Starting delete_entity_sitelink for entity_id: {entity_id}, site: {site}"
    )
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)

    # Delete sitelink using EntityUpdateHandler
    update_handler = EntityUpdateHandler(state=state)
    result = await update_handler.delete_sitelink(
        entity_id,
        site,
        headers,
        state.validator,
    )

    return OperationResult(
        success=True, data=RevisionIdResult(revision_id=result.revision_id)
    )
