import logging

from fastapi import HTTPException

from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from models.api_models import EntityUpdateRequest, EntityResponse
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
        if not entity_id.startswith("Q"):
            raise HTTPException(
                status_code=400, detail="Entity ID must be an item (start with Q)"
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
