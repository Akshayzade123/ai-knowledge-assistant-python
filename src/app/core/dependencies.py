"""
Dependency Injection Container.

SOLID Principles Applied:
- Dependency Inversion (D): Central place for wiring dependencies
- Single Responsibility (S): Only handles dependency creation
- Open/Closed (O): Easy to add new dependencies

This module demonstrates the Dependency Injection pattern,
a key aspect of SOLID principles, particularly Dependency Inversion.
"""

import logging

from app.adapters.gemini_adapter import GeminiAdapter
from app.adapters.gemma_adapter import GemmaEmbeddingAdapter
from app.adapters.postgres_adapter import (
    DocumentRepository,
    PostgresAdapter,
    QueryLogRepository,
    UserRepository,
)
from app.adapters.weaviate_adapter import WeaviateAdapter
from app.core.config import get_settings
from app.interfaces.llm import IEmbeddingProvider
from app.services.auth_service import AuthService
from app.services.embed_service import EmbedService
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

# Global instances (initialized on startup)
_postgres_adapter: PostgresAdapter = None
_weaviate_adapter: WeaviateAdapter = None
_gemini_adapter: GeminiAdapter = None
_embedding_provider: IEmbeddingProvider = None


async def initialize_dependencies() -> None:
    """
    Initialize all infrastructure dependencies.

    Called during application startup.
    """
    global _postgres_adapter, _weaviate_adapter, _gemini_adapter, _embedding_provider

    settings = get_settings()

    logger.info("Initializing dependencies...")

    # Initialize PostgreSQL
    _postgres_adapter = PostgresAdapter(settings.database_url)
    await _postgres_adapter.initialize()
    logger.info("PostgreSQL initialized")

    # Initialize Weaviate
    _weaviate_adapter = WeaviateAdapter(
        host=settings.weaviate_host,
        port=settings.weaviate_port,
        grpc_port=settings.weaviate_grpc_port,
        api_key=settings.weaviate_api_key,
    )
    await _weaviate_adapter.initialize()
    logger.info("Weaviate initialized")

    # Initialize Docker AI Embedding Provider
    _embedding_provider = GemmaEmbeddingAdapter(
        base_url=settings.docker_ai_url,
        model_name=settings.embedding_model,
    )
    logger.info(f"Docker AI embedding provider initialized: {settings.embedding_model}")

    # Initialize Gemini for generation only
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY not set - LLM generation features will not work")

    _gemini_adapter = GeminiAdapter(
        api_key=settings.gemini_api_key,
        generation_model=settings.gemini_generation_model,
    )
    logger.info("Gemini generation provider initialized")

    logger.info("All dependencies initialized successfully")


async def shutdown_dependencies() -> None:
    """
    Cleanup dependencies on shutdown.

    Called during application shutdown.
    """
    global _postgres_adapter, _weaviate_adapter

    logger.info("Shutting down dependencies...")

    if _postgres_adapter:
        await _postgres_adapter.close()

    if _weaviate_adapter:
        await _weaviate_adapter.close()

    logger.info("Dependencies shut down")


# Dependency providers for FastAPI
def get_postgres_adapter() -> PostgresAdapter:
    """Get PostgreSQL adapter instance."""
    return _postgres_adapter


def get_weaviate_adapter() -> WeaviateAdapter:
    """Get Weaviate adapter instance."""
    return _weaviate_adapter


def get_gemini_adapter() -> GeminiAdapter:
    """Get Gemini adapter instance."""
    return _gemini_adapter


# Repository dependencies
def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    return UserRepository(_postgres_adapter)


def get_document_repository() -> DocumentRepository:
    """Get document repository instance."""
    return DocumentRepository(_postgres_adapter)


def get_query_log_repository() -> QueryLogRepository:
    """Get query log repository instance."""
    return QueryLogRepository(_postgres_adapter)


# Service dependencies
def get_auth_service() -> AuthService:
    """Get authentication service instance."""
    settings = get_settings()
    return AuthService(
        user_repository=get_user_repository(),
        secret_key=settings.secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
    )


def get_embed_service() -> EmbedService:
    """Get embedding service instance."""
    settings = get_settings()
    return EmbedService(
        embedding_provider=_embedding_provider,
        vector_store=_weaviate_adapter,
        document_repository=get_document_repository(),
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


def get_rag_service() -> RAGService:
    """Get RAG service instance."""
    settings = get_settings()
    return RAGService(
        embedding_provider=_embedding_provider,
        generation_provider=_gemini_adapter,
        vector_store=_weaviate_adapter,
        query_log_repository=get_query_log_repository(),
        top_k=settings.top_k_results,
        similarity_threshold=settings.similarity_threshold,
    )
