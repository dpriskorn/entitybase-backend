from fastapi import APIRouter

from . import entities, health, items, lexemes, properties, statements

v1_router = APIRouter()

# Include sub-routers
v1_router.include_router(entities.router, tags=["entities"])
v1_router.include_router(health.router, tags=["health"])
v1_router.include_router(items.router, tags=["items"])
v1_router.include_router(lexemes.router, tags=["lexemes"])
v1_router.include_router(properties.router, tags=["properties"])
v1_router.include_router(statements.router, tags=["statements"])
