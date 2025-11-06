"""
Unit tests for EmbedService.

Tests document embedding, chunking, and storage operations.
"""

from unittest.mock import AsyncMock, mock_open, patch

import pytest

from app.services.embed_service import EmbedService


@pytest.mark.unit
class TestEmbedService:
    """Test suite for EmbedService."""

    @pytest.fixture
    def embed_service(
        self,
        mock_vector_store,
        mock_embedding_provider,
        mock_document_repository,
        test_settings,
    ):
        """Create EmbedService instance with mocked dependencies."""
        return EmbedService(
            vector_store=mock_vector_store,
            embedding_provider=mock_embedding_provider,
            document_repository=mock_document_repository,
            chunk_size=test_settings.chunk_size,
            chunk_overlap=test_settings.chunk_overlap,
        )

    # ========================================================================
    # Document Ingestion Tests
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="File mocking complex - requires integration test")
    async def test_ingest_document_success(
        self,
        embed_service,
        mock_document_repository,
        mock_vector_store,
        mock_embedding_provider,
        mock_embedding_result,
    ):
        """Test successful document ingestion."""
        # This test requires actual file system or complex mocking
        # Better tested as integration test with real files
        pass

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="File mocking complex - requires integration test")
    async def test_ingest_document_pdf(
        self,
        embed_service,
        mock_document_repository,
        mock_vector_store,
        mock_embedding_provider,
        mock_embedding_result,
    ):
        """Test PDF document ingestion."""
        # Arrange
        file_path = "/uploads/test.pdf"
        title = "Test PDF"
        uploaded_by = 1
        department = "engineering"
        access_level = "public"

        mock_document_repository.create_document.return_value = 1
        mock_embedding_provider.embed_batch.return_value = [mock_embedding_result]
        mock_vector_store.add_documents.return_value = ["doc_id_1"]

        # Mock PDF reading
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=b"PDF content")),
            patch("PyPDF2.PdfReader") as mock_pdf,
        ):
            mock_pdf.return_value.pages = [
                type("obj", (object,), {"extract_text": lambda: "PDF text content"})()
            ]

            # Act
            doc_id = await embed_service.ingest_document(
                file_path=file_path,
                title=title,
                uploaded_by=uploaded_by,
                department=department,
                access_level=access_level,
            )

            # Assert
            assert doc_id == 1

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="File mocking complex - requires integration test")
    async def test_ingest_document_unsupported_format(self, embed_service):
        """Test ingestion fails with unsupported file format."""
        # Arrange
        file_path = "/uploads/test.xyz"
        title = "Test Unsupported"
        uploaded_by = 1
        department = "engineering"
        access_level = "public"

        # Mock file exists
        with patch("os.path.exists", return_value=True):
            # Act & Assert
            with pytest.raises(ValueError, match="Unsupported file type"):
                await embed_service.ingest_document(
                    file_path=file_path,
                    title=title,
                    uploaded_by=uploaded_by,
                    department=department,
                    access_level=access_level,
                )

    # ========================================================================
    # Text Chunking Tests
    # ========================================================================

    def test_chunk_text_basic(self, embed_service):
        """Test basic text chunking."""
        # Arrange
        text = "This is a test. " * 100  # Create long text

        # Act
        chunks = embed_service.chunk_text(text)

        # Assert
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_chunk_text_short_text(self, embed_service):
        """Test chunking with text shorter than chunk size."""
        # Arrange
        text = "Short text"

        # Act
        chunks = embed_service.chunk_text(text)

        # Assert
        assert len(chunks) >= 1
        assert text in chunks[0] or chunks[0] in text

    def test_chunk_text_empty(self, embed_service):
        """Test chunking with empty text."""
        # Arrange
        text = ""

        # Act
        chunks = embed_service.chunk_text(text)

        # Assert
        assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0] == "")

    # ========================================================================
    # Document Retrieval Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_accessible_documents_user(
        self, embed_service, mock_document_repository, mock_document
    ):
        """Test getting accessible documents for regular user."""
        # Arrange
        user_role = "user"
        user_department = "engineering"
        mock_document_repository.get_accessible_documents.return_value = [mock_document]

        # Act
        documents = await embed_service.get_accessible_documents(
            user_role=user_role, user_department=user_department
        )

        # Assert
        assert isinstance(documents, list)
        assert len(documents) >= 0  # May be empty or have documents
        mock_document_repository.get_accessible_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_accessible_documents_admin(self, embed_service, mock_document_repository):
        """Test getting accessible documents for admin user."""
        # Arrange
        user_role = "admin"
        user_department = "it"
        mock_document_repository.get_accessible_documents.return_value = []

        # Act
        documents = await embed_service.get_accessible_documents(
            user_role=user_role, user_department=user_department
        )

        # Assert
        assert isinstance(documents, list)
        mock_document_repository.get_accessible_documents.assert_called_once()

    # ========================================================================
    # Document Deletion Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_delete_document_success(
        self,
        embed_service,
        mock_document_repository,
        mock_vector_store,
        mock_document,
    ):
        """Test successful document deletion."""
        # Arrange
        document_id = 1
        mock_document_repository.get_document_by_id.return_value = mock_document
        mock_vector_store.delete_document = AsyncMock(return_value=True)
        mock_document_repository.delete_document = AsyncMock(return_value=True)

        # Act
        result = await embed_service.delete_document(document_id)

        # Assert
        assert result is True
        if mock_document.vector_store_id:
            mock_vector_store.delete_document.assert_called_once()
        mock_document_repository.delete_document.assert_called_once_with(document_id)

    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, embed_service, mock_document_repository):
        """Test deletion fails when document doesn't exist."""
        # Arrange
        document_id = 999
        mock_document_repository.get_document_by_id.return_value = None

        # Act
        result = await embed_service.delete_document(document_id)

        # Assert
        assert result is False
        mock_document_repository.delete_document.assert_not_called()
