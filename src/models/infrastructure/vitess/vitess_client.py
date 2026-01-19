"""Vitess client for database operations."""

import json
import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Generator, Optional, cast

from pydantic import BaseModel, Field
from pymysql import Connection

from models.infrastructure.vitess.connection import VitessConnectionManager
from models.infrastructure.vitess.entities import IdResolver
from models.infrastructure.vitess.vitess_config import VitessConfig
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

from models.infrastructure.vitess.repositories.watchlist import WatchlistRepository
from models.rest_api.entitybase.response.entity import EntityHistoryEntry
from models.rest_api.entitybase.response.listings import EntityListing

logger = logging.getLogger(__name__)

from models.infrastructure.client import Client

if TYPE_CHECKING:
    from models.infrastructure.s3.s3_client import MyS3Client
    from models.infrastructure.vitess.vitess_config import VitessConfig
    from models.infrastructure.vitess.repositories.user import UserRepository
from models.infrastructure.vitess.schema import SchemaManager

from models.rest_api.entitybase.response import ProtectionResponse
from models.rest_api.entitybase.response import FullRevisionResponse
from models.rest_api.utils import raise_validation_error
from models.infrastructure.vitess.backlink_entry import BacklinkRecord


class Backlink(BaseModel):
    """Model for a backlink entry."""

    internal_id: int
    entity_id: str
    property_id: str
    statement_id: str


class VitessClient(Client):
    """Vitess database client for entity operations."""

    config: "VitessConfig"  # type: ignore[override]
    connection_manager: Optional[VitessConnectionManager] = Field(
        default=None, init=False, exclude=True
    )  # type: ignore[override]
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
        self._create_tables()

    @property
    def _connection_manager(self) -> VitessConnectionManager:
        """Get the connection manager, asserting it's not None."""
        assert self.connection_manager is not None
        return self.connection_manager

    @property
    def _user_repository(self) -> "UserRepository":
        """Get the user repository, lazy loading it if necessary."""
        if self.user_repository is None:
            import importlib
            user_repo_module = importlib.import_module('models.infrastructure.vitess.repositories.user')
            UserRepository = user_repo_module.UserRepository
            self.user_repository = UserRepository(self.connection_manager)
        return cast("UserRepository", self.user_repository)
