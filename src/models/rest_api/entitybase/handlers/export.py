"""Data export handlers for RDF and TTL formats."""

import logging
from typing import Any, TYPE_CHECKING

from models.infrastructure.s3.s3_client import MyS3Client
from models.rest_api.entitybase.response import TtlResponse
from models.rest_api.entitybase.services.rdf_service import serialize_entity_to_turtle
from models.validation.utils import raise_validation_error

if TYPE_CHECKING:
    from models.infrastructure.vitess_client import VitessClient

logger = logging.getLogger(__name__)


class ExportHandler:
    """Handles export operations."""

    def get_entity_data_turtle(
        self,
        entity_id: str,
        vitess_client: "VitessClient",
        s3_client: MyS3Client,
        property_registry: Any,
    ) -> TtlResponse:
        """Get entity data in Turtle format."""
        logger.debug(f"Exporting entity {entity_id} to Turtle format")

        if vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if not vitess_client.entity_exists(entity_id):
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity has no revisions", status_code=404)

        revision = s3_client.read_revision(entity_id, head_revision_id)
        entity_data = revision.data["entity"]

        turtle = serialize_entity_to_turtle(entity_data, property_registry)
        return TtlResponse(turtle)
