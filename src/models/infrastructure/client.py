"""Base client classes for external service connections."""

from abc import ABC
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from models.rest_api.utils import raise_validation_error

from models.infrastructure.config import Config
from models.infrastructure.connection import ConnectionManager


class Client(ABC, BaseModel):
    """Abstract base class for service clients."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    config: Config
    connection_manager: Optional[ConnectionManager] = Field(
        default=None, init=False, exclude=True
    )

    @property
    def healthy_connection(self) -> bool:
        """Check if the client has a healthy connection."""
        if not self.connection_manager:
            raise_validation_error("Service unavailable", status_code=503)
        return bool(self.connection_manager.healthy_connection)
