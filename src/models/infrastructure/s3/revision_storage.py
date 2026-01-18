"""Revision storage operations."""

import logging
from datetime import timezone, datetime

from models.common import OperationResult
from models.config.settings import settings
from models.infrastructure.s3.base_storage import BaseS3Storage
from models.types import RevisionReadResponse, RevisionData

logger = logging.getLogger(__name__)


class RevisionStorage(BaseS3Storage):
    """Storage operations for entity revisions."""

    def __init__(self, connection_manager):
        super().__init__(connection_manager, settings.s3_revisions_bucket)

    def store_revision(
        self,
        entity_id: str,
        revision_id: int,
        data: RevisionData,
    ) -> OperationResult[None]:
        """Write entity revision data to S3."""
        key = f"{entity_id}/{revision_id}"
        metadata = {
            "schema_version": data.schema_version,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return self.store(key, data, metadata=metadata)

    def load_revision(self, entity_id: str, revision_id: int) -> RevisionReadResponse:
        """Read S3 object and return parsed revision."""
        key = f"{entity_id}/{revision_id}"
        response = self.connection_manager.boto_client.get_object(
            Bucket=self.bucket, Key=key
        )

        parsed_data = self.load(key)
        revision_data = RevisionData(**parsed_data)

        return RevisionReadResponse(
            entity_id=entity_id,
            revision_id=revision_id,
            data=revision_data,
            content=parsed_data.get("entity", {}),
            schema_version=parsed_data.get("schema_version", ""),
            created_at=response["Metadata"].get("created_at", ""),
        )

    def mark_published(
        self, entity_id: str, revision_id: int, publication_state: str
    ) -> None:
        """Update the publication state of an entity revision."""
        key = f"{entity_id}/{revision_id}"
        # Copy object with new metadata
        self.connection_manager.boto_client.copy_object(
            Bucket=self.bucket,
            CopySource={"Bucket": self.bucket, "Key": key},
            Key=key,
            Metadata={"publication_state": publication_state},
            MetadataDirective="REPLACE",
        )