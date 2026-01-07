import pymysql
from typing import Any


class HeadRepository:
    def __init__(self, connection_manager: Any, id_resolver: Any) -> None:
        self.connection_manager = connection_manager
        self.id_resolver = id_resolver

    def cas_update_with_status(
        self,
        entity_id: str,
        expected_head: int | None,
        new_head: int,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool,
        is_deleted: bool,
        is_redirect: bool = False,
    ) -> bool:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return False

        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE entity_head
                   SET head_revision_id = %s,
                       is_semi_protected = %s,
                       is_locked = %s,
                       is_archived = %s,
                       is_dangling = %s,
                       is_mass_edit_protected = %s,
                       is_deleted = %s,
                       is_redirect = %s
                   WHERE internal_id = %s AND head_revision_id = %s""",
            (
                new_head,
                is_semi_protected,
                is_locked,
                is_archived,
                is_dangling,
                is_mass_edit_protected,
                is_deleted,
                is_redirect,
                internal_id,
                expected_head,
            ),
        )
        affected_rows = int(cursor.rowcount)
        cursor.close()
        return affected_rows > 0

    def insert_with_status(
        self,
        entity_id: str,
        head_revision_id: int,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool,
        is_deleted: bool,
        is_redirect: bool = False,
    ) -> bool:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return False

        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO entity_head
                       (internal_id, head_revision_id, is_semi_protected, is_locked,
                        is_archived, is_dangling, is_mass_edit_protected, is_deleted, is_redirect)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    internal_id,
                    head_revision_id,
                    is_semi_protected,
                    is_locked,
                    is_archived,
                    is_dangling,
                    is_mass_edit_protected,
                    is_deleted,
                    is_redirect,
                ),
            )
            cursor.close()
            return True
        except pymysql.IntegrityError:
            cursor.close()
            return False

    def hard_delete(self, entity_id: str, head_revision_id: int) -> None:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            raise ValueError(f"Entity {entity_id} not found")
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE entity_head
                   SET is_deleted = TRUE,
                       head_revision_id = %s
                   WHERE internal_id = %s""",
            (head_revision_id, internal_id),
        )
        cursor.close()

    def soft_delete(self, entity_id: str) -> None:
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            raise ValueError(f"Entity {entity_id} not found")

        conn = self.connection_manager.connect()
        cursor = conn.cursor()

        cursor.execute(
            """UPDATE entity_head
                   SET is_deleted = TRUE,
                       head_revision_id = 0
                   WHERE internal_id = %s""",
            (internal_id,),
        )

        cursor.close()
