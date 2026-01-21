"""User-related routes."""

from fastapi import APIRouter, HTTPException, Request

from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.rest_api.entitybase.v1.handlers.user import UserHandler
from models.rest_api.entitybase.v1.request.user import (
    UserCreateRequest,
    WatchlistToggleRequest,
)
from models.rest_api.entitybase.v1.response.user import (
    WatchlistToggleResponse,
    UserCreateResponse,
)
from models.rest_api.entitybase.v1.response.misc import UserStatsResponse
from models.rest_api.entitybase.v1.response.user import UserResponse
from models.rest_api.utils import raise_validation_error


users_router = APIRouter(prefix="/entitybase", tags=["users"])


@users_router.post("/entitybase/v1/users", response_model=UserCreateResponse)
def create_user(request: UserCreateRequest, req: Request) -> UserCreateResponse:
    """Create a new user."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = UserHandler(state=state)
    result = handler.create_user(request)
    if not isinstance(result, UserCreateResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, UserCreateResponse)
    return result


@users_router.get("/entitybase/v1/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, req: Request) -> UserResponse:
    """Get user information by MediaWiki user ID."""
    state = req.app.state.state_handler
    handler = UserHandler(state=state)
    result = handler.get_user(user_id)
    if not isinstance(result, UserResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@users_router.put(
    "/v1/users/{user_id}/watchlist/toggle", response_model=WatchlistToggleResponse
)
def toggle_watchlist(
    user_id: int, request: WatchlistToggleRequest, req: Request
) -> WatchlistToggleResponse:
    """Enable or disable watchlist for user."""
    state = req.app.state.state_handler
    handler = UserHandler(state=state)
    try:
        result = handler.toggle_watchlist(user_id, request)
        if not isinstance(result, WatchlistToggleResponse):
            raise_validation_error("Invalid response type", status_code=500)
        assert isinstance(result, WatchlistToggleResponse)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@users_router.get("/entitybase/v1/users/stat", response_model=UserStatsResponse)
def get_user_stats(req: Request) -> UserStatsResponse:
    """Get user statistics."""
    state = req.app.state.state_handler
    handler = UserHandler(state=state)
    try:
        stats = handler.get_user_stats()
        return stats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
