"""Vitess client for database operations."""

import logging
from typing import Any
from typing import TYPE_CHECKING, Optional

from pydantic import Field, BaseModel

from models.infrastructure.vitess.connection import VitessConnectionManager
from models.infrastructure.vitess.id_resolver import IdResolver

from models.infrastructure.vitess.config import VitessConfig

logger = logging.getLogger(__name__)


class VitessClient(BaseModel):
    """Vitess database client for entity operations."""
    connection_manager: Optional[VitessConnectionManager] = Field(
        default=None, init=False, exclude=True
    )
    id_resolver: Optional[IdResolver] = Field(default=None, init=False, exclude=True)
    config: VitessConfig

    def __init__(self, config: VitessConfig, **kwargs: Any) -> None:
        super().__init__(config=config, **kwargs)
        logger.debug(f"Initializing VitessClient with host {config.host}")
        self.connection_manager = VitessConnectionManager(config=self.config)
        self.id_resolver = IdResolver(vitess_client=self)

        # Repositories
        from models.infrastructure.vitess.repositories.schema import SchemaRepository
        schema_repository: SchemaRepository = SchemaRepository(config=config)
        schema_repository.create_tables()

    @property
    def cursor(self) -> Any:
        return self.connection_manager.connection.cursor()


# Import UserRepository for model_rebuild to resolve forward references
VitessClient.model_rebuild()
