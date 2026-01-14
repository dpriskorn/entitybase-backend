"""Vitess entity ID resolution and management."""

from typing import Any


class IdResolver:
    """Handles mapping between external entity IDs and internal database IDs."""

    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    @staticmethod
    def resolve_id(conn: Any, entity_id: str) -> int:
        """Resolve external entity ID to internal database ID."""
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT internal_id FROM entity_id_mapping WHERE entity_id = %s",
                (entity_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def entity_exists(self, conn: Any, entity_id: str) -> bool:
        """Check if an entity exists in the database."""
        return self.resolve_id(conn, entity_id) != 0

    @staticmethod
    def resolve_entity_id(conn: Any, internal_id: int) -> str:
        """Resolve internal database ID to external entity ID."""
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT entity_id FROM entity_id_mapping WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else ""

    def register_entity(self, conn: Any, entity_id: str) -> None:
        """Register a new entity in the database with a unique internal ID."""
        from models.infrastructure.unique_id import generate_unique_id

        # Check if entity already exists
        if self.entity_exists(conn, entity_id):
            return  # Already registered, idempotent

        internal_id = generate_unique_id()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
                (entity_id, internal_id),
            )
