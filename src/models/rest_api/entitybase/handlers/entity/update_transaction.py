"""Entity update transaction management."""

import logging
from typing import Any

from models.infrastructure.s3.enums import EntityType
from models.rest_api.entitybase.response import EntityResponse
from models.rest_api.entitybase.response import StatementHashResult

from models.rest_api.entitybase.handlers.entity.entity_transaction import (
    EntityTransaction,
)


logger = logging.getLogger(__name__)


class UpdateTransaction(EntityTransaction):
    """Transaction for updating entities."""

    def process_statements(
        self,
        entity_id: str,
        request_data: dict,
        vitess_client: Any,
        s3_client: Any,
        validator: Any,
    ) -> StatementHashResult:
        """Process statements for the entity transaction."""
        logger.info(
            f"[UpdateTransaction] Starting statement processing for {entity_id}"
        )
        # Import here to avoid circular imports
        from models.rest_api.entitybase.services.statement_service import (
            hash_entity_statements,
        )

        hash_result = hash_entity_statements(request_data)
        if not hash_result.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(
                f"Failed to hash statements: {hash_result.error}", status_code=500
            )

        # Store new statements
        from models.rest_api.entitybase.services.statement_service import (
            deduplicate_and_store_statements,
        )

        store_result = deduplicate_and_store_statements(
            hash_result.data, vitess_client, s3_client, validator
        )
        if not store_result.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(
                f"Failed to store statements: {store_result.error}", status_code=500
            )

        # Record hashes for rollback
        self.statement_hashes.extend(hash_result.data.statements)

        return hash_result.data

    async def create_revision(
        self,
        entity_id: str,
        new_revision_id: int,
        head_revision_id: int,
        request_data: dict,
        entity_type: EntityType,
        hash_result: StatementHashResult,
        content_hash: int,
        is_mass_edit: bool,
        edit_type: Any,
        edit_summary: str,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool,
        vitess_client: Any,
        s3_client: Any,
        stream_producer: Any,
        is_creation: bool,
        user_id: int,
    ) -> EntityResponse:
        logger.debug(f"[UpdateTransaction] Starting revision creation for {entity_id}")
        from models.rest_api.entitybase.handlers.entity.handler import EntityHandler

        handler = EntityHandler()
        response = await handler._create_and_store_revision(
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
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=stream_producer,
            is_creation=is_creation,
            user_id=user_id,
        )
        self.operations.append(
            lambda: self._rollback_revision(entity_id, new_revision_id, vitess_client)
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
        **kwargs: Any,
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
            user_id: The id of the user who made the change.
            stream_producer: The producer instance for publishing events.

        Returns:
            None

        Note:
            The editor field in EntityChangeEvent is set to the editor parameter.
        """
        from_revision_id = kwargs.get('from_revision_id', 0)
        changed_at = kwargs.get('changed_at')
        edit_summary = kwargs.get('edit_summary', '')
        stream_producer = kwargs.get('stream_producer')

        logger.info(f"[UpdateTransaction] Starting event publishing for {entity_id}")
        if stream_producer:
            from models.infrastructure.stream.event import EntityChangeEvent

            event = EntityChangeEvent(
                id=entity_id,
                rev=revision_id,
                type=change_type,
                from_rev=from_revision_id,
                at=changed_at,
                summary=edit_summary,
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
