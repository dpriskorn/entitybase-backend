from typing import Any


class StatementRepository:
    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def insert_content(self, conn: Any, content_hash: int) -> bool:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM statement_content WHERE content_hash = %s",
                (content_hash,),
            )
            if cursor.fetchone() is not None:
                return False

            cursor.execute(
                "INSERT INTO statement_content (content_hash) VALUES (%s)",
                (content_hash,),
            )
            return True

    def increment_ref_count(self, conn: Any, content_hash: int) -> int:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE statement_content SET ref_count = ref_count + 1 WHERE content_hash = %s",
                (content_hash,),
            )
            cursor.execute(
                "SELECT ref_count FROM statement_content WHERE content_hash = %s",
                (content_hash,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def decrement_ref_count(self, conn: Any, content_hash: int) -> int:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE statement_content SET ref_count = ref_count - 1 WHERE content_hash = %s",
                (content_hash,),
            )
            cursor.execute(
                "SELECT ref_count FROM statement_content WHERE content_hash = %s",
                (content_hash,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_orphaned(self, conn: Any, older_than_days: int, limit: int) -> list[int]:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT content_hash
                        FROM statement_content
                        WHERE ref_count = 0
                        AND created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                        LIMIT %s""",
                (older_than_days, limit),
            )
            result = [row[0] for row in cursor.fetchall()]
            return result

    def get_most_used(self, conn: Any, limit: int, min_ref_count: int = 1) -> list[int]:
        with conn.cursor() as cursor:
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

    def get_ref_count(self, conn: Any, content_hash: int) -> int:
        """Get the reference count for a statement."""
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT ref_count FROM statement_content WHERE content_hash = %s",
                (content_hash,),
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def delete_content(self, conn: Any, content_hash: int) -> None:
        """Delete statement content when ref_count reaches 0."""
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM statement_content WHERE content_hash = %s AND ref_count <= 0",
                (content_hash,),
            )
