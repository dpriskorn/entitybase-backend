from fastapi import APIRouter, Request

from models.api import (
    EntityCreateRequest,
    EntityJsonImportRequest,
    EntityJsonImportResponse,
    EntityResponse,
    EntityUpdateRequest,
)
from ...handlers.entity.item import ItemCreateHandler
from ...handlers.entity.items.update import ItemUpdateHandler
from ...handlers.entity.property.update import PropertyUpdateHandler
from ...handlers.entity.lexeme.update import LexemeUpdateHandler
from ...handlers.entity.wikidata_import import EntityJsonImportHandler

router = APIRouter()


@router.post("/entities/items", response_model=EntityResponse)
async def create_item(request: EntityCreateRequest, req: Request) -> EntityResponse:
    """Create a new item entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    enumeration_service = req.app.state.enumeration_service
    handler = ItemCreateHandler(enumeration_service)
    return await handler.create_entity(
        request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.put("/item/{entity_id}", response_model=EntityResponse)
async def update_item(
    entity_id: str, request: EntityUpdateRequest, req: Request
) -> EntityResponse:
    """Update an existing item entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    handler = ItemUpdateHandler()
    # Convert to EntityUpdateRequest
    entity_request = EntityUpdateRequest(**request.model_dump())
    return await handler.update_entity(
        entity_id,
        entity_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.put("/property/{entity_id}", response_model=EntityResponse)
async def update_property(
    entity_id: str, request: EntityUpdateRequest, req: Request
) -> EntityResponse:
    """Update an existing property entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    handler = PropertyUpdateHandler()
    entity_request = EntityUpdateRequest(**request.model_dump())
    entity_request.type = "property"
    return await handler.update_entity(
        entity_id,
        entity_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.put("/lexeme/{entity_id}", response_model=EntityResponse)
async def update_lexeme(
    entity_id: str, request: EntityUpdateRequest, req: Request
) -> EntityResponse:
    """Update an existing lexeme entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    handler = LexemeUpdateHandler()
    entity_request = EntityUpdateRequest(**request.model_dump())
    entity_request.type = "lexeme"
    return await handler.update_entity(
        entity_id,
        entity_request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )


@router.post("/json-import", response_model=EntityJsonImportResponse)
async def import_entities_from_jsonl(
    request: EntityJsonImportRequest, req: Request
) -> EntityJsonImportResponse:
    """Import entities from Wikidata JSONL dump file."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    return await EntityJsonImportHandler.import_entities_from_jsonl(
        request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )
