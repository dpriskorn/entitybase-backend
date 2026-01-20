"""Metadata storage operations for terms and sitelinks."""

import logging
from typing import Any, TYPE_CHECKING, Union

from models.common import OperationResult
from models.config.settings import settings
from models.infrastructure.s3.base_storage import BaseS3Storage
from models.infrastructure.s3.connection import S3ConnectionManager
from models.infrastructure.s3.enums import MetadataType
from models.rest_api.utils import raise_validation_error

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class MetadataStorage(BaseS3Storage):
    """Storage operations for metadata (terms and sitelinks)."""

    def __init__(self, connection_manager: S3ConnectionManager) -> None:
        # Use a default bucket, but methods will override
        super().__init__(connection_manager, settings.s3_terms_bucket)

    def _get_bucket_for_type(self, metadata_type: MetadataType) -> str:
        """Get the appropriate bucket for metadata type."""
        if metadata_type in (
            MetadataType.LABELS,
            MetadataType.DESCRIPTIONS,
            MetadataType.ALIASES,
        ):
            return settings.s3_terms_bucket
        elif metadata_type == MetadataType.SITELINKS:
            return settings.s3_sitelinks_bucket
        else:
            raise_validation_error(
                f"Unknown metadata type: {metadata_type}", status_code=400
            )

    def store_metadata(
        self, metadata_type: MetadataType, content_hash: int, value: str
    ) -> OperationResult[None]:
        """Store metadata value (term or sitelink title)."""
        bucket = self._get_bucket_for_type(metadata_type)
        # Temporarily change bucket for this operation
        original_bucket = self.bucket
        self.bucket = bucket

        try:
            key = str(content_hash)
            # Terms are stored as plain text, sitelinks too
            result = self.store(key, value, content_type="text/plain")
            return result
        finally:
            self.bucket = original_bucket

    def load_metadata(
        self, metadata_type: MetadataType, content_hash: int
    ) -> Union[str, dict[str, Any]]:
        """Load metadata value."""
        bucket = self._get_bucket_for_type(metadata_type)
        original_bucket = self.bucket
        self.bucket = bucket

        try:
            key = str(content_hash)
            return self.load(key).data
        finally:
            self.bucket = original_bucket

    def delete_metadata(
        self, metadata_type: MetadataType, content_hash: int
    ) -> OperationResult[None]:
        """Delete metadata."""
        bucket = self._get_bucket_for_type(metadata_type)
        original_bucket = self.bucket
        self.bucket = bucket

        try:
            key = str(content_hash)
            return self.delete(key)
        finally:
            self.bucket = original_bucket
