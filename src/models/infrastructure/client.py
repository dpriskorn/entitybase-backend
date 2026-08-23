"""Base client classes for external service connections."""

from abc import ABC
from typing import Any, Optional, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from models.data.config.config import Config
from models.infrastructure.connection import ConnectionManager
from models.rest_api.utils import raise_validation_error


@runtime_checkable
class DatabaseClient(Protocol):
    """Protocol defining the interface for database clients.

    Both MysqlClient and SqliteClient implement this interface.
    """

    config: Any

    @property
    def cursor(self) -> Any:
        """Return a cursor context manager."""
        ...

    def disconnect(self) -> None:
        """Disconnect from the database."""
        ...

    @property
    def healthy_connection(self) -> bool:
        """Check if database connection is healthy."""
        ...

    @property
    def entity_repository(self) -> Any:
        """Get entity repository."""
        ...

    @property
    def revision_repository(self) -> Any:
        """Get revision repository."""
        ...

    @property
    def head_repository(self) -> Any:
        """Get head repository."""
        ...

    @property
    def user_repository(self) -> Any:
        """Get user repository."""
        ...

    @property
    def watchlist_repository(self) -> Any:
        """Get watchlist repository."""
        ...

    @property
    def endorsement_repository(self) -> Any:
        """Get endorsement repository."""
        ...

    @property
    def thanks_repository(self) -> Any:
        """Get thanks repository."""
        ...

    @property
    def redirect_repository(self) -> Any:
        """Get redirect repository."""
        ...

    @property
    def statement_repository(self) -> Any:
        """Get statement repository."""
        ...

    @property
    def backlink_repository(self) -> Any:
        """Get backlink repository."""
        ...

    def get_backlinks(
        self, referenced_internal_id: int, limit: int = 100, offset: int = 0
    ) -> list[Any]:
        """Get backlinks for an entity."""
        ...

    def create_revision(
        self,
        entity_id: str,
        entity_data: Any,
        revision_id: int,
        content_hash: int,
        expected_revision_id: int = 0,
    ) -> bool:
        """Create a new revision."""
        ...

    def create_tables(self) -> None:
        """Create database tables."""
        ...

    def entity_exists(self, entity_id: str) -> bool:
        """Check if an entity exists."""
        ...

    def resolve_id(self, entity_id: str) -> int:
        """Resolve entity ID to internal ID."""
        ...

    def get_head(self, entity_id: str) -> int:
        """Get head revision ID for an entity."""
        ...

    def get_history(
        self, entity_id: str, limit: int = 20, offset: int = 0
    ) -> list[Any]:
        """Get revision history for an entity."""
        ...

    def get_entity_history(
        self, entity_id: str, limit: int = 20, offset: int = 0
    ) -> list[Any]:
        """Get entity revision history."""
        ...

    def register_entity(self, entity_id: str) -> None:
        """Register a new entity."""
        ...

    def insert_revision(
        self,
        entity_id: str,
        revision_id: int,
        entity_data: Any,
        content_hash: int,
        expected_revision_id: int = 0,
    ) -> bool:
        """Insert a new revision."""
        ...

    def is_entity_deleted(self, entity_id: str) -> bool:
        """Check if an entity is deleted."""
        ...

    def is_entity_locked(self, entity_id: str) -> bool:
        """Check if an entity is locked."""
        ...

    def is_entity_archived(self, entity_id: str) -> bool:
        """Check if an entity is archived."""
        ...

    def get_redirect_target(self, entity_id: str) -> str:
        """Get redirect target for an entity."""
        ...

    def create_redirect(
        self,
        redirect_from_entity_id: str,
        redirect_to_entity_id: str,
        created_by: str = "rest-api",
    ) -> None:
        """Create a redirect from one entity to another."""
        ...

    def set_redirect_target(
        self,
        entity_id: str,
        redirects_to_entity_id: str,
    ) -> None:
        """Set redirect target for an entity."""
        ...

    def revert_redirect(self, entity_id: str) -> None:
        """Revert a redirect."""
        ...

    def get_orphaned_statements(self, older_than_days: int, limit: int) -> list[int]:
        """Get orphaned statement content hashes."""
        ...

    def delete_statement(self, content_hash: int) -> None:
        """Delete statement content from database."""
        ...

    def list_entities_by_type(
        self, entity_type: str, limit: int = 100, offset: int = 0
    ) -> list[str]:
        """List entities by type."""
        ...


class Client(ABC, BaseModel):
    """Abstract base class for service clients."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    config: Config
    connection_manager: Optional[ConnectionManager] = Field(
        default=None, init=False, exclude=True
    )

    @property
    def healthy_connection(self) -> bool:
        """Check if the client has a healthy connection."""
        if not self.connection_manager:
            raise_validation_error("Service unavailable", status_code=503)
        return bool(self.connection_manager.healthy_connection)
