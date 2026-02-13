"""Routes package."""

from typing import TYPE_CHECKING

from . import (
    batch,
    endorsements,
    entities,
    health,
    resolve,
    thanks,
    users,
)

if TYPE_CHECKING:
    from fastapi import FastAPI


def include_routes(app: "FastAPI") -> None:
    """Include all route routers in the app."""
    from models.config.settings import settings

    app.include_router(health.health_router)
    app.include_router(users.users_router, prefix=settings.api_prefix)
    app.include_router(thanks.thanks_router, prefix=settings.api_prefix)
    app.include_router(endorsements.endorsements_router, prefix=settings.api_prefix)
    app.include_router(entities.entities_router, prefix=settings.api_prefix)
    app.include_router(resolve.resolve_router, prefix=settings.api_prefix)
    # v1 routes are added via imports above
