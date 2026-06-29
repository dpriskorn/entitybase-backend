"""Unit tests for authentication response models."""

import pytest
from pydantic import ValidationError

from models.data.rest_api.v1.entitybase.response.auth import (
    LoginResponse,
    RegisterResponse,
)
from models.data.rest_api.v1.entitybase.response.user import UserResponse
from models.data.common.roles import UserRole


class TestLoginResponse:
    """Tests for LoginResponse model."""

    def test_valid_login_response(self) -> None:
        """Test valid login response."""
        user = UserResponse(
            user_id=1,
            username="testuser",
            role=UserRole.DEFAULT,
            created_at="2024-01-01T00:00:00Z",
        )
        resp = LoginResponse(
            access_token="eyJhbGciOiJIUzI1NiIs...",
            expires_in=1800,
            user=user,
        )
        assert resp.access_token == "eyJhbGciOiJIUzI1NiIs..."
        assert resp.token_type == "bearer"
        assert resp.expires_in == 1800
        assert resp.user.user_id == 1
        assert resp.user.username == "testuser"

    def test_token_type_default(self) -> None:
        """Test token_type defaults to 'bearer'."""
        user = UserResponse(
            user_id=1,
            username="testuser",
            role=UserRole.DEFAULT,
            created_at="2024-01-01T00:00:00Z",
        )
        resp = LoginResponse(
            access_token="token",
            expires_in=1800,
            user=user,
        )
        assert resp.token_type == "bearer"

    def test_model_dump(self) -> None:
        """Test model serialization."""
        user = UserResponse(
            user_id=1,
            username="testuser",
            role=UserRole.DEFAULT,
            created_at="2024-01-01T00:00:00Z",
        )
        resp = LoginResponse(
            access_token="token123",
            expires_in=1800,
            user=user,
        )
        dumped = resp.model_dump()
        assert dumped["access_token"] == "token123"
        assert dumped["token_type"] == "bearer"
        assert dumped["expires_in"] == 1800
        assert dumped["user"]["user_id"] == 1

    def test_extra_fields_forbidden(self) -> None:
        """Test extra fields raise ValidationError."""
        user = UserResponse(
            user_id=1,
            username="testuser",
            role=UserRole.DEFAULT,
            created_at="2024-01-01T00:00:00Z",
        )
        with pytest.raises(ValidationError):
            LoginResponse(
                access_token="token",
                expires_in=1800,
                user=user,
                extra="field",
            )


class TestRegisterResponse:
    """Tests for RegisterResponse model."""

    def test_valid_register_response(self) -> None:
        """Test valid register response."""
        resp = RegisterResponse(
            user_id=42,
            username="newuser",
            role="default",
        )
        assert resp.user_id == 42
        assert resp.username == "newuser"
        assert resp.role == "default"

    def test_model_dump(self) -> None:
        """Test model serialization."""
        resp = RegisterResponse(user_id=42, username="newuser", role="admin")
        dumped = resp.model_dump()
        assert dumped["user_id"] == 42
        assert dumped["username"] == "newuser"
        assert dumped["role"] == "admin"

    def test_extra_fields_forbidden(self) -> None:
        """Test extra fields raise ValidationError."""
        with pytest.raises(ValidationError):
            RegisterResponse(
                user_id=42,
                username="newuser",
                role="default",
                extra="field",
            )
