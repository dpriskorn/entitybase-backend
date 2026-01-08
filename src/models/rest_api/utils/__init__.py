"""Utility functions for entity API."""

import logging

from fastapi import HTTPException

from models.config.settings import settings

logger = logging.getLogger(__name__)


def raise_or_convert_to_500(e: Exception, detail: str) -> None:
    """Raise original exception if expose_original_exceptions is True, otherwise raise HTTPException 500.

    Args:
        e: The original exception
        detail: The detail message for HTTPException if converting
    """
    if settings.expose_original_exceptions:
        raise e
    raise HTTPException(status_code=500, detail=detail)
