"""Vitess client for database operations."""

import logging
from typing import Any
from typing import Optional

from pydantic import Field

from models.infrastructure.client import Client
from models.infrastructure.vitess.config import VitessConfig
from models.infrastructure.vitess.connection import VitessConnectionManager
from models.infrastructure.vitess.id_resolver import IdResolver

logger = logging.getLogger(__name__)


class VitessClient(Client):
    """Vitess database client for entity operations."""

    connection_manager: Optional[VitessConnectionManager] = Field(
        default=None, init=False, exclude=True
    )
    id_resolver: Optional[IdResolver] = Field(default=None, init=False, exclude=True)
    config: VitessConfig

    def model_post_init(self, context) -> None:
        logger.debug(f"Initializing VitessClient with host {self.config.host}")
        self.connection_manager = VitessConnectionManager(config=self.config)
        self.id_resolver = IdResolver(vitess_client=self)
        # self.create_tables()

    @property
    def cursor(self) -> Any:
        if self.connection_manager.connection is None:
            self.connection_manager.connect()
        return self.connection_manager.connection.cursor()

    @property
    def entity_repository(self) -> Any:
        """Get entity repository."""
        from models.infrastructure.vitess.repositories.entity import EntityRepository
        return EntityRepository(config=self.config)

    @property
    def revision_repository(self) -> Any:
        """Get revision repository."""
        from models.infrastructure.vitess.repositories.revision import RevisionRepository
        return RevisionRepository(config=self.config)

    @property
    def head_repository(self) -> Any:
        """Get head repository."""
        from models.infrastructure.vitess.repositories.head import HeadRepository
        return HeadRepository(config=self.config)

    @property
    def user_repository(self) -> Any:
        """Get user repository."""
        from models.infrastructure.vitess.repositories.user import UserRepository
        return UserRepository(config=self.config)

    @property
    def watchlist_repository(self) -> Any:
        """Get watchlist repository."""
        from models.infrastructure.vitess.repositories.watchlist import WatchlistRepository
        return WatchlistRepository(config=self.config)

    @property
    def endorsement_repository(self) -> Any:
        """Get endorsement repository."""
        from models.infrastructure.vitess.repositories.endorsement import EndorsementRepository
        return EndorsementRepository(config=self.config)

    @property
    def thanks_repository(self) -> Any:
        """Get thanks repository."""
        from models.infrastructure.vitess.repositories.thanks import ThanksRepository
        return ThanksRepository(config=self.config)

    def create_tables(self) -> None:
        from models.infrastructure.vitess.repositories.schema import SchemaRepository

        schema_repository: SchemaRepository = SchemaRepository(vitess_client=self)
        schema_repository.create_tables()


# Import UserRepository for model_rebuild to resolve forward references
VitessClient.model_rebuild()
