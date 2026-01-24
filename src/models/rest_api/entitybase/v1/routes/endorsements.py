"""Endorsement-related routes."""

from fastapi import APIRouter, Header, Query, Request

from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.rest_api.entitybase.v1.handlers.endorsements import EndorsementHandler
from models.data.rest_api.v1.entitybase.request import EndorsementListRequest
from models.data.rest_api.v1.entitybase.response import (
    BatchEndorsementStatsResponse,
    EndorsementListResponse,
    EndorsementResponse,
    EndorsementStatsResponse,
    SingleEndorsementStatsResponse,
)
from models.rest_api.utils import raise_validation_error


endorsements_router = APIRouter(tags=["interactions"])


@endorsements_router.post(
    "/entitybase/v1/statements/{statement_hash}/endorse",
    response_model=EndorsementResponse,
)
def endorse_statement_endpoint(
    req: Request, statement_hash: int, user_id: int = Header(..., alias="X-User-ID")
) -> EndorsementResponse:
    """Endorse a statement to signal trust."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler(state=state)
    result = handler.endorse_statement(statement_hash, user_id)
    if not isinstance(result, EndorsementResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementResponse)
    return result


@endorsements_router.delete(
    "/entitybase/v1/statements/{statement_hash}/endorse",
    response_model=EndorsementResponse,
)
def withdraw_endorsement_endpoint(
    req: Request, statement_hash: int, user_id: int = Header(..., alias="X-User-ID")
) -> EndorsementResponse:
    """Withdraw endorsement from a statement."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler(state=state)
    result = handler.withdraw_endorsement(statement_hash, user_id)
    if not isinstance(result, EndorsementResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementResponse)
    return result


@endorsements_router.get(
    "/entitybase/v1/statements/{statement_hash}/endorsements",
    response_model=EndorsementListResponse,
)
def get_statement_endorsements_endpoint(
    req: Request,
    statement_hash: int,
    limit: int = Query(
        50, ge=1, le=500, description="Maximum number of endorsements to return"
    ),
    offset: int = Query(0, ge=0, description="Number of endorsements to skip"),
    include_removed: bool = Query(False, description="Include withdrawn endorsements"),
) -> EndorsementListResponse:
    """Get endorsements for a statement."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler(state=state)
    request = EndorsementListRequest(
        limit=limit, offset=offset, include_removed=include_removed
    )
    result = handler.get_statement_endorsements(statement_hash, request)
    if not isinstance(result, EndorsementListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementListResponse)
    return result


@endorsements_router.get(
    "/entitybase/v1/users/{user_id}/endorsements",
    response_model=EndorsementListResponse,
)
def get_user_endorsements_endpoint(
    req: Request,
    user_id: int,
    limit: int = Query(
        50, ge=1, le=500, description="Maximum number of endorsements to return"
    ),
    offset: int = Query(0, ge=0, description="Number of endorsements to skip"),
    include_removed: bool = Query(False, description="Include withdrawn endorsements"),
) -> EndorsementListResponse:
    """Get endorsements given by a user."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler(state=state)
    request = EndorsementListRequest(
        limit=limit, offset=offset, include_removed=include_removed
    )
    result = handler.get_user_endorsements(user_id, request)
    if not isinstance(result, EndorsementListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementListResponse)
    return result


@endorsements_router.get(
    "/entitybase/v1/users/{user_id}/endorsements/stats",
    response_model=EndorsementStatsResponse,
)
def get_user_endorsement_stats_endpoint(
    req: Request, user_id: int
) -> EndorsementStatsResponse:
    """Get endorsement statistics for a user."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler(state=state)
    result = handler.get_user_endorsement_stats(user_id)
    if not isinstance(result, EndorsementStatsResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementStatsResponse)
    return result


@endorsements_router.get(
    "/entitybase/v1/statements/{statement_hash}/endorsements/stats",
    response_model=SingleEndorsementStatsResponse,
)
def get_statement_endorsement_stats(
    req: Request,
    statement_hash: int,
) -> SingleEndorsementStatsResponse:
    """Get endorsement statistics for a statement."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)

    # Get stats for single statement
    handler = EndorsementHandler(state=state)
    result = handler.get_batch_statement_endorsement_stats([statement_hash])
    if not isinstance(result, BatchEndorsementStatsResponse):
        raise_validation_error("Invalid response type", status_code=500)

    if not result.stats:
        raise_validation_error("Statement not found", status_code=404)

    # Convert batch response to single response
    stat = result.stats[0]
    return SingleEndorsementStatsResponse(
        total=stat.total, active=stat.active, withdrawn=stat.withdrawn
    )
