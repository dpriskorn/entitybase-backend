"""Create worker for S3 bucket setup and management."""

import logging
import os
import sys
from typing import Any, Dict, List, TypedDict

from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel, Field


class BucketHealthCheckResult(TypedDict):
    """Result of bucket health check."""

    overall_status: str
    buckets: Dict[str, Any]
    issues: List[str]


class BucketSetupResult(TypedDict):
    """Result of bucket setup operation."""

    buckets_created: Dict[str, str]
    health_check: BucketHealthCheckResult
    setup_status: str


logger = logging.getLogger(__name__)

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, src_path)


class CreateBuckets(BaseModel):
    """Create worker for S3 bucket management and setup tasks."""

    model_config = {"frozen": False}

    rustfs_endpoint: str = os.getenv("RUSTFS_ENDPOINT", "http://localhost:9000")
    rustfs_access_key: str = os.getenv("RUSTFS_ACCESS_KEY", "minioadmin")
    rustfs_secret_key: str = os.getenv("RUSTFS_SECRET_KEY", "minioadmin")
    required_buckets: List[str] = []
    s3_client: Any = Field(default=None, exclude=True)

    def model_post_init(self, context: Any) -> None:
        # noinspection PyPep8
        from models.config.settings import settings

        logger.info(
            f"CreateBuckets init: endpoint={self.rustfs_endpoint}, "
            f"access_key={self.rustfs_access_key[:4]}..., "
            f"env_RUSTFS_ENDPOINT={os.getenv('RUSTFS_ENDPOINT')}"
        )
        self.required_buckets: List[str] = [
            settings.s3_revisions_bucket,
            settings.s3_dump_bucket,
        ]

    def _create_s3_client(self) -> Any:
        """Create S3 client with shared credentials for all buckets."""
        logger.info(
            f"Creating S3 client with endpoint={self.rustfs_endpoint}, "
            f"access_key={self.rustfs_access_key[:4]}..."
        )
        endpoint = self.rustfs_endpoint
        if endpoint.startswith("http://"):
            endpoint = endpoint[7:]
        elif endpoint.startswith("https://"):
            endpoint = endpoint[8:]
        if "/" in endpoint:
            endpoint = endpoint.split("/")[0]
        self.s3_client = Minio(
            endpoint,
            access_key=self.rustfs_access_key,
            secret_key=self.rustfs_secret_key,
            secure=False,
        )
        logger.debug("S3 client created, verifying connection...")
        return self.s3_client

    def get_s3_client(self) -> Any:
        """Get S3 client, creating it if necessary."""
        if self.s3_client is None:
            self.s3_client = self._create_s3_client()
        return self.s3_client

    async def ensure_buckets_exist(self) -> Dict[str, str]:
        """Ensure all required buckets exist, creating them if necessary."""
        results = {}

        for bucket in self.required_buckets:
            try:
                if self.get_s3_client().bucket_exists(bucket):
                    results[bucket] = "exists"
                    logger.info(f"Bucket already exists: {bucket}")
                else:
                    try:
                        self.get_s3_client().make_bucket(bucket)
                        results[bucket] = "created"
                        logger.info(f"Created bucket: {bucket}")
                    except S3Error as create_error:
                        results[bucket] = f"create_failed: {create_error}"
                        logger.error(
                            f"Failed to create bucket {bucket}: {create_error}"
                        )
            except S3Error as e:
                results[bucket] = f"error: {e.code}"
                logger.error(
                    f"Error checking bucket {bucket}: {e.code} - "
                    f"response: {e}"
                )
            except Exception as e:
                results[bucket] = f"unexpected_error: {e}"
                logger.error(f"Unexpected error with bucket {bucket}: {e}")

        return results

    async def cleanup_buckets(self) -> Dict[str, str]:
        """Clean up development buckets (use with caution)."""
        results = {}

        for bucket in self.required_buckets:
            try:
                client = self.get_s3_client()
                try:
                    objects = client.list_objects(bucket)
                    for obj in objects:
                        client.remove_object(bucket, obj.object_name)
                except S3Error:
                    pass
                try:
                    client.remove_bucket(bucket)
                    results[bucket] = "deleted"
                    logger.info(f"Deleted bucket: {bucket}")
                except S3Error as e:
                    if e.code == "NoSuchBucket":
                        results[bucket] = "not_found"
                        logger.info(f"Bucket does not exist: {bucket}")
                    else:
                        results[bucket] = f"delete_failed: {e.code}"
                        logger.error(f"Failed to delete bucket {bucket}: {e.code}")
            except Exception as e:
                results[bucket] = f"unexpected_error: {e}"
                logger.error(f"Unexpected error deleting bucket {bucket}: {e}")

        return results

    async def bucket_health_check(self) -> BucketHealthCheckResult:
        """Perform health check on all required buckets."""
        health_status: BucketHealthCheckResult = {
            "overall_status": "healthy",
            "buckets": {},
            "issues": [],
        }

        for bucket in self.required_buckets:
            try:
                if self.get_s3_client().bucket_exists(bucket):
                    health_status["buckets"][bucket] = {
                        "status": "accessible",
                        "accessible": True,
                    }
                else:
                    health_status["buckets"][bucket] = {
                        "status": "not_found",
                        "accessible": False,
                    }
                    health_status["issues"].append(f"Bucket {bucket}: not_found")
                    health_status["overall_status"] = "unhealthy"
            except S3Error as e:
                health_status["buckets"][bucket] = {
                    "status": "error",
                    "error_code": e.code,
                    "accessible": False,
                }
                health_status["issues"].append(f"Bucket {bucket}: {e.code}")
                health_status["overall_status"] = "unhealthy"

        return health_status

    async def run_setup(self) -> BucketSetupResult:
        """Run complete setup process for development environment."""
        logger.info("Starting development environment setup")

        # Ensure buckets exist
        bucket_results = await self.ensure_buckets_exist()

        # Perform health check
        health_status = await self.bucket_health_check()

        setup_results: BucketSetupResult = {
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
