from abc import ABC

from pydantic import BaseModel, ConfigDict, Field

from models.infrastructure.config import Config
from models.infrastructure.connection import ConnectionManager


class Client(ABC, BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    config: Config
    connection_manager: ConnectionManager = Field(default=None, exclude=True)

    @property
    def healthy_connection(self) -> bool:
        """Helper method"""
        if not self.connection_manager:
            raise ConnectionError()
        return bool(self.connection_manager.healthy_connection)
