"""Redirect-related routes."""

from fastapi import APIRouter, Request

from models.rest_api.clients import Clients
from models.rest_api.v1.entitybase.handlers.redirect import RedirectHandler
from models.rest_api.v1.entitybase.request.entity import (
    EntityRedirectRequest,
    RedirectRevertRequest,
)
from models.rest_api.v1.entitybase.response.entity import EntityRevertResponse
from models.rest_api.v1.entitybase.response.entity.entitybase import EntityRedirectResponse
from models.rest_api.utils import raise_validation_error


redirects_router = APIRouter()


@redirects_router.post("/redirects", response_model=EntityRedirectResponse)
async def create_entity_redirect(
    request: EntityRedirectRequest, req: Request
) -> EntityRedirectResponse:
    """Create a redirect for an entity."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = RedirectHandler(clients.s3, clients.vitess, clients.stream_producer)
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
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = RedirectHandler(clients.s3, clients.vitess, clients.stream_producer)
    result = await handler.revert_entity_redirect(entity_id, request)
    if not isinstance(result, EntityRevertResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result
