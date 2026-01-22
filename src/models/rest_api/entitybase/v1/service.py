from abc import ABC
from typing import Any

from pydantic import BaseModel


class Service(ABC, BaseModel):
    state: Any  # this is the app state

    @property
    def vitess_client(self):
        return self.state.vitess_client
