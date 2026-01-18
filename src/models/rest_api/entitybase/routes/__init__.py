"""Routes package."""

from typing import TYPE_CHECKING

from . import (
    batch,
    endorsements,
    entities,
    health,
    thanks,
    users,
    watchlist,
)

if TYPE_CHECKING:
    from fastapi import FastAPI


def include_routes(app: "FastAPI") -> None:
    """Include all route routers in the app."""
    app.include_router(health.health_router)
    app.include_router(users.users_router)
    app.include_router(thanks.thanks_router)
    app.include_router(endorsements.endorsements_router)
    app.include_router(entities.entities_router)
    app.include_router(watchlist.watchlist_router)
    # v1 routes are added via imports above
