"""Repository for metadata content operations."""

"""Repository for metadata content operations."""

import logging
from typing import Any

from models.rest_api.response.misc import MetadataContent

logger = logging.getLogger(__name__)


class MetadataRepository:
    """Repository for metadata content operations."""

    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def insert_metadata_content(
        self, conn: Any, content_hash: int, content_type: str
    ) -> None:
        """Insert or increment ref_count for metadata content."""
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO metadata_content (content_hash, content_type, ref_count)
                VALUES (%s, %s, 1)
                ON DUPLICATE KEY UPDATE ref_count = ref_count + 1
                """,
                (content_hash, content_type),
            )

    def get_metadata_content(
        self, conn: Any, content_hash: int, content_type: str
    ) -> MetadataContent | None:
        """Get metadata content by hash and type."""
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT ref_count FROM metadata_content WHERE content_hash = %s AND content_type = %s",
                (content_hash, content_type),
            )
            result = cursor.fetchone()
            return MetadataContent(ref_count=result[0]) if result else None

    def decrement_ref_count(
        self, conn: Any, content_hash: int, content_type: str
    ) -> bool:
        """Decrement ref_count and return True if it reaches 0."""
        logger.debug(f"Decrementing ref count for metadata {content_type} hash {content_hash}")
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE metadata_content
                SET ref_count = ref_count - 1
                WHERE content_hash = %s AND content_type = %s
                """,
                (content_hash, content_type),
            )
            cursor.execute(
                "SELECT ref_count FROM metadata_content WHERE content_hash = %s AND content_type = %s",
                (content_hash, content_type),
            )
            result = cursor.fetchone()
            if result is None:
                return False
            ref_count: int = result[0]
            return ref_count <= 0

    def delete_metadata_content(
        self, conn: Any, content_hash: int, content_type: str
    ) -> None:
        """Delete metadata content when ref_count reaches 0."""
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM metadata_content WHERE content_hash = %s AND content_type = %s AND ref_count <= 0",
                (content_hash, content_type),
            )
