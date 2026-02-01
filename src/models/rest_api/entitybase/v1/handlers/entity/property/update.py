"""Handler for property update operations in the REST API."""

import logging
import re
from typing import Any

from models.common import EditHeaders
from models.data.rest_api.v1.entitybase.request import EntityUpdateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.utils import raise_validation_error
from ..update import EntityUpdateHandler

logger = logging.getLogger(__name__)


class PropertyUpdateHandler(EntityUpdateHandler):
    """Handler for property update operations with property-specific validation."""

    async def update_entity(
        self,
        entity_id: str,
        request: EntityUpdateRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update an existing property with validation that entity_id starts with P."""
        logger.debug(f"Updating property {entity_id}")
        # Validate entity type (must be property)
        if not re.match(r"^P\d+$", entity_id):
            raise_validation_error(
                "Entity ID must be a property (format: P followed by digits)",
                status_code=400,
            )

        # Delegate to parent implementation
        return await super().update_entity(
            entity_id,
            request,
            edit_headers,
            validator,
        )
