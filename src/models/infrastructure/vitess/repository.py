from models.infrastructure.vitess.client import VitessClient
from models.infrastructure.vitess.config import VitessConfig


class Repository(VitessClient):
    model_config = {"arbitrary_types_allowed": True}