from models.infrastructure.vitess.client import VitessClient


class Repository(VitessClient):
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self) -> None:
        super().__init__()