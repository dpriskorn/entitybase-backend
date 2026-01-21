"""Vitess head repository for entity head operations."""

import logging

from models.common import OperationResult
from models.infrastructure.vitess.repository import Repository

logger = logging.getLogger(__name__)


class HeadRepository(Repository):
    """Repository for entity head revision database operations."""

    def cas_update_with_status(
        self,
        entity_id: str,
        expected_head: int = 0,
        new_head: int = 0,
        is_semi_protected: bool = False,
        is_locked: bool = False,
        is_archived: bool = False,
        is_dangling: bool = False,
        is_mass_edit_protected: bool = False,
        is_deleted: bool = False,
        is_redirect: bool = False,
    ) -> OperationResult:
        """Update entity head with compare-and-swap semantics and status flags."""
        logger.debug(
            f"CAS update for entity {entity_id}, expected head {expected_head}, new head {new_head}"
        )
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return OperationResult(success=False, error="Entity not found")

        try:
            with self.connection_manager.connection.cursor() as cursor:
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

    def hard_delete(
        self, entity_id: str, head_revision_id: int
    ) -> OperationResult:
        """Mark an entity as hard deleted."""
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return OperationResult(success=False, error=f"Entity {entity_id} not found")

        try:
            with self.connection_manager.connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE entity_head
                           SET is_deleted = TRUE,
                               head_revision_id = %s
                           WHERE internal_id = %s""",
                    (head_revision_id, internal_id),
                )
            return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def soft_delete(self, entity_id: str) -> OperationResult:
        """Mark an entity as soft deleted."""
        internal_id = self.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return OperationResult(success=False, error=f"Entity {entity_id} not found")

        try:
            with self.connection_manager.connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE entity_head
                            SET is_deleted = TRUE,
                                head_revision_id = 0
                            WHERE internal_id = %s""",
                    (internal_id,),
                )
            return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def get_head_revision(self, internal_entity_id: int) -> OperationResult:
        """Get the current head revision for an entity by internal ID."""
        if internal_entity_id <= 0:
            return OperationResult(success=False, error="Invalid internal entity ID")

        try:
            with self.connection_manager.connection.cursor() as cursor:
                cursor.execute(
                    """SELECT head_revision_id FROM entity_head WHERE internal_id = %s""",
                    (internal_entity_id,),
                )
                result = cursor.fetchone()
                if result and len(result) > 0:
                    return OperationResult(success=True, data=int(result[0]))
                return OperationResult(success=False, error="Entity not found")
        except Exception as e:
            return OperationResult(success=False, error=str(e))
