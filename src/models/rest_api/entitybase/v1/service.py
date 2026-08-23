from abc import ABC
from typing import Any

from pydantic import BaseModel


class Service(ABC, BaseModel):
    state: Any  # this is the app state

    @property
    def db_client(self) -> Any:
        return self.state.db_client
