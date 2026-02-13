"""Tests for models.rest_api.utils module."""

import pytest
from fastapi import HTTPException


class TestRaiseValidationError:
    """Test suite for the raise_validation_error function."""

    def test_raises_http_exception_in_prod_environment(self, monkeypatch):
        """Test that HTTPException is raised in production environment."""
        from models.rest_api.utils import raise_validation_error

        monkeypatch.setenv("ENVIRONMENT", "prod")

        message = "Test validation error"
        status_code = 422

        with pytest.raises(HTTPException) as exc_info:
            raise_validation_error(message, status_code=status_code)

        assert exc_info.value.status_code == status_code
        assert exc_info.value.detail == message

    def test_default_status_code_is_400(self, monkeypatch):
        """Test that default status code is 400."""
        from models.rest_api.utils import raise_validation_error

        monkeypatch.setenv("ENVIRONMENT", "prod")

        message = "Test validation error"

        with pytest.raises(HTTPException) as exc_info:
            raise_validation_error(message)

        assert exc_info.value.status_code == 400

    def test_case_insensitive_environment_check(self, monkeypatch):
        """Test that environment check is case-insensitive."""
        from models.rest_api.utils import raise_validation_error

        monkeypatch.setenv("ENVIRONMENT", "PROD")

        with pytest.raises(HTTPException):
            raise_validation_error("test")

        monkeypatch.setenv("ENVIRONMENT", "Prod")

        with pytest.raises(HTTPException):
            raise_validation_error("test")

        monkeypatch.setenv("ENVIRONMENT", "PROD")

        with pytest.raises(HTTPException):
            raise_validation_error("test")
