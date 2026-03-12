"""Unit tests for S3 snak data models."""

import pytest

from models.data.infrastructure.s3.snak_data import (
    ProcessedSnakList,
    ProcessedSnakValue,
    S3ReferenceSnaks,
    S3SnakData,
)


class TestS3SnakData:
    """Unit tests for S3SnakData model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        data = S3SnakData(
            schema_version="1.0.0",
            snak={"snaktype": "value", "property": "P31"},
            content_hash=123456789,
            created_at="2023-01-01T12:00:00Z",
        )
        assert data.schema_version == "1.0.0"
        assert data.snak == {"snaktype": "value", "property": "P31"}
        assert data.content_hash == 123456789

    def test_with_alias(self):
        """Test instantiation using alias."""
        data = S3SnakData(
            schema="2.0.0",
            snak={},
            hash=999,
            created_at="2024-01-01T00:00:00Z",
        )
        assert data.schema_version == "2.0.0"
        assert data.content_hash == 999

    def test_model_dump(self):
        """Test model_dump()."""
        data = S3SnakData(
            schema_version="1.0.0",
            snak={},
            content_hash=123,
            created_at="2024-01-01T00:00:00Z",
        )
        dumped = data.model_dump()
        assert "snak" in dumped

    def test_model_dump_by_alias(self):
        """Test model_dump with alias."""
        data = S3SnakData(
            schema_version="1.0.0",
            snak={},
            content_hash=123,
            created_at="2024-01-01T00:00:00Z",
        )
        dumped = data.model_dump(by_alias=True)
        assert "schema" in dumped
        assert "hash" in dumped


class TestProcessedSnakValue:
    """Unit tests for ProcessedSnakValue model."""

    def test_with_int_value(self):
        """Test with integer value."""
        value = ProcessedSnakValue(value=123)
        assert value.value == 123

    def test_with_string_value(self):
        """Test with string value."""
        value = ProcessedSnakValue(value="test")
        assert value.value == "test"

    def test_with_dict_value(self):
        """Test with dict value."""
        value = ProcessedSnakValue(value={"key": "value"})
        assert value.value == {"key": "value"}

    def test_with_none_value(self):
        """Test with None value."""
        value = ProcessedSnakValue(value=None)
        assert value.value is None


class TestProcessedSnakList:
    """Unit tests for ProcessedSnakList model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        snak_list = ProcessedSnakList(
            key="P31",
            values=[ProcessedSnakValue(value=123)],
        )
        assert snak_list.key == "P31"
        assert len(snak_list.values) == 1

    def test_model_dump(self):
        """Test model_dump()."""
        snak_list = ProcessedSnakList(
            key="P31",
            values=[ProcessedSnakValue(value=123)],
        )
        dumped = snak_list.model_dump()
        assert dumped["key"] == "P31"


class TestS3ReferenceSnaks:
    """Unit tests for S3ReferenceSnaks model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        ref_snaks = S3ReferenceSnaks(
            snaks={"P854": [{"value": "https://example.com"}]},
            snaks_order=["P854"],
        )
        assert "P854" in ref_snaks.snaks
        assert ref_snaks.snaks_order == ["P854"]

    def test_default_snaks_order(self):
        """Test default snaks_order."""
        ref_snaks = S3ReferenceSnaks(snaks={})
        assert ref_snaks.snaks_order == []

    def test_model_dump(self):
        """Test model_dump()."""
        ref_snaks = S3ReferenceSnaks(
            snaks={"P854": []},
            snaks_order=["P854"],
        )
        dumped = ref_snaks.model_dump()
        assert "snaks" in dumped
