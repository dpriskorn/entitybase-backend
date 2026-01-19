"""Vitess client for database operations."""

import logging
from typing import Any, Optional
from typing import TYPE_CHECKING

from pydantic import Field

from models.infrastructure.vitess.connection import VitessConnectionManager
from models.infrastructure.vitess.entities import IdResolver
from models.infrastructure.vitess.repositories.backlink import BacklinkRepository
from models.infrastructure.vitess.repositories.endorsement import EndorsementRepository
from models.infrastructure.vitess.repositories.entity import EntityRepository
from models.infrastructure.vitess.repositories.head import HeadRepository
from models.infrastructure.vitess.repositories.listing import ListingRepository
from models.infrastructure.vitess.repositories.metadata import MetadataRepository
from models.infrastructure.vitess.repositories.redirect import RedirectRepository
from models.infrastructure.vitess.repositories.revision import RevisionRepository
from models.infrastructure.vitess.repositories.statement import StatementRepository
from models.infrastructure.vitess.repositories.thanks import ThanksRepository
from models.infrastructure.vitess.repositories.user import UserRepository
from models.infrastructure.vitess.repositories.watchlist import WatchlistRepository

if TYPE_CHECKING:
    pass
from models.infrastructure.vitess.vitess_config import VitessConfig

logger = logging.getLogger(__name__)

from models.infrastructure.client import Client

if TYPE_CHECKING:
    from models.infrastructure.vitess.vitess_config import VitessConfig
from models.infrastructure.vitess.schema import SchemaManager


class VitessClient(Client):
    """Vitess database client for entity operations."""

    config: "VitessConfig"  # type: ignore[override]
    connection_manager: Optional[VitessConnectionManager] = Field(default=None, init=False, exclude=True)
    schema_manager: Optional[SchemaManager] = Field(
        default=None, init=False, exclude=True
    )
    id_resolver: Optional[IdResolver] = Field(default=None, init=False, exclude=True)
    entity_repository: Optional[EntityRepository] = Field(
        default=None, init=False, exclude=True
    )
    revision_repository: Optional[RevisionRepository] = Field(
        default=None, init=False, exclude=True
    )
    redirect_repository: Optional[RedirectRepository] = Field(
        default=None, init=False, exclude=True
    )
    head_repository: Optional[HeadRepository] = Field(
        default=None, init=False, exclude=True
    )
    listing_repository: Optional[ListingRepository] = Field(
        default=None, init=False, exclude=True
    )
    statement_repository: Optional[StatementRepository] = Field(
        default=None, init=False, exclude=True
    )
    backlink_repository: Optional[BacklinkRepository] = Field(
        default=None, init=False, exclude=True
    )
    user_repository: Optional["UserRepository"] = Field(
        default=None, init=False, exclude=True
    )
    metadata_repository: Optional[MetadataRepository] = Field(
        default=None, init=False, exclude=True
    )
    watchlist_repository: Optional[WatchlistRepository] = Field(
        default=None, init=False, exclude=True
    )
    thanks_repository: Optional["ThanksRepository"] = Field(
        default=None, init=False, exclude=True
    )
    endorsement_repository: Optional["EndorsementRepository"] = Field(
        default=None, init=False, exclude=True
    )

    def __init__(self, config: VitessConfig, **kwargs: Any) -> None:
        super().__init__(config=config, **kwargs)
        logger.debug(f"Initializing VitessClient with host {config.host}")
        self.connection_manager = VitessConnectionManager(config=config)  # type: ignore[assignment]
        self.schema_manager = SchemaManager(self.connection_manager)
        self.id_resolver = IdResolver(self.connection_manager)
        self.entity_repository = EntityRepository(
            self.connection_manager, self.id_resolver
        )
        self.revision_repository = RevisionRepository(
            self.connection_manager, self.id_resolver
        )
        self.redirect_repository = RedirectRepository(
            self.connection_manager, self.id_resolver
        )
        self.head_repository = HeadRepository(self.connection_manager, self.id_resolver)
        self.listing_repository = ListingRepository(self.connection_manager)
        self.statement_repository = StatementRepository(self.connection_manager)
        self.backlink_repository = BacklinkRepository(self.connection_manager)
        self.metadata_repository = MetadataRepository(self.connection_manager)
        # user_repository is lazy loaded
        self.watchlist_repository = WatchlistRepository(
            self.connection_manager, self.id_resolver
        )
        self.thanks_repository = ThanksRepository(
            self.connection_manager, self.id_resolver
        )
        self.endorsement_repository = EndorsementRepository(self.connection_manager)
        self.schema_manager.create_tables()

    @property
    def _connection_manager(self) -> VitessConnectionManager:
        """Get the connection manager, asserting it's not None."""
        assert self.connection_manager is not None
        return self.connection_manager

    @property
    def _user_repository(self) -> "UserRepository":
        """Get the user repository, lazy loading it if necessary."""
        if self.user_repository is None:
            from models.infrastructure.vitess.repositories.user import UserRepository

            self.user_repository = UserRepository(self.connection_manager)
        assert self.user_repository is not None
        return self.user_repository

    def update_head_revision(self, entity_id: str, revision_id: int) -> None:
        """Update the head revision for an entity."""
        with self.connection_manager.get_connection() as conn:  # type: ignore
            self.entity_repository.update_head_revision(conn, entity_id, revision_id)  # type: ignore


# Import UserRepository for model_rebuild to resolve forward references
VitessClient.model_rebuild()
