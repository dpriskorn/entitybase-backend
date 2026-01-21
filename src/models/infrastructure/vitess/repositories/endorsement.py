"""Repository for managing statement endorsements in Vitess."""

import logging
from typing import List

from models.common import OperationResult
from models.infrastructure.vitess.repository import Repository
from models.rest_api.entitybase.v1.response.endorsements import (
    StatementEndorsementResponse,
)

logger = logging.getLogger(__name__)


class EndorsementRepository(Repository):
    """Repository for managing statement endorsements in Vitess."""

    def create_endorsement(self, user_id: int, statement_hash: int) -> OperationResult:
        """Create an endorsement for a statement."""
        if user_id <= 0 or statement_hash <= 0:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            logger.debug(
                f"Creating endorsement from user {user_id} for statement {statement_hash}"
            )

            cursor = self.vitess_client.cursor
            # Check if statement exists
            cursor.execute(
                "SELECT 1 FROM statement_content WHERE content_hash = %s",
                (statement_hash,),
            )
            if not cursor.fetchone():
                return OperationResult(success=False, error="Statement not found")

            # Check for existing endorsement (active or removed)
            cursor.execute(
                "SELECT id, removed_at FROM user_statement_endorsements WHERE user_id = %s AND statement_hash = %s",
                (user_id, statement_hash),
            )
            existing = cursor.fetchone()
            if existing:
                if existing[1] is None:  # Already active
                    return OperationResult(
                        success=False, error="Already endorsed this statement"
                    )
                else:  # Previously removed, reactivate
                    cursor.execute(
                        "UPDATE user_statement_endorsements SET removed_at = NULL WHERE id = %s",
                        (existing[0],),
                    )
                    return OperationResult(success=True, data=existing[0])

            # Create new endorsement
            cursor.execute(
                "INSERT INTO user_statement_endorsements (user_id, statement_hash) VALUES (%s, %s)",
                (user_id, statement_hash),
            )
            endorsement_id = cursor.lastrowid

            return OperationResult(success=True, data=endorsement_id)
        except Exception as e:
            logger.error(f"Error creating endorsement: {e}")
            return OperationResult(success=False, error=str(e))

    def withdraw_endorsement(
        self, user_id: int, statement_hash: int
    ) -> OperationResult:
        """Withdraw an endorsement for a statement."""
        if user_id <= 0 or statement_hash <= 0:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            logger.debug(
                f"Withdrawing endorsement from user {user_id} for statement {statement_hash}"
            )
            cursor = self.vitess_client.cursor
            # Check if active endorsement exists
            cursor.execute(
                "SELECT id FROM user_statement_endorsements WHERE user_id = %s AND statement_hash = %s AND removed_at IS NULL",
                (user_id, statement_hash),
            )
            existing = cursor.fetchone()
            if not existing:
                return OperationResult(
                    success=False, error="No active endorsement found"
                )

            # Soft delete the endorsement
            cursor.execute(
                "UPDATE user_statement_endorsements SET removed_at = NOW() WHERE id = %s",
                (existing[0],),
            )

            return OperationResult(success=True, data=existing[0])
        except Exception as e:
            logger.error(f"Error withdrawing endorsement: {e}")
            return OperationResult(success=False, error=str(e))

    def get_statement_endorsements(
        self,
        statement_hash: int,
        limit: int = 50,
        offset: int = 0,
        include_removed: bool = False,
    ) -> OperationResult:
        """Get all endorsements for a statement."""
        if statement_hash <= 0 or limit <= 0 or offset < 0:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            cursor = self.vitess_client.cursor
            # Build query based on include_removed flag
            removed_condition = (
                "" if include_removed else " AND e.removed_at IS NULL"
            )

            cursor.execute(
                f"""
                SELECT e.id, e.user_id, e.statement_hash, e.created_at, e.removed_at
                FROM user_statement_endorsements e
                WHERE e.statement_hash = %s{removed_condition}
                ORDER BY e.created_at DESC
                LIMIT %s OFFSET %s
                """,
                (statement_hash, limit, offset),
            )
            rows = cursor.fetchall()

            # Get total count
            cursor.execute(
                f"""
                SELECT COUNT(*) FROM user_statement_endorsements
                WHERE statement_hash = %s{removed_condition}
                """,
                (statement_hash,),
            )
            total_count = cursor.fetchone()[0]

            endorsements = []
            for row in rows:
                endorsements.append(
                    StatementEndorsementResponse(
                        id=row[0],
                        user_id=row[1],
                        statement_hash=row[2],
                        created_at=row[3],
                        removed_at=row[4],
                    )
                )

            return OperationResult(
                success=True,
                data={
                    "endorsements": endorsements,
                    "total_count": total_count,
                    "has_more": total_count > offset + len(endorsements),
                },
            )
        except Exception as e:
            logger.error(f"Error getting statement endorsements: {e}")
            return OperationResult(success=False, error=str(e))

    def get_user_endorsements(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        include_removed: bool = False,
    ) -> OperationResult:
        """Get endorsements given by a user."""
        if user_id <= 0 or limit <= 0 or offset < 0:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            cursor = self.vitess_client.cursor
            # Build query based on include_removed flag
            removed_condition = "" if include_removed else " AND removed_at IS NULL"

            cursor.execute(
                f"""
                SELECT id, user_id, statement_hash, created_at, removed_at
                FROM user_statement_endorsements
                WHERE user_id = %s{removed_condition}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, limit, offset),
            )
            rows = cursor.fetchall()

            # Get total count
            cursor.execute(
                f"""
                SELECT COUNT(*) FROM user_statement_endorsements
                WHERE user_id = %s{removed_condition}
                """,
                (user_id,),
            )
            total_count = cursor.fetchone()[0]

            endorsements = []
            for row in rows:
                endorsements.append(
                    StatementEndorsementResponse(
                        id=row[0],
                        user_id=row[1],
                        statement_hash=row[2],
                        created_at=row[3],
                        removed_at=row[4],
                    )
                )

            return OperationResult(
                success=True,
                data={
                    "endorsements": endorsements,
                    "total_count": total_count,
                    "has_more": total_count > offset + len(endorsements),
                },
            )
        except Exception as e:
            logger.error(f"Error getting user endorsements: {e}")
            return OperationResult(success=False, error=str(e))

    def get_user_endorsement_stats(self, user_id: int) -> OperationResult:
        """Get endorsement statistics for a user."""
        if user_id <= 0:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            cursor = self.vitess_client.cursor
            # Total endorsements given (including withdrawn)
            cursor.execute(
                "SELECT COUNT(*) FROM user_statement_endorsements WHERE user_id = %s",
                (user_id,),
            )
            total_given = cursor.fetchone()[0]

            # Active endorsements
            cursor.execute(
                "SELECT COUNT(*) FROM user_statement_endorsements WHERE user_id = %s AND removed_at IS NULL",
                (user_id,),
            )
            active_count = cursor.fetchone()[0]

            return OperationResult(
                success=True,
                data={
                    "total_endorsements_given": total_given,
                    "total_endorsements_active": active_count,
                },
            )
        except Exception as e:
            logger.error(f"Error getting user endorsement stats: {e}")
            return OperationResult(success=False, error=str(e))

    def get_batch_statement_endorsement_stats(
        self, statement_hashes: List[int]
    ) -> OperationResult:
        """Get endorsement statistics for multiple statements."""
        if not statement_hashes or len(statement_hashes) > 50:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            # Create placeholders for SQL IN clause
            placeholders = ",".join(["%s"] * len(statement_hashes))

            cursor = self.vitess_client.cursor
            cursor.execute(
                f"""
                SELECT
                    statement_hash,
                    COUNT(*) as total_endorsements,
                    SUM(CASE WHEN removed_at IS NULL THEN 1 ELSE 0 END) as active_endorsements,
                    SUM(CASE WHEN removed_at IS NOT NULL THEN 1 ELSE 0 END) as withdrawn_endorsements
                FROM user_statement_endorsements
                WHERE statement_hash IN ({placeholders})
                GROUP BY statement_hash
                """,
                statement_hashes,
            )
            rows = cursor.fetchall()

            # Create a map of statement_hash -> stats
            stats_map = {
                row[0]: {
                    "statement_hash": row[0],
                    "total_endorsements": row[1],
                    "active_endorsements": row[2],
                    "withdrawn_endorsements": row[3],
                }
                for row in rows
            }

            # Include statements with 0 endorsements
            all_stats = []
            for statement_hash in statement_hashes:
                if statement_hash in stats_map:
                    all_stats.append(stats_map[statement_hash])
                else:
                    all_stats.append(
                        {
                            "statement_hash": statement_hash,
                            "total_endorsements": 0,
                            "active_endorsements": 0,
                            "withdrawn_endorsements": 0,
                        }
                    )

            return OperationResult(success=True, data=all_stats)
        except Exception as e:
            logger.error(f"Error getting batch statement endorsement stats: {e}")
            return OperationResult(success=False, error=str(e))
