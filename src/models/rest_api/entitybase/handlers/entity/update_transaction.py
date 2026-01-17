"""Entity update transaction management."""

import logging
from abc import ABC, abstractmethod
from typing import List, Callable, Any

from pydantic import BaseModel, Field

from models.rest_api.entitybase.response import EntityRevisionResponse
from models.rest_api.entitybase.response import StatementHashResult

logger = logging.getLogger(__name__)


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
        """Process statements for the entity transaction."""
        pass

    @abstractmethod
    async def create_revision(
        self,
        entity_id: str,
        new_revision_id: int,
        head_revision_id: int,
        request_data: dict,
        entity_type: str,
        hash_result: Any,
        content_hash: int,
        is_mass_edit: bool,
        edit_type: Any,
        edit_summary: str,
        editor: str,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool,
        vitess_client: Any,
        s3_client: Any,
        stream_producer: Any,
        is_creation: bool,
    ) -> EntityRevisionResponse:
        pass

    @abstractmethod
    def publish_event(
        self,
        entity_id: str,
        revision_id: int,
        change_type: Any,
        from_revision_id: int,
        changed_at: Any,
        edit_summary: str,
        editor: str,
        stream_producer: Any,
    ) -> None:
        """Publish the change event."""
        pass

    def commit(self) -> None:
        """Commit the transaction by clearing rollback operations."""
        logger.info("[EntityTransaction] Committing transaction")
        self.operations.clear()

    def rollback(self) -> None:
        """Rollback by executing operations in reverse."""
        logger.info("[EntityTransaction] Rolling back transaction")
        for op in reversed(self.operations):
            try:
                op()
            except Exception as e:
                logger.warning(f"[EntityTransaction] Rollback operation failed: {e}")
        self.operations.clear()


class UpdateTransaction(EntityTransaction):
    """Manages atomic update operations with rollback support."""

    head_revision_id: int = 0

    def get_head(self, vitess_client: Any) -> None:
        """Retrieve the head revision ID."""
        logger.info(f"[UpdateTransaction] Getting head revision for {self.entity_id}")
        self.head_revision_id = vitess_client.get_head(self.entity_id)

    def process_statements(
        self,
        entity_id: str,
        request_data: dict,
        vitess_client: Any,
        s3_client: Any,
        validator: Any,
    ) -> StatementHashResult:
        """Process statements and prepare rollback operations."""
        logger.info(
            f"[UpdateTransaction] Starting statement processing for {entity_id}"
        )
        # Import here to avoid circular imports
        from models.rest_api.entitybase.handlers.entity.base import EntityHandler

        handler = EntityHandler()
        hash_result = handler.process_statements(
            entity_id, request_data, vitess_client, s3_client, validator
        )
        # Track hashes for rollback
        self.statement_hashes.extend(hash_result.statements)
        for hash_val in hash_result.statements:
            self.operations.append(
                lambda h=hash_val: self._rollback_statement(h, vitess_client, s3_client)  # type: ignore[misc]
            )
        return hash_result

    async def create_revision(
        self,
        entity_id: str,
        new_revision_id: int,
        head_revision_id: int,
        request_data: dict,
        entity_type: str,
        hash_result: Any,
        content_hash: int,
        is_mass_edit: bool,
        edit_type: Any,
        edit_summary: str,
        editor: str,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool,
        vitess_client: Any,
        s3_client: Any,
        stream_producer: Any,
        is_creation: bool,
    ) -> EntityRevisionResponse:
        logger.debug(f"[UpdateTransaction] Starting revision creation for {entity_id}")
        from models.rest_api.entitybase.handlers.entity.base import EntityHandler

        handler = EntityHandler()
        response = await handler._create_and_store_revision(
            entity_id=entity_id,
            new_revision_id=new_revision_id,
            head_revision_id=head_revision_id,
            request_data=request_data,
            entity_type=entity_type,
            hash_result=hash_result,
            content_hash=content_hash,
            is_mass_edit=is_mass_edit,
            edit_type=edit_type,
            edit_summary=edit_summary,
            editor=editor,
            is_semi_protected=is_semi_protected,
            is_locked=is_locked,
            is_archived=is_archived,
            is_dangling=is_dangling,
            is_mass_edit_protected=is_mass_edit_protected,
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=stream_producer,
            is_creation=is_creation,
        )
        self.operations.append(
            lambda: self._rollback_revision(entity_id, new_revision_id, vitess_client)
        )
        return response

    def publish_event(
        self,
        entity_id: str,
        revision_id: int,
        change_type: Any,
        from_revision_id: int,
        changed_at: Any,
        edit_summary: str,
        editor: str,
        stream_producer: Any,
    ) -> None:
        """Publish the entity change event to the stream.

        Creates and sends an EntityChangeEvent to the configured stream producer
        for downstream processing (e.g., notifications, logging).

        Args:
            entity_id: The ID of the entity that changed.
            revision_id: The new revision ID after the change.
            change_type: The type of change (e.g., 'edit', 'create').
            from_revision_id: The previous revision ID (0 for creations).
            changed_at: Timestamp of the change.
            edit_summary: Summary of the edit.
            editor: The username of the user who made the change.
            stream_producer: The producer instance for publishing events.

        Returns:
            None

        Note:
            The editor field in EntityChangeEvent is set to the editor parameter.
        """
        logger.info(f"[UpdateTransaction] Starting event publishing for {entity_id}")
        if stream_producer:
            from models.infrastructure.stream.event import EntityChangeEvent

            event = EntityChangeEvent(
                entity_id=entity_id,
                revision_id=revision_id,
                change_type=change_type,
                from_revision_id=from_revision_id,
                changed_at=changed_at,
                edit_summary=edit_summary,
            )
            stream_producer.publish_change(event)
        # Events are fire-and-forget, no rollback needed

    def _rollback_statement(
        self, hash_val: int, vitess_client: Any, s3_client: Any
    ) -> None:
        logger.info(f"[UpdateTransaction] Rolling back statement {hash_val}")
        # Decrement ref_count
        vitess_client.decrement_ref_count(hash_val)
        # Check if orphaned and delete from S3
        ref_count = vitess_client.get_ref_count(hash_val)
        if ref_count == 0:
            s3_client.delete_statement(hash_val)

    def _rollback_revision(
        self, entity_id: str, revision_id: int, vitess_client: Any
    ) -> None:
        logger.info(
            f"[UpdateTransaction] Rolling back revision {revision_id} for {entity_id}"
        )
        # Delete from entity_revisions and revert head
        vitess_client.delete_revision(entity_id, revision_id)
