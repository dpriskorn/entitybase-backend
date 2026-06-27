"""Authentication routes for login, register, and user management."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from models.data.common.roles import UserRole
from models.data.rest_api.v1.entitybase.request.auth import LoginRequest, RegisterRequest
from models.data.rest_api.v1.entitybase.response.auth import LoginResponse, RegisterResponse
from models.rest_api.auth import (
    AuthenticatedRequest,
    create_access_token,
    hash_password,
    require_role,
    verify_auth,
    verify_password,
)
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)

auth_router = APIRouter(tags=["authentication"])


def get_user_repository(state):
    """Get user repository from app state."""
    if not hasattr(state, "vitess_client") or not state.vitess_client:
        raise_validation_error("Database not available", status_code=503)
    return state.vitess_client.user_repository


@auth_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request) -> LoginResponse:
    """Authenticate user and return JWT token."""
    logger.debug(f"Login attempt for user: {request.username}")

    state = req.app.state.state_handler
    user_repo = get_user_repository(state)

    success, user = user_repo.verify_user_credentials(request.username, request.password)

    if not success or user is None:
        logger.warning(f"Failed login attempt for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    from models.rest_api.auth.models import User

    auth_user = User(
        user_id=user.user_id,
        username=user.username,
        role=user.role,
    )

    access_token = create_access_token(auth_user)

    logger.info(f"User {user.username} logged in successfully")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800,
        user=user,
    )


@auth_router.post("/auth/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    req: Request,
    auth: AuthenticatedRequest = Depends(require_role(UserRole.ADMIN)),
) -> RegisterResponse:
    """Register a new user. Admin only.

    New users get the 'default' role by default.
    """
    logger.debug(f"Admin {auth.user.username} registering new user: {request.username}")

    state = req.app.state.state_handler
    user_repo = get_user_repository(state)

    if user_repo.user_exists_by_username(request.username):
        raise_validation_error("Username already exists", status_code=409)

    password_hash = hash_password(request.password)

    result = user_repo.create_user_with_password(
        username=request.username,
        password_hash=password_hash,
        role=UserRole.DEFAULT.value,
    )

    if not result.success:
        logger.error(f"Failed to create user: {result.error}")
        raise_validation_error(result.error or "Failed to create user", status_code=400)

    data = result.data
    logger.info(f"Admin {auth.user.username} created user: {request.username}")

    return RegisterResponse(
        user_id=data["user_id"],
        username=data["username"],
        role=UserRole.DEFAULT.value,
    )


@auth_router.delete("/auth/users/{user_id}")
async def delete_user(
    user_id: int,
    req: Request,
    auth: AuthenticatedRequest = Depends(verify_auth),
) -> None:
    """Delete a user.

    Admins can delete any user. Users can delete themselves.
    """
    logger.debug(f"Delete user request: user_id={user_id}, auth user={auth.user.user_id}")

    if auth.user.user_id != user_id and auth.user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete your own account",
        )

    state = req.app.state.state_handler
    user_repo = get_user_repository(state)

    if not user_repo.user_exists(user_id):
        raise_validation_error("User not found", status_code=404)

    if user_id == auth.user.user_id and auth.user.role == UserRole.ADMIN:
        raise_validation_error(
            "Admins cannot delete themselves via this endpoint",
            status_code=400,
        )

    result = user_repo.delete_user(user_id)

    if not result.success:
        logger.error(f"Failed to delete user: {result.error}")
        raise_validation_error(result.error or "Failed to delete user", status_code=400)

    logger.info(f"User {auth.user.username} deleted user_id={user_id}")
