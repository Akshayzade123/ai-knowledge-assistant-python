"""
RAG Service - Retrieval-Augmented Generation logic.

SOLID Principles Applied:
- Single Responsibility (S): Only handles RAG query processing
- Dependency Inversion (D): Depends on interfaces for all external dependencies
- Open/Closed (O): Can be extended with new retrieval strategies
"""

import logging
from dataclasses import dataclass
from typing import Any

from app.interfaces.auth import AuthenticatedUser
from app.interfaces.database import IQueryLogRepository
from app.interfaces.llm import IEmbeddingProvider, IGenerationProvider
from app.interfaces.vector_store import IVectorStore, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """Response from RAG query."""

    answer: str
    sources: list[dict[str, Any]]
    confidence: float
    tokens_used: int


class RAGService:
    """
    Retrieval-Augmented Generation service.

    This service orchestrates the RAG pipeline:
    1. Embed user query
    2. Retrieve relevant documents (with access control)
    3. Generate answer using LLM with context
    4. Log query and response
    """

    def __init__(
        self,
        embedding_provider: IEmbeddingProvider,
        generation_provider: IGenerationProvider,
        vector_store: IVectorStore,
        query_log_repository: IQueryLogRepository,
        top_k: int = 5,
        similarity_threshold: float = 0.3,
    ):
        """
        Initialize RAG service.

        Args:
            embedding_provider: Provider for query embeddings
            generation_provider: Provider for answer generation
            vector_store: Vector database for retrieval
            query_log_repository: Repository for query logging
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score
        """
        self.embedding_provider = embedding_provider
        self.generation_provider = generation_provider
        self.vector_store = vector_store
        self.query_log_repository = query_log_repository
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

        logger.info("RAGService initialized")

    async def query(
        self, question: str, user: AuthenticatedUser, collection_name: str = "Documents"
    ) -> RAGResponse:
        """
        Process a RAG query with user access control.

        Args:
            question: User's question
            user: Authenticated user information
            collection_name: Vector store collection to search

        Returns:
            RAGResponse with answer and sources
        """
        try:
            logger.info(f"Processing query from user {user.username}: {question}")

            # Step 1: Embed the query
            query_embedding = await self.embedding_provider.embed_text(question)

            # Step 2: Retrieve relevant documents with access control
            filters = self._build_access_filters(user)
            search_results = await self.vector_store.search(
                query_embedding=query_embedding.embedding,
                collection_name=collection_name,
                limit=self.top_k,
                filters=filters,
            )

            # Filter by similarity threshold
            scores = [r.score for r in search_results]
            logger.info(f"Search returned {len(search_results)} results with scores: {scores}")
            logger.info(f"Using similarity threshold: {self.similarity_threshold}")

            relevant_results = [
                result for result in search_results if result.score >= self.similarity_threshold
            ]

            if not relevant_results:
                logger.warning(f"No relevant documents found for query: {question}")
                return RAGResponse(
                    answer="I couldn't find any relevant information to answer your question.",
                    sources=[],
                    confidence=0.0,
                    tokens_used=0,
                )

            logger.info(f"Found {len(relevant_results)} relevant documents")

            # Step 3: Build context from retrieved documents
            context = self._build_context(relevant_results)

            # Step 4: Generate answer using LLM
            system_prompt = self._get_system_prompt()
            generation_result = await self.generation_provider.generate_with_system(
                system_prompt=system_prompt,
                user_prompt=question,
                context=context,
                max_tokens=1000,
                temperature=0.7,
            )

            # Step 5: Prepare response
            sources = self._format_sources(relevant_results)
            confidence = self._calculate_confidence(relevant_results)

            response = RAGResponse(
                answer=generation_result.text,
                sources=sources,
                confidence=confidence,
                tokens_used=generation_result.tokens_used,
            )

            # Step 6: Log query and response
            await self._log_query(user, question, response)

            logger.info(f"Successfully processed query for user {user.username}")
            return response

        except Exception as e:
            logger.error(f"Error processing RAG query: {e}")
            raise

    def _build_access_filters(self, user: AuthenticatedUser) -> dict[str, Any]:
        """
        Build access control filters based on user role and department.

        Args:
            user: Authenticated user

        Returns:
            Filter dictionary for vector store
        """
        filters = {}

        if user.role == "admin":
            # Admins can access everything
            pass
        elif user.role == "user":
            # Users can access public and their department documents
            if user.department:
                filters["department"] = user.department
        else:  # viewer
            # Viewers can only access public documents
            filters["access_level"] = "public"

        return filters

    def _build_context(self, search_results: list[SearchResult]) -> str:
        """
        Build context string from search results.

        Args:
            search_results: List of retrieved documents

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, result in enumerate(search_results, 1):
            title = result.metadata.get("title", "Unknown")
            context_parts.append(f"[Document {i}: {title}]\n{result.content}\n")

        return "\n".join(context_parts)

    def _get_system_prompt(self) -> str:
        """
        Get system prompt for answer generation.

        Returns:
            System prompt string
        """
        return """You are an AI assistant for an enterprise knowledge base system.
Your role is to provide accurate, helpful answers based on the provided context documents.

Guidelines:
- Answer questions using ONLY the information from the provided context
- If the context doesn't contain enough information, say so clearly
- Cite specific documents when referencing information
- Be concise but thorough
- Maintain a professional tone
- If asked about sensitive information, remind users about data access policies"""

    def _format_sources(self, search_results: list[SearchResult]) -> list[dict[str, Any]]:
        """
        Format search results as source citations.

        Args:
            search_results: List of retrieved documents

        Returns:
            List of source dictionaries
        """
        sources = []

        for result in search_results:
            source = {
                "title": result.metadata.get("title", "Unknown"),
                "score": round(result.score, 3),
                "chunk_index": result.metadata.get("chunk_index", 0),
                "excerpt": (
                    result.content[:200] + "..." if len(result.content) > 200 else result.content
                ),
            }
            sources.append(source)

        return sources

    def _calculate_confidence(self, search_results: list[SearchResult]) -> float:
        """
        Calculate confidence score based on retrieval results.

        Args:
            search_results: List of retrieved documents

        Returns:
            Confidence score between 0 and 1
        """
        if not search_results:
            return 0.0

        # Average of top scores
        avg_score = sum(r.score for r in search_results) / len(search_results)

        # Adjust based on number of results
        result_factor = min(len(search_results) / self.top_k, 1.0)

        confidence = avg_score * result_factor
        return round(confidence, 3)

    async def _log_query(
        self, user: AuthenticatedUser, question: str, response: RAGResponse
    ) -> None:
        """
        Log query and response for audit and analytics.

        Args:
            user: Authenticated user
            question: User's question
            response: RAG response
        """
        try:
            # Extract source titles for logging
            source_titles = [s["title"] for s in response.sources]

            # Create summary of response (first 200 chars)
            response_summary = (
                response.answer[:200] + "..." if len(response.answer) > 200 else response.answer
            )

            await self.query_log_repository.log_query(
                user_id=user.user_id,
                query_text=question,
                response_summary=response_summary,
                sources_used=source_titles,
            )

        except Exception as e:
            # Don't fail the query if logging fails
            logger.error(f"Error logging query: {e}")

    async def get_query_history(
        self, user: AuthenticatedUser, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get user's query history.

        Args:
            user: Authenticated user
            limit: Maximum number of queries to return

        Returns:
            List of query log entries
        """
        try:
            logs = await self.query_log_repository.get_user_history(
                user_id=user.user_id, limit=limit
            )

            return [
                {
                    "id": log.id,
                    "query": log.query_text,
                    "response": log.response_summary,
                    "sources": log.sources_used,
                    "timestamp": log.timestamp.isoformat(),
                }
                for log in logs
            ]

        except Exception as e:
            logger.error(f"Error getting query history: {e}")
            return []
