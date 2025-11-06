"""
Integration tests for authentication routes.

Tests the complete authentication flow including registration, login, and token validation.
"""

import pytest

from app.core.dependencies import get_auth_service
from app.main import app


@pytest.mark.integration
class TestAuthRoutes:
    """Test suite for authentication API routes."""

    # ========================================================================
    # Registration Tests
    # ========================================================================

    def test_register_user_success(self, test_client, authenticated_user):
        """Test successful user registration."""
        # Arrange
        from unittest.mock import AsyncMock

        from app.interfaces.auth import TokenData

        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "role": "user",
            "department": "engineering",
        }

        # Create a fresh mock for this test
        mock_service = AsyncMock()
        mock_service.register_user = AsyncMock(return_value=authenticated_user)
        mock_service.create_access_token = AsyncMock(
            return_value=TokenData(
                access_token="mock_token_12345", token_type="bearer", expires_in=1800
            )
        )

        # Override the dependency
        app.dependency_overrides[get_auth_service] = lambda: mock_service

        try:
            # Act
            response = test_client.post("/api/v1/auth/register", json=user_data)

            # Assert
            assert response.status_code == 201
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
        finally:
            # Clean up
            app.dependency_overrides.clear()

    def test_register_user_duplicate_username(self, test_client, mock_auth_service):
        """Test registration fails with duplicate username."""
        # Arrange
        user_data = {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "SecurePass123!",
            "role": "user",
            "department": "engineering",
        }

        # Mock the auth service to raise ValueError
        mock_auth_service.register_user.side_effect = ValueError("Username already exists")
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        try:
            # Act
            response = test_client.post("/api/v1/auth/register", json=user_data)

            # Assert
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
        finally:
            app.dependency_overrides.clear()

    def test_register_user_invalid_data(self, test_client):
        """Test registration fails with invalid data."""
        # Arrange
        user_data = {
            "username": "u",  # Too short
            "email": "invalid-email",  # Invalid email
            "password": "123",  # Too short
        }

        # Act
        response = test_client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 422  # Validation error

    # ========================================================================
    # Login Tests
    # ========================================================================

    def test_login_success(self, test_client, authenticated_user):
        """Test successful user login."""
        # Arrange
        from unittest.mock import AsyncMock

        from app.interfaces.auth import TokenData

        credentials = {"username": "testuser", "password": "correct_password"}

        # Create a fresh mock for this test
        mock_service = AsyncMock()
        mock_service.authenticate_user = AsyncMock(return_value=authenticated_user)
        mock_service.create_access_token = AsyncMock(
            return_value=TokenData(
                access_token="mock_token_12345", token_type="bearer", expires_in=1800
            )
        )

        app.dependency_overrides[get_auth_service] = lambda: mock_service

        try:
            # Act
            response = test_client.post("/api/v1/auth/login", json=credentials)

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
        finally:
            app.dependency_overrides.clear()

    def test_login_invalid_credentials(self, test_client):
        """Test login fails with invalid credentials."""
        # Arrange
        from unittest.mock import AsyncMock

        credentials = {"username": "testuser", "password": "wrong_password"}

        # Create a fresh mock that returns None (invalid credentials)
        mock_service = AsyncMock()
        mock_service.authenticate_user = AsyncMock(return_value=None)

        app.dependency_overrides[get_auth_service] = lambda: mock_service

        try:
            # Act
            response = test_client.post("/api/v1/auth/login", json=credentials)

            # Assert
            assert response.status_code == 401
            data = response.json()
            assert "detail" in data
        finally:
            app.dependency_overrides.clear()

    def test_login_missing_fields(self, test_client):
        """Test login fails with missing fields."""
        # Arrange
        credentials = {"username": "testuser"}  # Missing password

        # Act
        response = test_client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == 422  # Validation error

    # ========================================================================
    # Current User Tests
    # ========================================================================

    def test_get_current_user_success(self, test_client, authenticated_user):
        """Test getting current user information."""
        # Mock the get_current_user dependency
        from app.routes.auth_router import get_current_user

        app.dependency_overrides[get_current_user] = lambda: authenticated_user

        try:
            # Act
            response = test_client.get(
                "/api/v1/auth/me",
                headers={"Authorization": "Bearer mock_token"},
            )

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == authenticated_user.username
            assert data["role"] == authenticated_user.role
            assert data["user_id"] == authenticated_user.user_id
        finally:
            app.dependency_overrides.clear()

    def test_get_current_user_unauthorized(self, test_client):
        """Test getting current user fails without token."""
        # Act
        response = test_client.get("/api/v1/auth/me")

        # Assert
        assert response.status_code == 403  # Forbidden (no token)

    def test_get_current_user_invalid_token(self, test_client):
        """Test getting current user fails with invalid token."""
        # Don't override - let the real auth flow handle invalid token
        # Act
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        # Assert - should fail authentication
        assert response.status_code in [401, 403]

    # ========================================================================
    # Token Format Tests
    # ========================================================================

    def test_token_format_validation(self, test_client):
        """Test API validates token format."""
        # Act
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "InvalidFormat"},
        )

        # Assert
        assert response.status_code in [401, 403]

    def test_bearer_scheme_required(self, test_client):
        """Test API requires Bearer scheme."""
        # Act
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Basic dGVzdDp0ZXN0"},
        )

        # Assert
        assert response.status_code in [401, 403]
