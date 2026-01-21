from pydantic import BaseModel

from models.infrastructure.vitess.client import VitessClient


class Repository(BaseModel):
    # model_config = {"arbitrary_types_allowed": True}
    # This is needed for all repositories
    vitess_client: VitessClient

