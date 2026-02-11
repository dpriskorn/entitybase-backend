"""User-related routes."""

from fastapi import APIRouter, HTTPException, Request, Query

from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.rest_api.entitybase.v1.handlers.user import UserHandler
from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler
from models.data.rest_api.v1.entitybase.request import (
    UserCreateRequest,
    WatchlistToggleRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    WatchlistToggleResponse,
    UserCreateResponse,
)
from models.data.rest_api.v1.entitybase.response import UserStatsResponse
from models.data.rest_api.v1.entitybase.response import UserResponse
from models.data.rest_api.v1.entitybase.response import (
    UserActivityResponse,
    GeneralStatsResponse,
)
from models.rest_api.utils import raise_validation_error


users_router = APIRouter(tags=["users"])


@users_router.post("/users", response_model=UserCreateResponse)
def create_user(request: UserCreateRequest, req: Request) -> UserCreateResponse:
    """Create a new user."""
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = UserHandler(state=state)
    try:
        result = handler.create_user(request)
        if not isinstance(result, UserCreateResponse):
            raise_validation_error("Invalid response type", status_code=500)
        assert isinstance(result, UserCreateResponse)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@users_router.get("/users/stat", response_model=UserStatsResponse)
def get_user_stats(req: Request) -> UserStatsResponse:
    """Get user statistics."""
    state = req.app.state.state_handler
    handler = UserHandler(state=state)
    try:
        stats = handler.get_user_stats()
        return stats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@users_router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, req: Request) -> UserResponse:
    """Get user information by MediaWiki user ID."""
    state = req.app.state.state_handler
    handler = UserHandler(state=state)
    try:
        result = handler.get_user(user_id)
        if not isinstance(result, UserResponse):
            raise_validation_error("Invalid response type", status_code=500)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@users_router.put(
    "/users/{user_id}/watchlist/toggle", response_model=WatchlistToggleResponse
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


@users_router.get("/users/{user_id}/activity", response_model=UserActivityResponse)
def get_user_activity(
    user_id: int,
    req: Request,
    activity_type: str | None = Query(None, alias="type", description="Activity type filter"),
    hours: int = Query(24, ge=1, description="Hours to look back"),
    limit: int = Query(50, ge=1, description="Max activities to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> UserActivityResponse:
    """Get user's activity with filtering."""
    state = req.app.state.state_handler
    handler = UserActivityHandler(state=state)
    try:
        return handler.get_user_activity(user_id, activity_type, hours, limit, offset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@users_router.get("/stats", response_model=GeneralStatsResponse)
def get_general_stats(req: Request) -> GeneralStatsResponse:
    """Get general wiki statistics."""
    state = req.app.state.state_handler
    handler = UserHandler(state=state)
    try:
        return handler.get_general_stats()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
