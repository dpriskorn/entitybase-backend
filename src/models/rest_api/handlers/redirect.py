import logging
from typing import TYPE_CHECKING

from models.api import (
    EntityRedirectRequest,
    EntityRedirectResponse,
    EntityResponse,
)
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from models.rest_api.services.redirects import RedirectService

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class RedirectHandler:
    """Handles redirect operations."""

    def __init__(
        self,
        s3_client: S3Client,
        vitess_client: VitessClient,
        stream_producer: StreamProducerClient | None = None,
    ):
        self.redirect_service = RedirectService(
            s3_client, vitess_client, stream_producer
        )

    async def create_entity_redirect(
        self, request: EntityRedirectRequest
    ) -> EntityRedirectResponse:
        """Create a redirect from one entity to another."""
        logger.debug(
            f"Creating redirect from {request.redirect_from_id} to {request.redirect_to_id}"
        )
        return await self.redirect_service.create_redirect(request)

    async def revert_entity_redirect(
        self, entity_id: str, revert_to_revision_id: int
    ) -> EntityResponse:
        """Revert a redirect entity back to normal using revision-based restore."""
        logger.debug(
            f"Reverting redirect for entity {entity_id} to revision {revert_to_revision_id}"
        )
        return await self.redirect_service.revert_redirect(
            entity_id, revert_to_revision_id
        )
