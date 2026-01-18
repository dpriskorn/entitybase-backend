"""Shared common models."""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class OperationResult(BaseModel, Generic[T]):
    """Model for operation results."""

    success: bool
    error: str = Field(default="")
    data: Optional[T] = Field(default=None)
