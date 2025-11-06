"""
Database Interface - Defines contract for relational database operations.

SOLID Principles Applied:
- Interface Segregation (I): Separate interfaces for different data concerns
- Dependency Inversion (D): Services depend on abstractions, not concrete DB
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """User entity."""

    id: int
    username: str
    email: str
    hashed_password: str
    role: str
    department: str | None
    created_at: datetime
    is_active: bool


@dataclass
class Document:
    """Document metadata entity."""

    id: int
    title: str
    file_path: str
    file_type: str
    uploaded_by: int
    department: str | None
    access_level: str  # public, department, restricted
    created_at: datetime
    vector_store_id: str | None


@dataclass
class QueryLog:
    """Query logging entity."""

    id: int
    user_id: int
    query_text: str
    response_summary: str
    timestamp: datetime
    sources_used: list[str]


class IUserRepository(ABC):
    """Repository interface for user operations."""

    @abstractmethod
    async def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
        role: str,
        department: str | None = None,
    ) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> User | None:
        """Retrieve user by username."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve user by ID."""
        pass

    @abstractmethod
    async def update_user(self, user_id: int, **kwargs) -> User | None:
        """Update user attributes."""
        pass


class IDocumentRepository(ABC):
    """Repository interface for document metadata operations."""

    @abstractmethod
    async def create_document(
        self,
        title: str,
        file_path: str,
        file_type: str,
        uploaded_by: int,
        department: str | None,
        access_level: str,
        vector_store_id: str | None = None,
    ) -> Document:
        """Create document metadata record."""
        pass

    @abstractmethod
    async def get_document_by_id(self, doc_id: int) -> Document | None:
        """Retrieve document by ID."""
        pass

    @abstractmethod
    async def get_accessible_documents(
        self, user_role: str, user_department: str | None
    ) -> list[Document]:
        """Get documents accessible to user based on role and department."""
        pass

    @abstractmethod
    async def delete_document(self, doc_id: int) -> bool:
        """Delete document metadata."""
        pass


class IQueryLogRepository(ABC):
    """Repository interface for query logging."""

    @abstractmethod
    async def log_query(
        self, user_id: int, query_text: str, response_summary: str, sources_used: list[str]
    ) -> QueryLog:
        """Log a user query and response."""
        pass

    @abstractmethod
    async def get_user_history(self, user_id: int, limit: int = 10) -> list[QueryLog]:
        """Retrieve user's query history."""
        pass
