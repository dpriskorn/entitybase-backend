"""Entitybase v1 API router."""

from fastapi import APIRouter

from . import (
    admin,
    entities,
    items,
    lexemes,
    properties,
    qualifiers,
    redirects,
    references,
    statements,
    sync,
)


v1_router = APIRouter()

# Include sub-routers
v1_router.include_router(entities.router, tags=["entities"])
v1_router.include_router(items.router, tags=["items"])
v1_router.include_router(lexemes.router, tags=["lexeme"])
v1_router.include_router(properties.router, tags=["properties"])
v1_router.include_router(statements.router, tags=["statements"])
v1_router.include_router(admin.admin_router, tags=["list"])
v1_router.include_router(qualifiers.qualifiers_router, tags=["qualifiers"])
v1_router.include_router(references.references_router, tags=["references"])
v1_router.include_router(redirects.redirects_router, tags=["redirects"])
v1_router.include_router(sync.sync_router, tags=["sync"])
