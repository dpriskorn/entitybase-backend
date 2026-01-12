"""Vitess entity repository for database operations."""

from typing import Any

from models.rest_api.response.entity import ProtectionResponse


class EntityRepository:
    """Repository for entity-related database operations."""

    def __init__(self, connection_manager: Any, id_resolver: Any) -> None:
        self.connection_manager = connection_manager
        self.id_resolver = id_resolver

    def get_head(self, conn: Any, entity_id: str) -> int:
        """Get the current head revision ID for an entity."""
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            return 0
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT head_revision_id FROM entity_head WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def is_deleted(self, conn: Any, entity_id: str) -> bool:
        """Check if an entity is marked as deleted."""
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            return False
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT is_deleted FROM entity_head WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else False

    def is_locked(self, conn: Any, entity_id: str) -> bool:
        """Check if an entity is locked for editing."""
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            return False
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT is_locked FROM entity_head WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else False

    def is_archived(self, conn: Any, entity_id: str) -> bool:
        """Check if an entity is archived."""
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            return False
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT is_archived FROM entity_head WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else False

    def get_protection_info(self, conn: Any, entity_id: str) -> ProtectionResponse | None:
        """Get protection status information for an entity."""
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            return None

        with conn.cursor() as cursor:
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
            is_semi_protected=bool(result[0]),
            is_locked=bool(result[1]),
            is_archived=bool(result[2]),
            is_dangling=bool(result[3]),
            is_mass_edit_protected=bool(result[4]),
        )
