"""Entity redirect management handlers."""

import logging
from typing import cast

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest
from models.data.rest_api.v1.entitybase.request import RedirectRevertRequest
from models.data.rest_api.v1.entitybase.response import (
    EntityRedirectResponse,
)
from models.data.rest_api.v1.entitybase.response import EntityRevertResponse


logger = logging.getLogger(__name__)


class RedirectHandler(Handler):
    """Handles redirect operations."""

    async def create_entity_redirect(
        self, request: EntityRedirectRequest, edit_headers: EditHeaders
    ) -> EntityRedirectResponse:
        """Create a redirect from one entity to another."""
        logger.debug(
            f"Creating redirect from {request.redirect_from_id} to {request.redirect_to_id}"
        )
        return cast(
            EntityRedirectResponse,
            await self.state.redirect_service.create_redirect(request, edit_headers),
        )

    async def revert_entity_redirect(
        self, entity_id: str, request: RedirectRevertRequest, edit_headers: EditHeaders
    ) -> EntityRevertResponse:
        """Revert a redirect entity back to normal using the general revert."""
        logger.debug(
            f"Reverting redirect for entity {entity_id} to revision {request.revert_to_revision_id}"
        )
        return cast(
            EntityRevertResponse,
            await self.state.redirect_service.revert_redirect(
                entity_id, request.revert_to_revision_id, edit_headers
            ),
        )
