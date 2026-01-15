"""Validation utilities for REST API."""

import logging
import os

from typing import NoReturn, Optional

logger = logging.getLogger(__name__)


def raise_validation_error(
    message: str,
    status_code: int = 400,
    exception_class: Optional[type[Exception]] = None,
) -> NoReturn:
    """Raise exception for validation errors."""
    logger.info(f"Raising validation error: {message} with status {status_code}")
    from fastapi import HTTPException

    raise HTTPException(status_code=status_code, detail=message)
