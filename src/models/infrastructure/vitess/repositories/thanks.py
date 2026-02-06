"""Repository for managing thanks in Vitess."""

import logging

from models.data.common import OperationResult
from models.data.infrastructure.vitess.records.thanks import ThankItem
from models.infrastructure.vitess.repository import Repository

logger = logging.getLogger(__name__)


class ThanksRepository(Repository):
    """Repository for managing thanks in Vitess."""

    def send_thank(
        self, from_user_id: int, entity_id: str, revision_id: int
    ) -> OperationResult:
        """Send a thank for a revision."""
        if from_user_id <= 0 or not entity_id or revision_id <= 0:
            return OperationResult(success=False, error="Invalid parameters")

        logger.debug(
            f"Sending thank from user {from_user_id} for {entity_id}:{revision_id}"
        )

        cursor = self.vitess_client.cursor
        error = None
        thank_id = None

        try:
            # Resolve entity_id to internal_id
            internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
            if not internal_id:
                error = "Entity not found"
            else:
                # Get the user_id of the revision author
                cursor.execute(
                    "SELECT user_id FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
                    (internal_id, revision_id),
                )
                row = cursor.fetchone()
                if not row:
                    error = "Revision not found"
                else:
                    to_user_id = row[0]
                    if to_user_id == from_user_id:
                        error = "Cannot thank your own revision"
                    else:
                        # Check for existing thank
                        cursor.execute(
                            "SELECT id FROM user_thanks WHERE from_user_id = %s AND internal_entity_id = %s AND revision_id = %s",
                            (from_user_id, internal_id, revision_id),
                        )
                        if cursor.fetchone():
                            error = "Already thanked this revision"
                        else:
                            # Insert thank
                            cursor.execute(
                                "INSERT INTO user_thanks (from_user_id, to_user_id, internal_entity_id, revision_id) VALUES (%s, %s, %s, %s)",
                                (from_user_id, to_user_id, internal_id, revision_id),
                            )
                            thank_id = cursor.lastrowid
        except Exception as e:
            logger.error(f"Error sending thank: {e}")
            return OperationResult(success=False, error=str(e))

        if error:
            return OperationResult(success=False, error=error)
        return OperationResult(success=True, data=thank_id)

    def get_thanks_received(
        self, user_id: int, hours: int = 24, limit: int = 50, offset: int = 0
    ) -> OperationResult:
        """Get thanks received by user."""
        if user_id <= 0 or hours <= 0 or limit <= 0 or offset < 0:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            cursor = self.vitess_client.cursor
            cursor.execute(
                """
                SELECT t.id, t.from_user_id, t.to_user_id, m.entity_id, t.revision_id, t.created_at
                FROM user_thanks t
                JOIN entity_id_mapping m ON t.internal_entity_id = m.internal_id
                WHERE t.to_user_id = %s AND t.created_at >= NOW() - INTERVAL %s HOUR
                ORDER BY t.created_at DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, hours, limit, offset),
            )
            rows = cursor.fetchall()

            # Get total count
            cursor.execute(
                """
                SELECT COUNT(*) FROM user_thanks
                WHERE to_user_id = %s AND created_at >= NOW() - INTERVAL %s HOUR
                """,
                (user_id, hours),
            )
            total_count = cursor.fetchone()[0]

            thanks = []
            for row in rows:
                thanks.append(
                    ThankItem(
                        id=row[0],
                        from_user_id=row[1],
                        to_user_id=row[2],
                        entity_id=row[3],
                        revision_id=row[4],
                        created_at=row[5],
                    )
                )

            return OperationResult(
                success=True,
                data={
                    "thanks": thanks,
                    "total_count": total_count,
                    "has_more": total_count > offset + len(thanks),
                },
            )
        except Exception as e:
            logger.error(f"Error getting thanks received: {e}")
            return OperationResult(success=False, error=str(e))

    def get_thanks_sent(
        self, user_id: int, hours: int = 24, limit: int = 50, offset: int = 0
    ) -> OperationResult:
        """Get thanks sent by user."""
        if user_id <= 0 or hours <= 0 or limit <= 0 or offset < 0:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            cursor = self.vitess_client.cursor
            cursor.execute(
                """
                SELECT t.id, t.from_user_id, t.to_user_id, m.entity_id, t.revision_id, t.created_at
                FROM user_thanks t
                JOIN entity_id_mapping m ON t.internal_entity_id = m.internal_id
                WHERE t.from_user_id = %s AND t.created_at >= NOW() - INTERVAL %s HOUR
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, hours, limit, offset),
            )
            rows = cursor.fetchall()

            # Get total count
            cursor.execute(
                """
                SELECT COUNT(*) FROM user_thanks
                WHERE from_user_id = %s AND created_at >= NOW() - INTERVAL %s HOUR
                """,
                (user_id, hours),
            )
            total_count = cursor.fetchone()[0]

            thanks = []
            for row in rows:
                thanks.append(
                    ThankItem(
                        id=row[0],
                        from_user_id=row[1],
                        to_user_id=row[2],
                        entity_id=row[3],
                        revision_id=row[4],
                        created_at=row[5],
                    )
                )

            return OperationResult(
                success=True,
                data={
                    "thanks": thanks,
                    "total_count": total_count,
                    "has_more": total_count > offset + len(thanks),
                },
            )
        except Exception as e:
            logger.error(f"Error getting thanks sent: {e}")
            return OperationResult(success=False, error=str(e))

    def get_revision_thanks(self, entity_id: str, revision_id: int) -> OperationResult:
        """Get all thanks for a specific revision."""
        if not entity_id or revision_id <= 0:
            return OperationResult(success=False, error="Invalid parameters")

        try:
            cursor = self.vitess_client.cursor
            # Resolve entity_id to internal_id
            internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
            if not internal_id:
                return OperationResult(success=False, error="Entity not found")

            cursor.execute(
                """
                SELECT t.id, t.from_user_id, t.to_user_id, m.entity_id, t.revision_id, t.created_at
                FROM user_thanks t
                JOIN entity_id_mapping m ON t.internal_entity_id = m.internal_id
                WHERE t.internal_entity_id = %s AND t.revision_id = %s
                ORDER BY t.created_at DESC
                """,
                (internal_id, revision_id),
            )
            rows = cursor.fetchall()

            thanks = []
            for row in rows:
                thanks.append(
                    ThankItem(
                        id=row[0],
                        from_user_id=row[1],
                        to_user_id=row[2],
                        entity_id=row[3],
                        revision_id=row[4],
                        created_at=row[5],
                    )
                )

            return OperationResult(success=True, data=thanks)
        except Exception as e:
            logger.error(f"Error getting revision thanks: {e}")
            return OperationResult(success=False, error=str(e))
