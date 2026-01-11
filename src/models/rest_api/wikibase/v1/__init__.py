"""Wikibase v1 API router."""

from fastapi import APIRouter

from . import entities


wikibase_v1_router = APIRouter()

# Include sub-routers
wikibase_v1_router.include_router(entities.router, tags=["wikibase-entities"])
