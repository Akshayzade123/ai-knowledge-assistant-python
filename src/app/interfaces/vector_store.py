"""
Vector Store Interface - Defines contract for vector database operations.

SOLID Principles Applied:
- Interface Segregation (I): Focused interface for vector operations only
- Dependency Inversion (D): High-level modules depend on this abstraction
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class VectorDocument:
    """Represents a document with vector embedding."""

    id: str
    content: str
    embedding: list[float]
    metadata: dict[str, Any]


@dataclass
class SearchResult:
    """Represents a search result from vector store."""

    id: str
    content: str
    metadata: dict[str, Any]
    score: float


class IVectorStore(ABC):
    """
    Abstract interface for vector database operations.
    Implementations: WeaviateAdapter, etc.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector store connection and schema."""
        pass

    @abstractmethod
    async def add_documents(
        self, documents: list[VectorDocument], collection_name: str
    ) -> list[str]:
        """
        Add documents with embeddings to the vector store.

        Args:
            documents: List of documents with embeddings
            collection_name: Target collection/class name

        Returns:
            List of document IDs
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        collection_name: str,
        limit: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """
        Perform semantic search using query embedding.

        Args:
            query_embedding: Vector representation of query
            collection_name: Collection to search in
            limit: Maximum number of results
            filters: Optional metadata filters (e.g., user permissions)

        Returns:
            List of search results with scores
        """
        pass

    @abstractmethod
    async def delete_document(self, document_id: str, collection_name: str) -> bool:
        """Delete a document from the vector store."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the vector store connection."""
        pass
