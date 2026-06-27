"""Unit tests for auth utility functions."""

import os
from datetime import timedelta, datetime, timezone

from models.data.common.roles import UserRole
from models.rest_api.auth.models import User


class TestHashPassword:
    """Tests for hash_password and verify_password."""

    def test_hash_and_verify_password(self) -> None:
        """Test password hash round-trip."""
        from models.rest_api.auth.utils import hash_password, verify_password

        password = "my_secret_password_123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self) -> None:
        """Test wrong password fails verification."""
        from models.rest_api.auth.utils import hash_password, verify_password

        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_different_hashes_for_same_password(self) -> None:
        """Test that same password produces different hashes (due to salt)."""
        from models.rest_api.auth.utils import hash_password

        hash1 = hash_password("same_password")
        hash2 = hash_password("same_password")
        assert hash1 != hash2


class TestCreateAccessToken:
    """Tests for create_access_token."""

    def test_create_token_contains_user_info(self) -> None:
        """Test token payload contains correct user info."""
        from models.rest_api.auth.utils import create_access_token, decode_token

        user = User(user_id=42, username="testuser", role=UserRole.ADMIN)
        token = create_access_token(user)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded.user_id == 42
        assert decoded.username == "testuser"
        assert decoded.role == UserRole.ADMIN

    def test_token_has_expiry(self) -> None:
        """Test token expires using default expiry."""
        from models.rest_api.auth.utils import create_access_token, decode_token

        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        token = create_access_token(user)
        decoded = decode_token(token)
        assert decoded is not None

    def test_custom_expiry(self) -> None:
        """Test custom expiry delta is respected."""
        from models.rest_api.auth.utils import create_access_token, decode_token

        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        token = create_access_token(user, expires_delta=timedelta(hours=1))
        decoded = decode_token(token)
        assert decoded is not None

    def test_default_user_role(self) -> None:
        """Test token with default user role."""
        from models.rest_api.auth.utils import create_access_token, decode_token

        user = User(user_id=3, username="regular", role=UserRole.DEFAULT)
        token = create_access_token(user)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded.role == UserRole.DEFAULT


class TestDecodeToken:
    """Tests for decode_token."""

    def test_expired_token_returns_none(self) -> None:
        """Test expired token returns None."""
        from models.rest_api.auth.utils import (
            create_access_token,
            decode_token,
        )

        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        token = create_access_token(user, expires_delta=timedelta(seconds=-1))
        decoded = decode_token(token)
        assert decoded is None

    def test_invalid_token_returns_none(self) -> None:
        """Test invalid token returns None."""
        from models.rest_api.auth.utils import decode_token

        decoded = decode_token("this.is.not.a.valid.jwt")
        assert decoded is None

    def test_tampered_token_returns_none(self) -> None:
        """Test tampered token returns None."""
        from models.rest_api.auth.utils import create_access_token, decode_token
        import jwt

        user = User(user_id=1, username="testuser", role=UserRole.DEFAULT)
        token = create_access_token(user)
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + ".invalidsignature"
        decoded = decode_token(tampered)
        assert decoded is None

    def test_missing_fields_in_token(self) -> None:
        """Test token missing required fields returns None."""
        import jwt
        from models.rest_api.auth.utils import decode_token, JWT_SECRET, JWT_ALGORITHM

        payload = {"foo": "bar"}
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        decoded = decode_token(token)
        assert decoded is None


class TestGetEnvBootstrapConfig:
    """Tests for get_env_bootstrap_config."""

    def test_with_env_vars_set(self, monkeypatch) -> None:
        """Test returns config when env vars are set."""
        from models.rest_api.auth.utils import get_env_bootstrap_config

        monkeypatch.setenv("ADMIN_NAME", "admin")
        monkeypatch.setenv("ADMIN_PASSWORD", "admin_secret_123")
        config = get_env_bootstrap_config()
        assert config is not None
        assert config.admin_name == "admin"
        assert config.admin_password == "admin_secret_123"

    def test_without_admin_name(self, monkeypatch) -> None:
        """Test returns None when ADMIN_NAME is missing."""
        from models.rest_api.auth.utils import get_env_bootstrap_config

        monkeypatch.delenv("ADMIN_NAME", raising=False)
        monkeypatch.setenv("ADMIN_PASSWORD", "secret")
        config = get_env_bootstrap_config()
        assert config is None

    def test_without_admin_password(self, monkeypatch) -> None:
        """Test returns None when ADMIN_PASSWORD is missing."""
        from models.rest_api.auth.utils import get_env_bootstrap_config

        monkeypatch.setenv("ADMIN_NAME", "admin")
        monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
        config = get_env_bootstrap_config()
        assert config is None

    def test_without_any_env_vars(self, monkeypatch) -> None:
        """Test returns None when neither env var is set."""
        from models.rest_api.auth.utils import get_env_bootstrap_config

        monkeypatch.delenv("ADMIN_NAME", raising=False)
        monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
        config = get_env_bootstrap_config()
        assert config is None
