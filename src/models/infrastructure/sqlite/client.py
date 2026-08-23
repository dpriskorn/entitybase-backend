"""SQLite client for database operations."""

import logging
from typing import Any, cast

from pydantic import Field

from models.data.config.sqlite import SqliteConfig
from models.infrastructure.client import Client
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.sqlite.connection import (
    SqliteConnectionManager,
    SqliteCursorContextManager,
)
from models.infrastructure.db.id_resolver import IdResolver
from models.infrastructure.db.repositories.backlink import BacklinkRecord
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class SqliteClient(Client):
    """SQLite database client with the same interface as MysqlClient."""

    connection_manager: SqliteConnectionManager | None = Field(
        default=None, init=False, exclude=True
    )
    id_resolver: IdResolver | None = Field(default=None, init=False, exclude=True)
    config: SqliteConfig

    def model_post_init(self, context: Any) -> None:
        """Initialize SQLite connection and id resolver."""
        logger.info("=== SqliteClient.model_post_init() START ===")
        self.connection_manager = SqliteConnectionManager(config=self.config)
        self.connection_manager.connect()
        self.id_resolver = IdResolver(db_client=self)
        logger.info("=== SqliteClient.model_post_init() END ===")

    @property
    def cursor(self) -> SqliteCursorContextManager:
        """Return a cursor context manager for SQLite."""
        if self.connection_manager is None:
            raise RuntimeError("Connection manager not initialized")
        return SqliteCursorContextManager(self.connection_manager)

    def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.connection_manager is not None:
            self.connection_manager.disconnect()
            logger.info("SqliteClient disconnected")

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
        from models.infrastructure.db.repositories.entity import (
            EntityRepository,
        )

        return EntityRepository(db_client=self)

    @property
    def revision_repository(self) -> Any:
        """Get revision repository."""
        from models.infrastructure.db.repositories.revision import (
            RevisionRepository,
        )

        return RevisionRepository(db_client=self)

    @property
    def head_repository(self) -> Any:
        """Get head repository."""
        from models.infrastructure.db.repositories.head import HeadRepository

        return HeadRepository(db_client=self)

    @property
    def user_repository(self) -> Any:
        """Get user repository."""
        from models.infrastructure.db.repositories.user import UserRepository

        return UserRepository(db_client=self)

    @property
    def watchlist_repository(self) -> Any:
        """Get watchlist repository."""
        from models.infrastructure.db.repositories.watchlist import (
            WatchlistRepository,
        )

        return WatchlistRepository(db_client=self)

    @property
    def endorsement_repository(self) -> Any:
        """Get endorsement repository."""
        from models.infrastructure.db.repositories.endorsement import (
            EndorsementRepository,
        )

        return EndorsementRepository(db_client=self)

    @property
    def thanks_repository(self) -> Any:
        """Get thanks repository."""
        from models.infrastructure.db.repositories.thanks import (
            ThanksRepository,
        )

        return ThanksRepository(db_client=self)

    @property
    def redirect_repository(self) -> Any:
        """Get redirect repository."""
        from models.infrastructure.db.repositories.redirect import (
            RedirectRepository,
        )

        return RedirectRepository(db_client=self)

    @property
    def statement_repository(self) -> Any:
        """Get statement repository."""
        from models.infrastructure.db.repositories.statement import (
            StatementRepository,
        )

        return StatementRepository(db_client=self)

    @property
    def backlink_repository(self) -> Any:
        """Get backlink repository."""
        from models.infrastructure.db.repositories.backlink import (
            BacklinkRepository,
        )

        return BacklinkRepository(db_client=self)

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
    ) -> bool:
        """Create a new revision.

        Returns:
            True if revision was created successfully.
            False if CAS failed (expected_revision_id didn't match current head).
        """
        return cast(
            bool,
            self.revision_repository.insert_revision(
                entity_id,
                revision_id,
                entity_data,
                content_hash,
                expected_revision_id,
            ),
        )

    def create_tables(self) -> None:
        """Create SQLite database tables."""
        from models.infrastructure.sqlite.repositories.schema import (
            SqliteSchemaRepository,
        )

        schema_repository = SqliteSchemaRepository(db_client=self)
        schema_repository.create_tables()

    def entity_exists(self, entity_id: str) -> bool:
        return self.id_resolver.entity_exists(entity_id)  # type: ignore[union-attr,no-any-return]

    def resolve_id(self, entity_id: str) -> int:
        return self.id_resolver.resolve_id(entity_id)  # type: ignore[union-attr,no-any-return]

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
        entity_data: Any,
        content_hash: int,
        expected_revision_id: int = 0,
    ) -> bool:
        return cast(
            bool,
            self.revision_repository.insert_revision(
                entity_id=entity_id,
                revision_id=revision_id,
                entity_data=entity_data,
                content_hash=content_hash,
                expected_revision_id=expected_revision_id,
            ),
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
        """Get orphaned statement content hashes."""
        from models.data.common import OperationResult

        result = self.statement_repository.get_orphaned(
            older_than_days=older_than_days, limit=limit
        )
        if not result.success or result.data is None:
            return []
        return cast(list[int], result.data)

    def delete_statement(self, content_hash: int) -> None:
        """Delete statement content from database."""
        self.statement_repository.delete_content(content_hash=content_hash)

    def list_entities_by_type(
        self, entity_type: str, limit: int = 100, offset: int = 0
    ) -> list[str]:
        """List entities by type (item, property, or lexeme)."""
        type_prefixes = {"item": "Q", "property": "P", "lexeme": "L"}

        if entity_type not in type_prefixes:
            return []

        prefix = type_prefixes[entity_type]
        with self.cursor as cur:
            cur.execute(
                """SELECT entity_id FROM entity_id_mapping
                   WHERE entity_id LIKE ? || '%'
                   LIMIT ? OFFSET ?""",
                (prefix, limit, offset),
            )
            return [row[0] for row in cur.fetchall()]
