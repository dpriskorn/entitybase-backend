"""User-related routes."""

from fastapi import APIRouter, HTTPException, Request

from models.rest_api.clients import Clients
from models.rest_api.entitybase.handlers.user import UserHandler
from models.rest_api.entitybase.request.user import (
    UserCreateRequest,
    WatchlistToggleRequest,
)
from models.rest_api.entitybase.response.user import (
    WatchlistToggleResponse,
    UserCreateResponse,
)
from models.user import User
from models.validation.utils import raise_validation_error


users_router = APIRouter()


@users_router.post("/v1/users", response_model=UserCreateResponse)
def create_user(request: UserCreateRequest, req: Request) -> UserCreateResponse:
    """Create a new user."""
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = UserHandler()
    result = handler.create_user(request, clients.vitess)
    if not isinstance(result, UserCreateResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, UserCreateResponse)
    return result


@users_router.get("/v1/users/{user_id}", response_model=User)
def get_user(user_id: int, req: Request) -> User:
    """Get user information by MediaWiki user ID."""
    clients = req.app.state.clients
    handler = UserHandler()
    result = handler.get_user(user_id, clients.vitess)
    if not isinstance(result, User):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@users_router.put(
    "/v1/users/{user_id}/watchlist/toggle", response_model=WatchlistToggleResponse
)
def toggle_watchlist(
    user_id: int, request: WatchlistToggleRequest, req: Request
) -> WatchlistToggleResponse:
    """Enable or disable watchlist for user."""
    clients = req.app.state.clients
    handler = UserHandler()
    try:
        result = handler.toggle_watchlist(user_id, request, clients.vitess)
        if not isinstance(result, WatchlistToggleResponse):
            raise_validation_error("Invalid response type", status_code=500)
        assert isinstance(result, WatchlistToggleResponse)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
