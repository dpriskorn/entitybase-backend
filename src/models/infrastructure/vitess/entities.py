from typing import Any


class IdResolver:
    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def resolve_id(self, entity_id: str) -> int:
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT internal_id FROM entity_id_mapping WHERE entity_id = %s",
            (entity_id,),
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else 0

    def entity_exists(self, entity_id: str) -> bool:
        return self.resolve_id(entity_id) != 0

    def register_entity(self, entity_id: str) -> None:
        from models.infrastructure.ulid_flake import generate_ulid_flake

        internal_id = generate_ulid_flake()
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
            (entity_id, internal_id),
        )
        cursor.close()
