"""Repository for managing entity backlinks in Vitess."""

"""Repository for managing entity backlinks in Vitess."""

import json
import logging
from typing import Any

from models.common import OperationResult
from models.rest_api.utils import raise_validation_error
from models.infrastructure.vitess.backlink_entry import BacklinkRecord
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class BacklinkRepository:
    """Repository for managing entity backlinks in Vitess."""

    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def insert_backlinks(
        self, conn: Any, backlinks: list[tuple[int, int, int, str, str]]
    ) -> OperationResult:
        """Insert backlinks into entity_backlinks table.

        backlinks: list of (referenced_internal_id, referencing_internal_id, statement_hash, property_id, rank)
        """
        if not backlinks:
            return OperationResult(success=True)

        try:
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
            return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def delete_backlinks_for_entity(
        self, conn: Any, referencing_internal_id: int
    ) -> OperationResult:
        """Delete all backlinks for a referencing entity (used for updates)."""
        if referencing_internal_id <= 0:
            return OperationResult(
                success=False, error="Invalid referencing internal ID"
            )

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM entity_backlinks WHERE referencing_internal_id = %s",
                    (referencing_internal_id,),
                )
            return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def get_backlinks(
        self, conn: Any, referenced_internal_id: int, limit: int = 100, offset: int = 0
    ) -> list[BacklinkRecord]:
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
                BacklinkRecord(
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
        """Insert daily backlink statistics.

        Args:
            conn: Database connection
            date: Date string in ISO format (YYYY-MM-DD)
            total_backlinks: Total number of backlinks
            unique_entities_with_backlinks: Number of unique entities with backlinks
            top_entities_by_backlinks: List of top entities by backlink count

        Raises:
            ValidationError: If input validation fails
            Exception: If database operation fails
        """
        # Input validation
        if not isinstance(date, str) or len(date) != 10:
            raise ValidationError(f"Invalid date format: {date}. Expected YYYY-MM-DD")
        if total_backlinks < 0:
            raise ValidationError(f"total_backlinks must be non-negative: {total_backlinks}")
        if unique_entities_with_backlinks < 0:
            raise ValidationError(f"unique_entities_with_backlinks must be non-negative: {unique_entities_with_backlinks}")
        if not isinstance(top_entities_by_backlinks, list):
            raise ValidationError("top_entities_by_backlinks must be a list")

        logger.debug(f"Inserting backlink statistics for date {date}")

        try:
            # Serialize top entities to JSON
            top_entities_json = json.dumps(top_entities_by_backlinks)
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Failed to serialize top_entities_by_backlinks: {e}")

        with conn.cursor() as cursor:
            try:
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
                        top_entities_json,
                    ),
                )
                logger.info(f"Successfully stored backlink statistics for {date}")
            except Exception as e:
                logger.error(f"Failed to insert backlink statistics for {date}: {e}")
                raise
