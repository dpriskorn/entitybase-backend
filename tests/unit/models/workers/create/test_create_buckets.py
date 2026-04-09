"""Unit tests for create_buckets."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

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
