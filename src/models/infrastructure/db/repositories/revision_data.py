"""Repository for entity revision data storage in MariaDB."""

import json
import logging
from typing import Any

from models.infrastructure.db.repository import Repository

logger = logging.getLogger(__name__)


class RevisionDataRepository(Repository):
    """Repository for storing and loading full revision JSON snapshots."""

    def store(self, content_hash: int, data: dict[str, Any]) -> None:
        """Store revision data by content hash."""
        with self.db_client.cursor as cursor:
            cursor.execute(
                "INSERT INTO entity_revision_data (content_hash, data) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE data = VALUES(data)",
                (content_hash, json.dumps(data, default=str)),
            )

    def load(self, content_hash: int) -> dict[str, Any] | None:
        """Load revision data by content hash."""
        with self.db_client.cursor as cursor:
            cursor.execute(
                "SELECT data FROM entity_revision_data WHERE content_hash = %s",
                (content_hash,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            data = row[0]
            if isinstance(data, str):
                return json.loads(data)
            return data

    def exists(self, content_hash: int) -> bool:
        """Check if revision data exists for a given content hash."""
        with self.db_client.cursor as cursor:
            cursor.execute(
                "SELECT 1 FROM entity_revision_data WHERE content_hash = %s",
                (content_hash,),
            )
            return cursor.fetchone() is not None
