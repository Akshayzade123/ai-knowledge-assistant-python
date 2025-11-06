"""
Weaviate Vector Store Adapter.

SOLID Principles Applied:
- Single Responsibility (S): Only handles Weaviate-specific operations
- Dependency Inversion (D): Implements IVectorStore interface
- Open/Closed (O): Can be extended without modifying interface
"""

import logging
from typing import Any

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.query import Filter

from app.interfaces.vector_store import IVectorStore, SearchResult, VectorDocument

logger = logging.getLogger(__name__)


class WeaviateAdapter(IVectorStore):
    """
    Concrete implementation of IVectorStore using Weaviate.

    This adapter encapsulates all Weaviate-specific logic,
    allowing the rest of the application to remain agnostic
    of the vector store implementation.
    """

    def __init__(self, host: str, port: int, grpc_port: int, api_key: str | None = None):
        """
        Initialize Weaviate adapter.

        Args:
            host: Weaviate host
            port: HTTP port
            grpc_port: gRPC port
            api_key: Optional API key for authentication
        """
        self.host = host
        self.port = port
        self.grpc_port = grpc_port
        self.api_key = api_key
        self.client: weaviate.WeaviateClient | None = None

    async def initialize(self) -> None:
        """Initialize Weaviate client and create schema if needed."""
        try:
            # Connect to Weaviate
            if self.api_key:
                self.client = weaviate.connect_to_custom(
                    http_host=self.host,
                    http_port=self.port,
                    http_secure=False,
                    grpc_host=self.host,
                    grpc_port=self.grpc_port,
                    grpc_secure=False,
                    auth_credentials=weaviate.auth.AuthApiKey(self.api_key),
                )
            else:
                self.client = weaviate.connect_to_local(
                    host=self.host, port=self.port, grpc_port=self.grpc_port
                )

            logger.info(f"Connected to Weaviate at {self.host}:{self.port}")

            # Create default collection if it doesn't exist
            await self._ensure_collection("Documents")

        except Exception as e:
            logger.error(f"Failed to initialize Weaviate: {e}")
            raise

    async def _ensure_collection(self, collection_name: str) -> None:
        """Ensure collection exists with proper schema."""
        try:
            if not self.client.collections.exists(collection_name):
                self.client.collections.create(
                    name=collection_name,
                    properties=[
                        Property(name="content", data_type=DataType.TEXT),
                        Property(name="title", data_type=DataType.TEXT),
                        Property(name="file_path", data_type=DataType.TEXT),
                        Property(name="department", data_type=DataType.TEXT),
                        Property(name="access_level", data_type=DataType.TEXT),
                        Property(name="uploaded_by", data_type=DataType.INT),
                        Property(name="chunk_index", data_type=DataType.INT),
                    ],
                    vector_config=Configure.Vectorizer.none(),  # We provide embeddings
                )
                logger.info(f"Created collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection {collection_name}: {e}")
            raise

    async def add_documents(
        self, documents: list[VectorDocument], collection_name: str
    ) -> list[str]:
        """Add documents with embeddings to Weaviate."""
        try:
            await self._ensure_collection(collection_name)
            collection = self.client.collections.get(collection_name)

            document_ids = []

            # Batch insert for efficiency
            with collection.batch.dynamic() as batch:
                for doc in documents:
                    uuid = batch.add_object(
                        properties={"content": doc.content, **doc.metadata}, vector=doc.embedding
                    )
                    document_ids.append(str(uuid))

            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return document_ids

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    async def search(
        self,
        query_embedding: list[float],
        collection_name: str,
        limit: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Perform semantic search with optional access control filters."""
        try:
            collection = self.client.collections.get(collection_name)

            # Build filter for access control
            query_filter = None
            if filters:
                # Example: Filter by department or access level
                if "department" in filters:
                    query_filter = Filter.by_property("department").equal(filters["department"])
                if "access_level" in filters:
                    level_filter = Filter.by_property("access_level").equal(filters["access_level"])
                    query_filter = query_filter & level_filter if query_filter else level_filter

            # Perform vector search
            response = collection.query.near_vector(
                near_vector=query_embedding,
                limit=limit,
                return_metadata=["distance"],
                filters=query_filter,
            )

            # Convert to SearchResult objects
            results = []
            for obj in response.objects:
                results.append(
                    SearchResult(
                        id=str(obj.uuid),
                        content=obj.properties.get("content", ""),
                        metadata={k: v for k, v in obj.properties.items() if k != "content"},
                        score=1.0 - obj.metadata.distance,  # Convert distance to similarity
                    )
                )

            logger.info(f"Found {len(results)} results for query")
            return results

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    async def delete_document(self, document_id: str, collection_name: str) -> bool:
        """Delete a document from Weaviate."""
        try:
            collection = self.client.collections.get(collection_name)
            collection.data.delete_by_id(document_id)
            logger.info(f"Deleted document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False

    async def close(self) -> None:
        """Close Weaviate connection."""
        if self.client:
            self.client.close()
            logger.info("Closed Weaviate connection")
