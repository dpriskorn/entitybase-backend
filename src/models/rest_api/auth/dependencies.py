"""FastAPI authentication dependencies."""

import logging
from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException, status

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.common.roles import UserRole
from models.rest_api.auth.models import AuthenticatedRequest, User
from models.rest_api.auth.utils import decode_token

logger = logging.getLogger(__name__)


async def verify_auth(
    Authorization: Annotated[str | None, Header()] = None,
    X_Edit_Summary: Annotated[
        str | None, Header(alias="X-Edit-Summary", convert_underscores=False)
    ] = None,
    X_Base_Revision_ID: Annotated[
        int, Header(alias="X-Base-Revision-ID", convert_underscores=False)
    ] = 0,
) -> AuthenticatedRequest:
    """Validate Bearer JWT token and X-Edit-Summary header.

    Token format: Bearer <jwt_token>

    Returns AuthenticatedRequest containing the authenticated user and edit summary.

    Raises HTTPException 401 if token is invalid or expired.
    Raises HTTPException 422 if X-Edit-Summary is missing.
    """
    if not Authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    if not Authorization.startswith("Bearer "):
        logger.warning("Invalid Authorization header format - must start with Bearer")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = Authorization[7:]
    user = decode_token(token)

    if user is None:
        logger.warning("Failed to decode token or token invalid/expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if not X_Edit_Summary:
        logger.warning("Missing X-Edit-Summary header")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="X-Edit-Summary header is required",
        )

    logger.debug(f"User {user.username} authenticated successfully")
    return AuthenticatedRequest(
        user=user,
        edit_summary=X_Edit_Summary,
        base_revision_id=X_Base_Revision_ID,
    )


def require_role(
    *roles: UserRole,
) -> Callable[[AuthenticatedRequest], Coroutine[Any, Any, AuthenticatedRequest]]:
    """Dependency factory for role-based access control.

    Usage:
        @router.post("/admin-only")
        async def admin_endpoint(
            auth: AuthenticatedRequest = Depends(require_role(UserRole.ADMIN))
        ):
            ...
    """

    async def role_checker(
        auth: AuthenticatedRequest = Depends(verify_auth),
    ) -> AuthenticatedRequest:
        if auth.user.role not in roles:
            logger.warning(
                f"User {auth.user.username} with role {auth.user.role.value} "
                f"attempted to access endpoint requiring roles: {[r.value for r in roles]}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return auth

    return role_checker


def auth_to_edit_headers(auth: AuthenticatedRequest) -> EditHeaders:
    """Convert AuthenticatedRequest to EditHeaders for handler compatibility."""
    return EditHeaders(
        x_edit_summary=auth.edit_summary,
        x_base_revision_id=auth.base_revision_id,
    )
