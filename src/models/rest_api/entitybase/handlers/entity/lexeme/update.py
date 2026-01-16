"""Handler for lexeme update operations in the REST API."""

import logging
from typing import Any

import re

from models.rest_api.entitybase.request import EntityUpdateRequest
from models.rest_api.entitybase.response import EntityResponse

from models.validation.utils import raise_validation_error
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from ..update import EntityUpdateHandler

logger = logging.getLogger(__name__)


class LexemeUpdateHandler(EntityUpdateHandler):
    """Handler for lexeme update operations with lexeme-specific validation."""

    async def update_entity(
        self,
        entity_id: str,
        request: EntityUpdateRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
        user_id: int | None = None,
    ) -> EntityResponse:
        """Update an existing lexeme with validation that entity_id starts with L."""
        logger.debug(f"Updating lexeme {entity_id}")
        # Validate entity type (must be lexeme)
        if not re.match(r"^L\d+$", entity_id):
            raise_validation_error(
                "Entity ID must be a lexeme (format: L followed by digits)",
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
