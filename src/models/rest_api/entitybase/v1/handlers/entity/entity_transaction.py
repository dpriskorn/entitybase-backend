"""Base class for entity transactions."""

from abc import ABC, abstractmethod
from typing import Any, Callable, List
import logging

from pydantic import BaseModel, Field

from models.rest_api.entitybase.v1.response.statement import StatementHashResult

logger = logging.getLogger(__name__)


class EntityTransaction(BaseModel, ABC):
    """Base class for entity transactions with shared rollback logic."""
    state: Any  # This is the app state
    entity_id: str = Field(default="")
    operations: List[Callable[[], None]] = Field(default_factory=list)
    statement_hashes: List[int] = Field(default_factory=list)

    @abstractmethod
    def process_statements(
        self,
        entity_id: str,
        request_data: dict,
        validator: Any,
    ) -> StatementHashResult:
        """Process statements for the transaction."""
        pass

    def register_entity(self, entity_id: str) -> None:
        """Register the entity in the database."""
        logger.info(f"[EntityTransaction] Registering entity {entity_id}")
        self.entity_id = entity_id
        self.state.vitess_client.entity_repository.create_entity(entity_id)
        self.operations.append(
            lambda: self._rollback_entity_registration()
        )

    def _rollback_entity_registration(self) -> None:
        """Rollback entity registration."""
        logger.info(
            f"[EntityTransaction] Rolling back entity registration for {self.entity_id}"
        )
        self.state.vitess_client.entity_repository.delete_entity(self.entity_id)

    def _rollback_revision(
        self, entity_id: str, revision_id: int,
    ) -> None:
        """Rollback a revision."""
        logger.info(
            f"[EntityTransaction] Rolling back revision {revision_id} for {entity_id}"
        )
        self.state.vitess_client.entity_repository.delete(entity_id, revision_id)

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
