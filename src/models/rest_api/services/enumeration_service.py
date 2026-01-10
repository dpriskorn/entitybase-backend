from models.config.settings import raise_validation_error
from models.infrastructure.vitess_client import VitessClient
from .id_range_manager import IdRangeManager


class EnumerationService:
    """Service for managing entity ID enumeration across different entity types."""

    def __init__(self, vitess_client: VitessClient, worker_id: str = "default-worker"):
        # Minimum IDs to avoid collisions with Wikidata.org
        min_ids = {
            "Q": 300_000_000,
            "P": 30_000,
            "L": 5_000_000,
            "E": 50_000,
        }
        self.range_manager = IdRangeManager(vitess_client, min_ids=min_ids)
        self.range_manager.set_worker_id(worker_id)

        # Initialize ranges from database
        try:
            self.range_manager.initialize_from_database()
        except Exception as e:
            # Log but don't fail - ranges will be allocated on demand
            import logging

            logger = logging.getLogger(__name__)
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

    def validate_entity_id(self, entity_id: str, entity_type: str) -> bool:
        """Validate that an entity ID matches the expected format for its type."""
        # Map entity types to single-character codes
        type_mapping = {
            "item": "Q",
            "property": "P",
            "lexeme": "L",
            "entityschema": "E",
        }

        if entity_type not in type_mapping:
            return False

        expected_prefix = type_mapping[entity_type]

        if not entity_id.startswith(expected_prefix):
            return False

        # Extract numeric part
        try:
            id_number = int(entity_id[1:])  # Skip the prefix
            return id_number >= 1  # All IDs start from 1
        except ValueError:
            return False

    def get_range_status(self) -> dict:
        """Get status of ID ranges for monitoring."""
        return self.range_manager.get_range_status()

    def confirm_id_usage(self, entity_id: str) -> None:
        """Confirm that an ID has been successfully used (handshake with worker)."""
        # TODO: Implement handshake, e.g., mark in range metadata
        pass
