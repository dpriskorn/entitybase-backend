"""Unit tests for S3 load response models."""

import pytest

from models.data.infrastructure.s3.load_response import (
    DictLoadResponse,
    LoadResponse,
    StringLoadResponse,
)


class TestStringLoadResponse:
    """Unit tests for StringLoadResponse model."""

    def test_with_string_data(self):
        """Test with string data."""
        response = StringLoadResponse(data="test string")
        assert response.data == "test string"

    def test_model_dump(self):
        """Test model_dump()."""
        response = StringLoadResponse(data="test")
        dumped = response.model_dump()
        assert dumped == {"data": "test"}

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        response = StringLoadResponse(data="test")
        json_str = response.model_dump_json()
        assert "test" in json_str


class TestDictLoadResponse:
    """Unit tests for DictLoadResponse model."""

    def test_with_dict_data(self):
        """Test with dict data."""
        response = DictLoadResponse(data={"key": "value"})
        assert response.data == {"key": "value"}

    def test_model_dump(self):
        """Test model_dump()."""
        response = DictLoadResponse(data={"key": "value"})
        dumped = response.model_dump()
        assert dumped == {"data": {"key": "value"}}

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        response = DictLoadResponse(data={"key": "value"})
        json_str = response.model_dump_json()
        assert "key" in json_str


class TestLoadResponse:
    """Unit tests for LoadResponse type alias."""

    def test_string_load_response_type(self):
        """Test LoadResponse with StringLoadResponse."""
        response: LoadResponse = StringLoadResponse(data="test")
        assert isinstance(response, StringLoadResponse)

    def test_dict_load_response_type(self):
        """Test LoadResponse with DictLoadResponse."""
        response: LoadResponse = DictLoadResponse(data={"key": "value"})
        assert isinstance(response, DictLoadResponse)
