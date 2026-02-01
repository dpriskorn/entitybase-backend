"""Entity creation transaction management."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from models.common import EditHeaders
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.entity.revision import CreateRevisionRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.rest_api.entitybase.v1.handlers.entity.entity_transaction import (
    EntityTransaction,
)

logger = logging.getLogger(__name__)


class CreationTransaction(EntityTransaction):
    def process_statements(
        self,
        entity_id: str,
        request_data: PreparedRequestData,
        validator: Any,
    ) -> StatementHashResult:
        """Process statements for the entity transaction."""
        logger.info(
            f"[CreationTransaction] Starting statement processing for {entity_id}"
        )
        # Import here to avoid circular imports
        from models.rest_api.entitybase.v1.handlers.entity.handler import EntityHandler

        handler = EntityHandler(state=self.state)
        hash_result = handler.process_statements(entity_id, request_data, validator)
        # Track hashes for rollback
        self.statement_hashes.extend(hash_result.statements)
        for hash_val in hash_result.statements:
            self.operations.append(
                lambda h=hash_val: self._rollback_statement(h)  # type: ignore[misc]
            )
        return hash_result

    async def create_revision(self, request: CreateRevisionRequest) -> EntityResponse:
        logger.debug(f"Creating revision for {request.entity_id}")
        from models.rest_api.entitybase.v1.handlers.entity.handler import EntityHandler

        handler = EntityHandler(state=self.state)
        response = await handler.create_and_store_revision(request)
        self.operations.append(
            lambda: self._rollback_revision(request.entity_id, request.new_revision_id)
        )
        if not response.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(response.error or "Failed to create revision")
        assert isinstance(response.data, EntityResponse)
        return response.data

    def publish_event(
        self,
        entity_id: str,
        revision_id: int,
        change_type: str,
        edit_headers: EditHeaders,
        changed_at: datetime | None = None,
        from_revision_id: int = 0,
    ) -> None:
        """Publish the entity creation event."""
        if changed_at is None:
            changed_at = datetime.now()
        logger.info(f"[CreationTransaction] Starting event publishing for {entity_id}")
        if self.state.entity_change_stream_producer:
            from models.infrastructure.stream.event import EntityChangeEvent

            event = EntityChangeEvent(
                id=entity_id,
                rev=revision_id,
                type=ChangeType(change_type),
                from_rev=from_revision_id,
                at=changed_at,
                summary=edit_headers.x_edit_summary,
            )
            self.state.entity_change_stream_producer.publish_change(event)
        # Events are fire-and-forget, no rollback needed

    def commit(self) -> None:
        """Commit the creation transaction."""
        logger.info(f"[CreationTransaction] Committing creation for {self.entity_id}")

        self.operations.clear()  # Prevent rollback after commit

    def rollback(self) -> None:
        """Rollback the creation transaction."""
        logger.info(f"[CreationTransaction] Rolling back creation for {self.entity_id}")
        for op in reversed(self.operations):
            try:
                op()
            except Exception as e:
                logger.warning(f"[CreationTransaction] Rollback operation failed: {e}")
        self.operations.clear()

    # Private rollback methods
    def _rollback_entity_registration(self) -> None:
        logger.info(
            f"[CreationTransaction] Rolling back entity registration for {self.entity_id}"
        )
        # TODO: Delete from entity_id_mapping if possible
        # Since register_entity just inserts, and we assume no conflicts, perhaps no action needed
        pass

    def _rollback_statement(self, hash_val: int) -> None:
        logger.info(f"[CreationTransaction] Rolling back statement {hash_val}")
        # Decrement ref_count
        self.state.vitess_client.decrement_ref_count(hash_val)
        # Check if orphaned and delete from S3
        ref_count = self.state.vitess_client.get_ref_count(hash_val)
        if ref_count == 0:
            self.state.s3_client.delete_statement(hash_val)

    def _rollback_revision(self, entity_id: str, revision_id: int) -> None:
        logger.info(
            f"[CreationTransaction] Rolling back revision {revision_id} for {entity_id}"
        )
        # Delete from entity_revisions and entity_head
        self.state.vitess_client.delete_revision(entity_id, revision_id)
        # S3 deletion if needed, but assume Vitess handles it or add s3_client.delete_revision
