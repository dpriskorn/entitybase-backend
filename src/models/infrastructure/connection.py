import abc
from abc import ABC
from typing import Any

from pydantic import BaseModel

from models.infrastructure.config import Config


class ConnectionManager(ABC, BaseModel):
    config: Config

    @abc.abstractmethod
    def connect(self) -> Any:
        pass

    @abc.abstractmethod
    def healthy_connection(self) -> bool:
        pass
