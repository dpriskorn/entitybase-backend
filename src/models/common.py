"""Shared common models."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class OperationResult(BaseModel):
    """Model for operation results."""

    success: bool
    error: str = Field(default="")
    data: Optional[Any] = Field(default=None)
