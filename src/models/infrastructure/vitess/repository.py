from pydantic import BaseModel, Field

from models.infrastructure.vitess.client import VitessClient
from models.infrastructure.vitess.config import VitessConfig


class Repository(BaseModel):
    # model_config = {"arbitrary_types_allowed": True}
    # This is needed for all repositories
    config: VitessConfig | None = None
    vitess_client: VitessClient = Field(init=False)

    def model_post_init(self, context):
        self.vitess_client = VitessClient(config=self.config)

