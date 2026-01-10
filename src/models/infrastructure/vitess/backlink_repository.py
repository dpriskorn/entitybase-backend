from typing import Any, Union


class BacklinkRepository:
    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def insert_backlinks(
        self, conn: Any, backlinks: list[tuple[int, int, int, str, str]]
    ) -> None:
        """Insert backlinks into entity_backlinks table.

        backlinks: list of (referenced_internal_id, referencing_internal_id, statement_hash, property_id, rank)
        """
        if not backlinks:
            return

        with conn.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO entity_backlinks 
                (referenced_internal_id, referencing_internal_id, statement_hash, property_id, rank)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                referenced_internal_id = referenced_internal_id  -- no-op, just to handle duplicates
                """,
                backlinks,
            )

    def delete_backlinks_for_entity(
        self, conn: Any, referencing_internal_id: int
    ) -> None:
        """Delete all backlinks for a referencing entity (used for updates)."""
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM entity_backlinks WHERE referencing_internal_id = %s",
                (referencing_internal_id,),
            )

    def get_backlinks(
        self, conn: Any, referenced_internal_id: int, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Union[int, str]]]:
        """Get backlinks for an entity."""
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT referencing_internal_id, statement_hash, property_id, rank
                FROM entity_backlinks
                WHERE referenced_internal_id = %s
                ORDER BY statement_hash
                LIMIT %s OFFSET %s
                """,
                (referenced_internal_id, limit, offset),
            )
            return [
                {
                    "referencing_internal_id": row[0],
                    "statement_hash": row[1],
                    "property_id": row[2],
                    "rank": row[3],
                }
                for row in cursor.fetchall()
            ]
