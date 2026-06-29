"""Authentication utilities for JWT tokens, password hashing, and user bootstrap."""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from pydantic import BaseModel

from models.data.common.roles import UserRole
from models.rest_api.auth.models import User

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class EnvBootstrapConfig(BaseModel):
    """Model for env-based admin bootstrap config."""

    admin_name: str
    admin_password: str


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed: bytes = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    result: bool = bcrypt.checkpw(password.encode(), password_hash.encode())
    return result


def create_access_token(user: User, expires_delta: timedelta | None = None) -> str:
    """Create JWT token with user info."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    to_encode = {
        "sub": str(user.user_id),
        "username": user.username,
        "role": user.role.value,
        "exp": expire,
        "iat": now,
    }
    token: str = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_token(token: str) -> User | None:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
        username = payload["username"]
        role = UserRole(payload["role"])
        return User(user_id=user_id, username=username, role=role)
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except (KeyError, ValueError) as e:
        logger.warning(f"Token missing or invalid field: {e}")
        return None


def get_env_bootstrap_config() -> EnvBootstrapConfig | None:
    """Get admin bootstrap config from environment variables.

    Returns EnvBootstrapConfig if both ADMIN_NAME and ADMIN_PASSWORD are set,
    None otherwise.
    """
    admin_name = os.getenv("ADMIN_NAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_name or not admin_password:
        return None

    return EnvBootstrapConfig(admin_name=admin_name, admin_password=admin_password)
