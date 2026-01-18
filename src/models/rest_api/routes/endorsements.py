"""Endorsement-related routes."""

from fastapi import APIRouter, Header, Query, Request

from models.rest_api.clients import Clients
from models.rest_api.entitybase.handlers.endorsements import EndorsementHandler
from models.rest_api.entitybase.request.endorsements import EndorsementListRequest
from models.rest_api.entitybase.response.endorsements import (
    BatchEndorsementStatsResponse,
    EndorsementListResponse,
    EndorsementResponse,
    EndorsementStatsResponse,
    SingleEndorsementStatsResponse,
)
from models.validation.utils import raise_validation_error


endorsements_router = APIRouter()


@endorsements_router.post(
    "/entitybase/v1/statements/{statement_hash}/endorse",
    response_model=EndorsementResponse,
)
def endorse_statement_endpoint(
    req: Request, statement_hash: int, user_id: int = Header(..., alias="X-User-ID")
) -> EndorsementResponse:
    """Endorse a statement to signal trust."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler()
    result = handler.endorse_statement(statement_hash, user_id, clients.vitess)
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
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler()
    result = handler.withdraw_endorsement(statement_hash, user_id, clients.vitess)
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
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler()
    request = EndorsementListRequest(
        limit=limit, offset=offset, include_removed=include_removed
    )
    result = handler.get_statement_endorsements(statement_hash, request, clients.vitess)
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
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler()
    request = EndorsementListRequest(
        limit=limit, offset=offset, include_removed=include_removed
    )
    result = handler.get_user_endorsements(user_id, request, clients.vitess)
    if not isinstance(result, EndorsementListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementListResponse)
    return result


@endorsements_router.get(
    "/entitybase/v1/users/{user_id}/endorsements/stats",
    response_model=EndorsementStatsResponse,
)
def get_user_endorsement_stats_endpoint(req: Request, user_id: int) -> EndorsementStatsResponse:
    """Get endorsement statistics for a user."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler()
    result = handler.get_user_endorsement_stats(user_id, clients.vitess)
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
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)

    # Get stats for single statement
    handler = EndorsementHandler()
    result = handler.get_batch_statement_endorsement_stats(
        [statement_hash], clients.vitess
    )
    if not isinstance(result, BatchEndorsementStatsResponse):
        raise_validation_error("Invalid response type", status_code=500)

    if not result.stats:
        raise_validation_error("Statement not found", status_code=404)

    # Convert batch response to single response
    stat = result.stats[0]
    return SingleEndorsementStatsResponse(
        total=stat.total, active=stat.active, withdrawn=stat.withdrawn
    )