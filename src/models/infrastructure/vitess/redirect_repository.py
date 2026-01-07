from typing import Any


class RedirectRepository:
    def __init__(self, connection_manager: Any, id_resolver: Any) -> None:
        self.connection_manager = connection_manager
        self.id_resolver = id_resolver

    def set_target(self, entity_id: str, redirects_to_entity_id: str | None) -> None:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            raise ValueError(f"Entity {entity_id} not found")

        redirects_to_internal_id = None
        if redirects_to_entity_id:
            redirects_to_internal_id = self.id_resolver.resolve_id(
                redirects_to_entity_id
            )
            if not redirects_to_internal_id:
                raise ValueError(f"Entity {redirects_to_entity_id} not found")

        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE entity_head SET redirects_to = %s WHERE internal_id = %s",
            (redirects_to_internal_id, internal_id),
        )
        cursor.close()

    def create(
        self,
        redirect_from_entity_id: str,
        redirect_to_entity_id: str,
        created_by: str = "entity-api",
    ) -> None:
        redirect_from_internal_id = self.id_resolver.resolve_id(redirect_from_entity_id)
        redirect_to_internal_id = self.id_resolver.resolve_id(redirect_to_entity_id)

        if not redirect_from_internal_id:
            raise ValueError(f"Source entity {redirect_from_entity_id} not found")
        if not redirect_to_internal_id:
            raise ValueError(f"Target entity {redirect_to_entity_id} not found")

        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO entity_redirects
                   (redirect_from_id, redirect_to_id, created_by)
                   VALUES (%s, %s, %s)""",
            (redirect_from_internal_id, redirect_to_internal_id, created_by),
        )
        cursor.close()

    def get_incoming_redirects(self, entity_id: str) -> list[str]:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return []

        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.entity_id
                   FROM entity_redirects r
                   JOIN entity_id_mapping m ON r.redirect_from_id = m.internal_id
                   WHERE r.redirect_to_id = %s""",
            (internal_id,),
        )
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result

    def get_target(self, entity_id: str) -> str | None:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return None
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.entity_id
                   FROM entity_head h
                   JOIN entity_id_mapping m ON h.redirects_to = m.internal_id
                   WHERE h.internal_id = %s""",
            (internal_id,),
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
