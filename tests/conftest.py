"""
Pytest configuration and shared fixtures.

This module provides reusable fixtures for testing the AI Knowledge Assistant.
Follows SOLID principles by using dependency injection and interface-based mocking.
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.interfaces.auth import AuthenticatedUser, TokenData
from app.interfaces.database import Document, QueryLog, User
from app.interfaces.llm import EmbeddingResult, GenerationResult
from app.interfaces.vector_store import SearchResult, VectorDocument

# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def test_settings() -> Settings:
    """Provide test configuration settings."""
    return Settings(
        app_name="AI Knowledge Assistant Test",
        app_version="1.0.0-test",
        api_prefix="/api/v1",
        debug=True,
        # Database
        postgres_host="localhost",
        postgres_port=5432,
        postgres_user="test_user",
        postgres_password="test_password",
        postgres_db="test_db",
        # Weaviate
        weaviate_host="localhost",
        weaviate_port=8080,
        weaviate_grpc_port=50051,
        # Gemini (generation only)
        gemini_api_key="test_api_key",
        gemini_generation_model="gemini-2.5-flash",
        # Docker AI (embeddings)
        docker_ai_url="http://localhost:12434",
        embedding_model="ai/embeddinggemma",
        # Security
        secret_key="test_secret_key_for_testing_only",
        jwt_algorithm="HS256",
        access_token_expire_minutes=30,
        # RAG
        chunk_size=500,
        chunk_overlap=50,
        top_k_results=3,
        similarity_threshold=0.5,
    )


# ============================================================================
# User and Authentication Fixtures
# ============================================================================


@pytest.fixture
def mock_user() -> User:
    """Provide a mock user for testing."""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$test_hashed_password",
        role="user",
        department="engineering",
        created_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def mock_admin_user() -> User:
    """Provide a mock admin user for testing."""
    return User(
        id=2,
        username="admin",
        email="admin@example.com",
        hashed_password="$2b$12$test_hashed_password",
        role="admin",
        department="it",
        created_at=datetime.now(),
        is_active=True,
    )


@pytest.fixture
def authenticated_user(mock_user: User) -> AuthenticatedUser:
    """Provide an authenticated user for testing."""
    return AuthenticatedUser(
        user_id=mock_user.id,
        username=mock_user.username,
        role=mock_user.role,
        department=mock_user.department,
    )


@pytest.fixture
def authenticated_admin(mock_admin_user: User) -> AuthenticatedUser:
    """Provide an authenticated admin user for testing."""
    return AuthenticatedUser(
        user_id=mock_admin_user.id,
        username=mock_admin_user.username,
        role=mock_admin_user.role,
        department=mock_admin_user.department,
    )


@pytest.fixture
def mock_token_data() -> TokenData:
    """Provide mock token data for testing."""
    return TokenData(
        user_id=1,
        username="testuser",
        role="user",
        exp=datetime.now() + timedelta(hours=1),
    )


@pytest.fixture
def valid_jwt_token() -> str:
    """Provide a valid JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"


# ============================================================================
# Document Fixtures
# ============================================================================


@pytest.fixture
def mock_document() -> Document:
    """Provide a mock document for testing."""
    return Document(
        id=1,
        title="Test Document",
        file_path="/uploads/test.pdf",
        file_type="pdf",
        uploaded_by=1,
        department="engineering",
        access_level="public",
        created_at=datetime.now(),
        vector_store_id=None,
    )


@pytest.fixture
def mock_vector_document() -> VectorDocument:
    """Provide a mock vector document for testing."""
    return VectorDocument(
        id="test_doc_1",
        content="This is test content for vector search.",
        embedding=[0.1] * 768,  # Mock embedding vector
        metadata={
            "title": "Test Document",
            "file_path": "/uploads/test.pdf",
            "department": "engineering",
            "access_level": "public",
            "uploaded_by": 1,
            "chunk_index": 0,
        },
    )


@pytest.fixture
def mock_search_result() -> SearchResult:
    """Provide a mock search result for testing."""
    return SearchResult(
        id="test_doc_1",
        content="This is test content for vector search.",
        score=0.95,
        metadata={
            "title": "Test Document",
            "file_path": "/uploads/test.pdf",
            "department": "engineering",
            "access_level": "public",
            "uploaded_by": 1,
            "chunk_index": 0,
        },
    )


# ============================================================================
# LLM Fixtures
# ============================================================================


@pytest.fixture
def mock_embedding_result() -> EmbeddingResult:
    """Provide a mock embedding result for testing."""
    return EmbeddingResult(
        embedding=[0.1] * 768,  # Mock 768-dimensional embedding
        model="ai/embeddinggemma",
        dimensions=768,
    )


@pytest.fixture
def mock_generation_result() -> GenerationResult:
    """Provide a mock generation result for testing."""
    return GenerationResult(
        text="This is a generated response based on the provided context.",
        model="gemini-2.5-flash",
        tokens_used=50,
        finish_reason="stop",
    )


# ============================================================================
# Repository Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_user_repository():
    """Provide a mock user repository for testing."""
    mock_repo = AsyncMock()
    mock_repo.create_user = AsyncMock(return_value=1)
    mock_repo.get_user_by_id = AsyncMock(return_value=None)
    mock_repo.get_user_by_username = AsyncMock(return_value=None)
    mock_repo.get_user_by_email = AsyncMock(return_value=None)
    mock_repo.update_user = AsyncMock(return_value=True)
    mock_repo.delete_user = AsyncMock(return_value=True)
    return mock_repo


@pytest.fixture
def mock_document_repository():
    """Provide a mock document repository for testing."""
    mock_repo = AsyncMock()
    mock_repo.create_document = AsyncMock(return_value=1)
    mock_repo.get_document_by_id = AsyncMock(return_value=None)
    mock_repo.get_documents_by_user = AsyncMock(return_value=[])
    mock_repo.get_accessible_documents = AsyncMock(return_value=[])
    mock_repo.update_document = AsyncMock(return_value=True)
    mock_repo.delete_document = AsyncMock(return_value=True)
    return mock_repo


@pytest.fixture
def mock_query_log_repository():
    """Provide a mock query log repository for testing."""
    mock_repo = AsyncMock()
    mock_repo.log_query = AsyncMock(return_value=1)
    mock_repo.get_user_queries = AsyncMock(return_value=[])
    mock_repo.get_query_by_id = AsyncMock(return_value=None)
    return mock_repo


# ============================================================================
# Adapter Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_vector_store():
    """Provide a mock vector store for testing."""
    mock_store = AsyncMock()
    mock_store.initialize = AsyncMock()
    mock_store.add_documents = AsyncMock(return_value=["id1", "id2"])
    mock_store.search = AsyncMock(return_value=[])
    mock_store.delete_by_metadata = AsyncMock(return_value=True)
    mock_store.close = AsyncMock()
    return mock_store


@pytest.fixture
def mock_embedding_provider():
    """Provide a mock embedding provider for testing."""
    mock_provider = AsyncMock()
    mock_provider.embed_text = AsyncMock()
    mock_provider.embed_batch = AsyncMock(return_value=[])
    return mock_provider


@pytest.fixture
def mock_generation_provider():
    """Provide a mock generation provider for testing."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_provider.generate_with_system = AsyncMock()
    return mock_provider


# ============================================================================
# Service Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_auth_service():
    """Provide a mock authentication service for testing."""
    mock_service = AsyncMock()
    mock_service.register_user = AsyncMock(return_value="mock_token")
    mock_service.authenticate_user = AsyncMock(return_value="mock_token")
    mock_service.verify_token = AsyncMock()
    mock_service.get_current_user = AsyncMock()
    mock_service.check_permission = AsyncMock(return_value=True)
    return mock_service


@pytest.fixture
def mock_embed_service():
    """Provide a mock embedding service for testing."""
    mock_service = AsyncMock()
    mock_service.ingest_document = AsyncMock(return_value=1)
    mock_service.get_accessible_documents = AsyncMock(return_value=[])
    mock_service.delete_document = AsyncMock(return_value=True)
    return mock_service


@pytest.fixture
def mock_rag_service():
    """Provide a mock RAG service for testing."""
    mock_service = AsyncMock()
    mock_service.query = AsyncMock()
    mock_service.get_query_history = AsyncMock(return_value=[])
    return mock_service


# ============================================================================
# Query Log Fixtures
# ============================================================================


@pytest.fixture
def mock_query_log() -> QueryLog:
    """Provide a mock query log for testing."""
    return QueryLog(
        id=1,
        user_id=1,
        query_text="What is the test question?",
        response_summary="This is the test response.",
        timestamp=datetime.now(),
        sources_used=["Test Doc"],
    )


# ============================================================================
# Test Client Fixtures
# ============================================================================


@pytest.fixture
def test_client():
    """Provide a FastAPI test client."""
    from app.main import app

    return TestClient(app)


# ============================================================================
# Async Event Loop
# ============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
