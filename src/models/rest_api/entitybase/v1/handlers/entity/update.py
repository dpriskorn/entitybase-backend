"""Entity update handlers."""

import logging
from typing import Any

from models.data.infrastructure.s3.enums import EntityType
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request import EntityUpdateRequest
from models.data.rest_api.v1.entitybase.request import UserActivityType
from models.data.rest_api.v1.entitybase.request.entity.revision import CreateRevisionRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.utils import raise_validation_error
from .handler import EntityHandler
from .update_transaction import UpdateTransaction

logger = logging.getLogger(__name__)


class EntityUpdateHandler(EntityHandler):
    """Handler for entity update operations"""

    async def update_entity(  # type: ignore[return]
        self,
        entity_id: str,
        request: EntityUpdateRequest,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update an existing entity with transaction rollback."""
        # Check entity exists (404 if not)
        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        # Check deletion status (410 if deleted)
        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        # Check lock status (423 if locked)
        if self.state.vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        # Validate JSON (Pydantic)
        # Already handled by FastAPI

        # Create transaction
        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id
        try:
            # Get head revision
            head_revision_id = tx.state.vitess_client.get_head(entity_id)
            # Prepare data
            request_data = request.data.copy()
            request_data["id"] = entity_id
            # Process statements
            hash_result = tx.process_statements(entity_id, request_data, validator)
            # Create revision
            revision_request = CreateRevisionRequest(
                entity_id=entity_id,
                new_revision_id=head_revision_id + 1,
                head_revision_id=head_revision_id,
                request_data=request_data,
                entity_type=EntityType(request.type),
                hash_result=hash_result,
                is_mass_edit=request.is_mass_edit,
                edit_type=request.edit_type,
                edit_summary=request.edit_headers.x_edit_summary,
                is_semi_protected=request.is_semi_protected,
                is_locked=request.is_locked,
                is_archived=request.is_archived,
                is_dangling=request.is_dangling,
                is_mass_edit_protected=request.is_mass_edit_protected,
                is_creation=False,
                user_id=request.edit_headers.x_user_id,
            )
            response = await tx.create_revision(revision_request)
            # Publish event
            tx.publish_event(
                entity_id=entity_id,
                revision_id=response.revision_id,
                change_type=ChangeType.EDIT,
                edit_headers=request.edit_headers,
                from_revision_id=head_revision_id,
                changed_at=None,  # TODO
            )
            # Log activity
            if request.edit_headers.x_user_id:
                activity_result = (
                    self.state.vitess_client.user_repository.log_user_activity(
                        user_id=request.edit_headers.x_user_id,
                        activity_type=UserActivityType.ENTITY_EDIT,
                        entity_id=entity_id,
                        revision_id=response.revision_id,
                    )
                )
                if not activity_result.success:
                    logger.warning(
                        f"Failed to log user activity: {activity_result.error}"
                    )

            # Commit
            tx.commit()
            return response  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Entity update failed for {entity_id}: {e}", exc_info=True)
            logger.error(f"Entity update failed - full details: {type(e).__name__}: {str(e)}")
            logger.error(f"Entity update failed - traceback:", exc_info=True)
            tx.rollback()
            raise_validation_error(f"Update failed: {type(e).__name__}: {str(e)}", status_code=500)
