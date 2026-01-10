from fastapi import APIRouter, Request

from models.api import EntityCreateRequest, EntityResponse
from ...handlers.entity.property import PropertyCreateHandler

router = APIRouter()


@router.post("/entities/properties", response_model=EntityResponse)
async def create_property(request: EntityCreateRequest, req: Request) -> EntityResponse:
    """Create a new property entity."""
    clients = req.app.state.clients
    validator = req.app.state.validator
    enumeration_service = req.app.state.enumeration_service
    handler = PropertyCreateHandler(enumeration_service)
    return await handler.create_entity(
        request,
        clients.vitess,
        clients.s3,
        clients.stream_producer,
        validator,
    )
