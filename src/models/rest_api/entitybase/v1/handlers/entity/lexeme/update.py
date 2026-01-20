"""Handler for lexeme update operations in the REST API."""

import logging
import re
from typing import Any

from models.rest_api.entitybase.v1.request import EntityUpdateRequest
from models.rest_api.entitybase.v1.response import EntityResponse
from models.rest_api.utils import raise_validation_error
from ..update import EntityUpdateHandler

logger = logging.getLogger(__name__)


class LexemeUpdateHandler(EntityUpdateHandler):
    """Handler for lexeme update operations with lexeme-specific validation."""

    async def update_entity(
        self,
        entity_id: str,
        request: EntityUpdateRequest,
        validator: Any | None = None,
        user_id: int = 0,
    ) -> EntityResponse:
        """Update an existing lexeme with validation that entity_id starts with L."""
        logger.debug(f"Updating lexeme {entity_id}")
        # Validate entity type (must be lexeme)
        if not re.match(r"^L\d+$", entity_id):
            raise_validation_error(
                "Entity ID must be a lexeme (format: L followed by digits)",
                status_code=400,
            )

        # Delegate to parent implementation
        return await super().update_entity(
            entity_id,
            request,
            validator,
        )
