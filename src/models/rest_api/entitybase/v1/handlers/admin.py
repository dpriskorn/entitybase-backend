"""Admin API handlers for system management."""

import logging
from typing import TYPE_CHECKING

from models.rest_api.entitybase.v1.handler import Handler

if TYPE_CHECKING:
    pass
from models.rest_api.entitybase.v1.response import EntityListResponse
from models.rest_api.entitybase.v1.response.misc import RawRevisionResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class AdminHandler(Handler):
    """Handles administrative operations."""

    def list_entities(
        self,
        entity_type: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> EntityListResponse:
        """List entities by type or all entities."""
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        # Get entity IDs
        entity_ids = self.state.vitess_client.list_entities_by_type(entity_type, limit, offset)

        # Build response with ID and revision info
        entities = []
        for entity_id in entity_ids:
            try:
                head_revision_id = self.state.vitess_client.get_head(entity_id)
                entities.append(
                    {
                        "id": entity_id,
                        "revision_id": head_revision_id,
                    }
                )
            except Exception:
                # Skip entities with issues
                continue

        return EntityListResponse(entities=entities, count=len(entities))

    def get_raw_revision(
        self,
        entity_id: str,
        revision_id: int,
    ) -> RawRevisionResponse:
        """Returns raw S3 entity data for specific revision.

        Pure S3 data - no wrapper, no transformation.

        Returns 404 with typed error_type if:
        - Entity doesn't exist in ID mapping (ENTITY_NOT_FOUND)
        - Entity has no revisions (NO_REVISIONS)
        - Requested revision doesn't exist (REVISION_NOT_FOUND)
        """
        logger.debug(
            f"get_raw_revision called for entity {entity_id}, revision {revision_id}"
        )
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        # Check if entity exists and get history
        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error(
                f"Entity {entity_id} not found in ID mapping", status_code=404
            )

        # Check if revisions exist for entity
        history = self.state.vitess_client.get_history(entity_id)
        if not history:
            raise_validation_error(
                f"Entity {entity_id} has no revisions", status_code=404
            )

        # Check if requested revision exists
        revision_ids = sorted([r.revision_id for r in history])
        if revision_id not in revision_ids:
            raise_validation_error(
                f"Revision {revision_id} not found for entity {entity_id}. Available revisions: {revision_ids}",
                status_code=404,
            )

        # Read full revision schema from S3
        if self.state.s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        revision = self.state.s3_client.read_full_revision(entity_id, revision_id)

        # Type assertion to ensure MyPy compatibility
        if not isinstance(revision.data, dict):
            raise_validation_error(
                f"Invalid revision data type: expected dict, got {type(revision.data)}",
                status_code=500,
            )

        # Return full revision wrapped in response model
        return RawRevisionResponse(data=revision.data)
