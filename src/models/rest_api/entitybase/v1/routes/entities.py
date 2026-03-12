"""Entity-related routes."""

from fastapi import APIRouter, Request

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import EntityRevertRequest
from models.data.rest_api.v1.entitybase.response import EntityRevertResponse
from models.rest_api.entitybase.v1.handlers.entity.revert import EntityRevertHandler
from models.rest_api.utils import raise_validation_error, validate_state_clients

entities_router = APIRouter()


@entities_router.post(
    "/entities/{entity_id}/revert",
    response_model=EntityRevertResponse,
    tags=["entities"],
)
async def revert_entity(
    req: Request,
    entity_id: str,
    request: EntityRevertRequest,
    headers: EditHeadersType,
) -> EntityRevertResponse:
    """Revert entity to a previous revision."""
    state = req.app.state.state_handler
    validate_state_clients(state)

    handler = EntityRevertHandler(state=state)
    result = await handler.revert_entity(entity_id, request, edit_headers=headers)
    if not isinstance(result, EntityRevertResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result
