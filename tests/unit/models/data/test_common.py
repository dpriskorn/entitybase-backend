"""Unit tests for data/common.py."""

import pytest

from models.data.common import OperationResult


class TestOperationResult:
    """Unit tests for OperationResult model."""

    def test_success_with_data(self):
        """Test successful operation result with data."""
        result = OperationResult(success=True, data=42)

        assert result.success is True
        assert result.error == ""
        assert result.data == 42

    def test_failure_with_error(self):
        """Test failed operation result with error message."""
        result = OperationResult(success=False, error="Something went wrong")

        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.data is None

    def test_get_data_returns_value(self):
        """Test get_data returns the stored data."""
        result = OperationResult(success=True, data=[1, 2, 3])

        assert result.get_data() == [1, 2, 3]

    def test_get_data_raises_on_none(self):
        """Test get_data raises ValueError when data is None."""
        result = OperationResult(success=False, error="Not found")

        with pytest.raises(ValueError, match="Data is None"):
            result.get_data()

    def test_extra_fields_forbidden(self):
        """Test that extra fields are not allowed."""
        with pytest.raises(ValueError):
            OperationResult(success=True, extra_field="not allowed")
