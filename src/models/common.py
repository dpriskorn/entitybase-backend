"""Shared common models."""

import logging
import os
from typing import Generic, NoReturn, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


def raise_validation_error(
    message: str,
    status_code: int = 400,
    exception_class: Optional[type[Exception]] = Field(default=None),
) -> NoReturn:
    """Raise exception based on ENVIRONMENT and optional exception_class.

    HTTPException is only raised in production when explicitly requested.
    In development, HTTPException requests fall back to ValueError.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Raising validation error: {message} with status {status_code}")
    from fastapi import HTTPException

    is_prod = os.getenv("ENVIRONMENT", "dev").lower() == "prod"

    if exception_class is not None:
        if exception_class == HTTPException and is_prod:
            raise HTTPException(status_code=status_code, detail=message)
        else:
            # In dev, or if not HTTPException, raise the specified exception
            raise exception_class(message)
    else:
        # Default behavior
        if is_prod:
            raise HTTPException(status_code=status_code, detail=message)
        else:
            raise ValueError(message)


class OperationResult(BaseModel, Generic[T]):
    """Model for operation results."""

    success: bool
    error: str = Field(default="")
    data: Optional[T] = Field(default=None)
