"""Unit tests for S3SitelinkData model."""

import pytest

from models.data.infrastructure.s3.sitelink_data import S3SitelinkData


class TestS3SitelinkData:
    """Unit tests for S3SitelinkData."""

    def test_create_sitelink_data(self):
        """Test creating S3SitelinkData with title_hash and badges."""
        data = S3SitelinkData(title_hash=12345, badges=["featured", "good"])
        assert data.title_hash == 12345
        assert data.badges == ["featured", "good"]

    def test_create_sitelink_data_default_badges(self):
        """Test creating S3SitelinkData with default empty badges."""
        data = S3SitelinkData(title_hash=67890)
        assert data.title_hash == 67890
        assert data.badges == []

    def test_sitelink_data_model_dump(self):
        """Test model_dump includes all fields."""
        data = S3SitelinkData(title_hash=111, badges=["test"])
        dumped = data.model_dump()
        assert dumped == {"title_hash": 111, "badges": ["test"]}

    def test_sitelink_data_from_dict(self):
        """Test creating from dict."""
        data = S3SitelinkData.model_validate({"title_hash": 222, "badges": []})
        assert data.title_hash == 222
        assert data.badges == []