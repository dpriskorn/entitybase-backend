"""Entity update handlers."""

import logging
from typing import Any

from models.infrastructure.s3.enums import EntityType
from models.infrastructure.s3.client import MyS3Client
from models.infrastructure.stream.change_type import ChangeType
from ...request.enums import UserActivityType
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess.client import VitessClient
from models.rest_api.utils import raise_validation_error
from models.rest_api.entitybase.v1.request import EntityUpdateRequest
from .handler import EntityHandler
from .update_transaction import UpdateTransaction

from models.rest_api.entitybase.v1.response import EntityResponse

logger = logging.getLogger(__name__)


class EntityUpdateHandler(EntityHandler):
    """Handler for entity update operations"""

    async def update_entity(  # type: ignore[return]
        self,
        entity_id: str,
        request: EntityUpdateRequest,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
        user_id: int = 0,
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
                entity_type=EntityType(request.type),
                hash_result=hash_result,
                content_hash=0,  # TODO: calculate
                is_mass_edit=request.is_mass_edit,
                edit_type=request.edit_type,
                edit_summary=request.edit_summary,
                is_semi_protected=request.is_semi_protected,
                is_locked=request.is_locked,
                is_archived=request.is_archived,
                is_dangling=request.is_dangling,
                is_mass_edit_protected=request.is_mass_edit_protected,
                vitess_client=vitess_client,
                s3_client=s3_client,
                stream_producer=stream_producer,
                is_creation=False,
                user_id=request.user_id,
            )
            # Publish event
            tx.publish_event(
                entity_id=entity_id,
                revision_id=response.revision_id,
                change_type=ChangeType.EDIT,
                user_id=0,  # TODO: get from auth
                from_revision_id=tx.head_revision_id,
                changed_at=None,  # TODO
                edit_summary=request.edit_summary,
                stream_producer=stream_producer,
            )
            # Log activity
            if user_id:
                activity_result = vitess_client.user_repository.log_user_activity(
                    user_id=user_id,
                    activity_type=UserActivityType.ENTITY_EDIT,
                    entity_id=entity_id,
                    revision_id=response.revision_id,
                )
                if not activity_result.success:
                    logger.warning(
                        f"Failed to log user activity: {activity_result.error}"
                    )

            # Commit
            tx.commit()
            return response  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Entity update failed for {entity_id}: {e}")
            tx.rollback()
            raise_validation_error("Update failed", status_code=500)
