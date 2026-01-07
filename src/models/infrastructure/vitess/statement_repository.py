from typing import Any


class StatementRepository:
    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def insert_content(self, content_hash: int) -> bool:
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM statement_content WHERE content_hash = %s",
            (content_hash,),
        )
        if cursor.fetchone() is not None:
            cursor.close()
            return False

        cursor.execute(
            "INSERT INTO statement_content (content_hash) VALUES (%s)",
            (content_hash,),
        )
        cursor.close()
        return True

    def increment_ref_count(self, content_hash: int) -> int:
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE statement_content SET ref_count = ref_count + 1 WHERE content_hash = %s",
            (content_hash,),
        )
        cursor.execute(
            "SELECT ref_count FROM statement_content WHERE content_hash = %s",
            (content_hash,),
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else 0

    def decrement_ref_count(self, content_hash: int) -> int:
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE statement_content SET ref_count = ref_count - 1 WHERE content_hash = %s",
            (content_hash,),
        )
        cursor.execute(
            "SELECT ref_count FROM statement_content WHERE content_hash = %s",
            (content_hash,),
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else 0

    def get_orphaned(self, older_than_days: int, limit: int) -> list[int]:
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT content_hash
                    FROM statement_content
                    WHERE ref_count = 0
                    AND created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                    LIMIT %s""",
            (older_than_days, limit),
        )
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result

    def get_most_used(self, limit: int, min_ref_count: int = 1) -> list[int]:
        conn = self.connection_manager.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT content_hash
                    FROM statement_content
                    WHERE ref_count >= %s
                    ORDER BY ref_count DESC
                    LIMIT %s""",
            (min_ref_count, limit),
        )
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result
