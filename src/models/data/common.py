"""Shared common models."""

import logging
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
T = TypeVar("T")


class OperationResult(BaseModel, Generic[T]):
    """Model for operation results."""

    model_config = {"extra": "forbid"}

    success: bool
    error: str = Field(default="")
    data: Optional[T] = Field(default=None)

    def get_data(self) -> T:
        """Return data, assuming success has been checked.

        Use this after checking .success to get properly typed data.
        """
        if self.data is None:
            msg = "Data is None"
            raise ValueError(msg)
        return self.data
