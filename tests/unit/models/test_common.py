"""Unit tests for common."""

import pytest
from pydantic import ValidationError

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders


class TestEditHeaders:
    """Tests for EditHeaders model."""

    def test_valid_instantiation_basic(self):
        """Test basic valid instantiation as used in the codebase."""
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")
        assert edit_headers.x_user_id == 123
        assert edit_headers.x_edit_summary == "test"

    def test_valid_instantiation_with_zero_user_id(self):
        """Test valid instantiation with minimum user_id (0)."""
        edit_headers = EditHeaders(x_user_id=0, x_edit_summary="System edit")
        assert edit_headers.x_user_id == 0
        assert edit_headers.x_edit_summary == "System edit"

    def test_valid_instantiation_large_user_id(self):
        """Test valid instantiation with large user_id."""
        edit_headers = EditHeaders(x_user_id=999999, x_edit_summary="Large user ID")
        assert edit_headers.x_user_id == 999999
        assert edit_headers.x_edit_summary == "Large user ID"

    def test_valid_instantiation_minimum_summary_length(self):
        """Test valid instantiation with minimum summary length (1 character)."""
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="x")
        assert edit_headers.x_user_id == 123
        assert edit_headers.x_edit_summary == "x"

    def test_valid_instantiation_maximum_summary_length(self):
        """Test valid instantiation with maximum summary length (200 characters)."""
        summary = "a" * 200
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary=summary)
        assert edit_headers.x_user_id == 123
        assert edit_headers.x_edit_summary == summary
        assert len(edit_headers.x_edit_summary) == 200

    def test_validation_error_negative_user_id(self):
        """Test ValidationError for negative user_id."""
        with pytest.raises(ValidationError) as exc_info:
            EditHeaders(x_user_id=-1, x_edit_summary="test")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("x_user_id",) for error in errors)
        assert any("greater than or equal to 0" in str(error) for error in errors)

    def test_validation_error_empty_summary(self):
        """Test ValidationError for empty edit summary."""
        with pytest.raises(ValidationError) as exc_info:
            EditHeaders(x_user_id=123, x_edit_summary="")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("x_edit_summary",) for error in errors)
        assert any("at least 1 character" in str(error) or "min_length" in str(error) for error in errors)

    def test_validation_error_summary_too_long(self):
        """Test ValidationError for edit summary exceeding 200 characters."""
        summary = "a" * 201
        with pytest.raises(ValidationError) as exc_info:
            EditHeaders(x_user_id=123, x_edit_summary=summary)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("x_edit_summary",) for error in errors)
        assert any("at most 200 character" in str(error) or "max_length" in str(error) for error in errors)

    def test_type_validation_user_id_float(self):
        """Test ValidationError when user_id is a float instead of int."""
        with pytest.raises(ValidationError) as exc_info:
            EditHeaders(x_user_id=123.5, x_edit_summary="test")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("x_user_id",) for error in errors)

    def test_type_validation_summary_int(self):
        """Test ValidationError when edit_summary is an int instead of str."""
        with pytest.raises(ValidationError) as exc_info:
            EditHeaders(x_user_id=123, x_edit_summary=123)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("x_edit_summary",) for error in errors)

    def test_model_dump(self):
        """Test that model_dump returns correct values."""
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")
        dumped = edit_headers.model_dump()
        assert dumped == {"x_user_id": 123, "x_edit_summary": "test"}

    def test_model_dump_by_alias(self):
        """Test that model_dump with by_alias returns HTTP header names."""
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")
        dumped = edit_headers.model_dump(by_alias=True)
        assert dumped == {"X-User-ID": 123, "X-Edit-Summary": "test"}
