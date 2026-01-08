import logging
from typing import TYPE_CHECKING

from models.api_models import (
    EntityRedirectRequest,
    EntityRedirectResponse,
    EntityResponse,
)
from models.infrastructure.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient
from services.entity_api.redirects import RedirectService

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class RedirectHandler:
    """Handles redirect operations."""

    def __init__(self, s3_client: S3Client, vitess_client: VitessClient):
        self.redirect_service = RedirectService(s3_client, vitess_client)

    def create_entity_redirect(
        self, request: EntityRedirectRequest
    ) -> EntityRedirectResponse:
        """Create a redirect from one entity to another."""
        logger.debug(
            f"Creating redirect from {request.redirect_from_id} to {request.redirect_to_id}"
        )
        return self.redirect_service.create_redirect(request)

    def revert_entity_redirect(
        self, entity_id: str, revert_to_revision_id: int
    ) -> EntityResponse:
        """Revert a redirect entity back to normal using revision-based restore."""
        logger.debug(
            f"Reverting redirect for entity {entity_id} to revision {revert_to_revision_id}"
        )
        return self.redirect_service.revert_redirect(entity_id, revert_to_revision_id)
