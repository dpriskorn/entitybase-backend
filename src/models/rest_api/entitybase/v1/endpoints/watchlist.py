"""Watchlist routes."""

from fastapi import APIRouter, HTTPException, Request, Query

from models.rest_api.entitybase.v1.handlers.watchlist import WatchlistHandler
from models.data.rest_api.v1.request import (
    WatchlistAddRequest,
    WatchlistRemoveRequest,
    MarkCheckedRequest,
)
from models.data.rest_api.v1.response import WatchCounts
from models.data.rest_api.v1.response import (
    MessageResponse,
    NotificationResponse,
)
from models.data.rest_api.v1.response import WatchlistResponse

watchlist_router = APIRouter(tags=["watchlist"])


@watchlist_router.post("/users/{user_id}/watchlist", response_model=MessageResponse)
def add_watch(
    user_id: int, request: WatchlistAddRequest, req: Request
) -> MessageResponse:
    """Add a watchlist entry for user."""
    state = req.app.state.state_handler
    handler = WatchlistHandler(state=state)
    try:
        request.user_id = user_id  # Override to ensure consistency
        result = handler.add_watch(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@watchlist_router.post(
    "/users/{user_id}/watchlist/remove", response_model=MessageResponse
)
def remove_watch(
    user_id: int, request: WatchlistRemoveRequest, req: Request
) -> MessageResponse:
    """Remove a watchlist entry for user."""
    state = req.app.state.state_handler
    handler = WatchlistHandler(state=state)
    try:
        request.user_id = user_id  # Override to ensure consistency
        result = handler.remove_watch(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@watchlist_router.delete(
    "/users/{user_id}/watchlist/{watch_id}", response_model=MessageResponse
)
def remove_watch_by_id(watch_id: int, req: Request) -> MessageResponse:
    """Remove a watchlist entry by ID."""
    state = req.app.state.state_handler
    handler = WatchlistHandler(state=state)
    try:
        result = handler.remove_watch_by_id(watch_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@watchlist_router.get("/users/{user_id}/watchlist", response_model=WatchlistResponse)
def get_watches(user_id: int, req: Request) -> WatchlistResponse:
    """Get user's watchlist."""
    state = req.app.state.state_handler
    handler = WatchlistHandler(state=state)
    try:
        result = handler.get_watches(user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@watchlist_router.get(
    "/users/{user_id}/watchlist/notifications", response_model=NotificationResponse
)
def get_notifications(
    user_id: int,
    req: Request,
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(50, ge=1, le=100, description="Max notifications to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> NotificationResponse:
    """Get user's recent watchlist notifications."""
    state = req.app.state.state_handler
    handler = WatchlistHandler(state=state)
    try:
        result = handler.get_notifications(user_id, hours, limit, offset)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@watchlist_router.put(
    "/users/{user_id}/watchlist/notifications/{notification_id}/check",
    response_model=MessageResponse,
)
def mark_checked(user_id: int, notification_id: int, req: Request) -> MessageResponse:
    """Mark a notification as checked."""
    state = req.app.state.state_handler
    handler = WatchlistHandler(state=state)
    try:
        request = MarkCheckedRequest(notification_id=notification_id)
        result = handler.mark_checked(user_id, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@watchlist_router.get("/users/{user_id}/watchlist/stats", response_model=WatchCounts)
def get_watch_counts(user_id: int, req: Request) -> WatchCounts:
    """Get user's watchlist statistics."""
    state = req.app.state.state_handler
    handler = WatchlistHandler(state=state)
    try:
        result = handler.get_watch_counts(user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
