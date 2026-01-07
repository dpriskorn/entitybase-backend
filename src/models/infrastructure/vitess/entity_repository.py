from typing import Any


class EntityRepository:
    def __init__(self, connection_manager: Any, id_resolver: Any) -> None:
        self.connection_manager = connection_manager
        self.id_resolver = id_resolver

    def get_head(self, entity_id: str) -> int:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return 0
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT head_revision_id FROM entity_head WHERE internal_id = %s",
            (internal_id,),
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else 0

    def is_deleted(self, entity_id: str) -> bool:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return False
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_deleted FROM entity_head WHERE internal_id = %s",
            (internal_id,),
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else False

    def is_locked(self, entity_id: str) -> bool:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return False
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_locked FROM entity_head WHERE internal_id = %s",
            (internal_id,),
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else False

    def is_archived(self, entity_id: str) -> bool:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return False
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_archived FROM entity_head WHERE internal_id = %s",
            (internal_id,),
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else False

    def get_protection_info(self, entity_id: str) -> dict[str, bool]:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return {}

        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected
                   FROM entity_head
                   WHERE internal_id = %s""",
            (internal_id,),
        )
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return {}

        return {
            "is_semi_protected": bool(result[0]),
            "is_locked": bool(result[1]),
            "is_archived": bool(result[2]),
            "is_dangling": bool(result[3]),
            "is_mass_edit_protected": bool(result[4]),
        }
