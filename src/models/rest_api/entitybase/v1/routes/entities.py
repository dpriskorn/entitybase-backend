"""Entity-related routes."""

from fastapi import APIRouter, Header, Request

from models.rest_api.state import State
from models.rest_api.entitybase.v1.handlers.entity.revert import EntityRevertHandler
from models.rest_api.entitybase.v1.request.entity import EntityRevertRequest
from models.rest_api.entitybase.v1.response.entity import EntityRevertResponse
from models.rest_api.utils import raise_validation_error


entities_router = APIRouter()


@entities_router.post(
    "/entitybase/v1/entities/{entity_id}/revert",
    response_model=EntityRevertResponse,
    tags=["entities"],
)
async def revert_entity(
    req: Request,
    entity_id: str,
    request: EntityRevertRequest,
    user_id: int = Header(..., alias="X-User-ID"),
) -> EntityRevertResponse:
    """Revert entity to a previous revision."""
    state = req.app.state.clients
    if not isinstance(state, State):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EntityRevertHandler(state=state)
    result = await handler.revert_entity(entity_id, request, user_id)
    if not isinstance(result, EntityRevertResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EntityRevertResponse)
    return result
