"""Vitess client for database operations."""

import logging
from typing import Any, cast
from typing import Optional

from pydantic import Field

from models.infrastructure.client import Client
from models.data.config.vitess import VitessConfig
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.vitess.connection import (
    VitessConnectionManager,
    CursorContextManager,
)
from models.infrastructure.vitess.id_resolver import IdResolver
from models.infrastructure.vitess.repositories.backlink import BacklinkRecord
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class VitessClient(Client):
    """Vitess database client for entity operations with connection pooling."""

    connection_manager: Optional[VitessConnectionManager] = Field(
        default=None, init=False, exclude=True
    )
    id_resolver: Optional[IdResolver] = Field(default=None, init=False, exclude=True)
    config: VitessConfig

    def model_post_init(self, context: Any) -> None:
        logger.info("=== VitessClient.model_post_init() START ===")
        logger.debug(
            f"Initializing VitessClient with host='{self.config.host}', port={self.config.port}, database='{self.config.database}', user='{self.config.user}', password_length={len(self.config.password)}"
        )
        logger.debug("Creating VitessConnectionManager...")
        self.connection_manager = VitessConnectionManager(config=self.config)
        logger.debug("VitessConnectionManager created, calling connect()...")
        self.connection_manager.connect()
        logger.debug("Connection established, creating IdResolver...")
        self.id_resolver = IdResolver(vitess_client=self)
        logger.info("=== VitessClient.model_post_init() END ===")
        # self.create_tables()

    @property
    def cursor(self) -> CursorContextManager:
        """Return a cursor context manager that properly manages connection lifecycle."""
        if self.connection_manager is None:
            raise RuntimeError("Connection manager not initialized")
        return CursorContextManager(self.connection_manager)

    def disconnect(self) -> None:
        """Disconnect from the database and close all pooled connections."""
        if self.connection_manager is not None:
            self.connection_manager.disconnect()
            logger.info("VitessClient disconnected")

    @property
    def healthy_connection(self) -> bool:
        """Check if database connection is healthy."""
        if self.connection_manager is None:
            logger.warning("Connection manager not initialized")
            return False
        return self.connection_manager.healthy_connection

    @property
    def entity_repository(self) -> Any:
        """Get entity repository."""
        from models.infrastructure.vitess.repositories.entity import EntityRepository

        return EntityRepository(vitess_client=self)

    @property
    def revision_repository(self) -> Any:
        """Get revision repository."""
        from models.infrastructure.vitess.repositories.revision import (
            RevisionRepository,
        )

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
        from models.infrastructure.vitess.repositories.watchlist import (
            WatchlistRepository,
        )

        return WatchlistRepository(vitess_client=self)

    @property
    def endorsement_repository(self) -> Any:
        """Get endorsement repository."""
        from models.infrastructure.vitess.repositories.endorsement import (
            EndorsementRepository,
        )

        return EndorsementRepository(vitess_client=self)

    @property
    def thanks_repository(self) -> Any:
        """Get thanks repository."""
        from models.infrastructure.vitess.repositories.thanks import ThanksRepository

        return ThanksRepository(vitess_client=self)

    @property
    def redirect_repository(self) -> Any:
        """Get redirect repository."""
        from models.infrastructure.vitess.repositories.redirect import (
            RedirectRepository,
        )

        return RedirectRepository(vitess_client=self)

    @property
    def statement_repository(self) -> Any:
        """Get statement repository."""
        from models.infrastructure.vitess.repositories.statement import (
            StatementRepository,
        )

        return StatementRepository(vitess_client=self)

    @property
    def backlink_repository(self) -> Any:
        """Get backlink repository."""
        from models.infrastructure.vitess.repositories.backlink import (
            BacklinkRepository,
        )

        return BacklinkRepository(vitess_client=self)

    def get_backlinks(
        self, referenced_internal_id: int, limit: int = 100, offset: int = 0
    ) -> list[BacklinkRecord]:
        """Get backlinks for an entity."""
        return self.backlink_repository.get_backlinks(  # type: ignore[no-any-return]
            referenced_internal_id, limit, offset
        )

    def create_revision(
        self,
        entity_id: str,
        entity_data: RevisionData,
        revision_id: int,
        content_hash: int,
        expected_revision_id: int = 0,
    ) -> None:
        """Create a new revision."""
        self.revision_repository.insert_revision(
            entity_id, revision_id, entity_data, content_hash, expected_revision_id
        )

    def create_tables(self) -> None:
        from models.infrastructure.vitess.repositories.schema import SchemaRepository

        schema_repository: SchemaRepository = SchemaRepository(vitess_client=self)
        schema_repository.create_tables()

    def entity_exists(self, entity_id: str) -> bool:
        return self.id_resolver.entity_exists(entity_id)  # type: ignore[union-attr]

    def resolve_id(self, entity_id: str) -> int:
        return self.id_resolver.resolve_id(entity_id)  # type: ignore[union-attr]

    def get_head(self, entity_id: str) -> int:
        return cast(int, self.entity_repository.get_head(entity_id))

    def get_history(
        self, entity_id: str, limit: int = 20, offset: int = 0
    ) -> list[Any]:
        return cast(
            list[Any], self.revision_repository.get_history(entity_id, limit, offset)
        )

    def get_entity_history(
        self, entity_id: str, limit: int = 20, offset: int = 0
    ) -> list[Any]:
        return cast(
            list[Any], self.revision_repository.get_history(entity_id, limit, offset)
        )

    def register_entity(self, entity_id: str) -> None:
        self.id_resolver.register_entity(entity_id)  # type: ignore[union-attr]

    def insert_revision(
        self,
        entity_id: str,
        revision_id: int,
        entity_data: Any,  # type_: RevisionData
        content_hash: int,
        expected_revision_id: int = 0,
    ) -> None:
        self.revision_repository.insert_revision(
            entity_id=entity_id,
            revision_id=revision_id,
            entity_data=entity_data,
            content_hash=content_hash,
            expected_revision_id=expected_revision_id,
        )

    def is_entity_deleted(self, entity_id: str) -> bool:
        return cast(bool, self.entity_repository.is_deleted(entity_id))

    def is_entity_locked(self, entity_id: str) -> bool:
        return cast(bool, self.entity_repository.is_locked(entity_id))

    def is_entity_archived(self, entity_id: str) -> bool:
        return cast(bool, self.entity_repository.is_archived(entity_id))

    def get_redirect_target(self, entity_id: str) -> str:
        """Get the redirect target for an entity."""
        return self.redirect_repository.get_target(entity_id)  # type: ignore[no-any-return]

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
            raise_validation_error(result.error, status_code=400)

    def revert_redirect(self, entity_id: str) -> None:
        """Revert a redirect by clearing the redirect target."""
        self.set_redirect_target(entity_id=entity_id, redirects_to_entity_id="")

    def get_orphaned_statements(self, older_than_days: int, limit: int) -> list[int]:
        """Get orphaned statement content hashes.

        Args:
            older_than_days: Minimum age in days
            limit: Maximum number of statements to return

        Returns:
            List of statement content hashes
        """
        from models.data.common import OperationResult

        result = self.statement_repository.get_orphaned(
            older_than_days=older_than_days, limit=limit
        )
        if not result.success or result.data is None:
            return []
        return cast(list[int], result.data)

    def delete_statement(self, content_hash: int) -> None:
        """Delete statement content from database.

        Args:
            content_hash: Hash of the statement to delete
        """
        self.statement_repository.delete_content(content_hash=content_hash)

    def list_entities_by_type(
        self, entity_type: str, limit: int = 100, offset: int = 0
    ) -> list[str]:
        """List entities by type (item, property, or lexeme).

        Args:
            entity_type: The type of entity ('item', 'property', or 'lexeme')
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entity IDs matching the type
        """
        type_prefixes = {"item": "Q", "property": "P", "lexeme": "L"}

        if entity_type not in type_prefixes:
            return []

        prefix = type_prefixes[entity_type]
        with self.cursor as cur:
            cur.execute(
                """SELECT entity_id FROM entity_id_mapping
                   WHERE entity_id LIKE %s
                   LIMIT %s OFFSET %s""",
                (f"{prefix}%", limit, offset),
            )
            return [row[0] for row in cur.fetchall()]
