from typing import Any


class IdResolver:
    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    
    def resolve_id(self, entity_id: str) -> int:
        with self.connection_manager.connection.cursor() as cursor:
            cursor.execute(
                "SELECT internal_id FROM entity_id_mapping WHERE entity_id = %s",
                (entity_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def entity_exists(self, entity_id: str) -> bool:
        return self.resolve_id(entity_id) != 0

    
    def resolve_entity_id(self, internal_id: int) -> str:
        with self.connection_manager.connection.cursor() as cursor:
            cursor.execute(
                "SELECT entity_id FROM entity_id_mapping WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else ""

    def register_entity(self, entity_id: str) -> None:
        from models.infrastructure.unique_id import UniqueIdGenerator

        # Check if entity already exists
        if self.entity_exists(entity_id):
            return  # Already registered, idempotent

        generator = UniqueIdGenerator()
        internal_id = generator.generate_unique_id()
        with self.connection_manager.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
                (entity_id, internal_id),
            )
