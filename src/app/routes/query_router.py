"""
Query Router - Handles RAG query and document management endpoints.

SOLID Principles Applied:
- Single Responsibility (S): Only handles query-related HTTP endpoints
- Dependency Inversion (D): Depends on service interfaces
"""

import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.dependencies import get_embed_service, get_rag_service
from app.interfaces.auth import AuthenticatedUser
from app.models.schemas import (
    DocumentInfo,
    DocumentListResponse,
    ErrorResponse,
    QueryHistoryItem,
    QueryRequest,
    QueryResponse,
    SourceInfo,
)
from app.routes.auth_router import get_current_user
from app.services.embed_service import EmbedService
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Query & Documents"])


@router.post(
    "/ask",
    response_model=QueryResponse,
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def ask_question(
    query: QueryRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
) -> QueryResponse:
    """
    Ask a question using RAG.

    Args:
        query: Query request with question
        current_user: Authenticated user
        rag_service: RAG service

    Returns:
        Answer with sources and confidence
    """
    try:
        logger.info(f"Processing query from user {current_user.username}")

        # Process RAG query
        response = await rag_service.query(
            question=query.question, user=current_user, collection_name=query.collection_name
        )

        # Convert to response schema
        return QueryResponse(
            answer=response.answer,
            sources=[
                SourceInfo(
                    title=s["title"],
                    score=s["score"],
                    chunk_index=s["chunk_index"],
                    excerpt=s["excerpt"],
                )
                for s in response.sources
            ],
            confidence=response.confidence,
            tokens_used=response.tokens_used,
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process query"
        ) from e


@router.get(
    "/history", response_model=list[QueryHistoryItem], responses={401: {"model": ErrorResponse}}
)
async def get_query_history(
    limit: int = 10,
    current_user: AuthenticatedUser = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
) -> list[QueryHistoryItem]:
    """
    Get user's query history.

    Args:
        limit: Maximum number of queries to return
        current_user: Authenticated user
        rag_service: RAG service

    Returns:
        List of query history items
    """
    try:
        history = await rag_service.get_query_history(current_user, limit)

        return [
            QueryHistoryItem(
                id=item["id"],
                query=item["query"],
                response=item["response"],
                sources=item["sources"],
                timestamp=item["timestamp"],
            )
            for item in history
        ]

    except Exception as e:
        logger.error(f"Error getting query history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve query history",
        ) from e


@router.post(
    "/documents/upload",
    response_model=DocumentInfo,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    department: str = Form(None),
    access_level: str = Form(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
    embed_service: EmbedService = Depends(get_embed_service),
) -> DocumentInfo:
    """
    Upload and ingest a document.

    Args:
        file: Document file
        title: Document title
        department: Department (optional)
        access_level: Access level (public, department, restricted)
        current_user: Authenticated user
        embed_service: Embedding service

    Returns:
        Document information
    """
    try:
        # Check permissions (only users and admins can upload)
        if current_user.role not in ["user", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to upload documents",
            )

        # Validate access level
        if access_level not in ["public", "department", "restricted"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access level"
            )

        # Create upload directory if it doesn't exist
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)

        # Save file with unique name
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Saved file: {file_path}")

        # Ingest document
        doc_id = await embed_service.ingest_document(
            file_path=str(file_path),
            title=title,
            uploaded_by=current_user.user_id,
            department=department or current_user.department,
            access_level=access_level,
        )

        logger.info(f"Document {title} ingested successfully with ID {doc_id}")

        return DocumentInfo(
            id=doc_id,
            title=title,
            file_type=file_extension,
            department=department or current_user.department,
            access_level=access_level,
            created_at=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload document"
        ) from e


@router.get(
    "/documents", response_model=DocumentListResponse, responses={401: {"model": ErrorResponse}}
)
async def list_documents(
    current_user: AuthenticatedUser = Depends(get_current_user),
    embed_service: EmbedService = Depends(get_embed_service),
) -> DocumentListResponse:
    """
    List documents accessible to current user.

    Args:
        current_user: Authenticated user
        embed_service: Embedding service

    Returns:
        List of accessible documents
    """
    try:
        documents = await embed_service.get_accessible_documents(
            user_role=current_user.role, user_department=current_user.department
        )

        return DocumentListResponse(
            documents=[
                DocumentInfo(
                    id=doc["id"],
                    title=doc["title"],
                    file_type=doc["file_type"],
                    department=doc["department"],
                    access_level=doc["access_level"],
                    created_at=doc["created_at"],
                )
                for doc in documents
            ],
            total=len(documents),
        )

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list documents"
        ) from e


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def delete_document(
    document_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    embed_service: EmbedService = Depends(get_embed_service),
):
    """
    Delete a document.

    Args:
        document_id: Document ID
        current_user: Authenticated user
        embed_service: Embedding service
    """
    try:
        # Check permissions (only admins can delete)
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete documents",
            )

        # Delete document
        success = await embed_service.delete_document(document_id)

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        logger.info(f"Document {document_id} deleted by {current_user.username}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete document"
        ) from e
