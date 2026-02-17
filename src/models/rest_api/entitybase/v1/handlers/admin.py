"""Admin API handlers for system management."""

import logging

from typing import Any, cast

from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.response import EntityListResponse
from models.data.rest_api.v1.entitybase.request.entity_filter import EntityFilterRequest
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class AdminHandler(Handler):
    """Handles administrative operations."""

    def list_entities(
        self,
        entity_type: str = "",
        status: str = "",
        edit_type: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> EntityListResponse:
        """List entities by type, status, or edit_type."""
        logger.debug(
            f"list_entities called with entity_type={entity_type}, status={status}, "
            f"edit_type={edit_type}, limit={limit}, offset={offset}"
        )
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if not entity_type and not status and not edit_type:
            raise_validation_error(
                "At least one filter parameter (entity_type, status, or edit_type) is required",
                status_code=400,
            )

        status_column_map = {
            "locked": "locked",
            "semi_protected": "semi_protected",
            "archived": "archived",
            "dangling": "dangling",
        }

        if status and status not in status_column_map:
            raise_validation_error(
                f"Invalid status: {status}. Valid values are: {', '.join(status_column_map.keys())}",
                status_code=400,
            )

        logger.debug("Fetching entities from repository")
        filter_request = EntityFilterRequest(
            entity_type=entity_type,
            status=status,
            edit_type=edit_type,
            limit=limit,
            offset=offset,
        )
        entities = self.state.vitess_client.entity_repository.list_entities_filtered(
            filter_request=filter_request
        )

        logger.debug(f"Successfully fetched {len(entities)} entities")
        return EntityListResponse(entities=entities, count=len(entities))

    def list_entities_by_type(
        self, entity_type: str, limit: int = 100, offset: int = 0
    ) -> list[str]:
        """List entity IDs by type (item, property, or lexeme).

        Args:
            entity_type: The type of entity ('item', 'property', or 'lexeme')
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entity IDs matching the type
        """
        logger.debug(
            f"list_entities_by_type called with entity_type={entity_type}, "
            f"limit={limit}, offset={offset}"
        )
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        return cast(
            list[str],
            self.state.vitess_client.list_entities_by_type(
                entity_type=entity_type, limit=limit, offset=offset
            ),
        )

    # def get_raw_revision(
    #     self,
    #     entity_id: str,
    #     revision_id: int,
    # ) -> RawRevisionResponse:
    #     """Returns raw S3 entity data for specific revision.
    #
    #     Pure S3 data - no wrapper, no transformation.
    #
    #     Returns 404 with typed error_type if:
    #     - Entity doesn't exist in ID mapping (ENTITY_NOT_FOUND)
    #     - Entity has no revisions (NO_REVISIONS)
    #     - Requested revision doesn't exist (REVISION_NOT_FOUND)
    #     """
    #     logger.debug(
    #         f"get_raw_revision called for entity {entity_id}, revision {revision_id}"
    #     )
    #     if self.state.vitess_client is None:
    #         raise_validation_error("Vitess not initialized", status_code=503)
    #
    #     # Check if entity exists and get history
    #     if not self.state.vitess_client.entity_exists(entity_id):
    #         raise_validation_error(
    #             f"Entity {entity_id} not found in ID mapping", status_code=404
    #         )
    #
    #     # Check if revisions exist for entity
    #     history = self.state.vitess_client.get_history(entity_id)
    #     if not history:
    #         raise_validation_error(
    #             f"Entity {entity_id} has no revisions", status_code=404
    #         )
    #
    #     # Check if requested revision exists
    #     revision_ids = sorted([r.revision_id for r in history])
    #     if revision_id not in revision_ids:
    #         raise_validation_error(
    #             f"Revision {revision_id} not found for entity {entity_id}. Available revisions: {revision_ids}",
    #             status_code=404,
    #         )
    #
    #     # Read full revision schema from S3
    #     if self.state.s3_client is None:
    #         raise_validation_error("S3 not initialized", status_code=503)
    #
    #     revision = self.state.s3_client.read_full_revision(entity_id, revision_id)
    #
    #     # Type assertion to ensure MyPy compatibility
    #     if not isinstance(revision.data, dict):
    #         raise_validation_error(
    #             f"Invalid revision data type: expected dict, got {type(revision.data)}",
    #             status_code=500,
    #         )
    #
    #     # Return full revision wrapped in response model
    #     return RawRevisionResponse(data=revision.data)
