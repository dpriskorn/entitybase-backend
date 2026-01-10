import logging
from datetime import datetime, timezone

from fastapi import HTTPException

from models.api_models import DeleteType, EntityDeleteRequest, EntityDeleteResponse
from models.config.settings import settings
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import (
    ChangeType,
    EntityChangeEvent,
    StreamProducerClient,
)
from models.infrastructure.vitess_client import VitessClient

logger = logging.getLogger(__name__)


class EntityDeleteHandler:
    """Handler for entity delete operations"""

    async def delete_entity(
        self,
        entity_id: str,
        request: EntityDeleteRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
    ) -> EntityDeleteResponse:
        """Delete entity (soft or hard delete)."""
        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        if s3_client is None:
            raise HTTPException(status_code=503, detail="S3 not initialized")

        logger.info(
            f"=== ENTITY DELETE START: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "delete_type": request.delete_type.value,
                "edit_summary": request.edit_summary,
                "editor": request.editor,
                "bot": request.bot,
                "operation": "delete_entity_start",
            },
        )

        # Check entity exists
        if not vitess_client.entity_exists(entity_id):
            raise HTTPException(status_code=404, detail="Entity not found")

        # Check if entity is already deleted
        if vitess_client.is_entity_deleted(entity_id):
            raise HTTPException(
                status_code=410, detail=f"Entity {entity_id} has been deleted"
            )

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise HTTPException(status_code=404, detail="Entity not found")

        logger.debug(f"Current head revision for {entity_id}: {head_revision_id}")

        # Check protection settings
        protection_info = vitess_client.get_protection_info(entity_id)
        logger.debug(f"Protection info for {entity_id}: {protection_info}")

        try:
            # Archived items block all edits
            if protection_info.get("is_archived", False):
                raise HTTPException(403, "Item is archived and cannot be edited")

            # Locked items block all edits
            if protection_info.get("is_locked", False):
                raise HTTPException(403, "Item is locked from all edits")
        except HTTPException:
            raise
        except Exception:
            pass

        # Calculate next revision ID
        new_revision_id = head_revision_id + 1

        # Read current revision to preserve entity data
        current_revision = s3_client.read_revision(entity_id, head_revision_id)

        # Prepare deletion revision data
        edit_type = (
            "soft_delete" if request.delete_type == DeleteType.SOFT else "hard_delete"
        )

        revision_data = {
            "schema_version": settings.s3_revision_version,
            "revision_id": new_revision_id,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "created_by": "rest-api",
            "entity_type": current_revision.data.get("entity_type", "item"),
            "entity": current_revision.data.get("entity", {}),
            "statements": current_revision.data.get("statements", []),
            "properties": current_revision.data.get("properties", {}),
            "property_counts": current_revision.data.get("property_counts", {}),
            "content_hash": current_revision.data.get("content_hash", 0),
            "edit_summary": request.edit_summary,
            "editor": request.editor,
            "edit_type": edit_type,
            "is_semi_protected": current_revision.data.get("is_semi_protected", False),
            "is_locked": current_revision.data.get("is_locked", False),
            "is_archived": current_revision.data.get("is_archived", False),
            "is_dangling": current_revision.data.get("is_dangling", False),
            "is_mass_edit_protected": current_revision.data.get(
                "is_mass_edit_protected", False
            ),
            "is_deleted": True,
            "is_redirect": False,
        }

        # Decrement ref_count for hard delete
        if request.delete_type == DeleteType.HARD:
            old_statements = current_revision.data.get("statements", [])
            for statement_hash in old_statements:
                try:
                    vitess_client.decrement_ref_count(statement_hash)
                except Exception as e:
                    logger.warning(
                        f"Failed to decrement ref count for statement {statement_hash}: {e}"
                    )

        # Write deletion revision to S3
        s3_client.write_revision(
            entity_id=entity_id, revision_id=new_revision_id, data=revision_data
        )

        # Update head pointer
        vitess_client.create_revision(entity_id, new_revision_id, revision_data)

        # Publish change event
        if stream_producer:
            try:
                change_type = (
                    ChangeType.SOFT_DELETE
                    if request.delete_type == DeleteType.SOFT
                    else ChangeType.HARD_DELETE
                )
                await stream_producer.publish_change(
                    EntityChangeEvent(
                        entity_id=entity_id,
                        revision_id=new_revision_id,
                        change_type=change_type,
                        from_revision_id=head_revision_id,
                        changed_at=datetime.now(timezone.utc),
                        editor=request.editor,
                        edit_summary=request.edit_summary,
                    )
                )
                logger.debug(
                    f"Entity {entity_id}: Published delete event for revision {new_revision_id}"
                )
            except Exception as e:
                logger.warning(
                    f"Entity {entity_id}: Failed to publish delete event: {e}"
                )

        return EntityDeleteResponse(
            id=entity_id,
            revision_id=new_revision_id,
            is_deleted=True,
            deletion_type=str(request.delete_type.value),
            deletion_status="soft_deleted"
            if request.delete_type == DeleteType.SOFT
            else "hard_deleted",
        )
