"""Thanks-related routes."""

from fastapi import APIRouter, Header, Query, Request

from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler
from models.data.rest_api.v1.entitybase.request.thanks import ThanksListRequest
from models.data.rest_api.v1.entitybase.response import (
    ThankResponse,
    ThanksListResponse,
)
from models.rest_api.utils import raise_validation_error


thanks_router = APIRouter(tags=["interactions"])


@thanks_router.post(
    "/entities/{entity_id}/revisions/{revision_id}/thank",
    response_model=ThankResponse,
)
def send_thank_endpoint(
    req: Request,
    entity_id: str,
    revision_id: int,
    user_id: int = Header(..., alias="X-User-ID"),
) -> ThankResponse:
    """Send a thank for a specific revision."""
    state = req.app.state.state_handler
    if not (hasattr(state, "vitess_client") and hasattr(state, "s3_client")):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler(state=state)
    result = handler.send_thank(entity_id, revision_id, user_id)
    if not isinstance(result, ThankResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@thanks_router.get(
    "/users/{user_id}/thanks/received", response_model=ThanksListResponse
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
    state = req.app.state.state_handler
    if not (hasattr(state, "vitess_client") and hasattr(state, "s3_client")):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler(state=state)
    request = ThanksListRequest(limit=limit, offset=offset, hours=hours)
    result = handler.get_thanks_received(user_id, request)
    if not isinstance(result, ThanksListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@thanks_router.get("/users/{user_id}/thanks/sent", response_model=ThanksListResponse)
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
    state = req.app.state.state_handler
    if not (hasattr(state, "vitess_client") and hasattr(state, "s3_client")):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler(state=state)
    request = ThanksListRequest(limit=limit, offset=offset, hours=hours)
    result = handler.get_thanks_sent(user_id, request)
    if not isinstance(result, ThanksListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@thanks_router.get(
    "/entities/{entity_id}/revisions/{revision_id}/thanks",
    response_model=ThanksListResponse,
)
def get_revision_thanks_endpoint(
    req: Request, entity_id: str, revision_id: int
) -> ThanksListResponse:
    """Get all thanks for a specific revision."""
    state = req.app.state.state_handler
    if not (hasattr(state, "vitess_client") and hasattr(state, "s3_client")):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler(state=state)
    result = handler.get_revision_thanks(entity_id, revision_id)
    if not isinstance(result, ThanksListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result
