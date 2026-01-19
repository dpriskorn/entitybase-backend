"""Lexeme creation handlers."""

import logging
from typing import Any

from models.infrastructure.s3.s3_client import MyS3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess.vitess_client import VitessClient
from models.rest_api.entitybase.request.entity import EntityCreateRequest
from models.rest_api.entitybase.response import EntityResponse
from models.rest_api.entitybase.services.enumeration_service import EnumerationService
from ..create import EntityCreateHandler

logger = logging.getLogger(__name__)


class LexemeCreateHandler(EntityCreateHandler):
    """Handler for lexeme creation operations"""

    def __init__(self, enumeration_service: EnumerationService, /, **data: Any):
        super().__init__(**data)
        self.enumeration_service = enumeration_service

    async def create_entity(
        self,
        request: EntityCreateRequest,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
        auto_assign_id: bool = False,
        user_id: int = 0,
    ) -> EntityResponse:
        """Create a new lexeme with auto-assigned L ID."""
        logger.debug("Creating new lexeme")
        response = await super().create_entity(
            request,
            vitess_client,
            s3_client,
            stream_producer,
            validator,
            auto_assign_id=True,
        )
        # Confirm ID usage to worker
        if request.id and self.enumeration_service:
            self.enumeration_service.confirm_id_usage(request.id)
        return response
