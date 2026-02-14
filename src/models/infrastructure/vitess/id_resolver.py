import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class IdResolver(BaseModel):
    vitess_client: Any  # VitessClient

    def resolve_id(self, entity_id: str) -> int:
        logger.debug(f"[IdResolver] resolve_id({entity_id}) called")
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                "SELECT internal_id FROM entity_id_mapping WHERE entity_id = %s",
                (entity_id,),
            )
            result = cursor.fetchone()
            internal_id = result[0] if result else 0
            logger.debug(f"[IdResolver] resolve_id({entity_id}) result: {internal_id}")
            return internal_id

    def entity_exists(self, entity_id: str) -> bool:
        internal_id = self.resolve_id(entity_id)
        exists = internal_id != 0
        logger.debug(f"[IdResolver] entity_exists({entity_id}): {exists} (internal_id={internal_id})")
        return exists

    def resolve_entity_id(self, internal_id: int) -> str:
        with self.vitess_client.cursor as cursor:
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
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
                (entity_id, internal_id),
            )
