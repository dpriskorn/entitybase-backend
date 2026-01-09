from typing import Dict

from models.infrastructure.vitess_client import VitessClient
from models.rest_api.handlers.entity.enumeration import (
    EntitySchemaEnumerationHandler,
    EnumerationHandler,
    ItemEnumerationHandler,
    LexemeEnumerationHandler,
    PropertyEnumerationHandler,
)


class EnumerationService:
    """Service for managing entity ID enumeration across different entity types."""

    def __init__(self, vitess_client: VitessClient):
        self.vitess_client = vitess_client
        self._handlers: Dict[str, EnumerationHandler] = {
            "item": ItemEnumerationHandler(),
            "property": PropertyEnumerationHandler(),
            "lexeme": LexemeEnumerationHandler(),
            "entityschema": EntitySchemaEnumerationHandler(),
        }

    def get_next_entity_id(self, entity_type: str) -> str:
        """Get the next available entity ID for the given entity type."""
        if entity_type not in self._handlers:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        handler = self._handlers[entity_type]

        # TODO: Implement database-backed ID generation
        # For now, return placeholder
        return handler.next_entity_id

    def validate_entity_id(self, entity_id: str, entity_type: str) -> bool:
        """Validate that an entity ID matches the expected format for its type."""
        if entity_type not in self._handlers:
            return False

        handler = self._handlers[entity_type]
        expected_prefix = handler.entity_type_prefix

        if not entity_id.startswith(expected_prefix):
            return False

        # Extract numeric part
        try:
            id_number = int(entity_id[1:])  # Skip the prefix
            return id_number >= handler.min_id
        except ValueError:
            return False
