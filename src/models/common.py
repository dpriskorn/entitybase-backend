"""Shared common models."""

from typing import Optional

from pydantic import BaseModel, Field


class OperationResult(BaseModel):
    """Model for operation results."""

    success: bool
    error: Optional[str] = Field(default=None)
