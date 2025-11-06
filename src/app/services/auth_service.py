"""
Authentication Service - Handles user authentication and authorization.

SOLID Principles Applied:
- Single Responsibility (S): Only handles authentication/authorization logic
- Dependency Inversion (D): Depends on IUserRepository and IAuthProvider interfaces
- Open/Closed (O): Can be extended with new auth methods without modification
"""

import logging
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.interfaces.auth import AuthenticatedUser, IAuthProvider, TokenData
from app.interfaces.database import IUserRepository

logger = logging.getLogger(__name__)


class AuthService(IAuthProvider):
    """
    Authentication service implementing JWT-based authentication.

    This service orchestrates authentication logic while delegating
    data persistence to the repository layer.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ):
        """
        Initialize authentication service.

        Args:
            user_repository: Repository for user data access
            secret_key: Secret key for JWT signing
            algorithm: JWT algorithm
            access_token_expire_minutes: Token expiration time
        """
        self.user_repository = user_repository
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

        # Password hashing context
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        logger.info("AuthService initialized")

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, username: str, password: str) -> AuthenticatedUser | None:
        """
        Authenticate user with credentials.

        Args:
            username: Username
            password: Plain text password

        Returns:
            AuthenticatedUser if valid, None otherwise
        """
        try:
            # Retrieve user from repository
            user = await self.user_repository.get_user_by_username(username)

            if not user:
                logger.warning(f"Authentication failed: User {username} not found")
                return None

            if not user.is_active:
                logger.warning(f"Authentication failed: User {username} is inactive")
                return None

            # Verify password
            if not self.verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed: Invalid password for {username}")
                return None

            logger.info(f"User {username} authenticated successfully")

            return AuthenticatedUser(
                user_id=user.id, username=user.username, role=user.role, department=user.department
            )

        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return None

    async def create_access_token(self, user_data: AuthenticatedUser) -> TokenData:
        """
        Create JWT access token.

        Args:
            user_data: Authenticated user information

        Returns:
            TokenData with JWT token
        """
        try:
            # Create token payload
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

            payload = {
                "sub": user_data.username,
                "user_id": user_data.user_id,
                "role": user_data.role,
                "department": user_data.department,
                "exp": expire,
            }

            # Encode JWT
            access_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            logger.info(f"Created access token for user {user_data.username}")

            return TokenData(
                access_token=access_token,
                token_type="bearer",
                expires_in=self.access_token_expire_minutes * 60,
            )

        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise

    async def verify_token(self, token: str) -> AuthenticatedUser | None:
        """
        Verify JWT token and extract user data.

        Args:
            token: JWT token string

        Returns:
            AuthenticatedUser if valid, None otherwise
        """
        try:
            # Decode JWT
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            role: str = payload.get("role")
            department: str | None = payload.get("department")

            if username is None or user_id is None:
                return None

            # Verify user still exists and is active
            user = await self.user_repository.get_user_by_id(user_id)
            if not user or not user.is_active:
                return None

            return AuthenticatedUser(
                user_id=user_id, username=username, role=role, department=department
            )

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None

    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "user",
        department: str | None = None,
    ) -> AuthenticatedUser:
        """
        Register a new user.

        Args:
            username: Username
            email: Email address
            password: Plain text password
            role: User role (default: user)
            department: Optional department

        Returns:
            AuthenticatedUser for the new user

        Raises:
            ValueError: If user already exists
        """
        try:
            # Check if user exists
            existing_user = await self.user_repository.get_user_by_username(username)
            if existing_user:
                raise ValueError(f"User {username} already exists")

            # Hash password and create user
            hashed_password = self.hash_password(password)

            user = await self.user_repository.create_user(
                username=username,
                email=email,
                hashed_password=hashed_password,
                role=role,
                department=department,
            )

            logger.info(f"Registered new user: {username}")

            return AuthenticatedUser(
                user_id=user.id, username=user.username, role=user.role, department=user.department
            )

        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise

    def check_permission(self, user: AuthenticatedUser, required_role: str) -> bool:
        """
        Check if user has required role.

        Args:
            user: Authenticated user
            required_role: Required role (admin, user, viewer)

        Returns:
            True if user has permission
        """
        role_hierarchy = {"admin": 3, "user": 2, "viewer": 1}

        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level
