"""Shared common models."""

import logging
from typing import Annotated, Generic, NoReturn, Optional, TypeVar

from fastapi import Header
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
T = TypeVar("T")


class EditHeaders(BaseModel):
    """Model for required editing headers (X-User-ID and X-Edit-Summary)."""
    
    x_user_id: int = Field(..., alias="X-User-ID", ge=0, description="User ID making the edit")
    x_edit_summary: str = Field(..., alias="X-Edit-Summary", min_length=1, max_length=200, description="Edit summary")
    
    model_config = {"populate_by_name": True}


EditHeadersType = Annotated[EditHeaders, Header(convert_underscores=False)]


def raise_validation_error(
    message: str,
    status_code: int = 400,
    exception_class: type[Exception] | None = Field(default=None),
) -> NoReturn:
    """Raise exception based on ENVIRONMENT and optional exception_class.

    HTTPException is only raised in production when explicitly requested.
    In development, HTTPException requests fall back to ValueError.
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
    # Default behavior
    elif is_prod:
        raise HTTPException(status_code=status_code, detail=message)
    else:
        raise ValueError(message)


class OperationResult(BaseModel, Generic[T]):
    """Model for operation results."""

    success: bool
    error: str = Field(default="")
    data: Optional[T] = Field(default=None)
