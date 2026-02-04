"""Unit tests for EditHeaders model."""

import pytest

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from pydantic import ValidationError


class TestEditHeaders:
    """Unit tests for EditHeaders."""

    def test_basic_instantiation(self):
        """Test basic instantiation with snake_case fields."""
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")
        assert edit_headers.x_user_id == 123
        assert edit_headers.x_edit_summary == "test"

    def test_minimum_user_id(self):
        """Test minimum user_id (0) works."""
        edit_headers = EditHeaders(x_user_id=0, x_edit_summary="System")
        assert edit_headers.x_user_id == 0
        assert edit_headers.x_edit_summary == "System"

    def test_negative_user_id_fails(self):
        """Test negative user_id raises ValidationError."""
        with pytest.raises(ValidationError):
            EditHeaders(x_user_id=-1, x_edit_summary="test")

    def test_empty_summary_fails(self):
        """Test empty summary raises ValidationError."""
        with pytest.raises(ValidationError):
            EditHeaders(x_user_id=123, x_edit_summary="")

    def test_minimum_summary_length(self):
        """Test minimum summary length (1 char) works."""
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="x")
        assert edit_headers.x_edit_summary == "x"

    def test_maximum_summary_length(self):
        """Test maximum summary length (200 chars) works."""
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="a" * 200)
        assert edit_headers.x_edit_summary == "a" * 200

    def test_too_long_summary_fails(self):
        """Test too long summary (201+ chars) raises ValidationError."""
        with pytest.raises(ValidationError):
            EditHeaders(x_user_id=123, x_edit_summary="a" * 201)

    def test_alias_instantiation(self):
        """Test instantiation using kebab-case aliases."""
        edit_headers = EditHeaders(X_User_ID=999, X_Edit_Summary="Alias test")
        assert edit_headers.x_user_id == 999
        assert edit_headers.x_edit_summary == "Alias test"

    def test_model_dump(self):
        """Test model_dump() works correctly."""
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")
        dumped = edit_headers.model_dump()
        assert dumped == {"x_user_id": 123, "x_edit_summary": "test"}

    def test_model_dump_by_alias(self):
        """Test model_dump(by_alias=True) works correctly."""
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="test")
        dumped = edit_headers.model_dump(by_alias=True)
        assert dumped == {"X-User-ID": 123, "X-Edit-Summary": "test"}
