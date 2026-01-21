from pydantic import BaseModel

from models.infrastructure.vitess.client import VitessClient


class Repository(BaseModel):
    # This is needed for all repositories
    vitess_client: VitessClient
