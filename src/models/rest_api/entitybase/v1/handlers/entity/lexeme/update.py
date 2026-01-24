"""Handler for lexeme update operations in the REST API."""

import logging
import re
from typing import Any

from models.internal_representation.metadata_extractor import MetadataExtractor
from models.data.rest_api.v1.entitybase.request import EntityUpdateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
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

        # Process lexeme terms for deduplication
        await self._process_lexeme_terms(request, entity_id)

        # Delegate to parent implementation
        return await super().update_entity(
            entity_id,
            request,
            validator,
            user_id,
        )

    async def _process_lexeme_terms(self, request: EntityUpdateRequest, entity_id: str) -> None:
        """Process and deduplicate lexeme form representations and sense glosses."""
        logger.debug(f"Processing lexeme terms for {entity_id}")

        # Extract forms and senses from request data
        forms = request.data.get("forms", [])
        senses = request.data.get("senses", [])

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
