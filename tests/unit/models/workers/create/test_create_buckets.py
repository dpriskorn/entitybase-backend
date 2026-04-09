"""Unit tests for create_buckets."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from botocore.exceptions import ClientError

from models.workers.create.create_buckets import (
    CreateBuckets,
)


class TestCreateBuckets:
    """Unit tests for CreateBuckets."""

    def test_initialization_defaults(self):
        """Test CreateBuckets initialization with defaults."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            assert worker.minio_endpoint == "http://localhost:9000"
            assert worker.minio_access_key == "minioadmin"
            assert worker.minio_secret_key == "minioadmin"

    def test_initialization_custom(self):
        """Test CreateBuckets initialization with custom values."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets(
                minio_endpoint="http://custom:9000",
                minio_access_key="custom_key",
                minio_secret_key="custom_secret",
            )
            assert worker.minio_endpoint == "http://custom:9000"
            assert worker.minio_access_key == "custom_key"
            assert worker.minio_secret_key == "custom_secret"

    def test_required_buckets_attribute(self):
        """Test required_buckets attribute exists."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            # The model_post_init sets required_buckets from settings
            # Just verify the attribute can be set
            worker.required_buckets = ["test-bucket"]
            assert "test-bucket" in worker.required_buckets

    def test_model_dump(self):
        """Test model_dump includes expected fields."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["test"]

            dumped = worker.model_dump()
            assert "minio_endpoint" in dumped
            assert "minio_access_key" in dumped
            assert "minio_secret_key" in dumped

    @pytest.mark.asyncio
    async def test_ensure_buckets_exist_bucket_exists(self):
        """Test ensure_buckets_exist when bucket already exists."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["test-bucket"]
            worker.s3_client = MagicMock()
            worker.s3_client.head_bucket.return_value = None

            result = await worker.ensure_buckets_exist()

            assert result["test-bucket"] == "exists"
            worker.s3_client.head_bucket.assert_called_once_with(Bucket="test-bucket")

    @pytest.mark.asyncio
    async def test_ensure_buckets_exist_bucket_created(self):
        """Test ensure_buckets_exist when bucket needs to be created."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["new-bucket"]
            worker.s3_client = MagicMock()

            error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
            worker.s3_client.head_bucket.side_effect = ClientError(
                error_response, "HeadBucket"
            )

            result = await worker.ensure_buckets_exist()

            assert result["new-bucket"] == "created"
            worker.s3_client.create_bucket.assert_called_once_with(Bucket="new-bucket")

    @pytest.mark.asyncio
    async def test_ensure_buckets_exist_create_failure(self):
        """Test ensure_buckets_exist when bucket creation fails."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["fail-bucket"]
            worker.s3_client = MagicMock()

            not_found_response = {"Error": {"Code": "404", "Message": "Not Found"}}
            worker.s3_client.head_bucket.side_effect = ClientError(
                not_found_response, "HeadBucket"
            )
            worker.s3_client.create_bucket.side_effect = Exception("Create failed")

            result = await worker.ensure_buckets_exist()

            assert "create_failed" in result["fail-bucket"]

    @pytest.mark.asyncio
    async def test_ensure_buckets_exist_other_client_error(self):
        """Test ensure_buckets_exist with other ClientError."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["error-bucket"]
            worker.s3_client = MagicMock()

            error_response = {"Error": {"Code": "500", "Message": "Internal Error"}}
            worker.s3_client.head_bucket.side_effect = ClientError(
                error_response, "HeadBucket"
            )

            result = await worker.ensure_buckets_exist()

            assert "error: 500" in result["error-bucket"]

    @pytest.mark.asyncio
    async def test_ensure_buckets_exist_unexpected_error(self):
        """Test ensure_buckets_exist with unexpected error."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["unexpected-bucket"]
            worker.s3_client = MagicMock()
            worker.s3_client.head_bucket.side_effect = ValueError("Unexpected")

            result = await worker.ensure_buckets_exist()

            assert "unexpected_error" in result["unexpected-bucket"]

    @pytest.mark.asyncio
    async def test_cleanup_buckets_success(self):
        """Test cleanup_buckets successfully deletes bucket."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["cleanup-bucket"]
            worker.s3_client = MagicMock()
            worker.s3_client.list_objects_v2.return_value = {}
            worker.s3_client.delete_bucket.return_value = None

            result = await worker.cleanup_buckets()

            assert result["cleanup-bucket"] == "deleted"

    @pytest.mark.asyncio
    async def test_cleanup_buckets_with_objects(self):
        """Test cleanup_buckets deletes objects before bucket."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["bucket-with-objects"]
            worker.s3_client = MagicMock()
            worker.s3_client.list_objects_v2.return_value = {
                "Contents": [
                    {"Key": "object1"},
                    {"Key": "object2"},
                ]
            }

            result = await worker.cleanup_buckets()

            assert result["bucket-with-objects"] == "deleted"
            assert worker.s3_client.delete_object.call_count == 2

    @pytest.mark.asyncio
    async def test_cleanup_buckets_not_found(self):
        """Test cleanup_buckets when bucket doesn't exist."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["missing-bucket"]
            worker.s3_client = MagicMock()

            error_response = {"Error": {"Code": "NoSuchBucket", "Message": "Not Found"}}
            worker.s3_client.list_objects_v2.side_effect = ClientError(
                error_response, "ListObjectsV2"
            )

            result = await worker.cleanup_buckets()

            assert result["missing-bucket"] == "not_found"

    @pytest.mark.asyncio
    async def test_cleanup_buckets_delete_failure(self):
        """Test cleanup_buckets when delete fails."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["delete-fail-bucket"]
            worker.s3_client = MagicMock()
            worker.s3_client.list_objects_v2.return_value = {}

            error_response = {"Error": {"Code": "AccessDenied", "Message": "Denied"}}
            worker.s3_client.delete_bucket.side_effect = ClientError(
                error_response, "DeleteBucket"
            )

            result = await worker.cleanup_buckets()

            assert "delete_failed" in result["delete-fail-bucket"]

    @pytest.mark.asyncio
    async def test_bucket_health_check_healthy(self):
        """Test bucket_health_check when all buckets are healthy."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["healthy-bucket"]
            worker.s3_client = MagicMock()
            worker.s3_client.head_bucket.return_value = None

            result = await worker.bucket_health_check()

            assert result["overall_status"] == "healthy"
            assert result["buckets"]["healthy-bucket"]["accessible"] is True

    @pytest.mark.asyncio
    async def test_bucket_health_check_unhealthy(self):
        """Test bucket_health_check when bucket is unhealthy."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["unhealthy-bucket"]
            worker.s3_client = MagicMock()

            error_response = {"Error": {"Code": "403", "Message": "Forbidden"}}
            worker.s3_client.head_bucket.side_effect = ClientError(
                error_response, "HeadBucket"
            )

            result = await worker.bucket_health_check()

            assert result["overall_status"] == "unhealthy"
            assert result["buckets"]["unhealthy-bucket"]["accessible"] is False
            assert len(result["issues"]) > 0

    @pytest.mark.asyncio
    async def test_run_setup_healthy(self):
        """Test run_setup when health check passes."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["setup-bucket"]
            worker.s3_client = MagicMock()
            worker.s3_client.head_bucket.return_value = None

            result = await worker.run_setup()

            assert result["setup_status"] == "completed"
            assert result["buckets_created"]["setup-bucket"] == "exists"
            assert result["health_check"]["overall_status"] == "healthy"

    @pytest.mark.asyncio
    async def test_run_setup_failed(self):
        """Test run_setup when health check fails."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["fail-bucket"]
            worker.s3_client = MagicMock()

            error_response = {"Error": {"Code": "403", "Message": "Forbidden"}}
            worker.s3_client.head_bucket.side_effect = ClientError(
                error_response, "HeadBucket"
            )

            result = await worker.run_setup()

            assert result["setup_status"] == "failed"
            assert result["health_check"]["overall_status"] == "unhealthy"

    def test_s3_client_creation(self):
        """Test S3 client is created with correct parameters."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets(
                minio_endpoint="http://custom:9000",
                minio_access_key="mykey",
                minio_secret_key="mysecret",
            )
            worker.required_buckets = []

            with patch("models.workers.create.create_buckets._boto3") as mock_boto3:
                _ = worker.s3_client
                mock_boto3.client.assert_called_once_with(
                    "s3",
                    endpoint_url="http://custom:9000",
                    aws_access_key_id="mykey",
                    aws_secret_access_key="mysecret",
                )


class TestBucketHealthCheckResult:
    """Unit tests for BucketHealthCheckResult."""

    def test_bucket_health_check_result_creation(self):
        """Test BucketHealthCheckResult creation."""
        from models.workers.create.create_buckets import BucketHealthCheckResult

        result: BucketHealthCheckResult = {
            "overall_status": "healthy",
            "buckets": {"test-bucket": {"status": "accessible"}},
            "issues": [],
        }

        assert result["overall_status"] == "healthy"
        assert "test-bucket" in result["buckets"]


class TestBucketSetupResult:
    """Unit tests for BucketSetupResult."""

    def test_bucket_setup_result_creation(self):
        """Test BucketSetupResult creation."""
        from models.workers.create.create_buckets import BucketSetupResult

        health_check: BucketHealthCheckResult = {
            "overall_status": "healthy",
            "buckets": {},
            "issues": [],
        }

        result: BucketSetupResult = {
            "buckets_created": {"test-bucket": "created"},
            "health_check": health_check,
            "setup_status": "completed",
        }

        assert result["setup_status"] == "completed"
        assert result["buckets_created"]["test-bucket"] == "created"
