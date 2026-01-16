"""REST API for Wikibase backend."""

from .main import app
from .entitybase import handlers

__all__ = ["app", "handlers"]
