"""Unit tests for BaseDiff model."""

import pytest

from models.rdf_builder.base_diff import BaseDiff
from models.rdf_builder.diff_result import DiffResult


class TestBaseDiffComputeDictDiff:
    """Test suite for _compute_dict_diff static method."""

    def test_no_changes(self):
        """Test diff when old and new items are identical."""
        old_items = {"a": 1, "b": 2}
        new_items = {"a": 1, "b": 2}

        result = BaseDiff._compute_dict_diff(old_items, new_items)

        assert isinstance(result, DiffResult)
        assert result.added == []
        assert result.removed == []
        assert result.modified == []

    def test_all_added(self):
        """Test diff when all items are new."""
        old_items = {}
        new_items = {"a": 1, "b": 2}

        result = BaseDiff._compute_dict_diff(old_items, new_items)

        assert len(result.added) == 2
        assert result.removed == []
        assert result.modified == []

    def test_all_removed(self):
        """Test diff when all items are removed."""
        old_items = {"a": 1, "b": 2}
        new_items = {}

        result = BaseDiff._compute_dict_diff(old_items, new_items)

        assert result.added == []
        assert len(result.removed) == 2
        assert result.modified == []

    def test_mixed_changes(self):
        """Test diff with mixed additions, removals, and modifications."""
        old_items = {"a": 1, "b": 2, "c": 3}
        new_items = {"a": 1, "b": 20, "d": 4}

        result = BaseDiff._compute_dict_diff(old_items, new_items)

        assert len(result.added) == 1
        assert result.added == [4]

        assert len(result.removed) == 1
        assert result.removed == [3]

        assert len(result.modified) == 1
        assert result.modified == [{"old": 2, "new": 20}]

    def test_empty_dicts(self):
        """Test diff with empty dictionaries."""
        old_items = {}
        new_items = {}

        result = BaseDiff._compute_dict_diff(old_items, new_items)

        assert result.added == []
        assert result.removed == []
        assert result.modified == []

    def test_complex_values(self):
        """Test diff with complex dictionary values."""
        old_items = {
            "a": {"nested": "value1"},
            "b": [1, 2, 3],
        }
        new_items = {
            "a": {"nested": "value2"},
            "c": {"new": "value"},
        }

        result = BaseDiff._compute_dict_diff(old_items, new_items)

        assert len(result.added) == 1
        assert len(result.removed) == 1
        assert len(result.modified) == 1
        assert result.modified[0]["old"] == {"nested": "value1"}
        assert result.modified[0]["new"] == {"nested": "value2"}

    def test_none_values(self):
        """Test diff with None values."""
        old_items = {"a": None, "b": 1}
        new_items = {"a": 1, "b": None}

        result = BaseDiff._compute_dict_diff(old_items, new_items)

        assert len(result.modified) == 2
