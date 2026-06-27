"""Unit tests for auth internal models."""

import pytest
from pydantic import ValidationError

from models.data.common.roles import UserRole
from models.rest_api.auth.models import User, AuthenticatedRequest


class TestUser:
    """Tests for internal User model."""

    def test_valid_user(self) -> None:
        """Test valid user creation."""
        user = User(user_id=1, username="testuser", role=UserRole.ADMIN)
        assert user.user_id == 1
        assert user.username == "testuser"
        assert user.role == UserRole.ADMIN

    def test_default_user_role(self) -> None:
        """Test user with default role."""
        user = User(user_id=2, username="regular", role=UserRole.DEFAULT)
        assert user.role == UserRole.DEFAULT

    def test_extra_fields_forbidden(self) -> None:
        """Test extra fields raise ValidationError."""
        with pytest.raises(ValidationError):
            User(user_id=1, username="test", role=UserRole.ADMIN, email="x@x.com")


class TestAuthenticatedRequest:
    """Tests for AuthenticatedRequest model."""

    def test_valid_request(self) -> None:
        """Test valid authenticated request."""
        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        req = AuthenticatedRequest(user=user, edit_summary="test edit")
        assert req.user.user_id == 1
        assert req.edit_summary == "test edit"
        assert req.base_revision_id == 0

    def test_with_base_revision_id(self) -> None:
        """Test with explicit base revision ID."""
        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        req = AuthenticatedRequest(user=user, edit_summary="test", base_revision_id=42)
        assert req.base_revision_id == 42

    def test_empty_edit_summary_fails(self) -> None:
        """Test empty edit summary raises ValidationError."""
        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        with pytest.raises(ValidationError):
            AuthenticatedRequest(user=user, edit_summary="")

    def test_edit_summary_too_long_fails(self) -> None:
        """Test edit summary over 200 chars raises ValidationError."""
        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        with pytest.raises(ValidationError):
            AuthenticatedRequest(user=user, edit_summary="a" * 201)

    def test_extra_fields_forbidden(self) -> None:
        """Test extra fields raise ValidationError."""
        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        with pytest.raises(ValidationError):
            AuthenticatedRequest(user=user, edit_summary="test", extra="field")
