"""Unit tests for S3QualifierData model."""

import pytest

from models.data.infrastructure.s3.qualifier_data import S3QualifierData


class TestS3QualifierData:
    """Unit tests for S3QualifierData model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        data = S3QualifierData(
            qualifier={"property": "P580", "value": "2023-01-01"},
            content_hash=123456789,
            created_at="2023-01-01T12:00:00Z",
        )
        assert data.qualifier == {"property": "P580", "value": "2023-01-01"}
        assert data.content_hash == 123456789
        assert data.created_at == "2023-01-01T12:00:00Z"

    def test_with_alias(self):
        """Test instantiation using alias."""
        data = S3QualifierData(
            qualifier={"property": "P31"},
            hash=999,
            created_at="2024-01-01T00:00:00Z",
        )
        assert data.content_hash == 999

    def test_model_dump(self):
        """Test model_dump()."""
        data = S3QualifierData(
            qualifier={"property": "P31"},
            content_hash=123,
            created_at="2024-01-01T00:00:00Z",
        )
        dumped = data.model_dump()
        assert "qualifier" in dumped
        assert dumped["content_hash"] == 123

    def test_model_dump_by_alias(self):
        """Test model_dump with alias."""
        data = S3QualifierData(
            qualifier={"property": "P31"},
            content_hash=123,
            created_at="2024-01-01T00:00:00Z",
        )
        dumped = data.model_dump(by_alias=True)
        assert "hash" in dumped
        assert dumped["hash"] == 123

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        data = S3QualifierData(
            qualifier={"property": "P31"},
            content_hash=123,
            created_at="2024-01-01T00:00:00Z",
        )
        json_str = data.model_dump_json()
        assert "P31" in json_str
