"""Vitess head repository for entity head operations."""

import logging
from typing import Any

from models.common import OperationResult
from models.validation.utils import raise_validation_error

logger = logging.getLogger(__name__)


class HeadRepository:
    """Repository for entity head revision database operations."""

    def __init__(self, connection_manager: Any, id_resolver: Any) -> None:
        self.connection_manager = connection_manager
        self.id_resolver = id_resolver

    def cas_update_with_status(
        self,
        conn: Any,
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
    ) -> OperationResult:
        """Update entity head with compare-and-swap semantics and status flags."""
        logger.debug(
            f"CAS update for entity {entity_id}, expected head {expected_head}, new head {new_head}"
        )
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            return OperationResult(success=False, error="Entity not found")

        try:
            with conn.cursor() as cursor:
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
                if affected_rows > 0:
                    return OperationResult(success=True)
                else:
                    return OperationResult(
                        success=False, error="CAS failed: head mismatch"
                    )
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def hard_delete(self, conn: Any, entity_id: str, head_revision_id: int) -> None:
        """Mark an entity as hard deleted."""
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)

        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE entity_head
                       SET is_deleted = TRUE,
                           head_revision_id = %s
                       WHERE internal_id = %s""",
                (head_revision_id, internal_id),
            )

    def soft_delete(self, conn: Any, entity_id: str) -> None:
        """Mark an entity as soft deleted."""
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)

        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE entity_head
                        SET is_deleted = TRUE,
                            head_revision_id = 0
                        WHERE internal_id = %s""",
                (internal_id,),
            )

    def get_head_revision(self, internal_entity_id: int) -> int:
        """Get the current head revision for an entity by internal ID."""
        with self.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT head_revision_id FROM entity_head WHERE internal_id = %s""",
                    (internal_entity_id,),
                )
                result = cursor.fetchone()
                if result and len(result) > 0:
                    return int(result[0])
                return 0
