"""Vitess storage for small objects (statements, qualifiers, references, snaks).

This module provides storage classes that replace S3 buckets for small objects.
The average size per statement is ~10KB which is too small for efficient S3 storage.
"""

import json
import logging
from typing import Any, cast

from models.data.common import OperationResult
from models.infrastructure.vitess.repository import Repository

logger = logging.getLogger(__name__)


class BaseVitessStorage(Repository):
    """Base class for Vitess storage operations."""

    table_name: str = ""

    def _store(
        self,
        content_hash: int,
        data: dict[str, Any],
    ) -> OperationResult[None]:
        """Store data in the table, incrementing ref_count if already exists."""
        if content_hash <= 0:
            return OperationResult(success=False, error="Invalid content hash")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"""INSERT INTO {self.table_name} (content_hash, data, ref_count)
                        VALUES (%s, %s, 1)
                        ON DUPLICATE KEY UPDATE
                        ref_count = ref_count + 1,
                        data = VALUES(data)""",
                    (content_hash, json.dumps(data)),
                )
                return OperationResult(success=True, data=None)
        except Exception as e:
            logger.error(f"[VITESS_STORE] Failed to store {self.table_name}: {e}")
            return OperationResult(success=False, error=str(e))

    def _load(self, content_hash: int) -> dict[str, Any] | None:
        """Load data from the table."""
        if content_hash <= 0:
            return None

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"SELECT data FROM {self.table_name} WHERE content_hash = %s",
                    (content_hash,),
                )
                result = cursor.fetchone()
                if result:
                    return cast(dict[str, Any], json.loads(result[0]))
                return None
        except Exception as e:
            logger.error(f"[VITESS_LOAD] Failed to load {self.table_name}: {e}")
            return None

    def _load_batch(
        self, content_hashes: list[int]
    ) -> list[dict[str, Any] | None]:
        """Load multiple records by content hashes."""
        if not content_hashes:
            return []

        valid_hashes = [h for h in content_hashes if h > 0]
        if not valid_hashes:
            return [None] * len(content_hashes)

        try:
            with self.vitess_client.cursor as cursor:
                placeholders = ",".join(["%s"] * len(valid_hashes))
                cursor.execute(
                    f"""SELECT content_hash, data FROM {self.table_name}
                        WHERE content_hash IN ({placeholders})""",
                    valid_hashes,
                )
                rows = cursor.fetchall()
                hash_to_data = {row[0]: json.loads(row[1]) for row in rows}

                result = []
                for h in content_hashes:
                    result.append(hash_to_data.get(h))
                return result
        except Exception as e:
            logger.error(f"[VITESS_LOAD_BATCH] Failed: {e}")
            return [None] * len(content_hashes)

    def _delete(self, content_hash: int) -> OperationResult[None]:
        """Delete or decrement ref_count for content."""
        if content_hash <= 0:
            return OperationResult(success=False, error="Invalid content hash")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"""UPDATE {self.table_name} SET ref_count = ref_count - 1
                        WHERE content_hash = %s AND ref_count > 0""",
                    (content_hash,),
                )
                cursor.execute(
                    f"""DELETE FROM {self.table_name}
                        WHERE content_hash = %s AND ref_count <= 0""",
                    (content_hash,),
                )
                return OperationResult(success=True, data=None)
        except Exception as e:
            logger.error(f"[VITESS_DELETE] Failed: {e}")
            return OperationResult(success=False, error=str(e))

    def _increment_ref_count(self, content_hash: int) -> OperationResult[None]:
        """Increment reference count for existing content."""
        if content_hash <= 0:
            return OperationResult(success=False, error="Invalid content hash")

        import json
        empty_data = json.dumps({})

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"""INSERT INTO {self.table_name} (content_hash, data, ref_count)
                        VALUES (%s, %s, 1)
                        ON DUPLICATE KEY UPDATE ref_count = ref_count + 1""",
                    (content_hash, empty_data),
                )
                return OperationResult(success=True, data=None)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def _decrement_ref_count(self, content_hash: int) -> OperationResult[None]:
        """Decrement reference count, delete if reaches 0."""
        if content_hash <= 0:
            return OperationResult(success=False, error="Invalid content hash")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"""UPDATE {self.table_name} SET ref_count = ref_count - 1
                        WHERE content_hash = %s AND ref_count > 0""",
                    (content_hash,),
                )
                cursor.execute(
                    f"""DELETE FROM {self.table_name}
                        WHERE content_hash = %s AND ref_count <= 0""",
                    (content_hash,),
                )
                return OperationResult(success=True, data=None)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def _get_ref_count(self, content_hash: int) -> int:
        """Get reference count for content."""
        if content_hash <= 0:
            return 0

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"SELECT ref_count FROM {self.table_name} WHERE content_hash = %s",
                    (content_hash,),
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0

    def _exists(self, content_hash: int) -> bool:
        """Check if content exists in the table."""
        if content_hash <= 0:
            return False

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"SELECT 1 FROM {self.table_name} WHERE content_hash = %s LIMIT 1",
                    (content_hash,),
                )
                return cursor.fetchone() is not None
        except Exception:
            return False
