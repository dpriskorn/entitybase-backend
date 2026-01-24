"""Entity redirect management handlers."""

import logging

from models.rest_api.entitybase.v1.handler import Handler
from models.rest_api.entitybase.v1.handlers.entity.revert import EntityRevertHandler
from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest
from models.data.rest_api.v1.entitybase.request import EntityRevertRequest
from models.data.rest_api.v1.entitybase.request import RedirectRevertRequest
from models.data.rest_api.v1.entitybase.response import (
    EntityRedirectResponse,
)
from models.data.rest_api.v1.entitybase.response import EntityRevertResponse


logger = logging.getLogger(__name__)


class RedirectHandler(Handler):
    """Handles redirect operations."""

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
        general_handler = EntityRevertHandler(state=self.state)
        revert_result = await general_handler.revert_entity(
            entity_id,
            general_request,
            int(request.created_by),
        )
        return revert_result
