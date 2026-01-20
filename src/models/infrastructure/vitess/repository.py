from models.infrastructure.vitess.client import VitessClient
from models.infrastructure.vitess.config import VitessConfig


class Repository(VitessClient):
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, config: VitessConfig = None) -> None:
        super().__init__(config=config)