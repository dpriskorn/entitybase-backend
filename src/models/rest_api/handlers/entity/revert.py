"""Handler for entity revert operations."""

from datetime import datetime

from models.rest_api.request.entity.revert import EntityRevertRequest
from models.rest_api.response.entity.revert import EntityRevertResponse
from models.validation.utils import raise_validation_error


class EntityRevertHandler:
    """Handler for reverting entities to previous revisions."""

    def revert_entity(
        self, entity_id: str, request: EntityRevertRequest, vitess_client
    ) -> EntityRevertResponse:
        """Revert an entity to a specified revision."""
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

        # Get current head revision
        head_revision = vitess_client.head_repository.get_head_revision(
            internal_entity_id
        )
        if head_revision == request.to_revision_id:
            raise_validation_error(
                f"Entity {entity_id} is already at revision {request.to_revision_id}",
                status_code=400,
            )

        # Perform revert
        new_revision_id = vitess_client.revision_repository.revert_entity(
            internal_entity_id=internal_entity_id,
            to_revision_id=request.to_revision_id,
            reverted_by_user_id=request.reverted_by_user_id,
            reason=request.reason,
            watchlist_context=request.watchlist_context,
            vitess_client=vitess_client,
        )

        return EntityRevertResponse(
            entity_id=entity_id,
            new_revision_id=new_revision_id,
            reverted_from_revision_id=head_revision,
            reverted_at=datetime.utcnow().isoformat() + "Z",
        )
