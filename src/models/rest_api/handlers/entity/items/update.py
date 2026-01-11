"""Item-specific update handlers."""

import logging
import re

from models.rest_api.request import EntityUpdateRequest
from models.rest_api.response import EntityResponse

from models.validation.utils import raise_validation_error
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from ..update import EntityUpdateHandler

logger = logging.getLogger(__name__)


class ItemUpdateHandler(EntityUpdateHandler):
    """Handler for item update operations with item-specific validation."""

    async def update_entity(
        self,
        entity_id: str,
        request: EntityUpdateRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: object | None = None,
    ) -> EntityResponse:
        """Update an existing item with validation that entity_id starts with Q."""
        # Validate entity type (must be item)
        if not re.match(r"^Q\d+$", entity_id):
            raise_validation_error(
                "Entity ID must be an item (format: Q followed by digits)",
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
