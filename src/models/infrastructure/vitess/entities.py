from typing import Any


class IdResolver:
    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    @staticmethod
    def resolve_id(conn: Any, entity_id: str) -> int:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT internal_id FROM entity_id_mapping WHERE entity_id = %s",
                (entity_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def entity_exists(self, conn: Any, entity_id: str) -> bool:
        return self.resolve_id(conn, entity_id) != 0

    @staticmethod
    def resolve_entity_id(conn: Any, internal_id: int) -> str:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT entity_id FROM entity_id_mapping WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else ""

    def register_entity(self, conn: Any, entity_id: str) -> None:
        from models.infrastructure.unique_id import UniqueIdGenerator

        # Check if entity already exists
        if self.entity_exists(conn, entity_id):
            return  # Already registered, idempotent

        generator = UniqueIdGenerator()
        internal_id = generator.generate_unique_id()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
                (entity_id, internal_id),
            )
