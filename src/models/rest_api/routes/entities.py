"""Entity-related routes."""

from fastapi import APIRouter, Header, Request

from models.rest_api.clients import Clients
from models.rest_api.entitybase.handlers.entity.revert import EntityRevertHandler
from models.rest_api.entitybase.request.entity import EntityRevertRequest
from models.rest_api.entitybase.response.entity import EntityRevertResponse
from models.validation.utils import raise_validation_error


entities_router = APIRouter()


@entities_router.post(
    "/entitybase/v1/entities/{entity_id}/revert", response_model=EntityRevertResponse
)
async def revert_entity(
    req: Request,
    entity_id: str,
    request: EntityRevertRequest,
    user_id: int = Header(..., alias="X-User-ID"),
) -> EntityRevertResponse:
    """Revert entity to a previous revision."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EntityRevertHandler()
    result = await handler.revert_entity(
        entity_id, request, clients.vitess, clients.s3, clients.stream_producer, user_id
    )
    if not isinstance(result, EntityRevertResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EntityRevertResponse)
    return result