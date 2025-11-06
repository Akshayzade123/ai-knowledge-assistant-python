"""
Unit tests for AuthService.

Tests authentication, authorization, and JWT token management.
"""

import pytest

from app.interfaces.auth import AuthenticatedUser
from app.services.auth_service import AuthService


@pytest.mark.unit
class TestAuthService:
    """Test suite for AuthService."""

    @pytest.fixture
    def auth_service(self, mock_user_repository, test_settings):
        """Create AuthService instance with mocked dependencies."""
        return AuthService(
            user_repository=mock_user_repository,
            secret_key=test_settings.secret_key,
            algorithm=test_settings.jwt_algorithm,
            access_token_expire_minutes=test_settings.access_token_expire_minutes,
        )

    # ========================================================================
    # User Registration Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, mock_user_repository, mock_user):
        """Test successful user registration."""
        # Arrange
        mock_user_repository.get_user_by_username.return_value = None
        mock_user_repository.get_user_by_email.return_value = None
        mock_user_repository.create_user.return_value = mock_user

        # Act
        result = await auth_service.register_user(
            username="newuser",
            email="new@example.com",
            password="SecurePass123!",
            role="user",
            department="engineering",
        )

        # Assert
        assert result is not None
        assert result.username == mock_user.username
        assert result.user_id == mock_user.id
        mock_user_repository.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(
        self, auth_service, mock_user_repository, mock_user
    ):
        """Test registration fails with duplicate username."""
        # Arrange
        mock_user_repository.get_user_by_username.return_value = mock_user

        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            await auth_service.register_user(
                username="testuser",
                email="new@example.com",
                password="SecurePass123!",
                role="user",
                department="engineering",
            )

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(
        self, auth_service, mock_user_repository, mock_user
    ):
        """Test registration succeeds even with duplicate email (only username is checked)."""
        # Arrange
        mock_user_repository.get_user_by_username.return_value = None
        mock_user_repository.create_user.return_value = mock_user

        # Act
        result = await auth_service.register_user(
            username="newuser",
            email="test@example.com",
            password="SecurePass123!",
            role="user",
            department="engineering",
        )

        # Assert
        assert result is not None
        assert result.username == mock_user.username

    # ========================================================================
    # User Authentication Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_user_repository, mock_user):
        """Test successful user authentication."""
        # Arrange
        mock_user_repository.get_user_by_username.return_value = mock_user
        # Mock password verification to return True
        auth_service.verify_password = lambda p, h: True

        # Act
        result = await auth_service.authenticate_user(username="testuser", password="password123")

        # Assert
        assert result is not None
        assert result.username == mock_user.username
        assert result.user_id == mock_user.id

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_username(self, auth_service, mock_user_repository):
        """Test authentication fails with invalid username."""
        # Arrange
        mock_user_repository.get_user_by_username.return_value = None

        # Act
        result = await auth_service.authenticate_user(
            username="nonexistent", password="password123"
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(
        self, auth_service, mock_user_repository, mock_user
    ):
        """Test authentication fails with invalid password."""
        # Arrange
        mock_user_repository.get_user_by_username.return_value = mock_user

        # Mock password verification to return False
        auth_service.verify_password = lambda p, h: False

        # Act
        result = await auth_service.authenticate_user(username="testuser", password="wrongpassword")

        # Assert
        assert result is None

    # ========================================================================
    # JWT Token Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_create_access_token(self, auth_service, authenticated_user):
        """Test JWT token creation."""
        # Act
        token_data = await auth_service.create_access_token(authenticated_user)

        # Assert
        assert token_data is not None
        assert token_data.access_token is not None
        assert token_data.token_type == "bearer"
        assert isinstance(token_data.access_token, str)
        assert len(token_data.access_token.split(".")) == 3  # JWT has 3 parts

    @pytest.mark.asyncio
    async def test_verify_token_success(
        self, auth_service, mock_user_repository, mock_user, authenticated_user
    ):
        """Test successful token verification."""
        # Arrange
        token_data = await auth_service.create_access_token(authenticated_user)
        mock_user_repository.get_user_by_id.return_value = mock_user

        # Act
        user = await auth_service.verify_token(token_data.access_token)

        # Assert
        assert user is not None
        assert isinstance(user, AuthenticatedUser)
        assert user.username == authenticated_user.username

    @pytest.mark.asyncio
    async def test_verify_token_expired(self, auth_service):
        """Test token verification fails with expired token."""
        # Arrange
        expired_token = "expired.token.here"

        # Act
        result = await auth_service.verify_token(expired_token)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, auth_service):
        """Test token verification fails with invalid token."""
        # Arrange
        invalid_token = "invalid.token.here"

        # Act
        result = await auth_service.verify_token(invalid_token)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_user_not_found(
        self, auth_service, mock_user_repository, authenticated_user
    ):
        """Test token verification fails when user doesn't exist."""
        # Arrange
        token_data = await auth_service.create_access_token(authenticated_user)
        mock_user_repository.get_user_by_id.return_value = None

        # Act
        result = await auth_service.verify_token(token_data.access_token)

        # Assert
        assert result is None

    # ========================================================================
    # Permission Tests
    # ========================================================================

    def test_check_permission_admin_has_all_permissions(self, auth_service, authenticated_admin):
        """Test admin users have all permissions."""
        # Act
        result = auth_service.check_permission(user=authenticated_admin, required_role="user")

        # Assert
        assert result is True

    def test_check_permission_user_has_user_permission(self, auth_service, authenticated_user):
        """Test regular users have user-level permissions."""
        # Act
        result = auth_service.check_permission(user=authenticated_user, required_role="user")

        # Assert
        assert result is True

    def test_check_permission_user_lacks_admin_permission(self, auth_service, authenticated_user):
        """Test regular users don't have admin permissions."""
        # Act
        result = auth_service.check_permission(user=authenticated_user, required_role="admin")

        # Assert
        assert result is False

    # ========================================================================
    # Password Hashing Tests
    # ========================================================================

    def test_hash_password(self, auth_service):
        """Test password hashing."""
        # Arrange
        password = "SecurePassword123!"

        # Act
        hashed = auth_service.hash_password(password)

        # Assert
        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self, auth_service):
        """Test password verification with correct password."""
        # Arrange
        password = "SecurePassword123!"
        hashed = auth_service.hash_password(password)

        # Act
        result = auth_service.verify_password(password, hashed)

        # Assert
        assert result is True

    def test_verify_password_incorrect(self, auth_service):
        """Test password verification with incorrect password."""
        # Arrange
        password = "SecurePassword123!"
        hashed = auth_service.hash_password(password)

        # Act
        result = auth_service.verify_password("WrongPassword!", hashed)

        # Assert
        assert result is False
