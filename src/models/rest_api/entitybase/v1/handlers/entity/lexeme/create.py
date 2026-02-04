"""Lexeme creation handlers."""

import logging
from typing import Any

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.services.enumeration_service import (
    EnumerationService,
)
from ..create import EntityCreateHandler

logger = logging.getLogger(__name__)


class LexemeCreateHandler(EntityCreateHandler):
    """Handler for lexeme creation operations"""

    enumeration_service: EnumerationService

    async def create_entity(
        self,
        request: EntityCreateRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
        auto_assign_id: bool = False,
    ) -> EntityResponse:
        """Create a new lexeme with auto-assigned L ID."""
        logger.debug("Creating new lexeme")
        response = await super().create_entity(
            request,
            edit_headers,
            validator,
            auto_assign_id=True,
        )

        # Process lexeme terms for deduplication
        await self._process_lexeme_terms(request, response.id)

        # Confirm ID usage to worker
        if request.id and self.enumeration_service:
            self.enumeration_service.confirm_id_usage(request.id)
        return response

    async def _process_lexeme_terms(self, request: EntityCreateRequest, entity_id: str) -> None:
        """Process and deduplicate lexeme form representations and sense glosses."""
        logger.debug(f"Processing lexeme terms for {entity_id}")

        from models.rest_api.entitybase.v1.utils.lexeme_term_processor import (
            process_lexeme_terms,
        )

        process_lexeme_terms(
            forms=request.forms,
            senses=request.senses,
            s3_client=self.state.s3_client,
        )

        logger.debug(f"Completed processing lexeme terms for {entity_id}")
