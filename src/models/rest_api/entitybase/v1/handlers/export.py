"""Data export handlers for RDF and TTL formats."""

import logging

from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.response import TurtleResponse
from models.rest_api.entitybase.v1.services.rdf_service import (
    serialize_entity_to_turtle,
)
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class ExportHandler(Handler):
    """Handles export operations."""

    def get_entity_data_turtle(
        self,
        entity_id: str,
    ) -> TurtleResponse:
        """Get entity data in Turtle format."""
        logger.debug(f"Exporting entity {entity_id} to Turtle format")

        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)

        head_revision_id = self.state.vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity has no revisions", status_code=404)

        try:
            revision = self.state.s3_client.read_revision(entity_id, head_revision_id)
            entity_data = revision.revision.copy()
            entity_data["id"] = entity_id
        except S3NotFoundError:
            raise_validation_error(
                f"Entity revision not found: {entity_id}", status_code=404
            )

        logger.debug(
            f"Serializing entity {entity_id} to Turtle, entity_data keys: {entity_data.keys()}"
        )
        turtle = serialize_entity_to_turtle(entity_data, self.state.property_registry)
        logger.debug(f"Generated Turtle length: {len(turtle)}")
        return TurtleResponse(turtle=turtle)
