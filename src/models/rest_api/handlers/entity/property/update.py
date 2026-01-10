import logging

import re

from models.validation.utils import raise_validation_error
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from models.api import EntityUpdateRequest, EntityResponse
from ..update import EntityUpdateHandler

logger = logging.getLogger(__name__)


class PropertyUpdateHandler(EntityUpdateHandler):
    """Handler for property update operations with property-specific validation."""

    async def update_entity(
        self,
        entity_id: str,
        request: EntityUpdateRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: object | None = None,
    ) -> EntityResponse:
        """Update an existing property with validation that entity_id starts with P."""
        # Validate entity type (must be property)
        if not re.match(r"^P\d+$", entity_id):
            raise_validation_error(
                "Entity ID must be a property (format: P followed by digits)",
                status_code=400,
            )

        # Delegate to parent implementation
        return await super().update_entity(
            entity_id,
            request,
            vitess_client,
            s3_client,
            stream_producer,
            validator,
        )
