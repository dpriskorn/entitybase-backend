"""Unit tests for S3ReferenceData model."""

import pytest

from models.data.infrastructure.s3.reference_data import S3ReferenceData


class TestS3ReferenceData:
    """Unit tests for S3ReferenceData model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        data = S3ReferenceData(
            reference={"snaks": {"P854": [{"value": "https://example.com"}]}},
            content_hash=123456789,
            created_at="2023-01-01T12:00:00Z",
        )
        assert "snaks" in data.reference
        assert data.content_hash == 123456789

    def test_with_alias(self):
        """Test instantiation using alias."""
        data = S3ReferenceData(
            reference={"snaks": {}},
            hash=999,
            created_at="2024-01-01T00:00:00Z",
        )
        assert data.content_hash == 999

    def test_model_dump(self):
        """Test model_dump()."""
        data = S3ReferenceData(
            reference={"snaks": {}},
            content_hash=123,
            created_at="2024-01-01T00:00:00Z",
        )
        dumped = data.model_dump()
        assert "reference" in dumped

    def test_model_dump_by_alias(self):
        """Test model_dump with alias."""
        data = S3ReferenceData(
            reference={"snaks": {}},
            content_hash=123,
            created_at="2024-01-01T00:00:00Z",
        )
        dumped = data.model_dump(by_alias=True)
        assert "hash" in dumped

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        data = S3ReferenceData(
            reference={"snaks": {"P854": [{"value": "test"}]}},
            content_hash=123,
            created_at="2024-01-01T00:00:00Z",
        )
        json_str = data.model_dump_json()
        assert "P854" in json_str
