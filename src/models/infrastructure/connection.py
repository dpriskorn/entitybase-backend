"""Abstract base classes for database and service connections."""

import abc
from abc import ABC
from typing import Any

from pydantic import BaseModel, ConfigDict

from models.infrastructure.config import Config


class ConnectionManager(ABC, BaseModel):
    """Abstract base class for managing connections to external services."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    config: Config

    @abc.abstractmethod
    def connect(self) -> Any:
        """Establish connection to the service."""
        pass

    @property
    def healthy_connection(self) -> bool:
        """Check if the connection to the service is healthy."""
        raise NotImplementedError()
