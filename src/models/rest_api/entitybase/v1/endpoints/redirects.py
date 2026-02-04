"""Redirect-related routes."""

from fastapi import APIRouter, Request

from models.data.rest_api.v1.entitybase.request.headers import EditHeadersType
from models.data.rest_api.v1.entitybase.request import (
    EntityRedirectRequest,
    RedirectRevertRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityRedirectResponse,
)
from models.data.rest_api.v1.entitybase.response import EntityRevertResponse
from models.rest_api.entitybase.v1.handlers.entity.redirect import RedirectHandler
from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.rest_api.utils import raise_validation_error

redirects_router = APIRouter()


@redirects_router.post("/redirects", response_model=EntityRedirectResponse)
async def create_entity_redirect(
    request: EntityRedirectRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityRedirectResponse:
    """Create a redirect for an entity."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = RedirectHandler(state=state)
    result = await handler.create_entity_redirect(request, edit_headers=headers)
    if not isinstance(result, EntityRedirectResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@redirects_router.post(
    "/entities/{entity_id}/revert-redirect", response_model=EntityRevertResponse
)
async def revert_entity_redirect(  # type: ignore[no-any-return]
    entity_id: str,
    request: RedirectRevertRequest,
    req: Request,
    headers: EditHeadersType,
) -> EntityRevertResponse:
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = RedirectHandler(state=state)
    result = await handler.revert_entity_redirect(entity_id, request, edit_headers=headers)
    if not isinstance(result, EntityRevertResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result
