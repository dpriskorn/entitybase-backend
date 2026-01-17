"""Tests for REST API utility functions."""

import pytest
from unittest.mock import patch

from fastapi import HTTPException

from models.rest_api.utils import raise_or_convert_to_500


class TestRaiseOrConvertTo500:
    """Tests for raise_or_convert_to_500 function."""

    def test_raise_original_exception_when_expose_true(self):
        """Test that original exception is raised when expose_original_exceptions is True."""
        with patch("models.rest_api.utils.settings") as mock_settings:
            mock_settings.expose_original_exceptions = True
            original_exception = ValueError("test error")

            with pytest.raises(ValueError, match="test error"):
                raise_or_convert_to_500(original_exception, "converted detail")

    def test_raise_http_exception_when_expose_false(self):
        """Test that HTTPException 500 is raised when expose_original_exceptions is False."""
        with patch("models.rest_api.utils.settings") as mock_settings:
            mock_settings.expose_original_exceptions = False
            original_exception = ValueError("test error")

            with pytest.raises(HTTPException) as exc_info:
                raise_or_convert_to_500(original_exception, "converted detail")

            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == "converted detail"
