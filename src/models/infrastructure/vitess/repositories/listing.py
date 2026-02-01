"""Repository for entity listing operations."""

from models.infrastructure.vitess.repository import Repository
from models.data.rest_api.v1.entitybase.response import EntityListing


class ListingRepository(Repository):
    """Repository for entity listing operations."""

    @staticmethod
    def _get_entity_type_from_id(entity_id: str) -> str:
        """Derive entity type from entity_id pattern."""
        if entity_id.startswith("Q"):
            return "item"
        elif entity_id.startswith("L"):
            return "lexeme"
        elif entity_id.startswith("P"):
            return "property"
        return "unknown"

    def list_locked(self, limit: int) -> list[EntityListing]:
        cursor = self.vitess_client.cursor
        cursor.execute(
            """SELECT m.entity_id
                    FROM entity_head h
                    JOIN entity_id_mapping m ON h.internal_id = m.internal_id
                    WHERE h.is_locked = TRUE
                    LIMIT %s""",
            (limit,),
        )
        result = []
        for row in cursor.fetchall():
            entity_id = row[0]
            entity_type = self._get_entity_type_from_id(entity_id)
            result.append(EntityListing(entity_id=entity_id, entity_type=entity_type, reason="locked"))
        return result

    def list_semi_protected(self, limit: int) -> list[EntityListing]:
        cursor = self.vitess_client.cursor
        cursor.execute(
            """SELECT m.entity_id
                    FROM entity_head h
                    JOIN entity_id_mapping m ON h.internal_id = m.internal_id
                    WHERE h.is_semi_protected = TRUE
                    LIMIT %s""",
            (limit,),
        )
        result = []
        for row in cursor.fetchall():
            entity_id = row[0]
            entity_type = self._get_entity_type_from_id(entity_id)
            result.append(EntityListing(entity_id=entity_id, entity_type=entity_type, reason="semi_protected"))
        return result

    def list_archived(self, limit: int) -> list[EntityListing]:
        cursor = self.vitess_client.cursor
        cursor.execute(
            """SELECT m.entity_id
                    FROM entity_head h
                    JOIN entity_id_mapping m ON h.internal_id = m.internal_id
                    WHERE h.is_archived = TRUE
                    LIMIT %s""",
            (limit,),
        )
        result = []
        for row in cursor.fetchall():
            entity_id = row[0]
            entity_type = self._get_entity_type_from_id(entity_id)
            result.append(EntityListing(entity_id=entity_id, entity_type=entity_type, reason="archived"))
        return result

    def list_dangling(self, limit: int) -> list[EntityListing]:
        cursor = self.vitess_client.cursor
        cursor.execute(
            """SELECT m.entity_id
                    FROM entity_head h
                    JOIN entity_id_mapping m ON h.internal_id = m.internal_id
                    WHERE h.is_dangling = TRUE
                    LIMIT %s""",
            (limit,),
        )
        result = []
        for row in cursor.fetchall():
            entity_id = row[0]
            entity_type = self._get_entity_type_from_id(entity_id)
            result.append(EntityListing(entity_id=entity_id, entity_type=entity_type, reason="dangling"))
        return result

    def _list_entities_by_edit_type(
        self, edit_type: str, limit: int
    ) -> list[EntityListing]:
        cursor = self.vitess_client.cursor
        cursor.execute(
            """SELECT DISTINCT m.entity_id, r.edit_type
                    FROM entity_revisions r
                    JOIN entity_head h ON r.internal_id = h.internal_id
                    JOIN entity_id_mapping m ON h.internal_id = m.internal_id
                    WHERE r.edit_type = %s
                    LIMIT %s""",
            (edit_type, limit),
        )
        result = []
        for row in cursor.fetchall():
            entity_id = row[0]
            entity_type = self._get_entity_type_from_id(entity_id)
            result.append(EntityListing(entity_id=entity_id, entity_type=entity_type, reason=row[1]))
        return result
