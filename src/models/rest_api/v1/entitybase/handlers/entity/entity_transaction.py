"""Base class for entity transactions."""

from abc import ABC, abstractmethod
from typing import Any, Callable, List

from pydantic import BaseModel, Field

from models.rest_api.v1.entitybase.response.statement import StatementHashResult


class EntityTransaction(BaseModel, ABC):
    """Base class for entity transactions with shared rollback logic."""

    entity_id: str = Field(default="")
    operations: List[Callable[[], None]] = Field(default_factory=list)
    statement_hashes: List[int] = Field(default_factory=list)

    @abstractmethod
    def process_statements(
        self,
        entity_id: str,
        request_data: dict,
        vitess_client: Any,
        s3_client: Any,
        validator: Any,
    ) -> StatementHashResult:
        """Process statements for the transaction."""
        pass

    def register_entity(self, vitess_client: Any, entity_id: str) -> None:
        """Register the entity in the database."""
        from models.infrastructure.vitess.repositories.entity import EntityRepository

        logger.info(f"[EntityTransaction] Registering entity {entity_id}")
        self.entity_id = entity_id
        with vitess_client.get_connection() as conn:
            entity_repo = EntityRepository(
                vitess_client.connection_manager, vitess_client.id_resolver
            )
            entity_repo.create_entity(conn, entity_id)
        self.operations.append(
            lambda: self._rollback_entity_registration(vitess_client)
        )

    def _rollback_entity_registration(self, vitess_client: Any) -> None:
        """Rollback entity registration."""
        from models.infrastructure.vitess.repositories.entity import EntityRepository

        logger.info(
            f"[EntityTransaction] Rolling back entity registration for {self.entity_id}"
        )
        with vitess_client.get_connection() as conn:
            entity_repo = EntityRepository(
                vitess_client.connection_manager, vitess_client.id_resolver
            )
            entity_repo.delete_entity(conn, self.entity_id)

    def _rollback_revision(
        self, entity_id: str, revision_id: int, vitess_client: Any
    ) -> None:
        """Rollback a revision."""
        from models.infrastructure.vitess.repositories.revision import (
            RevisionRepository,
        )

        logger.info(
            f"[EntityTransaction] Rolling back revision {revision_id} for {entity_id}"
        )
        with vitess_client.get_connection() as conn:
            revision_repo = RevisionRepository(
                vitess_client.connection_manager, vitess_client.id_resolver
            )
            revision_repo.delete(conn, entity_id, revision_id)

    def publish_event(
        self,
        entity_id: str,
        revision_id: int,
        change_type: str,
        user_id: int = 0,
        **kwargs: Any,
    ) -> None:
        """Publish a change event."""
        from datetime import datetime, timezone
        from models.infrastructure.stream.event import EntityChangeEvent
        from models.infrastructure.stream.change_type import ChangeType

        logger.info(
            f"[EntityTransaction] Publishing event for {entity_id} revision {revision_id}"
        )
        event = EntityChangeEvent(
            id=entity_id,
            rev=revision_id,
            type=ChangeType(change_type),
            at=datetime.now(timezone.utc),
            summary="",
        )
        # TODO: Publish to stream
        logger.debug(f"Event: {event}")


# Import here to avoid circular imports
import logging

logger = logging.getLogger(__name__)
