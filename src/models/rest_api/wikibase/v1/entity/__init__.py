"""Entity operations router for Wikibase v1 API."""

from .general import router as general_router
from .items import router as items_router
from .properties import router as properties_router
from .lexemes import router as lexemes_router


__all__ = ["general_router", "items_router", "properties_router", "lexemes_router"]
