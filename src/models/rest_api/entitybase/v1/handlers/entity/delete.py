"""Entity deletion handlers."""

import logging

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.infrastructure.s3.enums import DeleteType
from models.data.rest_api.v1.entitybase.request import EditContext, EntityDeleteRequest
from models.data.rest_api.v1.entitybase.response import EntityDeleteResponse
from models.rest_api.entitybase.v1.handler import Handler
from models.rest_api.entitybase.v1.services.delete_service import DeleteService

logger = logging.getLogger(__name__)


# noinspection PyArgumentList
class EntityDeleteHandler(Handler):
    """Handler for entity delete operations"""

    async def delete_entity(
        self,
        entity_id: str,
        request: EntityDeleteRequest,
        edit_headers: EditHeaders,
    ) -> EntityDeleteResponse:
        """Delete entity (soft or hard delete)."""
        delete_service = DeleteService(state=self.state)

        logger.info(
            f"=== ENTITY DELETE START: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "delete_type": request.delete_type.value,
                "edit_summary": edit_headers.x_edit_summary,
                "operation": "delete_entity_start",
            },
        )

        delete_service.validate_delete_preconditions()
        head_revision_id = delete_service.validate_entity_state(entity_id)
        delete_service.validate_protection_status(entity_id)

        new_revision_id = head_revision_id + 1

        current_revision = self.state.s3_client.read_revision(
            entity_id, head_revision_id
        )

        edit_context = EditContext(
            user_id=edit_headers.x_user_id,
            edit_summary=edit_headers.x_edit_summary,
        )

        revision_data = delete_service.build_deletion_revision(
            entity_id=entity_id,
            current_revision=current_revision,
            new_revision_id=new_revision_id,
            request=request,
            edit_context=edit_context,
        )

        if request.delete_type == DeleteType.HARD:
            old_statements = current_revision.data.get("statements", [])
            delete_service.decrement_statement_references(old_statements)

        content_hash, s3_revision_data = delete_service.store_deletion_revision(
            revision_data
        )

        self.state.vitess_client.create_revision(
            entity_id=entity_id,
            revision_id=new_revision_id,
            entity_data=revision_data,
            expected_revision_id=head_revision_id,
            content_hash=content_hash,
        )

        await delete_service.publish_delete_event(
            entity_id=entity_id,
            new_revision_id=new_revision_id,
            head_revision_id=head_revision_id,
            edit_summary=edit_headers.x_edit_summary,
        )

        delete_service.log_delete_activity(
            user_id=edit_headers.x_user_id,
            entity_id=entity_id,
            new_revision_id=new_revision_id,
        )

        del_status = (
            "soft_deleted"
            if request.delete_type == DeleteType.SOFT
            else "hard_deleted"
        )

        return EntityDeleteResponse(
            id=entity_id,
            rev_id=new_revision_id,
            is_deleted=True,
            del_type=str(request.delete_type.value),
            del_status=del_status,
        )
