"""Service for entity deletion operations."""

import json
import logging
from datetime import datetime, timezone

from models.config.settings import settings
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import DeleteType, EditData, EditType, EntityType
from models.data.infrastructure.s3.hashes.aliases_hashes import AliasesHashes
from models.data.infrastructure.s3.hashes.descriptions_hashes import DescriptionsHashes
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.labels_hashes import LabelsHashes
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinkHashes
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.data.infrastructure.stream import ChangeType
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request import EntityDeleteRequest, UserActivityType
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.stream.event import EntityChangeEvent
from models.internal_representation.metadata_extractor import MetadataExtractor
from models.rest_api.entitybase.v1.service import Service
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


# noinspection PyArgumentList
class DeleteService(Service):
    """Service for handling entity deletion logic."""

    def validate_delete_preconditions(self) -> None:
        """Validate that required services are initialized."""
        if self.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if self.state.s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

    def validate_entity_state(self, entity_id: str) -> int:
        """Validate entity exists and retrieve current head revision.

        Args:
            entity_id: The entity ID to validate

        Returns:
            The current head revision ID

        Raises:
            ValueError: If entity doesn't exist or is already deleted
        """
        if not self.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        if self.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error(
                f"Entity {entity_id} has been deleted", status_code=410
            )

        head_revision_id = self.vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity not found", status_code=404)

        logger.debug(f"Current head revision for {entity_id}: {head_revision_id}")
        return int(head_revision_id)

    def validate_protection_status(self, entity_id: str) -> None:
        """Check if entity is protected from edits.

        Args:
            entity_id: The entity ID to check

        Raises:
            ValueError: If entity is archived or locked
        """
        from fastapi import HTTPException

        protection_info = self.vitess_client.get_protection_info(entity_id)
        logger.debug(f"Protection info for {entity_id}: {protection_info}")

        try:
            if protection_info and protection_info.is_archived:
                raise_validation_error(
                    "Item is archived and cannot be edited", status_code=403
                )

            if protection_info and protection_info.get("is_locked", False):
                raise_validation_error("Item is locked from all edits", status_code=403)
        except (HTTPException, ValueError):
            raise
        except Exception:
            pass

    @staticmethod
    def build_deletion_revision(
            entity_id: str,
        current_revision: S3RevisionData,
        new_revision_id: int,
        request: EntityDeleteRequest,
        edit_context: EditContext,
    ) -> RevisionData:
        """Build the deletion revision data.

        Args:
            entity_id: The entity ID being deleted
            current_revision: Current revision from S3
            new_revision_id: The new revision ID for deletion
            request: The delete request
            edit_context: Context containing user_id and edit_summary

        Returns:
            RevisionData for the deletion
        """
        edit_type = (
            EditType.SOFT_DELETE
            if request.delete_type == DeleteType.SOFT
            else EditType.HARD_DELETE
        )

        logger.debug(f"Building deletion revision for {entity_id}, revision {new_revision_id}, type={edit_type}")

        deletion_revision = RevisionData(
            schema_version=settings.s3_schema_revision_version,
            revision_id=new_revision_id,
            entity_type=EntityType(current_revision.revision.get("entity_type", "item")),
            properties=current_revision.revision.get("properties", {}),
            property_counts=current_revision.revision.get("property_counts", {}),
            hashes=HashMaps(
                statements=StatementsHashes(
                    root=current_revision.revision.get("statements", [])
                ),
                sitelinks=SitelinkHashes(
                    root=current_revision.revision.get("sitelinks", {})
                ),
                labels=LabelsHashes(
                    root=current_revision.revision.get("labels_hashes", {})
                ),
                descriptions=DescriptionsHashes(
                    root=current_revision.revision.get("descriptions_hashes", {})
                ),
                aliases=AliasesHashes(
                    root=current_revision.revision.get("aliases_hashes", {})
                ),
            ),
            edit=EditData(
                mass=False,
                type=edit_type,
                user_id=edit_context.user_id,
                summary=edit_context.edit_summary,
                at=datetime.now(timezone.utc).isoformat(),
            ),
            state=EntityState(
                sp=current_revision.revision.get("is_semi_protected", False),
                locked=current_revision.revision.get("is_locked", False),
                archived=current_revision.revision.get("is_archived", False),
                dangling=current_revision.revision.get("is_dangling", False),
                mep=current_revision.revision.get("is_mass_edit_protected", False),
                deleted=True,
            ),
        )

        logger.debug(f"Deletion revision built successfully for {entity_id}, revision {new_revision_id}")

        return deletion_revision

    def decrement_statement_references(self, statement_hashes: list[int]) -> None:
        """Decrement reference counts for statements during hard delete.

        Args:
            statement_hashes: List of statement hashes to decrement
        """
        for statement_hash in statement_hashes:
            try:
                self.vitess_client.decrement_ref_count(statement_hash)
            except Exception as e:
                logger.warning(
                    f"Failed to decrement ref count for statement {statement_hash}: {e}"
                )

    def store_deletion_revision(
        self, revision_data: RevisionData
    ) -> tuple[int, S3RevisionData]:
        """Store the deletion revision to S3.

        Args:
            revision_data: The revision data to store

        Returns:
            Tuple of (content_hash, s3_revision_data)
        """
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
        return content_hash, s3_revision_data

    async def publish_delete_event(
        self,
        entity_id: str,
        new_revision_id: int,
        head_revision_id: int,
        edit_summary: str,
    ) -> None:
        """Publish entity deletion event to stream.

        Args:
            entity_id: The entity ID being deleted
            new_revision_id: The new revision ID
            head_revision_id: The previous head revision ID
            edit_summary: Edit summary for the deletion
        """
        if self.state.entity_change_stream_producer:
            try:
                await self.state.entity_change_stream_producer.publish_change(
                    EntityChangeEvent(
                        id=entity_id,
                        rev=new_revision_id,
                        type=ChangeType.SOFT_DELETE,
                        from_rev=head_revision_id,
                        at=datetime.now(timezone.utc),
                        summary=edit_summary,
                    )
                )
                logger.debug(
                    f"Entity {entity_id}: Published delete event for revision {new_revision_id}"
                )
            except Exception as e:
                logger.warning(
                    f"Entity {entity_id}: Failed to publish delete event: {e}"
                )

    def log_delete_activity(
        self,
        user_id: int,
        entity_id: str,
        new_revision_id: int,
    ) -> None:
        """Log delete activity for the deletion operation.

        Args:
            user_id: User performing the deletion
            entity_id: The entity ID being deleted
            new_revision_id: The new revision ID
        """
        if user_id > 0:
            activity_result = self.vitess_client.user_repository.log_user_activity(
                user_id=user_id,
                activity_type=UserActivityType.ENTITY_DELETE,
                entity_id=entity_id,
                revision_id=new_revision_id,
            )
            if not activity_result.success:
                logger.warning(f"Failed to log user activity: {activity_result.error}")
