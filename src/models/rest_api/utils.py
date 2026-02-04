"""Validation utilities for REST API."""

import logging

from typing import NoReturn, Optional

logger = logging.getLogger(__name__)


def raise_validation_error(
    message: str,
    status_code: int = 400,
    exception_class: Optional[type[Exception]] = None,
) -> NoReturn:
    """Raise exception based on ENVIRONMENT and optional exception_class.

    HTTPException is only raised in production when explicitly requested.
    In development, HTTPException requests fall back to ValueError.

    NOTE: Always use this function instead of raising ValidationError directly
    to ensure proper HTTP error handling for user responses.
    """
    from models.config.settings import settings
    logger.info(f"Raising validation error: {message} with status {status_code}")
    from fastapi import HTTPException

    is_prod = settings.environment.lower() == "prod"

    if exception_class is not None:
        if exception_class == HTTPException and is_prod:
            raise HTTPException(status_code=status_code, detail=message)
        else:
            # In dev, or if not HTTPException, raise the specified exception
            raise exception_class(message)
    elif is_prod:
        raise HTTPException(status_code=status_code, detail=message)
    else:
        raise ValueError(message)
