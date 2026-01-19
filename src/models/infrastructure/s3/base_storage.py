"""Base S3 storage classes for modular client design."""

import json
import logging
from abc import ABC
from typing import Any, Dict, Optional

from botocore.exceptions import ClientError

from models.common import OperationResult
from models.infrastructure.s3.connection import S3ConnectionManager
from models.infrastructure.s3.exceptions import (
    S3StorageError,
    S3NotFoundError,
    S3ConnectionError,
)

logger = logging.getLogger(__name__)


class BaseS3Storage(ABC):
    """Base class for S3 storage operations with common patterns."""

    def __init__(self, connection_manager: S3ConnectionManager, bucket: str):
        self.connection_manager = connection_manager
        self.bucket = bucket
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _ensure_connection(self) -> None:
        """Ensure S3 connection is available."""
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise S3ConnectionError("S3 service unavailable")

    def _handle_client_error(self, e: ClientError, operation: str, key: str) -> None:
        """Handle boto3 ClientError with appropriate logging and exceptions."""
        error_code = e.response["Error"].get("Code", "Unknown")
        error_message = e.response["Error"].get("Message", str(e))

        if error_code in ["NoSuchKey", "404"]:
            self.logger.warning(
                f"S3 {operation} not found: bucket={self.bucket}, key={key}"
            )
            raise S3NotFoundError(f"Object not found: {key}")
        else:
            self.logger.error(
                f"S3 {operation} failed: bucket={self.bucket}, key={key}, "
                f"error_code={error_code}, error_message={error_message}",
                exc_info=True,
            )
            raise S3StorageError(f"{operation} failed: {error_message}")

    def store(
        self,
        key: str,
        data: Any,
        content_type: str = "application/json",
        metadata: Optional[Dict[str, str]] = None,
    ) -> OperationResult[None]:
        """Store data in S3 with common error handling."""
        self.logger.debug(f"Storing data to S3: bucket={self.bucket}, key={key}")
        self._ensure_connection()

        try:
            if isinstance(data, str):
                body = data.encode("utf-8")
                content_type = "text/plain"
            elif hasattr(data, "model_dump"):
                body = json.dumps(data.model_dump(mode="json")).encode("utf-8")
            else:
                body = (
                    json.dumps(data, default=str).encode("utf-8")
                    if isinstance(data, dict)
                    else str(data).encode("utf-8")
                )

            self.connection_manager.boto_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body,
                ContentType=content_type,
                Metadata=metadata or {},
            )

            self.logger.debug(f"S3 store successful: bucket={self.bucket}, key={key}")
            return OperationResult(success=True)

        except ClientError as e:
            self._handle_client_error(e, "store", key)
            return OperationResult(success=False, error=str(e))  # Won't reach here
        except Exception as e:
            self.logger.error(
                f"S3 store failed: bucket={self.bucket}, key={key}, error={e}",
                exc_info=True,
            )
            raise S3StorageError(f"Store failed: {e}")

    def load(self, key: str) -> object:
        """Load data from S3 with common error handling."""
        self._ensure_connection()

        try:
            response = self.connection_manager.boto_client.get_object(
                Bucket=self.bucket, Key=key
            )
            content_type = response.get("ContentType", "application/json")

            if content_type == "text/plain":
                data = response["Body"].read().decode("utf-8")
            else:
                data = json.loads(response["Body"].read().decode("utf-8"))

            self.logger.debug(f"S3 load successful: bucket={self.bucket}, key={key}")
            return data

        except ClientError as e:
            self._handle_client_error(e, "load", key)
        except Exception as e:
            self.logger.error(
                f"S3 load failed: bucket={self.bucket}, key={key}, error={e}",
                exc_info=True,
            )
            raise S3StorageError(f"Load failed: {e}")

    def delete(self, key: str) -> OperationResult[None]:
        """Delete data from S3."""
        self._ensure_connection()

        try:
            self.connection_manager.boto_client.delete_object(
                Bucket=self.bucket, Key=key
            )
            self.logger.debug(f"S3 delete successful: bucket={self.bucket}, key={key}")
            return OperationResult(success=True)

        except ClientError as e:
            self._handle_client_error(e, "delete", key)
            return OperationResult(success=False, error=str(e))  # Won't reach here
        except Exception as e:
            self.logger.error(
                f"S3 delete failed: bucket={self.bucket}, key={key}, error={e}",
                exc_info=True,
            )
            raise S3StorageError(f"Delete failed: {e}")

    def exists(self, key: str) -> bool:
        """Check if key exists in S3."""
        self._ensure_connection()

        try:
            self.connection_manager.boto_client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"].get("Code") in ["NoSuchKey", "404"]:
                return False
            raise S3StorageError(f"Exists check failed: {e}")
        except Exception as e:
            raise S3StorageError(f"Exists check failed: {e}")
