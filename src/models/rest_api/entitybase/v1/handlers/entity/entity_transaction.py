"""Base class for entity transactions."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable, List

from pydantic import BaseModel, Field

from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData, EditContext, EventPublishContext
from models.data.rest_api.v1.entitybase.response import StatementHashResult

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
        request_data: PreparedRequestData,
        validator: Any,
    ) -> StatementHashResult:
        """Process statements for the transaction."""
        pass

    def register_entity(self, entity_id: str) -> None:
        """Register the entity in the database."""
        logger.info(f"[EntityTransaction] Registering entity {entity_id}")
        self.entity_id = entity_id
        self.state.vitess_client.entity_repository.create_entity(entity_id)
        self.operations.append(lambda: self._rollback_entity_registration())

    def _rollback_entity_registration(self) -> None:
        """Rollback entity registration."""
        logger.info(
            f"[EntityTransaction] Rolling back entity registration for {self.entity_id}"
        )
        self.state.vitess_client.entity_repository.delete_entity(self.entity_id)

    def _rollback_revision(
        self,
        entity_id: str,
        revision_id: int,
    ) -> None:
        """Rollback a revision."""
        logger.info(
            f"[EntityTransaction] Rolling back revision {revision_id} for {entity_id}"
        )
        self.state.vitess_client.entity_repository.delete(entity_id, revision_id)

    def publish_event(
        self,
        event_context: EventPublishContext,
        edit_context: EditContext,
    ) -> None:
        """Publish a change event."""
        from models.infrastructure.stream.event import EntityChangeEvent
        from models.data.infrastructure.stream.change_type import ChangeType

        changed_at = event_context.changed_at
        if changed_at is None:
            changed_at = datetime.now(timezone.utc)

        logger.info(
            f"[EntityTransaction] Publishing event for {event_context.entity_id} revision {event_context.revision_id}"
        )
        event = EntityChangeEvent(
            id=event_context.entity_id,
            rev=event_context.revision_id,
            type=ChangeType(event_context.change_type),
            from_rev=event_context.from_revision_id,
            at=changed_at,
            summary=edit_context.edit_summary,
        )
        # TODO: Publish to stream
        logger.debug(f"Event: {event}")
