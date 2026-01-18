"""Routes package."""

from . import (
    admin,
    batch,
    endorsements,
    entities,
    health,
    redirects,
    references,
    sync,
    thanks,
    users,
    v1_entities,
)


def include_routes(app) -> None:
    """Include all route routers in the app."""
    app.include_router(health.health_router)
    app.include_router(users.users_router)
    app.include_router(thanks.thanks_router)
    app.include_router(endorsements.endorsements_router)
    app.include_router(entities.entities_router)
    app.include_router(redirects.redirects_router)
    app.include_router(references.references_router)
    app.include_router(admin.admin_router)
    app.include_router(sync.sync_router)
    # v1 routes are added via imports above
