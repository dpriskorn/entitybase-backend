"""Tests for the CreateBuckets."""

import pytest

pytestmark = pytest.mark.unit
from unittest.mock import AsyncMock, MagicMock, patch
from botocore.exceptions import ClientError
from models.workers.dev.create_buckets import CreateBuckets


class TestCreateBuckets:
    """Test cases for CreateBuckets functionality."""

    def test_initialization(self):
        """Test CreateBuckets initialization with default values."""
        worker = CreateBuckets()

        assert worker.minio_endpoint == "http://localhost:9000"
        assert worker.minio_access_key == "minioadmin"
        assert worker.minio_secret_key == "minioadmin"
        assert worker.required_buckets == [
            "terms",
            "statements",
            "revisions",
            "dumps",
            "sitelinks",
        ]

    def test_custom_initialization(self):
        """Test CreateBuckets initialization with custom values."""
        worker = CreateBuckets(
            minio_endpoint="http://custom:9000",
            minio_access_key="custom_key",
            minio_secret_key="custom_secret",
            required_buckets=["custom1", "custom2"],
        )

        assert worker.minio_endpoint == "http://custom:9000"
        assert worker.minio_access_key == "custom_key"
        assert worker.minio_secret_key == "custom_secret"
        assert worker.required_buckets == ["custom1", "custom2"]

    @patch("models.workers.dev.create_buckets._boto3")
    def test_s3_client_creation(self, mock_boto3):
        """Test S3 client creation."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        worker = CreateBuckets()
        client = worker.s3_client

        mock_boto3.client.assert_called_once_with(
            "s3",
            endpoint_url="http://localhost:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
        )
        assert client == mock_client

    @pytest.mark.asyncio
    @patch("models.workers.dev.create_buckets._boto3")
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

        worker = CreateBuckets()
        results = await worker.ensure_buckets_exist()

        # Should attempt to create all 5 buckets
        assert mock_client.create_bucket.call_count == 5
        assert all(status == "created" for status in results.values())
        assert set(results.keys()) == {
            "terms",
            "statements",
            "revisions",
            "dumps",
            "sitelinks",
        }

    @pytest.mark.asyncio
    @patch("models.workers.dev.create_buckets._boto3")
    async def test_ensure_buckets_exist_already_exist(self, mock_boto3):
        """Test bucket creation when buckets already exist."""
        # Setup mock S3 client
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        # head_bucket succeeds (buckets exist)
        mock_client.head_bucket.return_value = None

        worker = CreateBuckets()
        results = await worker.ensure_buckets_exist()

        # Should not call create_bucket
        mock_client.create_bucket.assert_not_called()
        assert all(status == "exists" for status in results.values())

    @pytest.mark.asyncio
    @patch("models.workers.dev.create_buckets._boto3")
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

        worker = CreateBuckets()
        results = await worker.ensure_buckets_exist()

        # Should not call create_bucket due to error
        mock_client.create_bucket.assert_not_called()
        assert all("error: AccessDenied" in status for status in results.values())

    @pytest.mark.asyncio
    @patch("models.workers.dev.create_buckets._boto3")
    async def test_bucket_health_check_success(self, mock_boto3):
        """Test successful bucket health check."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        # All buckets accessible
        mock_client.head_bucket.return_value = None

        worker = CreateBuckets()
        health = await worker.bucket_health_check()

        assert health["overall_status"] == "healthy"
        assert len(health["buckets"]) == 5
        assert all(
            bucket["status"] == "accessible" for bucket in health["buckets"].values()
        )
        assert health["issues"] == []

    @pytest.mark.asyncio
    @patch("models.workers.dev.create_buckets._boto3")
    async def test_bucket_health_check_partial_failure(self, mock_boto3):
        """Test bucket health check with some failures."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        def side_effect(Bucket):
            if Bucket == "terms":
                raise ClientError(
                    error_response={"Error": {"Code": "404"}},
                    operation_name="HeadBucket",
                )
            return None

        mock_client.head_bucket.side_effect = side_effect

        worker = CreateBuckets()
        health = await worker.bucket_health_check()

        assert health["overall_status"] == "unhealthy"
        assert health["buckets"]["terms"]["status"] == "error"
        assert health["buckets"]["terms"]["error_code"] == "404"
        assert health["buckets"]["statements"]["status"] == "accessible"
        assert len(health["issues"]) == 1
        assert "terms" in health["issues"][0]

    @pytest.mark.asyncio
    @patch("models.workers.dev.create_buckets._boto3")
    async def test_cleanup_buckets_success(self, mock_boto3):
        """Test successful bucket cleanup."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        # Mock list_objects_v2 to return empty (no objects to delete)
        mock_client.list_objects_v2.return_value = {}
        mock_client.delete_bucket.return_value = None

        worker = CreateBuckets()
        results = await worker.cleanup_buckets()

        # Should call delete_bucket for each bucket
        assert mock_client.delete_bucket.call_count == 5
        assert all(status == "deleted" for status in results.values())

    @pytest.mark.asyncio
    @patch("models.workers.dev.create_buckets._boto3")
    async def test_cleanup_buckets_with_objects(self, mock_boto3):
        """Test bucket cleanup that deletes objects first."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        # Mock objects in bucket
        mock_client.list_objects_v2.return_value = {
            "Contents": [{"Key": "object1"}, {"Key": "object2"}]
        }
        mock_client.delete_bucket.return_value = None

        worker = CreateBuckets()
        results = await worker.cleanup_buckets()

        # Should delete objects first, then bucket
        assert mock_client.delete_object.call_count == 10  # 2 objects × 5 buckets
        assert mock_client.delete_bucket.call_count == 5
        assert all(status == "deleted" for status in results.values())

    @pytest.mark.asyncio
    @patch("models.workers.dev.create_buckets._boto3")
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

        worker = CreateBuckets()
        with patch.object(
            CreateBuckets,
            "bucket_health_check",
            new=AsyncMock(return_value={"overall_status": "healthy"}),
        ):
            results = await worker.run_setup()

        assert results["setup_status"] == "completed"
        assert all(
            status == "created" for status in results["buckets_created"].values()
        )
        assert results["health_check"]["overall_status"] == "healthy"
