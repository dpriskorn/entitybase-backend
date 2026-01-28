"""Entity deletion handlers."""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException

from models.common import EditHeaders
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import DeleteType, EditType, EditData, EntityType
from models.data.infrastructure.s3.hashes.aliases_hashes import AliasesHashes
from models.data.infrastructure.s3.hashes.descriptions_hashes import DescriptionsHashes
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.labels_hashes import LabelsHashes
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinksHashes
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request import EntityDeleteRequest
from models.data.rest_api.v1.entitybase.request import UserActivityType
from models.data.rest_api.v1.entitybase.response import EntityDeleteResponse
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.stream.event import EntityChangeEvent
from models.rest_api.entitybase.v1.handler import Handler
from models.rest_api.utils import raise_validation_error

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
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if self.state.s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        logger.info(
            f"=== ENTITY DELETE START: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "delete_type": request.delete_type.value,
                "edit_summary": edit_headers.x_edit_summary,
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
        from models.config.settings import settings
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
                    root=current_revision.data.get("sitelinks", {})
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
                user_id=edit_headers.x_user_id,
                summary=edit_headers.x_edit_summary,
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
        import json
        from models.internal_representation.metadata_extractor import MetadataExtractor
        from models.data.infrastructure.s3.revision_data import S3RevisionData
        from models.config.settings import settings

        revision_dict = revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)

        s3_revision_data = S3RevisionData(
            schema=settings.s3_schema_revision_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        self.state.s3_client.store_revision(content_hash, s3_revision_data)

        # Update head pointer
        self.state.vitess_client.create_revision(
            entity_id=entity_id,
            revision_id=new_revision_id,
            entity_data=revision_data,
            expected_revision_id=head_revision_id,
            content_hash=content_hash,
        )

        # Publish change event
        if self.state.entity_change_stream_producer:
            try:
                # change_type = (
                #     ChangeType.SOFT_DELETE
                #     if request.delete_type == DeleteType.SOFT
                #     else ChangeType.HARD_DELETE
                # )
                await self.state.entity_change_stream_producer.publish_change(
                    EntityChangeEvent(
                        id=entity_id,
                        rev=new_revision_id,
                        type=ChangeType.SOFT_DELETE,
                        from_rev=head_revision_id,
                        at=datetime.now(timezone.utc),
                        summary=edit_headers.x_edit_summary,
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
        if edit_headers.x_user_id > 0:
            activity_result = (
                self.state.vitess_client.user_repository.log_user_activity(
                    user_id=edit_headers.x_user_id,
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
