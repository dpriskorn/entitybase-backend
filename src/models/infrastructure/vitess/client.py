"""Vitess client for database operations."""

import logging
from typing import Any
from typing import TYPE_CHECKING, Optional

from pydantic import Field, BaseModel

from models.infrastructure.vitess.connection import VitessConnectionManager
from models.infrastructure.vitess.id_resolver import IdResolver
from models.infrastructure.vitess.repositories.schema import SchemaRepository
from models.rest_api.state import State

if TYPE_CHECKING:
    from models.infrastructure.vitess.config import VitessConfig

logger = logging.getLogger(__name__)


class VitessClient(BaseModel):
    """Vitess database client for entity operations."""
    state: State
    connection_manager: Optional[VitessConnectionManager] = Field(
        default=None, init=False, exclude=True
    )
    id_resolver: Optional[IdResolver] = Field(default=None, init=False, exclude=True)

    def __init__(self, state: State, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        logger.debug(f"Initializing VitessClient with host {self.state.host}")
        self.connection_manager = VitessConnectionManager(config=self.config)
        self.id_resolver = IdResolver(vitess_client=self)

        # Repositories
        schema_repository: SchemaRepository = SchemaRepository()
        schema_repository.create_tables()

    @property
    def cursor(self) -> Any:
        return self.connection_manager.connection.cursor()


# Import UserRepository for model_rebuild to resolve forward references
VitessClient.model_rebuild()
