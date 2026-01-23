"""Service for storing and retrieving snaks with deduplication."""

import logging
from datetime import datetime
from typing import Any, Dict

from models.data.infrastructure.s3.snak_data import S3SnakData
from models.infrastructure.s3.client import MyS3Client
from models.internal_representation.metadata_extractor import MetadataExtractor
from models.rest_api.entitybase.v1.request.snak import SnakRequest
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class SnakHandler:
    """Handles snak storage and retrieval with rapidhash deduplication."""

    def __init__(self, s3_client: MyS3Client):
        """Initialize with S3 client."""
        self.s3_client = s3_client

    def store_snak(self, snak: SnakRequest) -> int:
        """Store snak in S3 with rapidhash key, return hash."""
        # Compute rapidhash for the snak
        snak_json = snak.model_dump_json()
        content_hash = MetadataExtractor.hash_string(snak_json)

        # Create S3SnakData object
        snak_data = S3SnakData(
            schema="1.0.0",
            snak=snak.model_dump(),
            hash=content_hash,
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        )

        # Store using S3 client
        try:
            self.s3_client.store_snak(content_hash, snak_data)
            logger.debug(f"Stored snak with hash {content_hash}")
        except Exception as e:
            logger.error(f"Failed to store snak {content_hash}: {e}")
            raise_validation_error(f"Failed to store snak: {e}")

        return content_hash

    def get_snak(self, snak_hash: int) -> Dict[str, Any] | None:
        """Retrieve snak from S3 by hash."""
        try:
            snak_data = self.s3_client.load_snak(snak_hash)
            return snak_data.snak if snak_data else None
        except Exception as e:
            logger.warning(f"Failed to retrieve snak {snak_hash}: {e}")
            return None