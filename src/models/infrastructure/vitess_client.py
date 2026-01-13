"""Vitess client for database operations."""

import json
import logging
from contextlib import contextmanager
from typing import Any, Generator

from pydantic import Field

logger = logging.getLogger(__name__)

from models.rest_api.response.misc import EntityListing
from models.infrastructure.client import Client
from models.infrastructure.vitess.backlink_repository import BacklinkRepository
from models.infrastructure.vitess.connection import VitessConnectionManager
from models.infrastructure.vitess.entities import IdResolver
from models.infrastructure.vitess.entity_repository import EntityRepository
from models.infrastructure.vitess.head_repository import HeadRepository
from models.infrastructure.vitess.listing_repository import ListingRepository
from models.infrastructure.vitess.metadata_repository import MetadataRepository
from models.infrastructure.vitess.redirect_repository import RedirectRepository
from models.infrastructure.vitess.revision_repository import RevisionRepository
from models.infrastructure.vitess.schema import SchemaManager
from models.infrastructure.vitess.statement_repository import StatementRepository
from models.infrastructure.vitess.user_repository import UserRepository
from models.infrastructure.vitess.watchlist_repository import WatchlistRepository
from models.rest_api.request.entity import RevisionInsertDataRequest
from models.rest_api.response.entity.entitybase import ProtectionResponse
from models.vitess_models import BacklinkData
from models.rest_api.response.rdf import FullRevisionData
from models.validation.utils import raise_validation_error
from models.vitess_models import VitessConfig


class VitessClient(Client):
    """Vitess database client for entity operations."""

    config: VitessConfig
    connection_manager: VitessConnectionManager = Field(default=None, exclude=True)
    schema_manager: SchemaManager = Field(default=None, exclude=True)
    id_resolver: IdResolver = Field(default=None, exclude=True)
    entity_repository: EntityRepository = Field(default=None, exclude=True)
    revision_repository: RevisionRepository = Field(default=None, exclude=True)
    redirect_repository: RedirectRepository = Field(default=None, exclude=True)
    head_repository: HeadRepository = Field(default=None, exclude=True)
    listing_repository: ListingRepository = Field(
        default=None, exclude=True
    )  # DISABLED: Not used
    statement_repository: StatementRepository = Field(default=None, exclude=True)
    backlink_repository: BacklinkRepository = Field(default=None, exclude=True)
    metadata_repository: MetadataRepository = Field(default=None, exclude=True)
    user_repository: UserRepository = Field(default=None, exclude=True)
    watchlist_repository: WatchlistRepository = Field(default=None, exclude=True)

    def __init__(self, config: VitessConfig, **kwargs: Any) -> None:
        super().__init__(config=config, **kwargs)
        logger.debug(f"Initializing VitessClient with host {config.host}")
        self.connection_manager = VitessConnectionManager(config=config)
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
        # self.listing_repository = ListingRepository(self.connection_manager)  # DISABLED: Listing not used
        self.statement_repository = StatementRepository(self.connection_manager)
        self.backlink_repository = BacklinkRepository(self.connection_manager)
        self.metadata_repository = MetadataRepository(self.connection_manager)
        self.user_repository = UserRepository(self.connection_manager)
        self.watchlist_repository = WatchlistRepository(
            self.connection_manager, self.id_resolver
        )
        self._create_tables()

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        self.schema_manager.create_tables()

    def connect(self) -> Any:
        """Create a new database connection.

        Returns:
            Any: A new database connection.
        """
        return self.connection_manager.connect()

    def healthy_connection(self) -> bool:
        """Check if the database connection is healthy."""
        return self.connection_manager.healthy_connection  # type: ignore[no-any-return]

    @contextmanager
    def get_connection(self) -> Generator[Any, None, None]:
        """Context manager for database connection."""
        conn = self.connection_manager.connect()
        try:
            yield conn
        finally:
            pass  # Connection is cached, don't close

    def _resolve_id(self, entity_id: str) -> int:
        """Resolve external entity ID to internal database ID."""
        with self.connection_manager.get_connection() as conn:
            return self.id_resolver.resolve_id(conn, entity_id)  # type: ignore[no-any-return]

    def entity_exists(self, entity_id: str) -> bool:
        """Check if an entity exists in the database.

        Args:
            entity_id (str): The entity ID to check.

        Returns:
            bool: True if the entity exists, False otherwise.
        """
        with self.connection_manager.get_connection() as conn:
            return self.id_resolver.entity_exists(conn, entity_id)  # type: ignore[no-any-return]

    def register_entity(self, entity_id: str) -> None:
        """Register a new entity in the database.

        Args:
            entity_id (str): The entity ID to register.

        Returns:
            None
        """
        with self.connection_manager.get_connection() as conn:
            return self.id_resolver.register_entity(conn, entity_id)  # type: ignore[no-any-return]

    def get_head(self, entity_id: str) -> int:
        """Get the current head revision ID for an entity."""
        with self.connection_manager.get_connection() as conn:
            return self.entity_repository.get_head(conn, entity_id)  # type: ignore[no-any-return]

    def is_entity_deleted(self, entity_id: str) -> bool:
        """Check if an entity is marked as deleted."""
        with self.connection_manager.get_connection() as conn:
            return self.entity_repository.is_deleted(conn, entity_id)  # type: ignore[no-any-return]

    def is_entity_locked(self, entity_id: str) -> bool:
        """Check if an entity is locked for editing."""
        with self.connection_manager.get_connection() as conn:
            return self.entity_repository.is_locked(conn, entity_id)  # type: ignore[no-any-return]

    def is_entity_archived(self, entity_id: str) -> bool:
        """Check if an entity is archived."""
        with self.connection_manager.get_connection() as conn:
            return self.entity_repository.is_archived(conn, entity_id)  # type: ignore[no-any-return]

    def get_protection_info(self, entity_id: str) -> ProtectionResponse | None:
        """Get protection information for an entity."""
        with self.connection_manager.get_connection() as conn:
            return self.entity_repository.get_protection_info(conn, entity_id)

    def get_history(
        self, entity_id: str, limit: int = 20, offset: int = 0
    ) -> list[Any]:
        """Get revision history for an entity."""
        with self.connection_manager.get_connection() as conn:
            return self.revision_repository.get_history(conn, entity_id, limit, offset)  # type: ignore[no-any-return]

    def insert_revision(
        self,
        entity_id: str,
        revision_id: int,
        is_mass_edit: bool = False,
        edit_type: str = "",
        statements: list[int] | None = None,
        properties: list[str] | None = None,
        property_counts: dict[str, int] | None = None,
    ) -> None:
        """Insert a new revision for an entity."""
        logger.debug(f"Inserting revision {revision_id} for entity {entity_id}")
        data = RevisionInsertDataRequest(
            is_mass_edit=is_mass_edit,
            edit_type=edit_type,
            statements=statements,
            properties=properties,
            property_counts=property_counts,
        )
        with self.connection_manager.get_connection() as conn:
            return self.revision_repository.insert(  # type: ignore[no-any-return]
                conn,
                entity_id,
                revision_id,
                data.model_dump(),
            )

    def create_revision(
        self,
        entity_id: str,
        revision_id: int,
        data: dict,
        expected_revision_id: int | None = None,
    ) -> None:
        """Create a new revision for an entity."""
        with self.connection_manager.get_connection() as conn:
            if expected_revision_id is not None:
                success = self.revision_repository.create_with_cas(
                    conn, entity_id, revision_id, data, expected_revision_id
                )
                if not success:
                    raise_validation_error(
                        "Concurrent modification detected", status_code=409
                    )
                return
            return self.revision_repository.create(conn, entity_id, revision_id, data)  # type: ignore[no-any-return]

    def set_redirect_target(
        self,
        entity_id: str,
        redirects_to_entity_id: str | None,
        expected_redirects_to: int | None = None,
    ) -> None:
        """Set the redirect target for an entity."""
        with self.connection_manager.get_connection() as conn:
            success = self.redirect_repository.set_target(
                conn, entity_id, redirects_to_entity_id, expected_redirects_to
            )
            if not success:
                raise_validation_error(
                    "Concurrent redirect modification detected", status_code=409
                )

    def create_redirect(
        self,
        redirect_from_entity_id: str,
        redirect_to_entity_id: str,
        created_by: str = "rest-api",
    ) -> None:
        """Create a redirect from one entity to another."""
        with self.connection_manager.get_connection() as conn:
            return self.redirect_repository.create(  # type: ignore[no-any-return]
                conn, redirect_from_entity_id, redirect_to_entity_id, created_by
            )

    def get_incoming_redirects(self, entity_id: str) -> list[str]:
        """Get entities that redirect to the given entity."""
        with self.connection_manager.get_connection() as conn:
            return self.redirect_repository.get_incoming_redirects(conn, entity_id)  # type: ignore[no-any-return]

    def get_redirect_target(self, entity_id: str) -> str | None:
        """Get the redirect target for an entity."""
        with self.connection_manager.get_connection() as conn:
            return self.redirect_repository.get_target(conn, entity_id)  # type: ignore[no-any-return]

    def cas_update_head_with_status(
        self,
        entity_id: str,
        expected_head: int | None,
        new_head: int,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool,
        is_deleted: bool,
        is_redirect: bool = False,
    ) -> bool:
        """Update entity head with compare-and-swap semantics."""
        logger.debug(
            f"CAS updating head for entity {entity_id} from {expected_head} to {new_head}"
        )
        with self.connection_manager.get_connection() as conn:
            return self.head_repository.cas_update_with_status(  # type: ignore[no-any-return]
                conn,
                entity_id,
                expected_head,
                new_head,
                is_semi_protected,
                is_locked,
                is_archived,
                is_dangling,
                is_mass_edit_protected,
                is_deleted,
                is_redirect,
            )

    def hard_delete_entity(
        self,
        entity_id: str,
        head_revision_id: int,
    ) -> None:
        """Hard delete an entity from the database."""
        with self.connection_manager.get_connection() as conn:
            return self.head_repository.hard_delete(conn, entity_id, head_revision_id)  # type: ignore[no-any-return]

    def delete_entity(self, entity_id: str) -> None:
        """Soft delete an entity."""
        with self.connection_manager.get_connection() as conn:
            return self.head_repository.soft_delete(conn, entity_id)  # type: ignore[no-any-return]

    def get_ref_count(self, content_hash: int) -> int:
        """Get reference count for statement content."""
        with self.connection_manager.get_connection() as conn:
            return self.statement_repository.get_ref_count(conn, content_hash)  # type: ignore[no-any-return]

    def delete_revision(self, entity_id: str, revision_id: int) -> None:
        """Delete a revision for an entity."""
        with self.connection_manager.get_connection() as conn:
            return self.revision_repository.delete(conn, entity_id, revision_id)  # type: ignore[no-any-return]

    def list_entities_by_type(
        self, entity_type: str | None, limit: int, offset: int
    ) -> list[str]:
        """List entity IDs by type with pagination."""
        logger.debug(
            f"Listing entities by type {entity_type} with limit {limit} offset {offset}"
        )
        if entity_type == "item":
            prefix = "Q"
        elif entity_type == "property":
            prefix = "P"
        elif entity_type == "lexeme":
            prefix = "L"
        elif entity_type == "entityschema":
            prefix = "E"
        else:
            # If no type specified, list all (no prefix filter)
            prefix = ""

        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            if prefix:
                cursor.execute(
                    "SELECT DISTINCT entity_id FROM entity_revisions WHERE entity_id LIKE %s ORDER BY entity_id LIMIT %s OFFSET %s",
                    (f"{prefix}%", limit, offset),
                )
            else:
                cursor.execute(
                    "SELECT DISTINCT entity_id FROM entity_revisions ORDER BY entity_id LIMIT %s OFFSET %s",
                    (limit, offset),
                )
            results = cursor.fetchall()
            cursor.close()
            return [row[0] for row in results]

    def list_locked_entities(self, limit: int) -> list[EntityListing]:
        # Stub implementation
        return []

    def list_semi_protected_entities(self, limit: int) -> list[EntityListing]:
        # Stub implementation
        return []

    def list_archived_entities(self, limit: int) -> list[EntityListing]:
        # Stub implementation
        return []

    def list_dangling_entities(self, limit: int) -> list[EntityListing]:
        # Stub implementation
        return []

    def list_by_edit_type(self, edit_type: str, limit: int) -> list[EntityListing]:
        # Stub implementation
        return []

    def insert_statement_content(self, content_hash: int) -> bool:
        """Insert statement content hash."""
        with self.connection_manager.get_connection() as conn:
            return self.statement_repository.insert_content(conn, content_hash)  # type: ignore[no-any-return]

    def increment_ref_count(self, content_hash: int) -> int:
        """Increment reference count for statement content."""
        with self.connection_manager.get_connection() as conn:
            return self.statement_repository.increment_ref_count(conn, content_hash)  # type: ignore[no-any-return]

    def decrement_ref_count(self, content_hash: int) -> int:
        """Decrement reference count for statement content."""
        with self.connection_manager.get_connection() as conn:
            return self.statement_repository.decrement_ref_count(conn, content_hash)  # type: ignore[no-any-return]

    def get_orphaned_statements(self, older_than_days: int, limit: int) -> list[int]:
        """Get orphaned statements older than specified days."""
        with self.connection_manager.get_connection() as conn:
            return self.statement_repository.get_orphaned(conn, older_than_days, limit)  # type: ignore[no-any-return]

    def get_most_used_statements(self, limit: int, min_ref_count: int = 1) -> list[int]:
        """Get most used statements by reference count."""
        with self.connection_manager.get_connection() as conn:
            return self.statement_repository.get_most_used(conn, limit, min_ref_count)  # type: ignore[no-any-return]

    def delete_statement(self, content_hash: int) -> None:
        """Delete a statement from the database."""
        with self.connection_manager.get_connection() as conn:
            self.statement_repository.delete_content(conn, content_hash)

    def write_entity_revision(
        self,
        entity_id: str,
        revision_id: int,
        data: dict,
        is_mass_edit: bool = False,
        edit_type: str = "",
    ) -> None:
        """Write an entity revision to the database."""
        logger.debug(f"Writing entity revision {revision_id} for {entity_id}")
        with self.connection_manager.get_connection() as conn:
            internal_id = self.id_resolver.resolve_id(conn, entity_id)
            if not internal_id:
                raise_validation_error(f"Entity {entity_id} not found", status_code=404)
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO entity_revisions (internal_id, revision_id, is_mass_edit, edit_type, statements, properties, property_counts) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        internal_id,
                        revision_id,
                        is_mass_edit,
                        edit_type,
                        json.dumps(data.get("statements", [])),
                        json.dumps(data.get("properties", [])),
                        json.dumps(data.get("property_counts", {})),
                    ),
                )

    def read_full_revision(
        self, entity_id: str, revision_id: int, s3_client: Any
    ) -> FullRevisionData:
        """Read full revision data including metadata from S3."""
        logger.debug(f"Reading full revision {revision_id} for entity {entity_id}")
        assert s3_client is not None

        with self.connection_manager.get_connection() as conn:
            internal_id = self.id_resolver.resolve_id(conn, entity_id)
            if not internal_id:
                raise_validation_error(f"Entity {entity_id} not found", status_code=404)
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT statements, properties, property_counts, labels_hashes, descriptions_hashes, aliases_hashes FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
                    (internal_id, revision_id),
                )
                result = cursor.fetchone()
                if not result:
                    raise_validation_error(
                        f"Revision {revision_id} not found for entity {entity_id}",
                        status_code=404,
                    )

                # Load metadata from S3 using hash maps
                labels_hashes = json.loads(result[3]) if result[3] else {}
                descriptions_hashes = json.loads(result[4]) if result[4] else {}
                aliases_hashes = json.loads(result[5]) if result[5] else {}

                # Reconstruct labels from per-language hashes
                labels = {}
                for lang, hash_value in labels_hashes.items():
                    label_value = s3_client.load_metadata("labels", hash_value)
                    labels[lang] = {"language": lang, "value": label_value}

                # Reconstruct descriptions from per-language hashes
                descriptions = {}
                for lang, hash_value in descriptions_hashes.items():
                    desc_value = s3_client.load_metadata("descriptions", hash_value)
                    descriptions[lang] = {"language": lang, "value": desc_value}

                # Reconstruct aliases from per-language hash arrays
                aliases: dict[str, list[dict[str, str]]] = {}
                for lang, hash_list in aliases_hashes.items():
                    aliases[lang] = []
                    for hash_value in hash_list:
                        alias_value = s3_client.load_metadata("aliases", hash_value)
                        aliases[lang].append({"language": lang, "value": alias_value})

                return FullRevisionData(
                    revision_id=revision_id,
                    statements=json.loads(result[0]) if result[0] else [],
                    properties=json.loads(result[1]) if result[1] else [],
                    property_counts=json.loads(result[2]) if result[2] else {},
                    labels=labels,
                    descriptions=descriptions,
                    aliases=aliases,
                )

    def insert_backlinks(self, backlinks: list[tuple[int, int, int, str, str]]) -> None:
        """Insert backlinks into entity_backlinks table."""
        with self.connection_manager.get_connection() as conn:
            self.backlink_repository.insert_backlinks(conn, backlinks)

    def delete_backlinks_for_entity(self, referencing_internal_id: int) -> None:
        """Delete all backlinks for a referencing entity."""
        with self.connection_manager.get_connection() as conn:
            self.backlink_repository.delete_backlinks_for_entity(
                conn, referencing_internal_id
            )

    def get_backlinks(
        self, referenced_internal_id: int, limit: int = 100, offset: int = 0
    ) -> list[tuple[int, str, str, str]]:
        """Get backlinks for an entity."""
        with self.connection_manager.get_connection() as conn:
            return self.backlink_repository.get_backlinks(
                conn, referenced_internal_id, limit, offset
            )  # type: ignore[no-any-return]
