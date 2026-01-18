"""Thanks-related routes."""

from fastapi import APIRouter, Header, Query, Request

from models.rest_api.clients import Clients
from models.rest_api.entitybase.handlers.thanks import ThanksHandler
from models.rest_api.entitybase.request.thanks import ThanksListRequest
from models.rest_api.entitybase.response.thanks import ThankResponse, ThanksListResponse
from models.validation.utils import raise_validation_error


thanks_router = APIRouter(tags=["interactions"])


@thanks_router.post(
    "/entitybase/v1/entities/{entity_id}/revisions/{revision_id}/thank",
    response_model=ThankResponse,
)
def send_thank_endpoint(
    req: Request,
    entity_id: str,
    revision_id: int,
    user_id: int = Header(..., alias="X-User-ID"),
) -> ThankResponse:
    """Send a thank for a specific revision."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler()
    result = handler.send_thank(entity_id, revision_id, user_id, clients.vitess)
    if not isinstance(result, ThankResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, ThankResponse)
    return result


@thanks_router.get(
    "/entitybase/v1/users/{user_id}/thanks/received", response_model=ThanksListResponse
)
def get_thanks_received_endpoint(
    req: Request,
    user_id: int,
    limit: int = Query(
        50, ge=1, le=500, description="Maximum number of thanks to return"
    ),
    offset: int = Query(0, ge=0, description="Number of thanks to skip"),
    hours: int = Query(24, ge=1, le=720, description="Time span in hours"),
) -> ThanksListResponse:
    """Get thanks received by user."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler()
    request = ThanksListRequest(limit=limit, offset=offset, hours=hours)
    result = handler.get_thanks_received(user_id, request, clients.vitess)
    if not isinstance(result, ThanksListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, ThanksListResponse)
    return result


@thanks_router.get(
    "/entitybase/v1/users/{user_id}/thanks/sent", response_model=ThanksListResponse
)
def get_thanks_sent_endpoint(
    req: Request,
    user_id: int,
    limit: int = Query(
        50, ge=1, le=500, description="Maximum number of thanks to return"
    ),
    offset: int = Query(0, ge=0, description="Number of thanks to skip"),
    hours: int = Query(24, ge=1, le=720, description="Time span in hours"),
) -> ThanksListResponse:
    """Get thanks sent by user."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler()
    request = ThanksListRequest(limit=limit, offset=offset, hours=hours)
    result = handler.get_thanks_sent(user_id, request, clients.vitess)
    if not isinstance(result, ThanksListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, ThanksListResponse)
    return result


@thanks_router.get(
    "/entitybase/v1/entities/{entity_id}/revisions/{revision_id}/thanks",
    response_model=ThanksListResponse,
)
def get_revision_thanks_endpoint(
    req: Request, entity_id: str, revision_id: int
) -> ThanksListResponse:
    """Get all thanks for a specific revision."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler()
    result = handler.get_revision_thanks(entity_id, revision_id, clients.vitess)
    if not isinstance(result, ThanksListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, ThanksListResponse)
    return result
