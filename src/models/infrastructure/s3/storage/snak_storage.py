"""Snak storage operations."""

import logging
from typing import List

from models.common import OperationResult
from models.config.settings import settings
from models.infrastructure.s3.base_storage import BaseS3Storage
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.revision.s3_snak_data import S3SnakData

logger = logging.getLogger(__name__)


class SnakStorage(BaseS3Storage):
    """Storage operations for snaks."""

    bucket: str = settings.s3_snaks_bucket

    def store_snak(
        self, content_hash: int, snak_data: S3SnakData
    ) -> OperationResult[None]:
        """Store a snak by its content hash."""
        key = str(content_hash)
        metadata = {"content_hash": str(content_hash)}
        return self.store(key, snak_data, metadata=metadata)

    def load_snak(self, content_hash: int) -> S3SnakData:
        """Load a snak by its content hash."""
        key = str(content_hash)
        data = self.load(key).data
        assert isinstance(data, S3SnakData)
        return data

    def load_snaks_batch(
        self, content_hashes: List[int]
    ) -> List[S3SnakData | None]:
        """Load multiple snaks by their content hashes."""
        results: List[S3SnakData | None] = []
        for h in content_hashes:
            try:
                snak = self.load_snak(h)
                results.append(snak)
            except S3NotFoundError:
                results.append(None)
        return results