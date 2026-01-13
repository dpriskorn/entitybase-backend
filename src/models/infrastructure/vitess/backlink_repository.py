"""Repository for managing entity backlinks in Vitess."""

"""Repository for managing entity backlinks in Vitess."""

import logging
from typing import Any

from models.vitess_models import BacklinkData

logger = logging.getLogger(__name__)


class BacklinkRepository:
    """Repository for managing entity backlinks in Vitess."""

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
    ) -> list[BacklinkData]:
        """Get backlinks for an entity."""
        logger.debug(
            f"Getting backlinks for internal_id {referenced_internal_id}, limit {limit}"
        )
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
                BacklinkData(
                    referencing_internal_id=row[0],
                    statement_hash=str(row[1]),
                    property_id=str(row[2]),
                    rank=str(row[3]),
                )
                for row in cursor.fetchall()
            ]

    def insert_backlink_statistics(
        self,
        conn: Any,
        date: str,
        total_backlinks: int,
        unique_entities_with_backlinks: int,
        top_entities_by_backlinks: list[dict],
    ) -> None:
        """Insert daily backlink statistics."""
        logger.debug(f"Inserting backlink statistics for date {date}")
        import json

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO backlink_statistics 
                (date, total_backlinks, unique_entities_with_backlinks, top_entities_by_backlinks)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                total_backlinks = VALUES(total_backlinks),
                unique_entities_with_backlinks = VALUES(unique_entities_with_backlinks),
                top_entities_by_backlinks = VALUES(top_entities_by_backlinks)
                """,
                (
                    date,
                    total_backlinks,
                    unique_entities_with_backlinks,
                    json.dumps(top_entities_by_backlinks),
                ),
            )
