"""Vitess client for database operations."""

import logging
from typing import Any, cast
from typing import Optional

from pydantic import Field

from models.infrastructure.client import Client
from models.data.config.vitess import VitessConfig
from models.infrastructure.s3.revision.revision_data import RevisionData
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

    def model_post_init(self, context: Any) -> None:
        logger.debug(f"Initializing VitessClient with host='{self.config.host}', port={self.config.port}, database='{self.config.database}', user='{self.config.user}', password_length={len(self.config.password)}")
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
        return EntityRepository(vitess_client=self)

    @property
    def revision_repository(self) -> Any:
        """Get revision repository."""
        from models.infrastructure.vitess.repositories.revision import RevisionRepository
        return RevisionRepository(vitess_client=self)

    @property
    def head_repository(self) -> Any:
        """Get head repository."""
        from models.infrastructure.vitess.repositories.head import HeadRepository
        return HeadRepository(vitess_client=self)

    @property
    def user_repository(self) -> Any:
        """Get user repository."""
        from models.infrastructure.vitess.repositories.user import UserRepository
        return UserRepository(vitess_client=self)

    @property
    def watchlist_repository(self) -> Any:
        """Get watchlist repository."""
        from models.infrastructure.vitess.repositories.watchlist import WatchlistRepository
        return WatchlistRepository(vitess_client=self)

    @property
    def endorsement_repository(self) -> Any:
        """Get endorsement repository."""
        from models.infrastructure.vitess.repositories.endorsement import EndorsementRepository
        return EndorsementRepository(vitess_client=self)

    @property
    def thanks_repository(self) -> Any:
        """Get thanks repository."""
        from models.infrastructure.vitess.repositories.thanks import ThanksRepository
        return ThanksRepository(vitess_client=self)

    @property
    def redirect_repository(self) -> Any:
        """Get redirect repository."""
        from models.infrastructure.vitess.repositories.redirect import RedirectRepository
        return RedirectRepository(vitess_client=self)

    def create_revision(self, entity_id: str, entity_data: RevisionData, revision_id: int, content_hash: int, expected_revision_id: int = 0) -> None:
        """Create a new revision."""
        self.revision_repository.insert_revision(entity_id, revision_id, entity_data, content_hash, expected_revision_id)

    def create_tables(self) -> None:
        from models.infrastructure.vitess.repositories.schema import SchemaRepository

        schema_repository: SchemaRepository = SchemaRepository(vitess_client=self)
        schema_repository.create_tables()

    def entity_exists(self, entity_id: str) -> bool:
        return self.id_resolver.entity_exists(entity_id)

    def resolve_id(self, entity_id: str) -> int:
        return self.id_resolver.resolve_id(entity_id)

    def get_head(self, entity_id: str) -> int:
        return cast(int, self.entity_repository.get_head(entity_id))

    def get_history(self, entity_id: str, limit: int = 20, offset: int = 0) -> list[Any]:
        return cast(list[Any], self.revision_repository.get_history(entity_id, limit, offset))

    def get_entity_history(self, entity_id: str, limit: int = 20, offset: int = 0) -> list[Any]:
        return cast(list[Any], self.revision_repository.get_history(entity_id, limit, offset))

    def register_entity(self, entity_id: str) -> None:
        self.id_resolver.register_entity(entity_id)

    def insert_revision(
        self,
        entity_id: str,
        revision_id: int,
        entity_data: Any,  # type_: RevisionData
        content_hash: int,
        expected_revision_id: int = 0,
    ) -> None:
        self.revision_repository.insert_revision(entity_id=entity_id, revision_id=revision_id, entity_data=entity_data, content_hash=content_hash, expected_revision_id=expected_revision_id)

    def is_entity_deleted(self, entity_id: str) -> bool:
        return cast(bool, self.entity_repository.is_deleted(entity_id))

    def is_entity_locked(self, entity_id: str) -> bool:
        return cast(bool, self.entity_repository.is_locked(entity_id))

    def is_entity_archived(self, entity_id: str) -> bool:
        return cast(bool, self.entity_repository.is_archived(entity_id))

    def list_entities_by_type(self, entity_type: str, limit: int = 100, offset: int = 0) -> list[str]:
        """List entity IDs by type using pattern matching on entity_id."""
        cursor = self.cursor
        pattern_map = {
            "item": "Q%",
            "lexeme": "L%",
            "property": "P%",
        }
        pattern = pattern_map.get(entity_type)
        if not pattern:
            return []
        cursor.execute(
            """SELECT entity_id FROM entity_id_mapping
               WHERE entity_id LIKE %s
               LIMIT %s OFFSET %s""",
            (pattern, limit, offset),
        )
        return [row[0] for row in cursor.fetchall()]

    def get_redirect_target(self, entity_id: str) -> str:
        """Get the redirect target for an entity."""
        return self.redirect_repository.get_target(entity_id)

    def create_redirect(
        self,
        redirect_from_entity_id: str,
        redirect_to_entity_id: str,
        created_by: str = "rest-api",
    ) -> None:
        """Create a redirect from one entity to another."""
        self.redirect_repository.create(
            redirect_from_entity_id=redirect_from_entity_id,
            redirect_to_entity_id=redirect_to_entity_id,
            created_by=created_by,
        )

    def set_redirect_target(
        self,
        entity_id: str,
        redirects_to_entity_id: str,
    ) -> None:
        """Set redirect target for an entity."""
        result = self.redirect_repository.set_target(
            entity_id=entity_id,
            redirects_to_entity_id=redirects_to_entity_id,
        )
        if not result.success:
            raise ValueError(result.error)

    def revert_redirect(self, entity_id: str) -> None:
        """Revert a redirect by clearing the redirect target."""
        self.set_redirect_target(entity_id=entity_id, redirects_to_entity_id="")
