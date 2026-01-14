"""General entity endpoints for Entitybase v1 API."""

from fastapi import APIRouter, Query, Request, Response

from models.rest_api.handlers.admin import AdminHandler
from ...handlers.entity.read import EntityReadHandler
from ...response import EntityResponse, EntityListResponse, EntityRevisionResponse
from ...response.entity.entitybase import EntityHistoryEntry

router = APIRouter()


@router.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str, req: Request) -> EntityResponse:
    """Retrieve a single entity by its ID."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    return handler.get_entity(  # type: ignore[no-any-return]
        entity_id, clients.vitess, clients.s3, fetch_metadata=True
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


@router.get("/entities/{entity_id}/revision/{revision_id}/rdf")
async def get_entity_rdf_revision(
    entity_id: str,
    revision_id: int,
    format: str = Query("turtle", enum=["turtle", "rdfxml", "ntriples"]),
    req: Request,
) -> Response:
    """Get RDF representation of a specific entity revision."""
    from models.workers.entity_diff_worker import RDFSerializer

    clients = req.app.state.clients
    revision_data = clients.s3.read_revision(entity_id, revision_id)

    serializer = RDFSerializer()
    rdf_content = serializer.entity_data_to_rdf(revision_data.data, format)

    content_type = {
        "turtle": "text/turtle",
        "rdfxml": "application/rdf+xml",
        "ntriples": "application/n-triples"
    }.get(format, "text/turtle")

    return Response(content=rdf_content, media_type=content_type)


@router.get("/entities/{entity_id}/revision/{revision_id}/json")
async def get_entity_json_revision(
    entity_id: str,
    revision_id: int,
    req: Request,
) -> dict:
    """Get JSON representation of a specific entity revision."""
    clients = req.app.state.clients
    revision_data = clients.s3.read_revision(entity_id, revision_id)

    return revision_data.data


@router.get("/entities", response_model=EntityListResponse)
def get_entities(
    req: Request,
    entity_type: str | None = Query(
        None,
        description="Entity type to filter by (item, property, lexeme, entityschema). Leave empty for all types",
    ),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of entities to return"
    ),
    offset: int = Query(0, ge=0, description="Number of entities to skip"),
) -> EntityListResponse:
    """List entities, optionally filtered by type (or all entities if no type specified)."""
    clients = req.app.state.clients
    handler = AdminHandler()
    return handler.list_entities(  # type: ignore[no-any-return]
        clients.vitess, entity_type=entity_type, limit=limit, offset=offset
    )
