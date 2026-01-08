import abc
from abc import ABC
from typing import Any

from pydantic import BaseModel, ConfigDict

from models.infrastructure.config import Config


class ConnectionManager(ABC, BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    config: Config

    @abc.abstractmethod
    def connect(self) -> Any:
        pass

    @property
    def healthy_connection(self) -> bool:
        raise NotImplementedError()
