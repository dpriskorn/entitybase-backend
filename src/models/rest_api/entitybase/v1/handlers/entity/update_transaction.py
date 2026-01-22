"""Entity update transaction management."""

import logging
from typing import Any
from datetime import datetime, timezone

from models.data.infrastructure.s3.enums import EntityType

from models.rest_api.entitybase.v1.response import EntityResponse
from models.rest_api.entitybase.v1.response import StatementHashResult

from models.rest_api.entitybase.v1.handlers.entity.entity_transaction import (
    EntityTransaction,
)
from models.data.infrastructure.stream.change_type import ChangeType
from models.rest_api.entitybase.v1.services.statement_service import StatementService

logger = logging.getLogger(__name__)


class UpdateTransaction(EntityTransaction):
    """Transaction for updating entities."""

    def process_statements(
        self,
        entity_id: str,
        request_data: dict,
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

    async def create_revision(
        self,
        entity_id: str,
        new_revision_id: int,
        head_revision_id: int,
        request_data: dict,
        entity_type: EntityType,
        hash_result: StatementHashResult,
        # content_hash: int,
        is_mass_edit: bool,
        edit_type: Any,
        edit_summary: str,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool,
        is_creation: bool,
        user_id: int,
    ) -> EntityResponse:
        logger.debug(f"[UpdateTransaction] Starting revision creation for {entity_id}")
        from models.rest_api.entitybase.v1.handlers.entity.handler import EntityHandler

        handler = EntityHandler(state=self.state)
        response = await handler.create_and_store_revision(
            entity_id=entity_id,
            new_revision_id=new_revision_id,
            head_revision_id=head_revision_id,
            request_data=request_data,
            entity_type=entity_type,
            hash_result=hash_result,
            is_mass_edit=is_mass_edit,
            edit_type=edit_type,
            edit_summary=edit_summary,
            is_semi_protected=is_semi_protected,
            is_locked=is_locked,
            is_archived=is_archived,
            is_dangling=is_dangling,
            is_mass_edit_protected=is_mass_edit_protected,
            is_creation=is_creation,
            user_id=user_id,
        )
        self.operations.append(
            lambda: self._rollback_revision(entity_id, new_revision_id)
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
        user_id: int = 0,
        changed_at: datetime | None = None,
        from_revision_id: int = 0,
        edit_summary: str = "",
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
        if self.state.stream_producer:
            from models.infrastructure.stream.event import EntityChangeEvent

            event = EntityChangeEvent(
                id=entity_id,
                rev=revision_id,
                type=ChangeType(change_type),
                from_rev=from_revision_id,
                at=changed_at,
                summary=edit_summary,
            )
            self.state.stream_producer.publish_change(event)
        # Events are fire-and-forget, no rollback needed

    def _rollback_statement(self, hash_val: int) -> None:
        logger.info(f"[UpdateTransaction] Rolling back statement {hash_val}")
        # Decrement ref_count
        self.state.vitess_client.decrement_ref_count(hash_val)
        # Check if orphaned and delete from S3
        ref_count = self.state.vitess_client.get_ref_count(hash_val)
        if ref_count == 0:
            self.state.s3_client.delete_statement(hash_val)

    def _rollback_revision(self, entity_id: str, revision_id: int) -> None:
        logger.info(
            f"[UpdateTransaction] Rolling back revision {revision_id} for {entity_id}"
        )
        # Delete from entity_revisions and revert head
        self.state.vitess_client.delete_revision(entity_id, revision_id)
