"""Reference storage operations."""

import logging
from typing import List

from models.common import OperationResult
from models.config.settings import settings
from models.infrastructure.s3.base_storage import BaseS3Storage
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.revision.s3_reference_data import S3ReferenceData

logger = logging.getLogger(__name__)


class ReferenceStorage(BaseS3Storage):
    """Storage operations for references."""
    bucket: str = settings.s3_references_bucket

    def store_reference(
        self, content_hash: int, reference_data: S3ReferenceData
    ) -> OperationResult[None]:
        """Store a reference by its content hash."""
        key = str(content_hash)
        metadata = {"content_hash": str(content_hash)}
        return self.store(key, reference_data, metadata=metadata)

    def load_reference(self, content_hash: int) -> S3ReferenceData:
        """Load a reference by its content hash."""
        key = str(content_hash)
        data = self.load(key).data
        assert isinstance(data, S3ReferenceData)
        return data

    def load_references_batch(
        self, content_hashes: List[int]
    ) -> List[S3ReferenceData | None]:
        """Load multiple references by their content hashes."""
        results: List[S3ReferenceData | None] = []
        for h in content_hashes:
            try:
                ref = self.load_reference(h)
                results.append(ref)
            except S3NotFoundError:
                results.append(None)
        return results
