"""Qualifier storage operations."""

import logging
from typing import List

from models.common import OperationResult
from models.config.settings import settings
from models.infrastructure.s3.base_storage import BaseS3Storage, S3NotFoundError
from models.infrastructure.s3.data import S3QualifierData

logger = logging.getLogger(__name__)


class QualifierStorage(BaseS3Storage):
    """Storage operations for qualifiers."""

    def __init__(self, connection_manager):
        super().__init__(connection_manager, settings.s3_qualifiers_bucket)

    def store_qualifier(self, content_hash: int, qualifier_data: S3QualifierData) -> OperationResult[None]:
        """Store a qualifier by its content hash."""
        key = str(content_hash)
        metadata = {"content_hash": str(content_hash)}
        return self.store(key, qualifier_data, metadata=metadata)

    def load_qualifier(self, content_hash: int) -> S3QualifierData:
        """Load a qualifier by its content hash."""
        key = str(content_hash)
        data = self.load(key)
        return S3QualifierData(**data)

    def load_qualifiers_batch(self, content_hashes: List[int]) -> List[S3QualifierData | None]:
        """Load multiple qualifiers by their content hashes."""
        results = []
        for h in content_hashes:
            try:
                qual = self.load_qualifier(h)
                results.append(qual)
            except S3NotFoundError:
                results.append(None)
        return results