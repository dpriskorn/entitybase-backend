"""Vitess statement repository for statement operations."""

import logging

from models.data.common import OperationResult
from models.infrastructure.vitess.repository import Repository

logger = logging.getLogger(__name__)


class StatementRepository(Repository):
    """Repository for statement-related database operations."""

    def insert_content(self, content_hash: int) -> OperationResult:
        """Insert statement content hash if it doesn't exist."""
        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    "SELECT 1 FROM statement_content WHERE content_hash = %s",
                    (content_hash,),
                )
                if cursor.fetchone() is not None:
                    return OperationResult(
                        success=False, error="Content hash already exists"
                    )

                cursor.execute(
                    "INSERT INTO statement_content (content_hash) VALUES (%s)",
                    (content_hash,),
                )
                return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def increment_ref_count(self, content_hash: int) -> OperationResult:
        """Increment reference count for statement content."""
        if content_hash <= 0:
            return OperationResult(success=False, error="Invalid content hash")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    "UPDATE statement_content SET ref_count = ref_count + 1 WHERE content_hash = %s",
                    (content_hash,),
                )
                cursor.execute(
                    "SELECT ref_count FROM statement_content WHERE content_hash = %s",
                    (content_hash,),
                )
                result = cursor.fetchone()
                new_count = result[0] if result else 0
                return OperationResult(success=True, data=new_count)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def decrement_ref_count(self, content_hash: int) -> OperationResult:
        """Decrement reference count for statement content."""
        if content_hash <= 0:
            return OperationResult(success=False, error="Invalid content hash")

        logger.debug(f"Decrementing ref count for content hash {content_hash}")
        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    "UPDATE statement_content SET ref_count = ref_count - 1 WHERE content_hash = %s",
                    (content_hash,),
                )
                cursor.execute(
                    "SELECT ref_count FROM statement_content WHERE content_hash = %s",
                    (content_hash,),
                )
                result = cursor.fetchone()
                new_count = result[0] if result else 0
                return OperationResult(success=True, data=new_count)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def get_orphaned(self, older_than_days: int, limit: int) -> OperationResult:
        """Get orphaned statement content hashes."""
        if older_than_days <= 0 or limit <= 0:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    """SELECT content_hash
                            FROM statement_content
                            WHERE ref_count = 0
                            AND created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                            LIMIT %s""",
                    (older_than_days, limit),
                )
                result = [row[0] for row in cursor.fetchall()]
                return OperationResult(success=True, data=result)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def get_most_used(self, limit: int, min_ref_count: int = 1) -> list[int]:
        """Get most used statement content hashes."""
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                """SELECT content_hash
                        FROM statement_content
                        WHERE ref_count >= %s
                        ORDER BY ref_count DESC
                        LIMIT %s""",
                (min_ref_count, limit),
            )
            result = [row[0] for row in cursor.fetchall()]
            return result

    def get_ref_count(self, content_hash: int) -> int:
        """Get the reference count for a statement."""
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                "SELECT ref_count FROM statement_content WHERE content_hash = %s",
                (content_hash,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def delete_content(self, content_hash: int) -> None:
        """Delete statement content when ref_count reaches 0."""
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                "DELETE FROM statement_content WHERE content_hash = %s AND ref_count <= 0",
                (content_hash,),
            )

    def get_all_statement_hashes(self) -> list[int]:
        """Get all statement content hashes."""
        with self.vitess_client.cursor as cursor:
            cursor.execute("SELECT content_hash FROM statement_content")
            result = [row[0] for row in cursor.fetchall()]
            return result
