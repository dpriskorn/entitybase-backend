"""Entity ID enumeration service."""

import logging
from typing import Any

from pydantic import BaseModel, Field

from models.rest_api.entitybase.v1.response.misc import RangeStatuses
from models.rest_api.utils import raise_validation_error
from .id_range_manager import IdRangeManager

logger = logging.getLogger(__name__)


class EnumerationService(BaseModel):
    """Service for managing entity ID enumeration across different entity types."""

    worker_id: str
    vitess_client: Any
    range_manager: Any = Field(default=None, exclude=True)

    def __init__(self, vitess_client, worker_id: str = "default-worker"):
        super().__init__(vitess_client=vitess_client, worker_id=worker_id)
        # Minimum IDs to avoid collisions with Wikidata.org
        min_ids = {
            "Q": 300_000_000,
            "P": 30_000,
            "L": 5_000_000,
            "E": 50_000,
        }
        self.range_manager = IdRangeManager(
            vitess_client=self.vitess_client, min_ids=min_ids
        )
        self.range_manager.set_worker_id(worker_id)

        # Initialize ranges from database
        try:
            self.range_manager.initialize_from_database()
        except Exception as e:
            # Log but don't fail - ranges will be allocated on demand
            logger.warning(f"Failed to initialize ID ranges from database: {e}")

    def get_next_entity_id(self, entity_type: str) -> str:
        """Get the next available entity ID for the given entity type."""
        # Map entity types to single-character codes
        type_mapping = {
            "item": "Q",
            "property": "P",
            "lexeme": "L",
            "entityschema": "E",
        }

        if entity_type not in type_mapping:
            raise_validation_error(f"Unsupported entity type: {entity_type}")

        entity_prefix = type_mapping[entity_type]
        return self.range_manager.get_next_id(entity_prefix)

    def get_range_status(self) -> RangeStatuses:
        """Get status of ID ranges for monitoring."""
        return self.range_manager.get_range_status()

    def confirm_id_usage(self, entity_id: str) -> None:
        """Confirm that an ID has been successfully used (handshake with worker)."""
        # Extract prefix and number
        prefix = entity_id[0]
        try:
            number = int(entity_id[1:])
        except ValueError:
            logger.warning(f"Invalid entity ID format for confirmation: {entity_id}")
            return

        # Mark in range metadata (placeholder for future implementation)
        logger.info(
            f"Confirmed usage of ID {entity_id} (prefix {prefix}, number {number})"
        )
        # TODO: Update range metadata, e.g., self.range_manager.mark_used(prefix, number)
