"""Handler for property creation operations in the REST API."""

import logging
from typing import Any

from models.rest_api.entitybase.v1.request.entity import EntityCreateRequest
from models.rest_api.entitybase.v1.response import EntityResponse
from ..create import EntityCreateHandler

logger = logging.getLogger(__name__)


class PropertyCreateHandler(EntityCreateHandler):
    """Handler for property creation operations"""

    async def create_entity(
        self,
        request: EntityCreateRequest,
        validator: Any | None = None,
        auto_assign_id: bool = False,
        user_id: int = 0,
    ) -> EntityResponse:
        """Create a new property with auto-assigned P ID."""
        logger.debug("Creating new property")
        response = await super().create_entity(
            request,
            validator,
            auto_assign_id=True,
        )
        # Confirm ID usage to worker
        if request.id and self.enumeration_service:
            self.enumeration_service.confirm_id_usage(request.id)
        return response
