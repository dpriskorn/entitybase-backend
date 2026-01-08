from typing import Any


class IdResolver:
    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def resolve_id(self, conn: Any, entity_id: str) -> int:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT internal_id FROM entity_id_mapping WHERE entity_id = %s",
                (entity_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def entity_exists(self, conn: Any, entity_id: str) -> bool:
        return self.resolve_id(conn, entity_id) != 0

    def register_entity(self, conn: Any, entity_id: str) -> None:
        from models.infrastructure.ulid_flake import generate_ulid_flake

        # Check if entity already exists
        if self.entity_exists(conn, entity_id):
            return  # Already registered, idempotent

        internal_id = generate_ulid_flake()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
                (entity_id, internal_id),
            )
