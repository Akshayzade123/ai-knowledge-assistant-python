"""
Pydantic schemas for API validation.

These models define the contract for API requests and responses,
providing automatic validation and documentation.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# Authentication Schemas
class UserRegister(BaseModel):
    """Schema for user registration."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    department: str | None = None


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str
    expires_in: int


class UserInfo(BaseModel):
    """Schema for user information."""

    user_id: int
    username: str
    email: str
    role: str
    department: str | None
    created_at: datetime
    is_active: bool


# Query Schemas
class QueryRequest(BaseModel):
    """Schema for RAG query request."""

    question: str = Field(..., min_length=1, max_length=1000)
    collection_name: str | None = "Documents"


class SourceInfo(BaseModel):
    """Schema for source citation."""

    title: str
    score: float
    chunk_index: int
    excerpt: str


class QueryResponse(BaseModel):
    """Schema for RAG query response."""

    answer: str
    sources: list[SourceInfo]
    confidence: float
    tokens_used: int


class QueryHistoryItem(BaseModel):
    """Schema for query history item."""

    id: int
    query: str
    response: str
    sources: list[str]
    timestamp: str


# Document Schemas
class DocumentUpload(BaseModel):
    """Schema for document upload metadata."""

    title: str = Field(..., min_length=1, max_length=255)
    department: str | None = None
    access_level: str = Field(..., pattern="^(public|department|restricted)$")


class DocumentInfo(BaseModel):
    """Schema for document information."""

    id: int
    title: str
    file_type: str
    department: str | None
    access_level: str
    created_at: str


class DocumentListResponse(BaseModel):
    """Schema for document list response."""

    documents: list[DocumentInfo]
    total: int


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error response."""

    error: str
    detail: str | None = None
    status_code: int


# Health Check Schema
class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str
    version: str
    services: dict[str, str]
