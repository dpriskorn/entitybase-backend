"""Entitybase v1 API router."""

from fastapi import APIRouter

from . import (
    admin,
    entities,
    items,
    lexemes,
    properties,
    property_hashes,
    qualifiers,
    redirects,
    references,
    statements,
    watchlist,
)


v1_router = APIRouter()

# Include sub-routers
v1_router.include_router(entities.router, tags=["entities"])
v1_router.include_router(items.router, tags=["items"])
v1_router.include_router(lexemes.router, tags=["lexeme"])
v1_router.include_router(properties.router, tags=["properties"])
v1_router.include_router(statements.router, tags=["statements"])
v1_router.include_router(admin.admin_router, tags=["list"])
v1_router.include_router(qualifiers.qualifiers_router, tags=["statements"])
v1_router.include_router(references.references_router, tags=["statements"])
v1_router.include_router(redirects.redirects_router, tags=["redirects"])
v1_router.include_router(watchlist.watchlist_router, tags=["watchlist"])
v1_router.include_router(property_hashes.property_hashes_router, tags=["properties"])
