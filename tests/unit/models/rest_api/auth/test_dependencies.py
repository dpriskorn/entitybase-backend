"""Unit tests for auth FastAPI dependencies.

These tests use FastAPI TestClient to create minimal app instances
that exercise the verify_auth, require_role, and auth_to_edit_headers
dependencies.
"""

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from models.data.common.roles import UserRole
from models.rest_api.auth.dependencies import (
    verify_auth,
    require_role,
    auth_to_edit_headers,
)
from models.rest_api.auth.models import AuthenticatedRequest, User
from models.rest_api.auth.utils import create_access_token


def _make_token(
    user_id: int = 1, username: str = "testuser", role: UserRole = UserRole.DEFAULT
) -> str:
    """Helper to create a JWT token for testing."""
    user = User(user_id=user_id, username=username, role=role)
    return create_access_token(user)


class TestVerifyAuth:
    """Tests for the verify_auth dependency."""

    def _make_app(self) -> FastAPI:
        """Create a minimal app with a protected endpoint."""
        app_ = FastAPI()

        @app_.get("/protected")
        async def protected(auth: AuthenticatedRequest = Depends(verify_auth)):
            return {
                "user_id": auth.user.user_id,
                "username": auth.user.username,
                "role": auth.user.role.value,
                "edit_summary": auth.edit_summary,
                "base_revision_id": auth.base_revision_id,
            }

        return app_

    def test_valid_auth(self) -> None:
        """Test valid auth returns AuthenticatedRequest."""
        app_ = self._make_app()
        token = _make_token(user_id=42, username="alice", role=UserRole.ADMIN)
        client = TestClient(app_)
        response = client.get(
            "/protected",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Edit-Summary": "test edit",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 42
        assert data["username"] == "alice"
        assert data["role"] == "admin"
        assert data["edit_summary"] == "test edit"

    def test_missing_authorization_header(self) -> None:
        """Test missing Authorization header returns 401."""
        app_ = self._make_app()
        client = TestClient(app_)
        response = client.get(
            "/protected",
            headers={"X-Edit-Summary": "test"},
        )
        assert response.status_code == 401
        assert "Missing authorization header" in response.text

    def test_invalid_bearer_format(self) -> None:
        """Test Authorization header without Bearer prefix returns 401."""
        app_ = self._make_app()
        client = TestClient(app_)
        response = client.get(
            "/protected",
            headers={
                "Authorization": "Token mytoken",
                "X-Edit-Summary": "test",
            },
        )
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.text

    def test_invalid_token(self) -> None:
        """Test invalid JWT returns 401."""
        app_ = self._make_app()
        client = TestClient(app_)
        response = client.get(
            "/protected",
            headers={
                "Authorization": "Bearer invalid.jwt.token",
                "X-Edit-Summary": "test",
            },
        )
        assert response.status_code == 401
        assert "Invalid or expired token" in response.text

    def test_missing_edit_summary(self) -> None:
        """Test missing X-Edit-Summary returns 422."""
        app_ = self._make_app()
        token = _make_token()
        client = TestClient(app_)
        response = client.get(
            "/protected",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
        assert response.status_code == 422
        assert "X-Edit-Summary" in response.text

    def test_base_revision_id_default(self) -> None:
        """Test base_revision_id defaults to 0 when not provided."""
        app_ = self._make_app()
        token = _make_token()
        client = TestClient(app_)
        response = client.get(
            "/protected",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Edit-Summary": "test",
            },
        )
        assert response.status_code == 200
        assert response.json()["base_revision_id"] == 0

    def test_custom_base_revision_id(self) -> None:
        """Test custom X-Base-Revision-ID is passed through."""
        app_ = self._make_app()
        token = _make_token()
        client = TestClient(app_)
        response = client.get(
            "/protected",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Edit-Summary": "test",
                "X-Base-Revision-ID": "99",
            },
        )
        assert response.status_code == 200
        assert response.json()["base_revision_id"] == 99


class TestRequireRole:
    """Tests for the require_role dependency factory."""

    def _make_app(self, *roles: UserRole) -> FastAPI:
        """Create a minimal app with role-guarded endpoint."""
        app_ = FastAPI()

        @app_.get("/admin-only")
        async def admin_endpoint(
            auth: AuthenticatedRequest = Depends(require_role(*roles)),
        ):
            return {
                "user_id": auth.user.user_id,
                "role": auth.user.role.value,
            }

        return app_

    def test_admin_allowed(self) -> None:
        """Test admin user is allowed for ADMIN role."""
        app_ = self._make_app(UserRole.ADMIN)
        token = _make_token(role=UserRole.ADMIN)
        client = TestClient(app_)
        response = client.get(
            "/admin-only",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Edit-Summary": "admin action",
            },
        )
        assert response.status_code == 200
        assert response.json()["role"] == "admin"

    def test_default_user_forbidden_from_admin(self) -> None:
        """Test default user is forbidden from ADMIN-only endpoint."""
        app_ = self._make_app(UserRole.ADMIN)
        token = _make_token(role=UserRole.DEFAULT)
        client = TestClient(app_)
        response = client.get(
            "/admin-only",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Edit-Summary": "user action",
            },
        )
        assert response.status_code == 403
        assert "Insufficient permissions" in response.text

    def test_multiple_allowed_roles(self) -> None:
        """Test user with one of multiple allowed roles passes."""
        app_ = self._make_app(UserRole.ADMIN, UserRole.DEFAULT)
        token = _make_token(role=UserRole.DEFAULT)
        client = TestClient(app_)
        response = client.get(
            "/admin-only",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Edit-Summary": "user action",
            },
        )
        assert response.status_code == 200
        assert response.json()["role"] == "default"

    def test_no_token_returns_401_before_role_check(self) -> None:
        """Test missing auth returns 401 before role check."""
        app_ = self._make_app(UserRole.ADMIN)
        client = TestClient(app_)
        response = client.get(
            "/admin-only",
            headers={"X-Edit-Summary": "test"},
        )
        assert response.status_code == 401


class TestAuthToEditHeaders:
    """Tests for auth_to_edit_headers utility function."""

    def test_converts_auth_to_edit_headers(self) -> None:
        """Test conversion includes edit_summary and base_revision_id."""
        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        auth = AuthenticatedRequest(
            user=user, edit_summary="my edit", base_revision_id=42
        )
        headers = auth_to_edit_headers(auth)
        assert headers.x_edit_summary == "my edit"
        assert headers.x_base_revision_id == 42

    def test_converts_with_default_revision_id(self) -> None:
        """Test conversion with default base_revision_id."""
        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        auth = AuthenticatedRequest(user=user, edit_summary="edit")
        headers = auth_to_edit_headers(auth)
        assert headers.x_edit_summary == "edit"
        assert headers.x_base_revision_id == 0
