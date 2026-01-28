"""Lexeme creation handlers."""

import logging
from typing import Any

from models.common import EditHeaders
from models.internal_representation.metadata_extractor import MetadataExtractor
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

        # Extract forms and senses from request data
        forms = request.forms
        senses = request.senses

        if not forms and not senses:
            logger.debug("No forms or senses to process")
            return

        extractor = MetadataExtractor()

        # Process form representations
        for form in forms:
            if "representations" in form:
                # Initialize hash mapping if not exists
                if "representation_hashes" not in form:
                    form["representation_hashes"] = {}

                for lang, rep_data in form["representations"].items():
                    if "value" in rep_data:
                        text = rep_data["value"]
                        hash_val = extractor.hash_string(text)
                        form["representation_hashes"][lang] = hash_val
                        try:
                            self.state.s3_client.store_form_representation(text, hash_val)
                            logger.debug(f"Stored form representation '{text[:20]}...' with hash {hash_val}")
                        except Exception as e:
                            logger.warning(f"Failed to store form representation: {e}")

        # Process sense glosses
        for sense in senses:
            if "glosses" in sense:
                # Initialize hash mapping if not exists
                if "gloss_hashes" not in sense:
                    sense["gloss_hashes"] = {}

                for lang, gloss_data in sense["glosses"].items():
                    if "value" in gloss_data:
                        text = gloss_data["value"]
                        hash_val = extractor.hash_string(text)
                        sense["gloss_hashes"][lang] = hash_val
                        try:
                            self.state.s3_client.store_sense_gloss(text, hash_val)
                            logger.debug(f"Stored sense gloss '{text[:20]}...' with hash {hash_val}")
                        except Exception as e:
                            logger.warning(f"Failed to store sense gloss: {e}")

        logger.debug(f"Completed processing lexeme terms for {entity_id}")
