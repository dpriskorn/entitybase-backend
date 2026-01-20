"""Entity redirect management handlers."""

import logging
from typing import TYPE_CHECKING

from models.rest_api.entitybase.v1.handlers.entity.revert import EntityRevertHandler
from models.rest_api.entitybase.v1.request.entity import EntityRedirectRequest
from models.rest_api.entitybase.v1.request.entity import EntityRevertRequest
from models.rest_api.entitybase.v1.request.entity.revert import RedirectRevertRequest
from models.rest_api.entitybase.v1.response import (
    EntityRedirectResponse,
)
from models.rest_api.entitybase.v1.response.entity.revert import EntityRevertResponse
from models.rest_api.entitybase.v1.services.redirects import RedirectService

if TYPE_CHECKING:
    from models.infrastructure.s3.s3_client import MyS3Client
    from models.infrastructure.stream.producer import StreamProducerClient
    from models.infrastructure.vitess.client import VitessClient

logger = logging.getLogger(__name__)


class RedirectHandler:
    """Handles redirect operations."""

    def __init__(
        self,
        s3_client: "MyS3Client",
        vitess_client: "VitessClient",
        stream_producer: "StreamProducerClient | None" = None,
    ):
        self._s3 = s3_client
        self._vitess = vitess_client
        self._stream_producer = stream_producer
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
        self, entity_id: str, request: RedirectRevertRequest
    ) -> EntityRevertResponse:
        """Revert a redirect entity back to normal using the general revert."""
        logger.debug(
            f"Reverting redirect for entity {entity_id} to revision {request.revert_to_revision_id}"
        )
        # Call general revert
        general_request = EntityRevertRequest(
            to_revision_id=request.revert_to_revision_id,
            reason=request.revert_reason,
            watchlist_context=None,  # Not used for redirects
        )
        general_handler = EntityRevertHandler()
        revert_result = await general_handler.revert_entity(
            entity_id,
            general_request,
            self._vitess,
            self._s3,
            self._stream_producer,
            int(request.created_by),
        )
        # Clear the redirect target
        self._vitess.revert_redirect(entity_id)
        return revert_result
