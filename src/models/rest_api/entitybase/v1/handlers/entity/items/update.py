"""Item-specific update handlers."""

import logging
import re
from typing import Any

from models.data.rest_api.v1.entitybase.request import EntityUpdateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.utils import raise_validation_error
from ..update import EntityUpdateHandler

logger = logging.getLogger(__name__)


class ItemUpdateHandler(EntityUpdateHandler):
    """Handler for item update operations with item-specific validation."""

    async def update_entity(
        self,
        entity_id: str,
        request: EntityUpdateRequest,
        validator: Any | None = None,
        user_id: int = 0,
    ) -> EntityResponse:
        """Update an existing item with validation that entity_id starts with Q."""
        logger.debug(f"Updating item {entity_id}")
        # Validate entity type (must be item)
        if not re.match(r"^Q\d+$", entity_id):
            raise_validation_error(
                "Entity ID must be an item (format: Q followed by digits)",
                status_code=400,
            )

        # Delegate to parent implementation
        return await super().update_entity(
            entity_id,
            request,
            validator,
        )
