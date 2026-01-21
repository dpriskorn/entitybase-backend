"""Entity read and retrieval handlers."""

import logging

from models.rest_api.entitybase.v1.handler import Handler
from models.rest_api.entitybase.v1.response import (
    EntityRevisionResponse,
)
from models.rest_api.entitybase.v1.response.entity import EntityHistoryEntry
from models.rest_api.entitybase.v1.response.entity import EntityState
from models.rest_api.entitybase.v1.response.entity.entitybase import EntityResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EntityReadHandler(Handler):
    """Handler for entity read operations"""

    def get_entity(
        self,
        entity_id: str,
    ) -> EntityResponse:
        """Get entity by ID."""
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if self.state.s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        head_revision_id = self.state.vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity not found", status_code=404)

        try:
            revision = self.state.s3_client.read_revision(entity_id, head_revision_id)
            data = revision.content.get("entity", {}).copy()

            response = EntityResponse(
                id=entity_id,
                rev_id=head_revision_id,
                data=data,
                state=EntityState(
                    sp=revision.content.get("is_semi_protected", False),
                    locked=revision.content.get("is_locked", False),
                    archived=revision.content.get("is_archived", False),
                    dangling=revision.content.get("is_dangling", False),
                    mep=revision.content.get("is_mass_edit_protected", False),
                ),
            )
            return response
        except Exception as e:
            logger.error(f"Failed to read entity {entity_id}: {e}")
            raise_validation_error("Failed to read entity", status_code=500)

    def get_entity_history(
        self,  # type: ignore[return,func-returns-value]
        entity_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[EntityHistoryEntry]:
        """Get entity revision history."""
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        try:
            return self.state.vitess_client.get_entity_history(entity_id, limit, offset)  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Failed to get entity history for {entity_id}: {e}")
            raise_validation_error("Failed to get entity history", status_code=500)

    def get_entity_revision(
        self,  # type: ignore[return]
        entity_id: str,
        revision_id: int,
    ) -> EntityRevisionResponse:
        """Get specific entity revision."""
        if self.state.s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        try:
            revision = self.state.s3_client.read_revision(entity_id, revision_id)
            revision_data = revision.data
            return EntityRevisionResponse(
                entity_id=entity_id,
                revision_id=revision_id,
                revision_data=revision_data,
            )
        except Exception as e:
            logger.error(
                f"Failed to read revision {revision_id} for entity {entity_id}: {e}"
            )
            raise_validation_error("Revision not found", status_code=404)
