"""Entity update handlers."""

import logging
from typing import Any

from pydantic import Field

from models.validation.utils import raise_validation_error

from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from .base import EntityHandler
from .update_transaction import UpdateTransaction
from ...request import EntityUpdateRequest
from ...response import EntityResponse

logger = logging.getLogger(__name__)


class EntityUpdateHandler(EntityHandler):
    """Handler for entity update operations"""

    async def update_entity(  # type: ignore[return]
        self,
        entity_id: str,
        request: EntityUpdateRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
        user_id: int | None = None,
    ) -> EntityResponse:
        """Update an existing entity with transaction rollback."""
        # Check entity exists (404 if not)
        if not vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        # Check deletion status (410 if deleted)
        if vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        # Check lock status (423 if locked)
        if vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        # Validate JSON (Pydantic)
        # Already handled by FastAPI

        # Create transaction
        tx = UpdateTransaction()
        tx.entity_id = entity_id
        try:
            # Get head revision
            tx.get_head(vitess_client)
            # Prepare data
            request_data = request.data.copy()
            request_data["id"] = entity_id
            # Process statements
            hash_result = tx.process_statements(
                entity_id, request_data, vitess_client, s3_client, validator
            )
            # Create revision
            response = await tx.create_revision(
                entity_id=entity_id,
                new_revision_id=tx.head_revision_id + 1,
                head_revision_id=tx.head_revision_id,
                request_data=request_data,
                entity_type=request.type,
                hash_result=hash_result,
                content_hash=0,  # TODO: calculate
                is_mass_edit=request.is_mass_edit,
                edit_type=request.edit_type,
                edit_summary=request.edit_summary,
                editor=request.editor,
                is_semi_protected=request.is_semi_protected,
                is_locked=request.is_locked,
                is_archived=request.is_archived,
                is_dangling=request.is_dangling,
                is_mass_edit_protected=request.is_mass_edit_protected,
                vitess_client=vitess_client,
                stream_producer=stream_producer,
                is_creation=False,
            )
            # Publish event
            tx.publish_event(
                entity_id=entity_id,
                revision_id=response.revision_id,
                change_type="edit",
                from_revision_id=tx.head_revision_id,
                changed_at=None,  # TODO
                editor=request.editor,
                edit_summary=request.edit_summary,
                stream_producer=stream_producer,
            )
            # Log activity
            if user_id:
                vitess_client.user_repository.log_user_activity(
                    user_id=user_id,
                    activity_type="entity_edit",
                    entity_id=entity_id,
                    revision_id=response.revision_id,
                )

            # Commit
            tx.commit()
            return response
        except Exception as e:
            logger.error(f"Entity update failed for {entity_id}: {e}")
            tx.rollback()
            raise_validation_error("Update failed", status_code=500)
