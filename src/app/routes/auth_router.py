"""
Authentication Router - Handles user authentication endpoints.

SOLID Principles Applied:
- Single Responsibility (S): Only handles auth-related HTTP endpoints
- Dependency Inversion (D): Depends on AuthService interface
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.dependencies import get_auth_service
from app.interfaces.auth import AuthenticatedUser
from app.models.schemas import ErrorResponse, TokenResponse, UserInfo, UserLogin, UserRegister
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedUser:
    """
    Dependency to extract and validate current user from JWT token.

    Args:
        credentials: HTTP Bearer token
        auth_service: Authentication service

    Returns:
        AuthenticatedUser

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    user = await auth_service.verify_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def register(
    user_data: UserRegister, auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Register a new user.

    Args:
        user_data: User registration data
        auth_service: Authentication service

    Returns:
        JWT access token
    """
    try:
        # Register user
        authenticated_user = await auth_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            department=user_data.department,
        )

        # Create access token
        token_data = await auth_service.create_access_token(authenticated_user)

        logger.info(f"User {user_data.username} registered successfully")

        return TokenResponse(
            access_token=token_data.access_token,
            token_type=token_data.token_type,
            expires_in=token_data.expires_in,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed"
        ) from e


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def login(
    credentials: UserLogin, auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Authenticate user and return access token.

    Args:
        credentials: User login credentials
        auth_service: Authentication service

    Returns:
        JWT access token
    """
    try:
        # Authenticate user
        authenticated_user = await auth_service.authenticate_user(
            username=credentials.username, password=credentials.password
        )

        if not authenticated_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        token_data = await auth_service.create_access_token(authenticated_user)

        logger.info(f"User {credentials.username} logged in successfully")

        return TokenResponse(
            access_token=token_data.access_token,
            token_type=token_data.token_type,
            expires_in=token_data.expires_in,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        ) from e


@router.get("/me", response_model=UserInfo, responses={401: {"model": ErrorResponse}})
async def get_current_user_info(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserInfo:
    """
    Get current user information.

    Args:
        current_user: Authenticated user from token

    Returns:
        User information
    """
    # Note: In production, fetch full user details from repository
    return UserInfo(
        user_id=current_user.user_id,
        username=current_user.username,
        email="",  # Would fetch from repository
        role=current_user.role,
        department=current_user.department,
        created_at=datetime.now(),  # Would fetch from repository
        is_active=True,
    )
