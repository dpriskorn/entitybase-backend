"""Vitess head repository for entity head operations."""

import logging

from models.data.common import OperationResult
from models.data.rest_api.v1.entitybase.request.entity.context import EntityHeadUpdateContext
from models.infrastructure.vitess.repository import Repository

logger = logging.getLogger(__name__)


class HeadRepository(Repository):
    """Repository for entity head revision database operations."""

    def cas_update_with_status(self, ctx: EntityHeadUpdateContext) -> OperationResult:
        """Update entity head with compare-and-swap semantics and status flags."""
        logger.debug(
            f"CAS update for entity {ctx.entity_id}, expected head {ctx.expected_head}, new head {ctx.new_head}"
        )
        internal_id = self.vitess_client.id_resolver.resolve_id(ctx.entity_id)
        if not internal_id:
            return OperationResult(success=False, error="Entity not found")

        try:
            cursor = self.vitess_client.cursor
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
                    ctx.new_head,
                    ctx.is_semi_protected,
                    ctx.is_locked,
                    ctx.is_archived,
                    ctx.is_dangling,
                    ctx.is_mass_edit_protected,
                    ctx.is_deleted,
                    ctx.is_redirect,
                    internal_id,
                    ctx.expected_head,
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

    def hard_delete(self, entity_id: str, head_revision_id: int) -> OperationResult:
        """Mark an entity as hard deleted."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return OperationResult(success=False, error=f"Entity {entity_id} not found")

        try:
            cursor = self.vitess_client.cursor
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
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return OperationResult(success=False, error=f"Entity {entity_id} not found")

        try:
            cursor = self.vitess_client.cursor
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
            cursor = self.vitess_client.cursor
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
