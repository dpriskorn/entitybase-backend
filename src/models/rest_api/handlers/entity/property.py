import logging
from typing import Any

from models.api_models import EntityCreateRequest, EntityResponse
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from models.rest_api.services.enumeration_service import EnumerationService
from .create import EntityCreateHandler

logger = logging.getLogger(__name__)


class PropertyCreateHandler(EntityCreateHandler):
    """Handler for property creation operations"""

    def __init__(self, enumeration_service: EnumerationService, /, **data: Any):
        super().__init__(**data)
        self.enumeration_service = enumeration_service

    async def create_entity(
        self,
        request: EntityCreateRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
        auto_assign_id: bool = False,
    ) -> EntityResponse:
        """Create a new property with auto-assigned P ID."""
        return await super().create_entity(
            request,
            vitess_client,
            s3_client,
            stream_producer,
            validator,
            auto_assign_id=True,
        )
