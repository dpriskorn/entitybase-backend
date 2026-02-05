"""Revision storage operations."""

import logging
from typing import TYPE_CHECKING, cast

from models.data.common import OperationResult
from models.config.settings import settings
from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.infrastructure.s3.base_storage import BaseS3Storage

if TYPE_CHECKING:
    pass

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
        load_response = self.load(key)
        if load_response is None:
            from models.infrastructure.s3.exceptions import S3NotFoundError
            raise S3NotFoundError(f"Revision not found: {key}")
        data = load_response.data
        return cast(S3RevisionData, S3RevisionData.model_validate(data))
