"""Base S3 storage classes for modular client design."""

import json
import logging
from abc import ABC
from typing import Any, Dict, Optional

from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

from models.data.common import OperationResult
from models.data.infrastructure.s3 import (
    DictLoadResponse,
    LoadResponse,
    StringLoadResponse,
)
from models.infrastructure.s3.exceptions import (
    S3StorageError,
    S3NotFoundError,
    S3ConnectionError,
)

logger = logging.getLogger(__name__)


class BaseS3Storage(ABC, BaseModel):
    """Base class for S3 storage operations with common patterns."""

    model_config = {"arbitrary_types_allowed": True}

    connection_manager: Any = Field(default=None)
    bucket: str

    def _ensure_connection(self) -> None:
        """Ensure S3 connection is available."""
        if (
            not self.connection_manager
            or not hasattr(self.connection_manager, "boto_client")
            or not self.connection_manager.boto_client
        ):
            raise S3ConnectionError("S3 service unavailable")

    def _handle_client_error(
        self, e: ClientError, operation: str, key: str, bucket: str | None = None
    ) -> None:
        """Handle boto3 ClientError with appropriate logging and exceptions."""
        bucket_to_use = bucket if bucket is not None else self.bucket
        error_code = e.response["Error"].get("Code", "Unknown")
        error_message = e.response["Error"].get("Message", str(e))

        if error_code in ["NoSuchKey", "404"]:
            logger.warning(
                f"S3 {operation} not found: bucket={bucket_to_use}, key={key}"
            )
            raise S3NotFoundError(f"Object not found: {key}")
        else:
            logger.error(
                f"S3 {operation} failed: bucket={bucket_to_use}, key={key}, "
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
        bucket: Optional[str] = None,
    ) -> OperationResult[None]:
        """Store data in S3 with common error handling."""
        bucket_to_use = bucket if bucket is not None else self.bucket
        logger.debug(f"Storing data to S3: bucket={bucket_to_use}, key={key}")
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

            assert self.connection_manager is not None  # For type checker
            self.connection_manager.boto_client.put_object(
                Bucket=bucket_to_use,
                Key=key,
                Body=body,
                ContentType=content_type,
                Metadata=metadata or {},
            )

            logger.debug(f"S3 store successful: bucket={bucket_to_use}, key={key}")
            return OperationResult(success=True)

        except ClientError as e:
            self._handle_client_error(e, "store", key, bucket_to_use)
            return OperationResult(success=False, error=str(e))  # Won't reach here
        except Exception as e:
            logger.error(
                f"S3 store failed: bucket={bucket_to_use}, key={key}, error={e}",
                exc_info=True,
            )
            raise S3StorageError(f"Store failed: {e}")

    def load(self, key: str, bucket: Optional[str] = None) -> LoadResponse | None:
        """Load data from S3 with common error handling."""
        bucket_to_use = bucket if bucket is not None else self.bucket
        self._ensure_connection()

        try:
            assert self.connection_manager is not None  # For type checker
            response = self.connection_manager.boto_client.get_object(
                Bucket=bucket_to_use, Key=key
            )
            content_type = response.get("ContentType", "application/json")

            if content_type == "text/plain":
                data = response["Body"].read().decode("utf-8")
                logger.debug(f"S3 load successful: bucket={bucket_to_use}, key={key}")
                return StringLoadResponse(data=data)
            else:
                data = json.loads(response["Body"].read().decode("utf-8"))
                logger.debug(f"S3 load successful: bucket={bucket_to_use}, key={key}")
                return DictLoadResponse(data=data)

        except ClientError as e:
            self._handle_client_error(e, "load", key, bucket_to_use)
            return None
        except Exception as e:
            logger.error(
                f"S3 load failed: bucket={bucket_to_use}, key={key}, error={e}",
                exc_info=True,
            )
            raise S3StorageError(f"Load failed: {e}")

    def delete(self, key: str, bucket: Optional[str] = None) -> OperationResult[None]:
        """Delete data from S3."""
        bucket_to_use = bucket if bucket is not None else self.bucket
        self._ensure_connection()

        try:
            assert self.connection_manager is not None  # For type checker
            self.connection_manager.boto_client.delete_object(
                Bucket=bucket_to_use, Key=key
            )
            logger.debug(f"S3 delete successful: bucket={bucket_to_use}, key={key}")
            return OperationResult(success=True)

        except ClientError as e:
            self._handle_client_error(e, "delete", key, bucket_to_use)
            return OperationResult(success=False, error=str(e))  # Won't reach here
        except Exception as e:
            logger.error(
                f"S3 delete failed: bucket={bucket_to_use}, key={key}, error={e}",
                exc_info=True,
            )
            raise S3StorageError(f"Delete failed: {e}")

    def exists(self, key: str, bucket: Optional[str] = None) -> bool:
        """Check if key exists in S3."""
        bucket_to_use = bucket if bucket is not None else self.bucket
        self._ensure_connection()

        try:
            assert self.connection_manager is not None  # For type checker
            self.connection_manager.boto_client.head_object(
                Bucket=bucket_to_use, Key=key
            )
            return True
        except ClientError as e:
            if e.response["Error"].get("Code") in ["NoSuchKey", "404"]:
                return False
            raise S3StorageError(f"Exists check failed: {e}")
        except Exception as e:
            raise S3StorageError(f"Exists check failed: {e}")
