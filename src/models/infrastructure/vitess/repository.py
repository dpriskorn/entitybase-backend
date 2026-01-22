from typing import Any

from pydantic import BaseModel, ConfigDict


class Repository(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # This is needed for all repositories
    vitess_client: Any
