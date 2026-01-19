"""Handler for entity revert operations."""

import logging
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from models.infrastructure.stream.change_type import ChangeType
from models.infrastructure.stream.event import EntityChangeEvent
from models.rest_api.v1.entitybase.request.entity import EntityRevertRequest
from models.rest_api.v1.entitybase.response.entity.revert import EntityRevertResponse
from models.rest_api.utils import raise_validation_error

if TYPE_CHECKING:
    from models.infrastructure.vitess.vitess_client import VitessClient

logger = logging.getLogger(__name__)


class EntityRevertHandler:
    """Handler for reverting entities to previous revisions."""

    async def revert_entity(
        self,
        entity_id: str,
        request: EntityRevertRequest,
        vitess_client: "VitessClient",
        s3_client: Any,
        stream_producer: Any,
        user_id: int,
    ) -> EntityRevertResponse:
        """Revert an entity to a specified revision."""
        logger.debug(
            f"Reverting entity {entity_id} to revision {request.to_revision_id}"
        )
        # Resolve internal ID
        with vitess_client.get_connection() as conn:
            internal_entity_id = vitess_client.id_resolver.resolve_id(conn, entity_id)

        if internal_entity_id == 0:
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)

        # Validate target revision exists
        target_revision = vitess_client.revision_repository.get_revision(
            internal_entity_id, request.to_revision_id, vitess_client
        )
        if not target_revision:
            raise_validation_error(
                f"Revision {request.to_revision_id} not found for entity {entity_id}",
                status_code=404,
            )

        # Read target revision content from S3
        target_revision_data = s3_client.read_full_revision(
            entity_id, request.to_revision_id
        )

        # Get current head revision
        head_result = vitess_client.head_repository.get_head_revision(
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

        # Create new revision data
        new_revision_data = {
            "schema_version": "1.1.0",
            "redirects_to": None,
            "entity": target_revision_data.data["entity"],
        }

        # Write new revision to S3
        s3_client.write_revision(
            entity_id=entity_id,
            revision_id=new_revision_id,
            data=new_revision_data,
            # publication_state="pending",
        )

        # Insert revision in DB
        vitess_client.insert_revision(
            entity_id,
            new_revision_id,
            is_mass_edit=False,
            edit_type="revert",
            statements=target_revision_data.data["entity"]["statements"],
            properties=target_revision_data.data["entity"]["properties"],
            property_counts=target_revision_data.data["entity"]["property_counts"],
        )

        # Mark as published
        # s3_client.mark_published(
        #     entity_id=entity_id,
        #     revision_id=new_revision_id,
        #     publication_state="published",
        # )

        # Publish event
        if stream_producer:
            event = EntityChangeEvent(
                id=entity_id,
                rev=new_revision_id,
                type=ChangeType.REVERT,
                from_rev=head_revision,
                at=datetime.now(timezone.utc),
                summary=request.reason,
            )
            await stream_producer.publish_event(event)

        return EntityRevertResponse(
            entity_id=entity_id,
            new_rev_id=new_revision_id,
            from_rev_id=head_revision,
            reverted_at=datetime.now(timezone.utc).isoformat(),
        )
