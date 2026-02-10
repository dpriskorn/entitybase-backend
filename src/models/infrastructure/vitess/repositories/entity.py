"""Vitess entity repository for database operations."""

import logging

from models.infrastructure.vitess.repository import Repository
from models.data.rest_api.v1.entitybase.response import ProtectionResponse
from models.data.rest_api.v1.entitybase.response.entity.entitybase import (
    EntityListItem,
    EntityListItemWithEditType,
)
from models.data.rest_api.v1.entitybase.request.entity_filter import EntityFilterRequest
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EntityRepository(Repository):
    """Repository for entity-related database operations."""

    def get_head(self, entity_id: str) -> int:
        """Get the current head revision ID for an entity."""
        logger.debug(f"Getting head revision for entity {entity_id}")
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            logger.debug(f"No internal ID found for entity {entity_id}")
            return 0
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                "SELECT head_revision_id FROM entity_head WHERE internal_id = %s",
                (internal_id,),
            )
            result = cursor.fetchone()
            head_rev = result[0] if result else 0
            logger.debug(f"Head revision for {entity_id}: {head_rev}")
            return head_rev

    def is_deleted(self, entity_id: str) -> bool:
        """Check if an entity is marked as deleted."""
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return False
        with self.vitess_client.cursor as cursor:
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
        with self.vitess_client.cursor as cursor:
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
        with self.vitess_client.cursor as cursor:
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

        with self.vitess_client.cursor as cursor:
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
        with self.vitess_client.cursor as cursor:
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
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                "DELETE FROM entity_head WHERE internal_id = %s", (internal_id,)
            )

    def list_entities_filtered(
        self, filter_request: EntityFilterRequest
    ) -> list[EntityListItem | EntityListItemWithEditType]:
        """List entities with optional filters by type, status, and edit_type."""
        entity_type = filter_request.entity_type
        status = filter_request.status
        edit_type = filter_request.edit_type
        limit = filter_request.limit
        offset = filter_request.offset
        logger.debug(
            f"Listing entities - type: {entity_type}, status: {status}, edit_type: {edit_type}, limit: {limit}, offset: {offset}"
        )

        with self.vitess_client.cursor as cursor:
            status_column_map = {
                "locked": "is_locked",
                "semi_protected": "is_semi_protected",
                "archived": "is_archived",
                "dangling": "is_dangling",
            }

            base_query = """SELECT e.entity_id, h.head_revision_id"""
            if edit_type:
                base_query += ", r.edit_type, r.revision_id"

            base_query += " FROM entity_id_mapping e"
            base_query += " JOIN entity_head h ON e.internal_id = h.internal_id"

            if edit_type:
                base_query += " JOIN entity_revisions r ON h.internal_id = r.internal_id AND h.head_revision_id = r.revision_id"

            conditions = []
            params = []

            if entity_type:
                pattern_map = {
                    "item": "Q%",
                    "lexeme": "L%",
                    "property": "P%",
                    "entityschema": "E%",
                }
                pattern = pattern_map.get(entity_type)
                if pattern:
                    conditions.append("e.entity_id LIKE %s")
                    params.append(pattern)

            if status:
                if status not in status_column_map:
                    logger.warning(f"Invalid status filter: {status}")
                    return []
                conditions.append(f"{status_column_map[status]} = TRUE")

            if edit_type:
                conditions.append("r.edit_type = %s")
                params.append(edit_type)

            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)

            base_query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(base_query, (*params,))
            rows = cursor.fetchall()

            entities = []
            for row in rows:
                if edit_type:
                    entities.append(
                        EntityListItemWithEditType(
                            entity_id=row[0],
                            head_revision_id=row[1],
                            edit_type=row[2],
                            revision_id=row[3],
                        )
                    )
                else:
                    entities.append(
                        EntityListItem(
                            entity_id=row[0],
                            head_revision_id=row[1],
                        )
                    )

            logger.debug(f"Found {len(entities)} entities matching filters")
            return entities
