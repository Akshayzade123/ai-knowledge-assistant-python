"""
PostgreSQL Database Adapter.

SOLID Principles Applied:
- Single Responsibility (S): Each repository handles one entity type
- Dependency Inversion (D): Implements repository interfaces
- Interface Segregation (I): Separate repositories for different concerns
"""

import logging
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.interfaces.database import (
    Document,
    IDocumentRepository,
    IQueryLogRepository,
    IUserRepository,
    QueryLog,
    User,
)

logger = logging.getLogger(__name__)

Base = declarative_base()


# SQLAlchemy ORM Models
class UserModel(Base):
    """SQLAlchemy model for users table."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # admin, user, viewer
    department = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class DocumentModel(Base):
    """SQLAlchemy model for documents table."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    department = Column(String(100), nullable=True)
    access_level = Column(String(50), nullable=False)  # public, department, restricted
    created_at = Column(DateTime, default=datetime.utcnow)
    vector_store_id = Column(String(255), nullable=True)


class QueryLogModel(Base):
    """SQLAlchemy model for query logs table."""

    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    response_summary = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sources_used = Column(ARRAY(String), nullable=False)


class PostgresAdapter:
    """
    PostgreSQL adapter managing database connection and session.

    This class provides the infrastructure for repository implementations.
    """

    def __init__(self, database_url: str):
        """
        Initialize PostgreSQL adapter.

        Args:
            database_url: PostgreSQL connection string
        """
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize(self) -> None:
        """Create all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

    async def close(self) -> None:
        """Close database connection."""
        await self.engine.dispose()
        logger.info("Database connection closed")

    def get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.async_session()


class UserRepository(IUserRepository):
    """
    Concrete implementation of IUserRepository using PostgreSQL.

    Single Responsibility: Manages user data persistence only.
    """

    def __init__(self, db_adapter: PostgresAdapter):
        """
        Initialize repository with database adapter.

        Args:
            db_adapter: PostgreSQL adapter instance
        """
        self.db_adapter = db_adapter

    async def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
        role: str,
        department: str | None = None,
    ) -> User:
        """Create a new user."""
        async with self.db_adapter.get_session() as session:
            user_model = UserModel(
                username=username,
                email=email,
                hashed_password=hashed_password,
                role=role,
                department=department,
            )
            session.add(user_model)
            await session.commit()
            await session.refresh(user_model)

            return self._to_entity(user_model)

    async def get_user_by_username(self, username: str) -> User | None:
        """Retrieve user by username."""
        async with self.db_adapter.get_session() as session:
            result = await session.execute(select(UserModel).where(UserModel.username == username))
            user_model = result.scalar_one_or_none()

            return self._to_entity(user_model) if user_model else None

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve user by ID."""
        async with self.db_adapter.get_session() as session:
            result = await session.execute(select(UserModel).where(UserModel.id == user_id))
            user_model = result.scalar_one_or_none()

            return self._to_entity(user_model) if user_model else None

    async def update_user(self, user_id: int, **kwargs) -> User | None:
        """Update user attributes."""
        async with self.db_adapter.get_session() as session:
            result = await session.execute(select(UserModel).where(UserModel.id == user_id))
            user_model = result.scalar_one_or_none()

            if not user_model:
                return None

            for key, value in kwargs.items():
                if hasattr(user_model, key):
                    setattr(user_model, key, value)

            await session.commit()
            await session.refresh(user_model)

            return self._to_entity(user_model)

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        """Convert ORM model to domain entity."""
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            role=model.role,
            department=model.department,
            created_at=model.created_at,
            is_active=model.is_active,
        )


class DocumentRepository(IDocumentRepository):
    """
    Concrete implementation of IDocumentRepository using PostgreSQL.

    Single Responsibility: Manages document metadata persistence only.
    """

    def __init__(self, db_adapter: PostgresAdapter):
        """
        Initialize repository with database adapter.

        Args:
            db_adapter: PostgreSQL adapter instance
        """
        self.db_adapter = db_adapter

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
        async with self.db_adapter.get_session() as session:
            doc_model = DocumentModel(
                title=title,
                file_path=file_path,
                file_type=file_type,
                uploaded_by=uploaded_by,
                department=department,
                access_level=access_level,
                vector_store_id=vector_store_id,
            )
            session.add(doc_model)
            await session.commit()
            await session.refresh(doc_model)

            return self._to_entity(doc_model)

    async def get_document_by_id(self, doc_id: int) -> Document | None:
        """Retrieve document by ID."""
        async with self.db_adapter.get_session() as session:
            result = await session.execute(select(DocumentModel).where(DocumentModel.id == doc_id))
            doc_model = result.scalar_one_or_none()

            return self._to_entity(doc_model) if doc_model else None

    async def get_accessible_documents(
        self, user_role: str, user_department: str | None
    ) -> list[Document]:
        """Get documents accessible to user based on role and department."""
        async with self.db_adapter.get_session() as session:
            # Build query based on access rules
            query = select(DocumentModel)

            if user_role == "admin":
                # Admins see everything
                pass
            elif user_role == "user":
                # Users see public + their department
                query = query.where(
                    (DocumentModel.access_level == "public")
                    | (
                        (DocumentModel.access_level == "department")
                        & (DocumentModel.department == user_department)
                    )
                )
            else:  # viewer
                # Viewers see only public
                query = query.where(DocumentModel.access_level == "public")

            result = await session.execute(query)
            doc_models = result.scalars().all()

            return [self._to_entity(doc) for doc in doc_models]

    async def delete_document(self, doc_id: int) -> bool:
        """Delete document metadata."""
        async with self.db_adapter.get_session() as session:
            result = await session.execute(select(DocumentModel).where(DocumentModel.id == doc_id))
            doc_model = result.scalar_one_or_none()

            if not doc_model:
                return False

            await session.delete(doc_model)
            await session.commit()
            return True

    @staticmethod
    def _to_entity(model: DocumentModel) -> Document:
        """Convert ORM model to domain entity."""
        return Document(
            id=model.id,
            title=model.title,
            file_path=model.file_path,
            file_type=model.file_type,
            uploaded_by=model.uploaded_by,
            department=model.department,
            access_level=model.access_level,
            created_at=model.created_at,
            vector_store_id=model.vector_store_id,
        )


class QueryLogRepository(IQueryLogRepository):
    """
    Concrete implementation of IQueryLogRepository using PostgreSQL.

    Single Responsibility: Manages query log persistence only.
    """

    def __init__(self, db_adapter: PostgresAdapter):
        """
        Initialize repository with database adapter.

        Args:
            db_adapter: PostgreSQL adapter instance
        """
        self.db_adapter = db_adapter

    async def log_query(
        self, user_id: int, query_text: str, response_summary: str, sources_used: list[str]
    ) -> QueryLog:
        """Log a user query and response."""
        async with self.db_adapter.get_session() as session:
            log_model = QueryLogModel(
                user_id=user_id,
                query_text=query_text,
                response_summary=response_summary,
                sources_used=sources_used,
            )
            session.add(log_model)
            await session.commit()
            await session.refresh(log_model)

            return self._to_entity(log_model)

    async def get_user_history(self, user_id: int, limit: int = 10) -> list[QueryLog]:
        """Retrieve user's query history."""
        async with self.db_adapter.get_session() as session:
            result = await session.execute(
                select(QueryLogModel)
                .where(QueryLogModel.user_id == user_id)
                .order_by(QueryLogModel.timestamp.desc())
                .limit(limit)
            )
            log_models = result.scalars().all()

            return [self._to_entity(log) for log in log_models]

    @staticmethod
    def _to_entity(model: QueryLogModel) -> QueryLog:
        """Convert ORM model to domain entity."""
        return QueryLog(
            id=model.id,
            user_id=model.user_id,
            query_text=model.query_text,
            response_summary=model.response_summary,
            timestamp=model.timestamp,
            sources_used=model.sources_used,
        )
