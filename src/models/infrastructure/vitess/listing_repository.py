from typing import Any


class ListingRepository:
    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    # DISABLED: Listing methods not currently used
    # Uncomment when entity listing endpoints are implemented

    # def list_locked(self, conn: Any, limit: int) -> list[dict]:
    #     with conn.cursor() as cursor:
    #         cursor.execute(
    #             """SELECT m.entity_id, h.head_revision_id
    #                    FROM entity_head h
    #                    JOIN entity_id_mapping m ON h.internal_id = m.internal_id
    #                    WHERE h.is_locked = TRUE
    #                    LIMIT %s""",
    #             (limit,),
    #         )
    #         result = [
    #             {"entity_id": row[0], "head_revision_id": row[1]}
    #             for row in cursor.fetchall()
    #         ]
    #         return result

    # def list_semi_protected(self, conn: Any, limit: int) -> list[dict]:
    #     with conn.cursor() as cursor:
    #         cursor.execute(
    #             """SELECT m.entity_id, h.head_revision_id
    #                    FROM entity_head h
    #                    JOIN entity_id_mapping m ON h.internal_id = m.internal_id
    #                    WHERE h.is_semi_protected = TRUE
    #                    LIMIT %s""",
    #             (limit,),
    #         )
    #         result = [
    #             {"entity_id": row[0], "head_revision_id": row[1]}
    #             for row in cursor.fetchall()
    #         ]
    #         return result

    # def list_archived(self, conn: Any, limit: int) -> list[dict]:
    #     with conn.cursor() as cursor:
    #         cursor.execute(
    #             """SELECT m.entity_id, h.head_revision_id
    #                    FROM entity_head h
    #                    JOIN entity_id_mapping m ON h.internal_id = m.internal_id
    #                    WHERE h.is_archived = TRUE
    #                    LIMIT %s""",
    #             (limit,),
    #         )
    #         result = [
    #             {"entity_id": row[0], "head_revision_id": row[1]}
    #             for row in cursor.fetchall()
    #         ]
    #         return result

    # def list_dangling(self, conn: Any, limit: int) -> list[dict]:
    #     with conn.cursor() as cursor:
    #         cursor.execute(
    #             """SELECT m.entity_id, h.head_revision_id
    #                    FROM entity_head h
    #                    JOIN entity_id_mapping m ON h.internal_id = m.internal_id
    #                    WHERE h.is_dangling = TRUE
    #                    LIMIT %s""",
    #             (limit,),
    #         )
    #         result = [
    #             {"entity_id": row[0], "head_revision_id": row[1]}
    #             for row in cursor.fetchall()
    #         ]
    #         return result

    # def list_by_edit_type(self, conn: Any, edit_type: str, limit: int) -> list[dict]:
    #     with conn.cursor() as cursor:
    #         cursor.execute(
    #             """SELECT DISTINCT m.entity_id, r.edit_type, r.revision_id
    #                    FROM entity_revisions r
    #                    JOIN entity_head h ON r.internal_id = h.internal_id
    #                    JOIN entity_id_mapping m ON h.internal_id = m.internal_id
    #                    WHERE r.edit_type = %s
    #                    LIMIT %s""",
    #             (edit_type, limit),
    #         )
    #         result = [
    #             {"entity_id": row[0], "edit_type": row[1], "revision_id": row[2]}
    #             for row in cursor.fetchall()
    #         ]
    #         return result
