"""Unit tests for authentication routes."""

from unittest.mock import MagicMock, PropertyMock
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from models.data.rest_api.v1.entitybase.response.user import UserResponse
from models.data.common.roles import UserRole
from models.rest_api.auth.models import User
from models.rest_api.auth.utils import create_access_token


@pytest.fixture
def mock_user_repo():
    """Fixture that creates a mock user repository and sets up app state."""
    from models.rest_api.main import app

    user_repo = MagicMock()
    mysql_client = MagicMock()
    type(mysql_client).user_repository = PropertyMock(return_value=user_repo)
    state_handler = MagicMock()
    type(state_handler).mysql_client = PropertyMock(return_value=mysql_client)
    app.state.state_handler = state_handler
    yield user_repo
    app.state.state_handler = None


@pytest.fixture
def admin_token():
    """Fixture that creates a valid admin JWT token."""
    user = User(user_id=1, username="admin", role=UserRole.ADMIN)
    return create_access_token(user)


@pytest.fixture
def default_user_token():
    """Fixture that creates a valid default user JWT token."""
    user = User(user_id=2, username="regular", role=UserRole.DEFAULT)
    return create_access_token(user)


class TestLoginEndpoint:
    """Tests for POST /v1/auth/login."""

    API_PREFIX = "/v1"

    def _user_response(self) -> UserResponse:
        return UserResponse(
            user_id=42,
            username="testuser",
            role=UserRole.DEFAULT,
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            preferences=None,
        )

    def test_login_success(self, mock_user_repo) -> None:
        """Test successful login returns token."""
        from models.rest_api.main import app

        mock_user_repo.verify_user_credentials.return_value = (
            True,
            self._user_response(),
        )
        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/login",
            json={"username": "testuser", "password": "correct_password"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
        assert data["user"]["user_id"] == 42
        assert data["user"]["username"] == "testuser"
        mock_user_repo.verify_user_credentials.assert_called_once_with(
            "testuser", "correct_password"
        )

    def test_login_invalid_credentials(self, mock_user_repo) -> None:
        """Test login with invalid credentials returns 401."""
        from models.rest_api.main import app

        mock_user_repo.verify_user_credentials.return_value = (False, None)
        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/login",
            json={"username": "testuser", "password": "wrong_password"},
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.text

    def test_login_empty_username_fails(self, mock_user_repo) -> None:
        """Test login with empty username returns 422."""
        from models.rest_api.main import app

        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/login",
            json={"username": "", "password": "password"},
        )
        assert response.status_code == 422

    def test_login_empty_password_fails(self, mock_user_repo) -> None:
        """Test login with empty password returns 422."""
        from models.rest_api.main import app

        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/login",
            json={"username": "testuser", "password": ""},
        )
        assert response.status_code == 422

    def test_login_database_unavailable(self, mock_user_repo) -> None:
        """Test login when DB is unavailable returns 503."""
        from models.rest_api.main import app

        app.state.state_handler = MagicMock(spec=[])
        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/login",
            json={"username": "testuser", "password": "password"},
        )
        assert response.status_code == 503
        app.state.state_handler = None


class TestRegisterEndpoint:
    """Tests for POST /v1/auth/register."""

    API_PREFIX = "/v1"

    def test_register_success(self, mock_user_repo, admin_token) -> None:
        """Test successful registration by admin."""
        from models.rest_api.main import app

        mock_user_repo.user_exists_by_username.return_value = False
        result_mock = MagicMock(
            spec=["success", "data", "get_data"],
            success=True,
            data={"user_id": 100, "username": "newuser"},
        )
        result_mock.get_data.return_value = {"user_id": 100, "username": "newuser"}
        mock_user_repo.create_user_with_password.return_value = result_mock
        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/register",
            json={"username": "newuser", "password": "password123"},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Edit-Summary": "admin register",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 100
        assert data["username"] == "newuser"
        assert data["role"] == "default"
        mock_user_repo.create_user_with_password.assert_called_once()

    def test_register_non_admin_forbidden(
        self, mock_user_repo, default_user_token
    ) -> None:
        """Test non-admin user receives 403."""
        from models.rest_api.main import app

        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/register",
            json={"username": "newuser", "password": "password123"},
            headers={
                "Authorization": f"Bearer {default_user_token}",
                "X-Edit-Summary": "user register",
            },
        )
        assert response.status_code == 403

    def test_register_duplicate_username(self, mock_user_repo, admin_token) -> None:
        """Test registering existing username returns 409."""
        from models.rest_api.main import app

        mock_user_repo.user_exists_by_username.return_value = True
        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/register",
            json={"username": "existing", "password": "password123"},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Edit-Summary": "admin register",
            },
        )
        assert response.status_code == 409
        assert "Username already exists" in response.text

    def test_register_missing_auth_header(self, mock_user_repo) -> None:
        """Test register without auth returns 401."""
        from models.rest_api.main import app

        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/register",
            json={"username": "newuser", "password": "password123"},
        )
        assert response.status_code == 401

    def test_register_username_too_short(self, mock_user_repo, admin_token) -> None:
        """Test register with too short username returns 422."""
        from models.rest_api.main import app

        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/register",
            json={"username": "ab", "password": "password123"},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Edit-Summary": "admin register",
            },
        )
        assert response.status_code == 422

    def test_register_password_too_short(self, mock_user_repo, admin_token) -> None:
        """Test register with too short password returns 422."""
        from models.rest_api.main import app

        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/register",
            json={"username": "newuser", "password": "short"},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Edit-Summary": "admin register",
            },
        )
        assert response.status_code == 422

    def test_register_creation_fails(self, mock_user_repo, admin_token) -> None:
        """Test register when user creation fails returns 400."""
        from models.rest_api.main import app

        mock_user_repo.user_exists_by_username.return_value = False
        mock_user_repo.create_user_with_password.return_value = MagicMock(
            success=False, error="Database error"
        )
        client = TestClient(app)
        response = client.post(
            f"{self.API_PREFIX}/auth/register",
            json={"username": "newuser", "password": "password123"},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Edit-Summary": "admin register",
            },
        )
        assert response.status_code == 400


class TestDeleteUserEndpoint:
    """Tests for DELETE /v1/auth/users/{user_id}."""

    API_PREFIX = "/v1"

    def test_delete_self(self, mock_user_repo, default_user_token) -> None:
        """Test user can delete themselves."""
        from models.rest_api.main import app

        mock_user_repo.user_exists.return_value = True
        mock_user_repo.delete_user.return_value = MagicMock(success=True)
        client = TestClient(app)
        response = client.delete(
            f"{self.API_PREFIX}/auth/users/2",
            headers={
                "Authorization": f"Bearer {default_user_token}",
                "X-Edit-Summary": "delete self",
            },
        )
        assert response.status_code == 200
        mock_user_repo.delete_user.assert_called_once_with(2)

    def test_admin_deletes_other_user(self, mock_user_repo, admin_token) -> None:
        """Test admin can delete another user."""
        from models.rest_api.main import app

        mock_user_repo.user_exists.return_value = True
        mock_user_repo.delete_user.return_value = MagicMock(success=True)
        client = TestClient(app)
        response = client.delete(
            f"{self.API_PREFIX}/auth/users/99",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Edit-Summary": "admin delete",
            },
        )
        assert response.status_code == 200
        mock_user_repo.delete_user.assert_called_once_with(99)

    def test_delete_other_user_forbidden(
        self, mock_user_repo, default_user_token
    ) -> None:
        """Test non-admin user cannot delete another user."""
        from models.rest_api.main import app

        client = TestClient(app)
        response = client.delete(
            f"{self.API_PREFIX}/auth/users/99",
            headers={
                "Authorization": f"Bearer {default_user_token}",
                "X-Edit-Summary": "delete other",
            },
        )
        assert response.status_code == 403

    def test_delete_nonexistent_user(self, mock_user_repo, default_user_token) -> None:
        """Test non-admin deleting other user returns 403 (not owner)."""
        from models.rest_api.main import app

        client = TestClient(app)
        response = client.delete(
            f"{self.API_PREFIX}/auth/users/999",
            headers={
                "Authorization": f"Bearer {default_user_token}",
                "X-Edit-Summary": "delete nonexistent",
            },
        )
        assert response.status_code == 403

    def test_admin_cannot_delete_self(self, mock_user_repo, admin_token) -> None:
        """Test admin cannot delete themselves via this endpoint."""
        from models.rest_api.main import app

        mock_user_repo.user_exists.return_value = True
        client = TestClient(app)
        response = client.delete(
            f"{self.API_PREFIX}/auth/users/1",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Edit-Summary": "admin delete self",
            },
        )
        assert response.status_code == 400
        assert "Admins cannot delete themselves" in response.text

    def test_delete_missing_auth(self, mock_user_repo) -> None:
        """Test delete without auth returns 401."""
        from models.rest_api.main import app

        client = TestClient(app)
        response = client.delete(
            f"{self.API_PREFIX}/auth/users/1",
        )
        assert response.status_code == 401

    def test_delete_user_not_found(self, mock_user_repo, default_user_token) -> None:
        """Test delete when user_repo lookup fails."""
        from models.rest_api.main import app

        mock_user_repo.user_exists.return_value = True
        mock_user_repo.delete_user.return_value = MagicMock(
            success=False, error="User not found"
        )
        client = TestClient(app)
        response = client.delete(
            f"{self.API_PREFIX}/auth/users/2",
            headers={
                "Authorization": f"Bearer {default_user_token}",
                "X-Edit-Summary": "delete self",
            },
        )
        assert response.status_code == 400
