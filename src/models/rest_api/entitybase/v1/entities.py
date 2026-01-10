from fastapi import APIRouter, Query, Request

from models.api import EntityListResponse, EntityResponse, RevisionMetadata
from models.rest_api.handlers.admin import AdminHandler
from ...handlers.entity.read import EntityReadHandler

router = APIRouter()


@router.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str, req: Request) -> EntityResponse:
    """Retrieve a single entity by its ID."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    return handler.get_entity(
        entity_id, clients.vitess, clients.s3, fetch_metadata=True
    )


@router.get("/entities/{entity_id}/history", response_model=list[RevisionMetadata])
def get_entity_history(
    entity_id: str,
    req: Request,
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of revisions to return"
    ),
    offset: int = Query(0, ge=0, description="Number of revisions to skip"),
) -> list:
    """Get the revision history for an entity."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    return handler.get_entity_history(  # type: ignore[no-any-return]
        entity_id, clients.vitess, clients.s3, limit, offset
    )


@router.get("/entities/{entity_id}/revision/{revision_id}", response_model=dict)
def get_entity_revision(entity_id: str, revision_id: int, req: Request) -> dict:
    """Get a specific revision of an entity."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    return handler.get_entity_revision(entity_id, revision_id, clients.s3)  # type: ignore


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
    return handler.list_entities(
        clients.vitess, entity_type=entity_type, limit=limit, offset=offset
    )
