"""Unit tests for PropertyCounts model."""

import pytest

from models.data.infrastructure.s3.property_counts import PropertyCounts


class TestPropertyCounts:
    """Unit tests for PropertyCounts model."""

    def test_empty_property_counts(self):
        """Test empty property counts."""
        counts = PropertyCounts(root={})
        assert counts.root == {}

    def test_with_properties(self):
        """Test property counts with data."""
        counts = PropertyCounts(root={"P31": 10, "P569": 5})
        assert counts.root == {"P31": 10, "P569": 5}

    def test_model_dump(self):
        """Test model_dump()."""
        counts = PropertyCounts(root={"P31": 10})
        dumped = counts.model_dump()
        assert dumped == {"P31": 10}

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        counts = PropertyCounts(root={"P31": 10, "P569": 5})
        json_str = counts.model_dump_json()
        assert "P31" in json_str
        assert "10" in json_str
