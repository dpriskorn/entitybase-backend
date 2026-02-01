"""Entity update transaction management."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
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
from models.rest_api.entitybase.v1.services.statement_service import StatementService

logger = logging.getLogger(__name__)


class UpdateTransaction(EntityTransaction):
    """Transaction for updating entities."""

    def process_statements(
        self,
        entity_id: str,
        request_data: PreparedRequestData,
        validator: Any,
    ) -> StatementHashResult:
        """Process statements for the entity transaction."""
        logger.info(
            f"[UpdateTransaction] Starting statement processing for {entity_id}"
        )
        # Import here to avoid circular imports
        ss = StatementService(state=self.state)

        hash_result = ss.hash_entity_statements(request_data)
        if not hash_result.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(
                f"Failed to hash statements: {hash_result.error}", status_code=500
            )

        # Store new statements
        assert hash_result.data is not None  # Guaranteed by success check above
        hash_data: StatementHashResult = hash_result.data
        store_result = ss.deduplicate_and_store_statements(hash_data, validator)
        if not store_result.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(
                f"Failed to store statements: {store_result.error}", status_code=500
            )

        # Record hashes for rollback
        self.statement_hashes.extend(hash_data.statements)

        return hash_data

    async def create_revision(self, request: CreateRevisionRequest) -> EntityResponse:
        logger.debug(f"[UpdateTransaction] Starting revision creation for {request.entity_id}")
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
        """Publish the entity change event to the stream.

        Creates and sends an EntityChangeEvent to the configured stream producer
        for downstream processing (e.g., notifications, logging).

        Note:
            The editor field in EntityChangeEvent is set to the editor parameter.
        """
        if changed_at is None:
            changed_at = datetime.now(timezone.utc)

        logger.info(f"[UpdateTransaction] Starting event publishing for {entity_id}")
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

    def _rollback_statement(self, hash_val: int) -> None:
        logger.info(f"[UpdateTransaction] Rolling back statement {hash_val}")
        # Decrement ref_count
        self.state.vitess_client.decrement_ref_count(hash_val)
        # Check if orphaned and delete from S3
        ref_count = self.state.vitess_client.get_ref_count(hash_val)
        if ref_count == 0:
            self.state.s3_client.delete_statement(hash_val)

    def commit(self) -> None:
        """Commit the update transaction."""
        logger.info(f"[UpdateTransaction] Committing update for {self.entity_id}")
        self.operations.clear()

    def rollback(self) -> None:
        """Rollback the update transaction."""
        logger.info(f"[UpdateTransaction] Rolling back update for {self.entity_id}")
        for op in reversed(self.operations):
            try:
                op()
            except Exception as e:
                logger.warning(f"[UpdateTransaction] Rollback operation failed: {e}")
        self.operations.clear()

    def _rollback_revision(self, entity_id: str, revision_id: int) -> None:
        logger.info(
            f"[UpdateTransaction] Rolling back revision {revision_id} for {entity_id}"
        )
        # Delete from entity_revisions and revert head
        self.state.vitess_client.delete_revision(entity_id, revision_id)
