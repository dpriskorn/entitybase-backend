"""Watchlist routes."""

from fastapi import APIRouter, HTTPException, Request, Query

from models.rest_api.entitybase.handlers.watchlist import WatchlistHandler
from models.rest_api.entitybase.request.user import (
    WatchlistAddRequest,
    WatchlistRemoveRequest,
    MarkCheckedRequest,
)
from models.rest_api.entitybase.response.misc import WatchCounts
from models.rest_api.entitybase.response.user import (
    MessageResponse,
    NotificationResponse,
    WatchlistResponse,
)
from models.rest_api.utils import raise_validation_error

watchlist_router = APIRouter(tags=["watchlist"])


@watchlist_router.post("/users/{user_id}/watchlist", response_model=MessageResponse)
def add_watch(
    user_id: int, request: WatchlistAddRequest, req: Request
) -> MessageResponse:
    """Add a watchlist entry for user."""
    clients = req.app.state.clients
    handler = WatchlistHandler()
    try:
        request.user_id = user_id  # Override to ensure consistency
        result = handler.add_watch(request, clients.vitess)
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
    clients = req.app.state.clients
    handler = WatchlistHandler()
    try:
        request.user_id = user_id  # Override to ensure consistency
        result = handler.remove_watch(request, clients.vitess)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@watchlist_router.get("/users/{user_id}/watchlist", response_model=WatchlistResponse)
def get_watches(user_id: int, req: Request) -> WatchlistResponse:
    """Get user's watchlist."""
    clients = req.app.state.clients
    handler = WatchlistHandler()
    try:
        result = handler.get_watches(user_id, clients.vitess)
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
    clients = req.app.state.clients
    handler = WatchlistHandler()
    try:
        result = handler.get_notifications(
            user_id, clients.vitess, hours, limit, offset
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@watchlist_router.put(
    "/users/{user_id}/watchlist/notifications/{notification_id}/check",
    response_model=MessageResponse,
)
def mark_checked(user_id: int, notification_id: int, req: Request) -> MessageResponse:
    """Mark a notification as checked."""
    clients = req.app.state.clients
    handler = WatchlistHandler()
    try:
        request = MarkCheckedRequest(notification_id=notification_id)
        result = handler.mark_checked(user_id, request, clients.vitess)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@watchlist_router.get("/users/{user_id}/watchlist/stats", response_model=WatchCounts)
def get_watch_counts(user_id: int, req: Request) -> WatchCounts:
    """Get user's watchlist statistics."""
    clients = req.app.state.clients
    handler = WatchlistHandler()
    try:
        result = handler.get_watch_counts(user_id, clients.vitess)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
