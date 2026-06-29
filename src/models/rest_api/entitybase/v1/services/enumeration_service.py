"""Entity ID enumeration service."""

import logging
from typing import Any, cast

from pydantic import BaseModel, Field

from models.data.rest_api.v1.entitybase.response import RangeStatuses
from models.rest_api.utils import raise_validation_error
from .id_range_manager import IdRangeManager

logger = logging.getLogger(__name__)


class SimpleIdCounter(BaseModel):
    """Simple in-memory ID counter for simple mode (no ID worker)."""

    next_ids: dict[str, int] = Field(
        default_factory=lambda: {"Q": 1, "P": 1, "L": 1, "E": 1}
    )

    def get_next_id(self, entity_prefix: str) -> str:
        """Get next ID for entity prefix."""
        next_num = self.next_ids.get(entity_prefix, 1)
        self.next_ids[entity_prefix] = next_num + 1
        return f"{entity_prefix}{next_num}"


class EnumerationService(BaseModel):
    """Service for managing entity ID enumeration across different entity types.

    Handles ID allocation by communicating with the ID worker to reserve
    ID ranges. Each entity type (item, property, lexeme) has separate
    minimum ID values to prevent conflicts with existing Wikidata entities.
    """

    worker_id: str
    mysql_client: Any
    id_worker_enabled: bool = True
    range_manager: Any = Field(default=None, exclude=True)
    simple_counter: SimpleIdCounter = Field(
        default_factory=SimpleIdCounter, exclude=True
    )

    def model_post_init(self, context: Any) -> None:
        if self.id_worker_enabled:
            min_ids = {
                "Q": 300_000_000,
                "P": 30_000,
                "L": 5_000_000,
                "E": 50_000,
            }
            self.range_manager = IdRangeManager(
                mysql_client=self.mysql_client, min_ids=min_ids
            )
            self.range_manager.set_worker_id(self.worker_id)

            try:
                self.range_manager.initialize_from_database()
            except Exception as e:
                logger.warning(f"Failed to initialize ID ranges from database: {e}")
        else:
            logger.info("ID worker disabled, using simple ID counter mode")

    def get_next_entity_id(self, entity_type: str) -> str:
        """Get next available entity ID for the given type.

        When ID worker is enabled: allocates IDs from a reserved range.
        When disabled: uses simple auto-increment from 1.

        Args:
            entity_type: Entity type (item, property, lexeme, entityschema)

        Returns:
            Entity ID string (e.g., Q42, P31)

        Raises:
            HTTPException 400: If entity_type is invalid
        """
        type_mapping = {
            "item": "Q",
            "property": "P",
            "lexeme": "L",
            "entityschema": "E",
        }

        if entity_type not in type_mapping:
            raise_validation_error(f"Unsupported entity type: {entity_type}")

        entity_prefix = type_mapping[entity_type]

        if self.id_worker_enabled:
            return cast(str, self.range_manager.get_next_id(entity_prefix))
        else:
            return self.simple_counter.get_next_id(entity_prefix)

    def get_range_status(self) -> RangeStatuses:
        """Get status of ID ranges for monitoring."""
        if not self.id_worker_enabled:
            return RangeStatuses(ranges={})
        return cast(RangeStatuses, self.range_manager.get_range_status())

    @staticmethod
    def confirm_id_usage(entity_id: str) -> None:
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
