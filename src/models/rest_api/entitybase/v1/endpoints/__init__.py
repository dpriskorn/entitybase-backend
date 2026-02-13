"""Entitybase v1 API router."""

from fastapi import APIRouter

from . import (
    admin,
    entities,
    entities_aliases,
    entities_descriptions,
    entities_labels,
    items,
    lexemes,
    properties,
    property_hashes,
    redirects,
    statements,
    stats,
    watchlist,
)

# Import the json_import module using importlib to avoid keyword conflict
import importlib

json_import = importlib.import_module(
    ".import", package="models.rest_api.entitybase.v1.endpoints"
)


v1_router = APIRouter()

# Include sub-routers
v1_router.include_router(entities.router, tags=["entities"])
v1_router.include_router(entities_labels.router, tags=["entities"])
v1_router.include_router(entities_descriptions.router, tags=["entities"])
v1_router.include_router(entities_aliases.router, tags=["entities"])
v1_router.include_router(items.router, tags=["items"])
v1_router.include_router(lexemes.router, tags=["lexemes"])
v1_router.include_router(properties.router, tags=["properties"])
v1_router.include_router(statements.router, tags=["statements"])
v1_router.include_router(admin.admin_router, tags=["list"])
v1_router.include_router(redirects.redirects_router, tags=["redirects"])
v1_router.include_router(watchlist.watchlist_router, tags=["watchlist"])
v1_router.include_router(stats.stats_router, tags=["statistics"])
v1_router.include_router(property_hashes.property_hashes_router, tags=["properties"])
v1_router.include_router(json_import.import_router, tags=["import"])
