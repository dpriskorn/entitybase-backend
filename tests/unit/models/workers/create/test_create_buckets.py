"""Unit tests for create_buckets."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from minio.error import S3Error

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
            assert worker.rustfs_endpoint == "http://localhost:9000"
            assert worker.rustfs_access_key == "minioadmin"
            assert worker.rustfs_secret_key == "minioadmin"

    def test_initialization_custom(self):
        """Test CreateBuckets initialization with custom values."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets(
                rustfs_endpoint="http://custom:9000",
                rustfs_access_key="custom_key",
                rustfs_secret_key="custom_secret",
            )
            assert worker.rustfs_endpoint == "http://custom:9000"
            assert worker.rustfs_access_key == "custom_key"
            assert worker.rustfs_secret_key == "custom_secret"

    def test_required_buckets_attribute(self):
        """Test required_buckets attribute exists."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
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
            assert "rustfs_endpoint" in dumped
            assert "rustfs_access_key" in dumped
            assert "rustfs_secret_key" in dumped

    @pytest.mark.asyncio
    async def test_ensure_buckets_exist_bucket_exists(self):
        """Test ensure_buckets_exist when bucket already exists."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["test-bucket"]

            mock_minio = MagicMock()
            mock_minio.bucket_exists.return_value = True

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
                result = await worker.ensure_buckets_exist()

                assert result["test-bucket"] == "exists"
                mock_minio.bucket_exists.assert_called_once_with("test-bucket")

    @pytest.mark.asyncio
    async def test_ensure_buckets_exist_bucket_created(self):
        """Test ensure_buckets_exist when bucket needs to be created."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["new-bucket"]

            mock_minio = MagicMock()
            mock_minio.bucket_exists.return_value = False

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
                result = await worker.ensure_buckets_exist()

                assert result["new-bucket"] == "created"
                mock_minio.make_bucket.assert_called_once_with("new-bucket")

    @pytest.mark.asyncio
    async def test_ensure_buckets_exist_create_failure(self):
        """Test ensure_buckets_exist when bucket creation fails."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["fail-bucket"]

            mock_minio = MagicMock()
            mock_minio.bucket_exists.return_value = False
            mock_minio.make_bucket.side_effect = S3Error(
                None, "make_bucket", "Internal Error", None, "req_id", "host_id"
            )

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
                result = await worker.ensure_buckets_exist()

                assert "create_failed" in result["fail-bucket"]

    @pytest.mark.asyncio
    async def test_ensure_buckets_exist_other_s3_error(self):
        """Test ensure_buckets_exist with other S3Error."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["error-bucket"]

            mock_minio = MagicMock()
            mock_minio.bucket_exists.side_effect = S3Error(
                None, "head_bucket", "Internal Error", None, "req_id", "host_id"
            )

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
                result = await worker.ensure_buckets_exist()

                assert "error: head_bucket" in result["error-bucket"]

    @pytest.mark.asyncio
    async def test_ensure_buckets_exist_unexpected_error(self):
        """Test ensure_buckets_exist with unexpected error."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["unexpected-bucket"]

            mock_minio = MagicMock()
            mock_minio.bucket_exists.side_effect = ValueError("Unexpected")

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
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

            mock_minio = MagicMock()
            mock_minio.list_objects.return_value = []

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
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

            mock_obj = MagicMock()
            mock_obj.object_name = "object1"

            mock_obj2 = MagicMock()
            mock_obj2.object_name = "object2"

            mock_minio = MagicMock()
            mock_minio.list_objects.return_value = [mock_obj, mock_obj2]

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
                result = await worker.cleanup_buckets()

                assert result["bucket-with-objects"] == "deleted"
                assert mock_minio.remove_object.call_count == 2

    @pytest.mark.asyncio
    async def test_cleanup_buckets_not_found(self):
        """Test cleanup_buckets when bucket doesn't exist."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets()
            worker.required_buckets = ["missing-bucket"]

            mock_minio = MagicMock()
            mock_minio.list_objects.side_effect = S3Error(
                None, "list_objects", "NoSuchBucket", None, "req_id", "host_id"
            )
            mock_minio.remove_bucket.side_effect = S3Error(
                None, "remove_bucket", "NoSuchBucket", None, "req_id", "host_id"
            )

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
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

            mock_minio = MagicMock()
            mock_minio.list_objects.return_value = []
            mock_minio.remove_bucket.side_effect = S3Error(
                None, "remove_bucket", "AccessDenied", None, "req_id", "host_id"
            )

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
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

            mock_minio = MagicMock()
            mock_minio.bucket_exists.return_value = True

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
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

            mock_minio = MagicMock()
            mock_minio.bucket_exists.side_effect = S3Error(None, "bucket_exists", "Forbidden", None, "req_id", "host_id")

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
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

            mock_minio = MagicMock()
            mock_minio.bucket_exists.return_value = True

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
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

            mock_minio = MagicMock()
            mock_minio.bucket_exists.side_effect = S3Error(None, "bucket_exists", "Forbidden", None, "req_id", "host_id")

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = mock_minio
                result = await worker.run_setup()

                assert result["setup_status"] == "failed"
                assert result["health_check"]["overall_status"] == "unhealthy"

    def test_s3_client_creation(self):
        """Test S3 client is created with correct parameters."""
        with patch(
            "models.workers.create.create_buckets.CreateBuckets.model_post_init"
        ):
            worker = CreateBuckets(
                rustfs_endpoint="http://custom:9000",
                rustfs_access_key="mykey",
                rustfs_secret_key="mysecret",
            )
            worker.required_buckets = []

            with patch("models.workers.create.create_buckets.Minio") as mock_minio_class:
                mock_minio_class.return_value = MagicMock()
                _ = worker.get_s3_client()
                mock_minio_class.assert_called_once_with(
                    "custom:9000",
                    access_key="mykey",
                    secret_key="mysecret",
                    secure=False,
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
