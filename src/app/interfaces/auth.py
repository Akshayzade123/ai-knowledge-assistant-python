"""
Authentication Interface - Defines contract for auth operations.

SOLID Principles Applied:
- Single Responsibility (S): Focused only on authentication concerns
- Interface Segregation (I): Minimal, focused interface
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TokenData:
    """JWT token data."""

    access_token: str
    token_type: str
    expires_in: int


@dataclass
class AuthenticatedUser:
    """Authenticated user information."""

    user_id: int
    username: str
    role: str
    department: str | None


class IAuthProvider(ABC):
    """Interface for authentication operations."""

    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> AuthenticatedUser | None:
        """
        Authenticate user with credentials.

        Returns:
            AuthenticatedUser if valid, None otherwise
        """
        pass

    @abstractmethod
    async def create_access_token(self, user_data: AuthenticatedUser) -> TokenData:
        """Create JWT access token."""
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> AuthenticatedUser | None:
        """Verify JWT token and extract user data."""
        pass

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash password securely."""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        pass
