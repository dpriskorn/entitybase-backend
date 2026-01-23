"""Repository for metadata content operations."""

import logging

from models.common import OperationResult
from models.infrastructure.vitess.repository import Repository
from models.data.rest_api.v1.response import MetadataContent

logger = logging.getLogger(__name__)


class MetadataRepository(Repository):
    """Repository for metadata content operations."""

    def insert_metadata_content(
        self, content_hash: int, content_type: str
    ) -> OperationResult:
        """Insert or increment ref_count for metadata content."""
        try:
            cursor = self.vitess_client.cursor
            cursor.execute(
                """
                INSERT INTO metadata_content (content_hash, content_type, ref_count)
                VALUES (%s, %s, 1)
                ON DUPLICATE KEY UPDATE ref_count = ref_count + 1
                """,
                (content_hash, content_type),
            )
            return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def get_metadata_content(
        self, content_hash: int, content_type: str
    ) -> OperationResult:
        """Get metadata content by hash and type."""
        if content_hash <= 0 or not content_type:
            return OperationResult(success=False, error="Invalid content hash or type")

        try:
            cursor = self.vitess_client.cursor
            cursor.execute(
                "SELECT ref_count FROM metadata_content WHERE content_hash = %s AND content_type = %s",
                (content_hash, content_type),
            )
            result = cursor.fetchone()
            if result:
                content = MetadataContent(ref_count=result[0])
                return OperationResult(success=True, data=content)
            else:
                return OperationResult(
                    success=False, error="Metadata content not found"
                )
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def decrement_ref_count(
        self, content_hash: int, content_type: str
    ) -> OperationResult:
        """Decrement ref_count and return True if it reaches 0."""
        if content_hash <= 0 or not content_type:
            return OperationResult(success=False, error="Invalid content hash or type")

        logger.debug(
            f"Decrementing ref count for metadata {content_type} hash {content_hash}"
        )
        try:
            cursor = self.vitess_client.cursor
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
                return OperationResult(
                    success=False, error="Metadata content not found"
                )
            ref_count: int = result[0]
            return OperationResult(success=True, data=ref_count <= 0)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def delete_metadata_content(self, content_hash: int, content_type: str) -> None:
        """Delete metadata content when ref_count reaches 0."""
        cursor = self.vitess_client.cursor
        cursor.execute(
                "DELETE FROM metadata_content WHERE content_hash = %s AND content_type = %s AND ref_count <= 0",
                (content_hash, content_type),
        )
