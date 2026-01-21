from models.infrastructure.vitess.client import VitessClient


class Repository(VitessClient):
    model_config = {"arbitrary_types_allowed": True}
