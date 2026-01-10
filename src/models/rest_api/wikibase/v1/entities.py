from fastapi import APIRouter

from .entity import general_router, items_router, properties_router, lexemes_router

router = APIRouter()

# Include sub-routers for different entity types
router.include_router(general_router)
router.include_router(items_router)
router.include_router(properties_router)
router.include_router(lexemes_router)
