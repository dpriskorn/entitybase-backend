import logging
from typing import Any

from fastapi import HTTPException

from models.api_models import TtlResponse
from models.infrastructure.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient
from models.rest_api.services.rdf_service import serialize_entity_to_turtle

logger = logging.getLogger(__name__)


class ExportHandler:
    """Handles export operations."""

    def get_entity_data_turtle(
        self,
        entity_id: str,
        vitess_client: VitessClient,
        s3_client: S3Client,
        property_registry: Any,
    ) -> TtlResponse:
        """Get entity data in Turtle format."""
        logger.debug(f"Exporting entity {entity_id} to Turtle format")

        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        if not vitess_client.entity_exists(entity_id):
            raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise HTTPException(status_code=404, detail="Entity has no revisions")

        revision = s3_client.read_revision(entity_id, head_revision_id)
        entity_data = revision.data["entity"]

        turtle = serialize_entity_to_turtle(entity_data, property_registry)
        return TtlResponse(turtle)
