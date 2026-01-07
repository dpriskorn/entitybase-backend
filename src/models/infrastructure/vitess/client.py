from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from models.vitess_models import VitessConfig

from models.infrastructure.vitess.connection import ConnectionManager
from models.infrastructure.vitess.schema import SchemaManager
from models.infrastructure.vitess.entities import IdResolver
from models.infrastructure.vitess.entity_repository import EntityRepository
from models.infrastructure.vitess.revision_repository import RevisionRepository
from models.infrastructure.vitess.redirect_repository import RedirectRepository
from models.infrastructure.vitess.head_repository import HeadRepository
from models.infrastructure.vitess.listing_repository import ListingRepository
from models.infrastructure.vitess.statement_repository import StatementRepository


class VitessClient(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: VitessConfig
    connection_manager: ConnectionManager = Field(default=None, exclude=True)
    schema_manager: SchemaManager = Field(default=None, exclude=True)
    id_resolver: IdResolver = Field(default=None, exclude=True)
    entity_repository: EntityRepository = Field(default=None, exclude=True)
    revision_repository: RevisionRepository = Field(default=None, exclude=True)
    redirect_repository: RedirectRepository = Field(default=None, exclude=True)
    head_repository: HeadRepository = Field(default=None, exclude=True)
    listing_repository: ListingRepository = Field(default=None, exclude=True)
    statement_repository: StatementRepository = Field(default=None, exclude=True)

    def __init__(self, config: VitessConfig, **kwargs: Any) -> None:
        super().__init__(config=config, **kwargs)
        self.connection_manager = ConnectionManager(config)
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
        self._create_tables()

    def _create_tables(self) -> None:
        self.schema_manager.create_tables()

    def connect(self) -> Any:
        return self.connection_manager.connect()

    def check_connection(self) -> bool:
        return self.connection_manager.check_connection()  # type: ignore[no-any-return]

    def _resolve_id(self, entity_id: str) -> int:
        return self.id_resolver.resolve_id(entity_id)  # type: ignore[no-any-return]

    def entity_exists(self, entity_id: str) -> bool:
        return self.id_resolver.entity_exists(entity_id)  # type: ignore[no-any-return]

    def register_entity(self, entity_id: str) -> None:
        return self.id_resolver.register_entity(entity_id)  # type: ignore[no-any-return]

    def get_head(self, entity_id: str) -> int:
        return self.entity_repository.get_head(entity_id)  # type: ignore[no-any-return]

    def is_entity_deleted(self, entity_id: str) -> bool:
        return self.entity_repository.is_deleted(entity_id)  # type: ignore[no-any-return]

    def is_entity_locked(self, entity_id: str) -> bool:
        return self.entity_repository.is_locked(entity_id)  # type: ignore[no-any-return]

    def is_entity_archived(self, entity_id: str) -> bool:
        return self.entity_repository.is_archived(entity_id)  # type: ignore[no-any-return]

    def get_protection_info(self, entity_id: str) -> dict[str, bool]:
        return self.entity_repository.get_protection_info(entity_id)  # type: ignore[no-any-return]

    def get_history(self, entity_id: str, limit: int = 20, offset: int = 0) -> list:
        return self.revision_repository.get_history(entity_id, limit, offset)  # type: ignore[no-any-return]

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
        return self.revision_repository.insert(  # type: ignore[no-any-return]
            entity_id,
            revision_id,
            is_mass_edit,
            edit_type,
            statements,
            properties,
            property_counts,
        )

    def create_revision_cas(
        self, entity_id: str, revision_id: int, data: dict, expected_revision_id: int
    ) -> bool:
        return self.revision_repository.create_with_cas(  # type: ignore[no-any-return]
            entity_id, revision_id, data, expected_revision_id
        )

    def create_revision(self, entity_id: str, revision_id: int, data: dict) -> None:
        return self.revision_repository.create(entity_id, revision_id, data)  # type: ignore[no-any-return]

    def set_redirect_target(
        self, entity_id: str, redirects_to_entity_id: str | None
    ) -> None:
        return self.redirect_repository.set_target(entity_id, redirects_to_entity_id)  # type: ignore[no-any-return]

    def create_redirect(
        self,
        redirect_from_entity_id: str,
        redirect_to_entity_id: str,
        created_by: str = "entity-api",
    ) -> None:
        return self.redirect_repository.create(  # type: ignore[no-any-return]
            redirect_from_entity_id, redirect_to_entity_id, created_by
        )

    def get_incoming_redirects(self, entity_id: str) -> list[str]:
        return self.redirect_repository.get_incoming_redirects(entity_id)  # type: ignore[no-any-return]

    def get_redirect_target(self, entity_id: str) -> str | None:
        return self.redirect_repository.get_target(entity_id)  # type: ignore[no-any-return]

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
        return self.head_repository.cas_update_with_status(  # type: ignore[no-any-return]
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

    def insert_head_with_status(
        self,
        entity_id: str,
        head_revision_id: int,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool,
        is_deleted: bool,
        is_redirect: bool = False,
    ) -> bool:
        return self.head_repository.insert_with_status(  # type: ignore[no-any-return]
            entity_id,
            head_revision_id,
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
        return self.head_repository.hard_delete(entity_id, head_revision_id)  # type: ignore[no-any-return]

    def delete_entity(self, entity_id: str) -> None:
        return self.head_repository.soft_delete(entity_id)  # type: ignore[no-any-return]

    def list_locked_entities(self, limit: int) -> list[dict]:
        return self.listing_repository.list_locked(limit)  # type: ignore[no-any-return]

    def list_semi_protected_entities(self, limit: int) -> list[dict]:
        return self.listing_repository.list_semi_protected(limit)  # type: ignore[no-any-return]

    def list_archived_entities(self, limit: int) -> list[dict]:
        return self.listing_repository.list_archived(limit)  # type: ignore[no-any-return]

    def list_dangling_entities(self, limit: int) -> list[dict]:
        return self.listing_repository.list_dangling(limit)  # type: ignore[no-any-return]

    def list_by_edit_type(self, edit_type: str, limit: int) -> list[dict]:
        return self.listing_repository.list_by_edit_type(edit_type, limit)  # type: ignore[no-any-return]

    def insert_statement_content(self, content_hash: int) -> bool:
        return self.statement_repository.insert_content(content_hash)  # type: ignore[no-any-return]

    def increment_ref_count(self, content_hash: int) -> int:
        return self.statement_repository.increment_ref_count(content_hash)  # type: ignore[no-any-return]

    def decrement_ref_count(self, content_hash: int) -> int:
        return self.statement_repository.decrement_ref_count(content_hash)  # type: ignore[no-any-return]

    def get_orphaned_statements(self, older_than_days: int, limit: int) -> list[int]:
        return self.statement_repository.get_orphaned(older_than_days, limit)  # type: ignore[no-any-return]

    def get_most_used_statements(self, limit: int, min_ref_count: int = 1) -> list[int]:
        return self.statement_repository.get_most_used(limit, min_ref_count)  # type: ignore[no-any-return]

    def write_entity_revision(
        self,
        entity_id: str,
        revision_id: int,
        data: dict,
        is_mass_edit: bool = False,
        edit_type: str = "",
    ) -> None:
        import json

        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            raise ValueError(f"Entity {entity_id} not found")
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entity_revisions (internal_id, revision_id, is_mass_edit, edit_type, data) VALUES (%s, %s, %s, %s)",
            (internal_id, revision_id, is_mass_edit, edit_type, json.dumps(data)),
        )
        cursor.close()

    def read_full_revision(self, entity_id: str, revision_id: int) -> dict:
        import json

        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            raise ValueError(f"Entity {entity_id} not found")
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT data FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
            (internal_id, revision_id),
        )
        result = cursor.fetchone()
        cursor.close()
        return {
            "revision_id": revision_id,
            "data": json.loads(result[0]) if result[0] else None,
        }
