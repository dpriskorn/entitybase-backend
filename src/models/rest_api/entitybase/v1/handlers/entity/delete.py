"""Entity deletion handlers."""

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from fastapi import HTTPException

from models.infrastructure.s3.hashes.hash_maps import (
    AliasesHashes,
    DescriptionsHashes,
    LabelsHashes,
    SitelinksHashes,
    StatementsHashes,
    HashMaps,
)
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.rest_api.entitybase.v1.handler import Handler
from models.rest_api.entitybase.v1.request.enums import UserActivityType

from models.infrastructure.s3.enums import DeleteType, EditType, EditData, EntityType
from models.rest_api.entitybase.v1.request.entity import EntityDeleteRequest
from models.rest_api.entitybase.v1.response import EntityDeleteResponse, EntityState
from models.config.settings import settings
from models.rest_api.utils import raise_validation_error
from models.infrastructure.stream.change_type import ChangeType
from models.infrastructure.stream.event import EntityChangeEvent


logger = logging.getLogger(__name__)


# noinspection PyArgumentList
class EntityDeleteHandler(Handler):
    """Handler for entity delete operations"""

    async def delete_entity(
        self,
        entity_id: str,
        request: EntityDeleteRequest,
        user_id: int = 0,
    ) -> EntityDeleteResponse:
        """Delete entity (soft or hard delete)."""
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if self.state.s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        logger.info(
            f"=== ENTITY DELETE START: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "delete_type": request.delete_type.value,
                "edit_summary": request.edit_summary,
                "operation": "delete_entity_start",
            },
        )

        # Check entity exists
        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        # Check if entity is already deleted
        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error(
                f"Entity {entity_id} has been deleted", status_code=410
            )

        head_revision_id = self.state.vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity not found", status_code=404)

        logger.debug(f"Current head revision for {entity_id}: {head_revision_id}")

        # Check protection settings
        protection_info = self.state.vitess_client.get_protection_info(entity_id)
        logger.debug(f"Protection info for {entity_id}: {protection_info}")

        try:
            # Archived items block all edits
            if protection_info and protection_info.is_archived:
                raise_validation_error(
                    "Item is archived and cannot be edited", status_code=403
                )

            # Locked items block all edits
            if protection_info and protection_info.get("is_locked", False):
                raise_validation_error("Item is locked from all edits", status_code=403)
        except (HTTPException, ValueError):
            raise
        except Exception:
            pass

        # Calculate next revision ID
        new_revision_id = head_revision_id + 1

        # Read current revision to preserve entity data
        current_revision = self.state.s3_client.read_revision(
            entity_id, head_revision_id
        )

        # Prepare deletion revision data
        revision_data = RevisionData(
            schema_version=settings.s3_schema_revision_version,
            revision_id=new_revision_id,
            entity_type=EntityType(current_revision.data.get("entity_type", "item")),
            properties=current_revision.data.get("properties", {}),
            property_counts=current_revision.data.get("property_counts", {}),
            hashes=HashMaps(
                statements=StatementsHashes(
                    root=current_revision.data.get("statements", [])
                ),
                sitelinks=SitelinksHashes(
                    root=current_revision.data.get("sitelinks_hashes", {})
                ),
                labels=LabelsHashes(
                    root=current_revision.data.get("labels_hashes", {})
                ),
                descriptions=DescriptionsHashes(
                    root=current_revision.data.get("descriptions_hashes", {})
                ),
                aliases=AliasesHashes(
                    root=current_revision.data.get("aliases_hashes", {})
                ),
            ),
            edit=EditData(
                mass=False,
                type=EditType.SOFT_DELETE
                if request.delete_type == DeleteType.SOFT
                else EditType.HARD_DELETE,
                user_id=user_id,
                summary=request.edit_summary,
                at=datetime.now(timezone.utc).isoformat(),
            ),
            state=EntityState(
                sp=current_revision.data.get("is_semi_protected", False),
                locked=current_revision.data.get("is_locked", False),
                archived=current_revision.data.get("is_archived", False),
                dangling=current_revision.data.get("is_dangling", False),
                mep=current_revision.data.get("is_mass_edit_protected", False),
                deleted=True,
            ),
        )

        # Decrement ref_count for hard delete
        if request.delete_type == DeleteType.HARD:
            old_statements = current_revision.data.get("statements", [])
            for statement_hash in old_statements:
                try:
                    self.state.vitess_client.decrement_ref_count(statement_hash)
                except Exception as e:
                    logger.warning(
                        f"Failed to decrement ref count for statement {statement_hash}: {e}"
                    )

        # Write deletion revision to S3
        self.state.s3_client.write_revision(
            entity_id=entity_id,
            revision_id=new_revision_id,
            data=revision_data,
        )

        # Update head pointer
        self.state.vitess_client.create_revision(
            entity_id=entity_id,
            revision_id=new_revision_id,
            expected_revision_id=head_revision_id,
            entity_data={},
        )

        # Publish change event
        if self.state.stream_producer:
            try:
                # change_type = (
                #     ChangeType.SOFT_DELETE
                #     if request.delete_type == DeleteType.SOFT
                #     else ChangeType.HARD_DELETE
                # )
                await self.state.stream_producer.publish_change(
                    EntityChangeEvent(
                        id=entity_id,
                        rev=new_revision_id,
                        type=ChangeType.SOFT_DELETE,
                        from_rev=head_revision_id,
                        at=datetime.now(timezone.utc),
                        summary=request.edit_summary,
                    )
                )
                logger.debug(
                    f"Entity {entity_id}: Published delete event for revision {new_revision_id}"
                )
            except Exception as e:
                logger.warning(
                    f"Entity {entity_id}: Failed to publish delete event: {e}"
                )

        # Log activity
        if user_id > 0:
            activity_result = (
                self.state.vitess_client.user_repository.log_user_activity(
                    user_id=user_id,
                    activity_type=UserActivityType.ENTITY_DELETE,
                    entity_id=entity_id,
                    revision_id=new_revision_id,
                )
            )
            if not activity_result.success:
                logger.warning(f"Failed to log user activity: {activity_result.error}")

        return EntityDeleteResponse(
            id=entity_id,
            rev_id=new_revision_id,
            is_deleted=True,
            del_type=str(request.delete_type.value),
            del_status="soft_deleted"
            if request.delete_type == DeleteType.SOFT
            else "hard_deleted",
        )
