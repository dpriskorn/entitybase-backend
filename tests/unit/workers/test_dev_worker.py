"""Tests for the DevWorker."""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from models.workers.dev.dev_worker import DevWorker


class TestDevWorker:
    """Test cases for DevWorker functionality."""

    def test_initialization(self):
        """Test DevWorker initialization with default values."""
        worker = DevWorker()

        assert worker.minio_endpoint == "http://localhost:9000"
        assert worker.minio_access_key == "minioadmin"
        assert worker.minio_secret_key == "minioadmin"
        assert worker.required_buckets == ["terms", "statements", "revisions", "dumps"]

    def test_custom_initialization(self):
        """Test DevWorker initialization with custom values."""
        worker = DevWorker(
            minio_endpoint="http://custom:9000",
            minio_access_key="custom_key",
            minio_secret_key="custom_secret",
            required_buckets=["custom1", "custom2"],
        )

        assert worker.minio_endpoint == "http://custom:9000"
        assert worker.minio_access_key == "custom_key"
        assert worker.minio_secret_key == "custom_secret"
        assert worker.required_buckets == ["custom1", "custom2"]

    @patch("models.workers.dev.dev_worker._boto3")
    def test_s3_client_creation(self, mock_boto3):
        """Test S3 client creation."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        worker = DevWorker()
        client = worker.s3_client

        mock_boto3.client.assert_called_once_with(
            "s3",
            endpoint_url="http://localhost:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
        )
        assert client == mock_client

    @pytest.mark.asyncio
    @patch("models.workers.dev.dev_worker._boto3")
    async def test_ensure_buckets_exist_success(self, mock_boto3):
        """Test successful bucket creation when buckets don't exist."""
        # Setup mock S3 client
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        # Mock ClientError for 404 (bucket doesn't exist)
        not_found_error = ClientError(
            error_response={"Error": {"Code": "404"}}, operation_name="HeadBucket"
        )

        # head_bucket raises 404, then create_bucket succeeds
        mock_client.head_bucket.side_effect = not_found_error
        mock_client.create_bucket.return_value = None

        worker = DevWorker()
        results = await worker.ensure_buckets_exist()

        # Should attempt to create all 4 buckets
        assert mock_client.create_bucket.call_count == 4
        assert all(status == "created" for status in results.values())
        assert set(results.keys()) == {"terms", "statements", "revisions", "dumps"}

    @pytest.mark.asyncio
    @patch("models.workers.dev.dev_worker._boto3")
    async def test_ensure_buckets_exist_already_exist(self, mock_boto3):
        """Test bucket creation when buckets already exist."""
        # Setup mock S3 client
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        # head_bucket succeeds (buckets exist)
        mock_client.head_bucket.return_value = None

        worker = DevWorker()
        results = await worker.ensure_buckets_exist()

        # Should not call create_bucket
        mock_client.create_bucket.assert_not_called()
        assert all(status == "exists" for status in results.values())

    @pytest.mark.asyncio
    @patch("models.workers.dev.dev_worker._boto3")
    async def test_ensure_buckets_exist_error(self, mock_boto3):
        """Test bucket creation error handling."""
        # Setup mock S3 client
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        permission_error = ClientError(
            error_response={"Error": {"Code": "AccessDenied"}},
            operation_name="HeadBucket",
        )

        mock_client.head_bucket.side_effect = permission_error

        worker = DevWorker()
        results = await worker.ensure_buckets_exist()

        # Should not call create_bucket due to error
        mock_client.create_bucket.assert_not_called()
        assert all("error: AccessDenied" in status for status in results.values())

    @pytest.mark.asyncio
    @patch("models.workers.dev.dev_worker._boto3")
    async def test_bucket_health_check_success(self, mock_boto3):
        """Test successful bucket health check."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        # All buckets accessible
        mock_client.head_bucket.return_value = None

        worker = DevWorker()
        health = await worker.bucket_health_check()

        assert health["overall_status"] == "healthy"
        assert len(health["buckets"]) == 4
        assert all(
            bucket["status"] == "accessible" for bucket in health["buckets"].values()
        )
        assert health["issues"] == []

    @pytest.mark.asyncio
    @patch("models.workers.dev.dev_worker._boto3")
    async def test_bucket_health_check_partial_failure(self, mock_boto3):
        """Test bucket health check with some failures."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        def side_effect(bucket_name):
            if bucket_name == "terms":
                raise ClientError(
                    error_response={"Error": {"Code": "404"}},
                    operation_name="HeadBucket",
                )
            return None

        mock_client.head_bucket.side_effect = side_effect

        worker = DevWorker()
        health = await worker.bucket_health_check()

        assert health["overall_status"] == "unhealthy"
        assert health["buckets"]["terms"]["status"] == "error"
        assert health["buckets"]["terms"]["error_code"] == "404"
        assert health["buckets"]["statements"]["status"] == "accessible"
        assert len(health["issues"]) == 1
        assert "terms" in health["issues"][0]

    @pytest.mark.asyncio
    @patch("models.workers.dev.dev_worker._boto3")
    async def test_cleanup_buckets_success(self, mock_boto3):
        """Test successful bucket cleanup."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        # Mock list_objects_v2 to return empty (no objects to delete)
        mock_client.list_objects_v2.return_value = {}
        mock_client.delete_bucket.return_value = None

        worker = DevWorker()
        results = await worker.cleanup_buckets()

        # Should call delete_bucket for each bucket
        assert mock_client.delete_bucket.call_count == 4
        assert all(status == "deleted" for status in results.values())

    @pytest.mark.asyncio
    @patch("models.workers.dev.dev_worker._boto3")
    async def test_cleanup_buckets_with_objects(self, mock_boto3):
        """Test bucket cleanup that deletes objects first."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        # Mock objects in bucket
        mock_client.list_objects_v2.return_value = {
            "Contents": [{"Key": "object1"}, {"Key": "object2"}]
        }
        mock_client.delete_bucket.return_value = None

        worker = DevWorker()
        results = await worker.cleanup_buckets()

        # Should delete objects first, then bucket
        assert mock_client.delete_object.call_count == 8  # 2 objects × 4 buckets
        assert mock_client.delete_bucket.call_count == 4
        assert all(status == "deleted" for status in results.values())

    @pytest.mark.asyncio
    @patch("models.workers.dev.dev_worker._boto3")
    async def test_run_setup_success(self, mock_boto3):
        """Test successful run_setup."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        # Setup mocks for success
        not_found_error = ClientError(
            error_response={"Error": {"Code": "404"}}, operation_name="HeadBucket"
        )
        mock_client.head_bucket.side_effect = not_found_error
        mock_client.create_bucket.return_value = None

        worker = DevWorker()
        results = await worker.run_setup()

        assert results["setup_status"] == "completed"
        assert all(
            status == "created" for status in results["buckets_created"].values()
        )
        assert results["health_check"]["overall_status"] == "healthy"

    def test_import_error_handling(self):
        """Test that DevWorker handles boto3 import errors gracefully."""
        with patch.dict("sys.modules", {"boto3": None}):
            with pytest.raises(ImportError, match="boto3 is required"):
                DevWorker()
