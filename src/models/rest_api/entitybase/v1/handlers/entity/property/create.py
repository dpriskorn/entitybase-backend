"""Handler for property creation operations in the REST API."""

import logging
from typing import Any

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from ..create import EntityCreateHandler

logger = logging.getLogger(__name__)


class PropertyCreateHandler(EntityCreateHandler):
    """Handler for property creation operations"""

    async def create_entity(
        self,
        request: EntityCreateRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
        auto_assign_id: bool = False,
    ) -> EntityResponse:
        """Create a new property with auto-assigned P ID if not provided."""
        logger.debug("Creating new property")
        response = await super().create_entity(
            request,
            edit_headers,
            validator,
            auto_assign_id=not bool(request.id),
        )
        return response
