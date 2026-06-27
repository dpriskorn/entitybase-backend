"""Vitess redirect repository for redirect operations."""

import logging

from models.data.common import OperationResult
from models.infrastructure.vitess.repository import Repository
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class RedirectRepository(Repository):
    """Repository for entity redirect database operations."""

    def set_target(
        self,
        entity_id: str,
        redirects_to_entity_id: str = "",
        expected_redirects_to: int = 0,
    ) -> OperationResult:
        """Set redirect target for an entity."""
        logger.debug(
            f"Setting redirect target for {entity_id} to {redirects_to_entity_id}"
        )
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return OperationResult(success=False, error=f"Entity {entity_id} not found")

        redirects_to_internal_id = None
        if redirects_to_entity_id:
            redirects_to_internal_id = self.vitess_client.id_resolver.resolve_id(
                redirects_to_entity_id
            )
            if not redirects_to_internal_id:
                return OperationResult(
                    success=False, error=f"Entity {redirects_to_entity_id} not found"
                )

        try:
            with self.vitess_client.cursor as cursor:
                if expected_redirects_to != 0:
                    cursor.execute(
                        "UPDATE entity_head SET redirects_to = %s WHERE internal_id = %s AND redirects_to = %s",
                        (redirects_to_internal_id, internal_id, expected_redirects_to),
                    )
                else:
                    cursor.execute(
                        "UPDATE entity_head SET redirects_to = %s WHERE internal_id = %s",
                        (redirects_to_internal_id, internal_id),
                    )
                affected_rows = int(cursor.rowcount)
                if affected_rows > 0:
                    return OperationResult(success=True)
                else:
                    return OperationResult(
                        success=False, error="CAS failed: redirect mismatch"
                    )
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def create(
        self,
        redirect_from_entity_id: str,
        redirect_to_entity_id: str,
        created_by: str = "rest-api",
    ) -> None:
        """Create a redirect from one entity to another."""
        logger.debug(
            f"Creating redirect from {redirect_from_entity_id} to {redirect_to_entity_id}"
        )
        redirect_from_internal_id = self.vitess_client.id_resolver.resolve_id(
            redirect_from_entity_id
        )
        redirect_to_internal_id = self.vitess_client.id_resolver.resolve_id(
            redirect_to_entity_id
        )

        if not redirect_from_internal_id:
            raise_validation_error(
                f"Source entity {redirect_from_entity_id} not found", status_code=404
            )
        if not redirect_to_internal_id:
            raise_validation_error(
                f"Target entity {redirect_to_entity_id} not found", status_code=404
            )

        with self.vitess_client.cursor as cursor:
            cursor.execute(
                """INSERT INTO entity_redirects
                           (redirect_from_id, redirect_to_id, created_by)
                           VALUES (%s, %s, %s)""",
                (redirect_from_internal_id, redirect_to_internal_id, created_by),
            )

    def get_incoming_redirects(self, entity_id: str) -> list[str]:
        """Get entities that redirect to the given entity."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return []

        with self.vitess_client.cursor as cursor:
            cursor.execute(
                """SELECT m.entity_id
                       FROM entity_redirects r
                       JOIN entity_id_mapping m ON r.redirect_from_id = m.internal_id
                       WHERE r.redirect_to_id = %s""",
                (internal_id,),
            )
            result = [row[0] for row in cursor.fetchall()]
            return result

    def get_target(self, entity_id: str) -> str:
        """Get the redirect target for an entity."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return ""
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                """SELECT m.entity_id
                       FROM entity_head h
                       JOIN entity_id_mapping m ON h.redirects_to = m.internal_id
                       WHERE h.internal_id = %s""",
                (internal_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else ""
