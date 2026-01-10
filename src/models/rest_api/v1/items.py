from fastapi import APIRouter, Request

from models.api_models import EntityCreateRequest, EntityResponse, EntityUpdateRequest
from ..handlers.entity.item import ItemCreateHandler
from ..handlers.entity.update import EntityUpdateHandler

router = APIRouter()


@router.post("/entities/items", response_model=EntityResponse)
async def create_item(request: EntityCreateRequest, req: Request) -> EntityResponse:
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
    clients = req.app.state.clients
    validator = req.app.state.validator
    handler = EntityUpdateHandler()
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
    clients = req.app.state.clients
    validator = req.app.state.validator
    handler = EntityUpdateHandler()
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
