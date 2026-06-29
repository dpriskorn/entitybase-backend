"""Authentication module for Entitybase API."""

from models.rest_api.auth.dependencies import (
    auth_to_edit_headers,
    require_role,
    verify_auth,
)
from models.rest_api.auth.models import AuthenticatedRequest, User
from models.rest_api.auth.utils import (
    create_access_token,
    decode_token,
    get_env_bootstrap_config,
    hash_password,
    verify_password,
)

__all__ = [
    "AuthenticatedRequest",
    "User",
    "auth_to_edit_headers",
    "create_access_token",
    "decode_token",
    "get_env_bootstrap_config",
    "hash_password",
    "require_role",
    "verify_auth",
    "verify_password",
]
