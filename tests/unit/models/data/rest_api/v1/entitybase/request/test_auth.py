"""Unit tests for authentication request models."""

import pytest
from pydantic import ValidationError

from models.data.rest_api.v1.entitybase.request.auth import (
    LoginRequest,
    RegisterRequest,
)


class TestLoginRequest:
    """Tests for LoginRequest model."""

    def test_valid_login(self) -> None:
        """Test valid login request."""
        req = LoginRequest(username="testuser", password="secret123")
        assert req.username == "testuser"
        assert req.password == "secret123"

    def test_empty_username_fails(self) -> None:
        """Test empty username raises ValidationError."""
        with pytest.raises(ValidationError):
            LoginRequest(username="", password="secret123")

    def test_empty_password_fails(self) -> None:
        """Test empty password raises ValidationError."""
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser", password="")

    def test_extra_fields_forbidden(self) -> None:
        """Test extra fields raise ValidationError."""
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser", password="secret123", extra="field")


class TestRegisterRequest:
    """Tests for RegisterRequest model."""

    def test_valid_register(self) -> None:
        """Test valid register request."""
        req = RegisterRequest(username="newuser", password="password123")
        assert req.username == "newuser"
        assert req.password == "password123"

    def test_username_too_short_fails(self) -> None:
        """Test username shorter than 3 chars fails."""
        with pytest.raises(ValidationError):
            RegisterRequest(username="ab", password="password123")

    def test_username_min_length(self) -> None:
        """Test username exactly 3 chars works."""
        req = RegisterRequest(username="abc", password="password123")
        assert req.username == "abc"

    def test_username_max_length(self) -> None:
        """Test username at max 50 chars works."""
        long_name = "a" * 50
        req = RegisterRequest(username=long_name, password="password123")
        assert req.username == long_name

    def test_username_too_long_fails(self) -> None:
        """Test username longer than 50 chars fails."""
        with pytest.raises(ValidationError):
            RegisterRequest(username="a" * 51, password="password123")

    def test_password_too_short_fails(self) -> None:
        """Test password shorter than 8 chars fails."""
        with pytest.raises(ValidationError):
            RegisterRequest(username="newuser", password="1234567")

    def test_password_min_length(self) -> None:
        """Test password exactly 8 chars works."""
        req = RegisterRequest(username="newuser", password="12345678")
        assert req.password == "12345678"

    def test_extra_fields_forbidden(self) -> None:
        """Test extra fields raise ValidationError."""
        with pytest.raises(ValidationError):
            RegisterRequest(
                username="newuser", password="password123", email="test@test.com"
            )
