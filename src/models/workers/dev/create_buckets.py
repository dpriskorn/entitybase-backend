"""Development worker for MinIO bucket setup and management."""

import logging
import os
from typing import Any, Dict, List

from botocore.exceptions import ClientError
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Lazy import boto3 to avoid import errors in environments without it
try:
    import boto3

    _boto3 = boto3
except ImportError:
    _boto3 = None


class CreateBuckets(BaseModel):
    """Development worker for MinIO bucket management and setup tasks."""

    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    required_buckets: List[str] = [
        "terms",
        "statements",
        "revisions",
        "dumps",
        "sitelinks",
    ]

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Lazy import boto3 to avoid import errors in environments without it
        try:
            import boto3

            self._boto3 = boto3
        except ImportError:
            raise ImportError(
                "boto3 is required for CreateBuckets. Install with: pip install boto3"
            )

    @property
    def s3_client(self) -> Any:
        """Get S3 client with shared credentials for all buckets."""
        return self._boto3.client(
            "s3",
            endpoint_url=self.minio_endpoint,
            aws_access_key_id=self.minio_access_key,
            aws_secret_access_key=self.minio_secret_key,
        )

    async def ensure_buckets_exist(self) -> Dict[str, str]:
        """Ensure all required buckets exist, creating them if necessary."""
        results = {}

        for bucket in self.required_buckets:
            try:
                # Check if bucket exists
                self.s3_client.head_bucket(Bucket=bucket)
                results[bucket] = "exists"
                logger.info(f"Bucket already exists: {bucket}")
            except ClientError as e:
                # Handle AWS/MinIO client errors
                error_code = e.response["Error"]["Code"]
                if error_code == "404" or error_code == "NoSuchBucket":
                    # Bucket doesn't exist, create it
                    try:
                        self.s3_client.create_bucket(Bucket=bucket)
                        results[bucket] = "created"
                        logger.info(f"Created bucket: {bucket}")
                    except Exception as create_error:
                        results[bucket] = f"create_failed: {create_error}"
                        logger.error(
                            f"Failed to create bucket {bucket}: {create_error}"
                        )
                else:
                    results[bucket] = f"error: {error_code}"
                    logger.error(f"Error checking bucket {bucket}: {error_code}")
            except Exception as e:
                results[bucket] = f"unexpected_error: {e}"
                logger.error(f"Unexpected error with bucket {bucket}: {e}")

        return results

    async def cleanup_buckets(self) -> Dict[str, str]:
        """Clean up development buckets (use with caution)."""
        results = {}

        for bucket in self.required_buckets:
            try:
                # Delete all objects in bucket first
                objects = self.s3_client.list_objects_v2(Bucket=bucket)
                if "Contents" in objects:
                    for obj in objects["Contents"]:
                        self.s3_client.delete_object(Bucket=bucket, Key=obj["Key"])

                # Delete the bucket
                self.s3_client.delete_bucket(Bucket=bucket)
                results[bucket] = "deleted"
                logger.info(f"Deleted bucket: {bucket}")
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "NoSuchBucket":
                    results[bucket] = "not_found"
                    logger.info(f"Bucket does not exist: {bucket}")
                else:
                    results[bucket] = f"delete_failed: {error_code}"
                    logger.error(f"Failed to delete bucket {bucket}: {error_code}")
            except Exception as e:
                results[bucket] = f"unexpected_error: {e}"
                logger.error(f"Unexpected error deleting bucket {bucket}: {e}")

        return results

    async def bucket_health_check(self) -> Dict[str, Any]:
        """Perform health check on all required buckets."""
        health_status: Dict[str, Any] = {
            "overall_status": "healthy",
            "buckets": {},
            "issues": [],
        }

        for bucket in self.required_buckets:
            try:
                self.s3_client.head_bucket(Bucket=bucket)
                health_status["buckets"][bucket] = {
                    "status": "accessible",
                    "accessible": True,
                }
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                health_status["buckets"][bucket] = {
                    "status": "error",
                    "error_code": error_code,
                    "accessible": False,
                }
                health_status["issues"].append(f"Bucket {bucket}: {error_code}")
                health_status["overall_status"] = "unhealthy"

        return health_status

    async def run_setup(self) -> Dict[str, Any]:
        """Run complete setup process for development environment."""
        logger.info("Starting development environment setup")

        # Ensure buckets exist
        bucket_results = await self.ensure_buckets_exist()

        # Perform health check
        health_status = await self.bucket_health_check()

        setup_results = {
            "buckets_created": bucket_results,
            "health_check": health_status,
            "setup_status": "completed"
            if health_status["overall_status"] == "healthy"
            else "failed",
        }

        logger.info(
            f"Development setup completed with status: {setup_results['setup_status']}"
        )
        return setup_results
