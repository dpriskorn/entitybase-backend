"""Revision storage operations."""

import logging

from typing import TYPE_CHECKING

from models.common import OperationResult
from models.config.settings import settings
from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.infrastructure.s3.base_storage import BaseS3Storage

if TYPE_CHECKING:
    from models.infrastructure.s3.revision.revision_data import RevisionData
    from models.rest_api.entitybase.v1.response.entity.revision_read_response import RevisionReadResponse

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
