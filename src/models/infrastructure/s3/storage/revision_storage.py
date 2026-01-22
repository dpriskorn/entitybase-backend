"""Revision storage operations."""

import logging

from models.common import OperationResult
from models.config.settings import settings
from models.infrastructure.s3.base_storage import BaseS3Storage
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.revision.s3_revision_data import S3RevisionData

logger = logging.getLogger(__name__)


class RevisionStorage(BaseS3Storage):
    """Storage operations for revisions."""

    bucket: str = settings.s3_revisions_bucket

    def store_revision(
        self, content_hash: int, revision_data: S3RevisionData
    ) -> OperationResult[None]:
        """Store a revision by its content hash."""
        key = str(content_hash)
        metadata = {"content_hash": str(content_hash)}
        return self.store(key, revision_data, metadata=metadata)

    def load_revision(self, content_hash: int) -> S3RevisionData:
        """Load a revision by its content hash."""
        key = str(content_hash)
        data = self.load(key).data
        assert isinstance(data, S3RevisionData)
        return data
