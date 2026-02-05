"""Qualifier storage operations."""

import logging
from typing import List, cast

from models.data.common import OperationResult
from models.config.settings import settings
from models.data.infrastructure.s3.qualifier_data import S3QualifierData
from models.infrastructure.s3.base_storage import BaseS3Storage
from models.infrastructure.s3.exceptions import S3NotFoundError

logger = logging.getLogger(__name__)


class QualifierStorage(BaseS3Storage):
    """Storage operations for qualifiers."""

    bucket: str = settings.s3_qualifiers_bucket

    def store_qualifier(
        self, content_hash: int, qualifier_data: S3QualifierData
    ) -> OperationResult[None]:
        """Store a qualifier by its content hash."""
        key = str(content_hash)
        metadata = {"content_hash": str(content_hash)}
        return self.store(key, qualifier_data, metadata=metadata)

    def load_qualifier(self, content_hash: int) -> S3QualifierData:
        """Load a qualifier by its content hash."""
        key = str(content_hash)
        load_response = self.load(key)
        if load_response is None:
            raise S3NotFoundError(f"Qualifier not found: {key}")
        data = load_response.data
        return cast(S3QualifierData, S3QualifierData.model_validate(data))

    def load_qualifiers_batch(
        self, content_hashes: List[int]
    ) -> List[S3QualifierData | None]:
        """Load multiple qualifiers by their content hashes."""
        results: List[S3QualifierData | None] = []
        for h in content_hashes:
            try:
                qual = self.load_qualifier(h)
                results.append(qual)
            except S3NotFoundError:
                results.append(None)
        return results
