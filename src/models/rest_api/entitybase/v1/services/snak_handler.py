"""Service for storing and retrieving snaks with deduplication."""

import json
import logging
from typing import Any, Dict

from models.config.settings import settings
from models.infrastructure.s3.client import MyS3Client
from models.internal_representation.metadata_extractor import hash_string
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class SnakHandler:
    """Handles snak storage and retrieval with rapidhash deduplication."""

    def __init__(self, s3_client: MyS3Client | None = None):
        """Initialize with S3 client."""
        self.s3_client = s3_client or MyS3Client()
        self.bucket = settings.s3_snaks_bucket

    def store_snak(self, snak: Dict[str, Any]) -> str:
        """Store snak in S3 with rapidhash key, return hash."""
        # Serialize snak to JSON for hashing and storage
        snak_json = json.dumps(snak, sort_keys=True)
        snak_hash = hash_string(snak_json)

        try:
            self.s3_client.put_object(
                bucket=self.bucket,
                key=snak_hash,
                body=snak_json,
                content_type="application/json"
            )
            logger.debug(f"Stored snak with hash {snak_hash}")
        except Exception as e:
            logger.error(f"Failed to store snak {snak_hash}: {e}")
            raise_validation_error(f"Failed to store snak: {e}")

        return snak_hash

    def get_snak(self, snak_hash: str) -> Dict[str, Any] | None:
        """Retrieve snak from S3 by hash."""
        try:
            response = self.s3_client.get_object(bucket=self.bucket, key=snak_hash)
            if response:
                return json.loads(response)
        except Exception as e:
            logger.warning(f"Failed to retrieve snak {snak_hash}: {e}")

        return None