"""Handler for entity revert operations."""

import logging
from datetime import datetime, timezone

from models.common import EditHeaders
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import EditType, EditData
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps

from models.data.infrastructure.stream.change_type import ChangeType
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.stream.event import EntityChangeEvent
from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.request import EntityRevertRequest
from models.data.rest_api.v1.entitybase.response import EntityRevertResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EntityRevertHandler(Handler):
    """Handler for reverting entities to previous revisions."""

    async def revert_entity(
        self,
        entity_id: str,
        request: EntityRevertRequest,
        edit_headers: EditHeaders,
    ) -> EntityRevertResponse:
        """Revert an entity to a specified revision."""
        logger.debug(
            f"Reverting entity {entity_id} to revision {request.to_revision_id}"
        )
        # Resolve internal ID
        internal_entity_id = self.state.vitess_client.id_resolver.resolve_id(
            entity_id
        )

        if internal_entity_id == 0:
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)

        # Validate target revision exists
        target_revision = self.state.vitess_client.revision_repository.get_revision(
            internal_entity_id, request.to_revision_id
        )
        if not target_revision:
            raise_validation_error(
                f"Revision {request.to_revision_id} not found for entity {entity_id}",
                status_code=404,
            )

        # Read target revision content from S3
        target_revision_data = self.state.s3_client.read_full_revision(
            entity_id, request.to_revision_id
        )

        # Get current head revision
        head_result = self.state.vitess_client.head_repository.get_head_revision(
            internal_entity_id
        )
        if not head_result.success:
            raise_validation_error(
                head_result.error or "Failed to get head revision", status_code=500
            )
        head_revision = head_result.data if isinstance(head_result.data, int) else 0
        if head_revision == request.to_revision_id:
            raise_validation_error(
                f"Entity {entity_id} is already at revision {request.to_revision_id}",
                status_code=400,
            )

        # Calculate new revision ID
        new_revision_id = head_revision + 1

        # Create new revision data using RevisionData model
        # For revert, we need to copy the entity data from target revision
        target_data = target_revision_data.data if hasattr(target_revision_data, 'data') else target_revision_data

        # Copy hashes from target revision
        target_hashes = target_data.get("hashes", {})
        if isinstance(target_hashes, dict):
            hashes = HashMaps(
                statements=target_hashes.get("statements"),
                labels=target_hashes.get("labels"),
                descriptions=target_hashes.get("descriptions"),
                aliases=target_hashes.get("aliases"),
                sitelinks=target_hashes.get("sitelinks"),
            )
        else:
            hashes = HashMaps()

        # Copy state from target revision
        target_state = target_data.get("state", {})
        if isinstance(target_state, dict):
            state = EntityState(
                sp=target_state.get("sp", target_state.get("is_semi_protected", False)),
                locked=target_state.get("locked", target_state.get("is_locked", False)),
                archived=target_state.get("archived", target_state.get("is_archived", False)),
                dangling=target_state.get("dangling", target_state.get("is_dangling", False)),
                mep=target_state.get("mep", target_state.get("is_mass_edit_protected", False)),
                deleted=target_state.get("deleted", target_state.get("is_deleted", False)),
            )
        else:
            state = EntityState()

        new_revision_data = RevisionData(
            revision_id=new_revision_id,
            entity_type=target_data.get("entity_type", "item"),
            edit=EditData(
                type=EditType.MANUAL_UPDATE,
                user_id=edit_headers.x_user_id,
                summary=f"Revert to revision {request.to_revision_id}",
                at=datetime.now(timezone.utc).isoformat(),
            ),
            hashes=hashes,
            redirects_to="",
            state=state,
            property_counts=target_data.get("property_counts"),
            properties=target_data.get("properties", []),
        )

        # Write new revision to S3
        import json
        from models.internal_representation.metadata_extractor import MetadataExtractor
        from models.data.infrastructure.s3.revision_data import S3RevisionData
        from models.config.settings import settings

        revision_dict = new_revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)

        s3_revision_data = S3RevisionData(
            schema=settings.s3_schema_revision_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        self.state.s3_client.store_revision(content_hash, s3_revision_data)

        # Insert revision in DB
        self.state.vitess_client.insert_revision(
            entity_id,
            new_revision_id,
            new_revision_data,
        )

        # Mark as published
        # s3_client.mark_published(
        #     entity_id=entity_id,
        #     revision_id=new_revision_id,
        #     publication_state="published",
        # )

        # Publish event
        if self.state.entity_change_stream_producer:
            event = EntityChangeEvent(
                id=entity_id,
                rev=new_revision_id,
                type=ChangeType.REVERT,
                from_rev=head_revision,
                at=datetime.now(timezone.utc),
                summary=edit_headers.x_edit_summary,
            )
            await self.state.entity_change_stream_producer.publish_event(event)

        return EntityRevertResponse(
            entity_id=entity_id,
            new_rev_id=new_revision_id,
            from_rev_id=head_revision,
            reverted_at=datetime.now(timezone.utc).isoformat(),
        )
