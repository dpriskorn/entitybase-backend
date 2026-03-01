"""Vitess head repository for entity head operations."""

import logging

from models.data.common import OperationResult
from models.infrastructure.vitess.repository import Repository

logger = logging.getLogger(__name__)


class HeadRepository(Repository):
    """Repository for entity head revision database operations."""

    def get_head_revision(self, internal_entity_id: int) -> OperationResult:
        """Get the current head revision for an entity by internal ID."""
        if internal_entity_id <= 0:
            return OperationResult(success=False, error="Invalid internal entity ID")

        try:
            with self.vitess_client.cursor as cursor:
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
