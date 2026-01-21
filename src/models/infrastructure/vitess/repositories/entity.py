"""Vitess entity repository for database operations."""

import logging

from models.infrastructure.vitess.repository import Repository
from models.rest_api.entitybase.v1.response import ProtectionResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EntityRepository(Repository):
    """Repository for entity-related database operations."""

    def get_head(self, entity_id: str) -> int:
        """Get the current head revision ID for an entity."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return 0
        cursor = self.vitess_client.cursor
            cursor.execute(
                "SELECT head_revision_id FROM entity_head WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def is_deleted(self, entity_id: str) -> bool:
        """Check if an entity is marked as deleted."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return False
        cursor = self.vitess_client.cursor
            cursor.execute(
                "SELECT is_deleted FROM entity_head WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else False

    def is_locked(self, entity_id: str) -> bool:
        """Check if an entity is locked for editing."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return False
        cursor = self.vitess_client.cursor
            cursor.execute(
                "SELECT is_locked FROM entity_head WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else False

    def is_archived(self, entity_id: str) -> bool:
        """Check if an entity is archived."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return False
        cursor = self.vitess_client.cursor
            cursor.execute(
                "SELECT is_archived FROM entity_head WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else False

    def get_protection_info(self, entity_id: str) -> ProtectionResponse | None:
        """Get protection status information for an entity."""
        logger.debug(f"Getting protection info for entity {entity_id}")
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return None

        cursor = self.vitess_client.cursor
            cursor.execute(
                """SELECT is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected
                       FROM entity_head
                       WHERE internal_id = %s""",
                (internal_id,),
            )
            result = cursor.fetchone()

        if not result:
            return None

        return ProtectionResponse(
            semi_prot=bool(result[0]),
            locked=bool(result[1]),
            archived=bool(result[2]),
            dangling=bool(result[3]),
            mass_edit=bool(result[4]),
        )

    def create_entity(self, entity_id: str) -> None:
        """Create a new entity in the database."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            self.vitess_client.id_resolver.register_entity(entity_id)
            internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
            if not internal_id:
                raise_validation_error(
                    f"Failed to register entity {entity_id}", status_code=500
                )
        cursor = self.vitess_client.cursor
            cursor.execute(
                """INSERT INTO entity_head
                   (internal_id, head_revision_id, is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected, is_deleted, is_redirect)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (internal_id, 0, False, False, False, False, False, False, False),
            )

    def delete_entity(self, entity_id: str) -> None:
        """Delete an entity from the database."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return
        cursor = self.vitess_client.cursor
            cursor.execute(
                "DELETE FROM entity_head WHERE internal_id = %s", (internal_id,)
            )

    def update_head_revision(self, entity_id: str, revision_id: int) -> None:
        """Update the head revision for an entity."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return
        cursor = self.vitess_client.cursor
            cursor.execute(
                "UPDATE entity_head SET head_revision_id = %s WHERE internal_id = %s",
                (revision_id, internal_id),
            )
