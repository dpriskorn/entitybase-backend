"""Repository for entity listing operations."""

from typing import Any

from pydantic import BaseModel

from models.rest_api.entitybase.response.listings import EntityListing


class EntityHeadListing(BaseModel):
    """Model for entity head listings."""

    entity_id: str
    head_revision_id: int


class EntityEditListing(BaseModel):
    """Model for entity edit type listings."""

    entity_id: str
    edit_type: str
    revision_id: int


class ListingRepository:
    """Repository for entity listing operations."""

    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def list_locked(self, conn: Any, limit: int) -> list[EntityListing]:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT m.entity_id, r.entity_type
                        FROM entity_head h
                        JOIN entity_id_mapping m ON h.internal_id = m.internal_id
                        JOIN entity_revisions r ON r.internal_id = h.internal_id AND r.revision_id = h.head_revision_id
                        WHERE h.is_locked = TRUE
                        LIMIT %s""",
                (limit,),
            )
            result = [
                EntityListing(entity_id=row[0], entity_type=row[1], reason="locked")
                for row in cursor.fetchall()
            ]
            return result

    def list_semi_protected(self, conn: Any, limit: int) -> list[EntityListing]:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT m.entity_id, r.entity_type
                        FROM entity_head h
                        JOIN entity_id_mapping m ON h.internal_id = m.internal_id
                        JOIN entity_revisions r ON r.internal_id = h.internal_id AND r.revision_id = h.head_revision_id
                        WHERE h.is_semi_protected = TRUE
                        LIMIT %s""",
                (limit,),
            )
            result = [
                EntityListing(
                    entity_id=row[0], entity_type=row[1], reason="semi_protected"
                )
                for row in cursor.fetchall()
            ]
            return result

    def list_archived(self, conn: Any, limit: int) -> list[EntityListing]:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT m.entity_id, r.entity_type
                        FROM entity_head h
                        JOIN entity_id_mapping m ON h.internal_id = m.internal_id
                        JOIN entity_revisions r ON r.internal_id = h.internal_id AND r.revision_id = h.head_revision_id
                        WHERE h.is_archived = TRUE
                        LIMIT %s""",
                (limit,),
            )
            result = [
                EntityListing(entity_id=row[0], entity_type=row[1], reason="archived")
                for row in cursor.fetchall()
            ]
            return result

    def list_dangling(self, conn: Any, limit: int) -> list[EntityListing]:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT m.entity_id, r.entity_type
                        FROM entity_head h
                        JOIN entity_id_mapping m ON h.internal_id = m.internal_id
                        JOIN entity_revisions r ON r.internal_id = h.internal_id AND r.revision_id = h.head_revision_id
                        WHERE h.is_dangling = TRUE
                        LIMIT %s""",
                (limit,),
            )
            result = [
                EntityListing(entity_id=row[0], entity_type=row[1], reason="dangling")
                for row in cursor.fetchall()
            ]
            return result

    def _list_entities_by_edit_type(
        self, conn: Any, edit_type: str, limit: int
    ) -> list[EntityListing]:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT DISTINCT m.entity_id, r.entity_type, r.edit_type
                        FROM entity_revisions r
                        JOIN entity_head h ON r.internal_id = h.internal_id
                        JOIN entity_id_mapping m ON h.internal_id = m.internal_id
                        WHERE r.edit_type = %s
                        LIMIT %s""",
                (edit_type, limit),
            )
            result = [
                EntityListing(entity_id=row[0], entity_type=row[1], reason=row[2])
                for row in cursor.fetchall()
            ]
            return result
