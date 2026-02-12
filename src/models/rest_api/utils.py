"""Validation utilities for REST API."""

import logging
from typing import NoReturn

logger = logging.getLogger(__name__)


def raise_validation_error(
    message: str,
    status_code: int = 400,
) -> NoReturn:
    """Raise HTTPException for validation errors.

    Always raises HTTPException regardless of environment for consistent
    HTTP error responses.

    NOTE: Always use this function instead of raising ValidationError directly
    to ensure proper HTTP error handling for user responses.
    """
    logger.info(f"Raising validation error: {message} with status {status_code}")
    from fastapi import HTTPException

    raise HTTPException(status_code=status_code, detail=message)
