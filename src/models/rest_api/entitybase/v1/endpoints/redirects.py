"""Redirect-related routes."""

from fastapi import APIRouter, Request

from models.rest_api.state import State
from models.rest_api.entitybase.v1.handlers.entity.redirect import RedirectHandler
from models.rest_api.entitybase.v1.request.entity import (
    EntityRedirectRequest,
    RedirectRevertRequest,
)
from models.rest_api.entitybase.v1.response.entity import EntityRevertResponse
from models.rest_api.entitybase.v1.response.entity.entitybase import (
    EntityRedirectResponse,
)
from models.rest_api.utils import raise_validation_error


redirects_router = APIRouter()


@redirects_router.post("/redirects", response_model=EntityRedirectResponse)
async def create_entity_redirect(
    request: EntityRedirectRequest, req: Request
) -> EntityRedirectResponse:
    """Create a redirect for an entity."""
    state = req.app.state.state
    if not isinstance(state, State):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = RedirectHandler(clients.s3_config)
    result = await handler.create_entity_redirect(request)
    if not isinstance(result, EntityRedirectResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@redirects_router.post(
    "/entities/{entity_id}/revert-redirect", response_model=EntityRevertResponse
)
async def revert_entity_redirect(  # type: ignore[no-any-return]
    entity_id: str, request: RedirectRevertRequest, req: Request
) -> EntityRevertResponse:
    state = req.app.state.state
    if not isinstance(state, State):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = RedirectHandler(clients.s3_config)
    result = await handler.revert_entity_redirect(entity_id, request)
    if not isinstance(result, EntityRevertResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result
