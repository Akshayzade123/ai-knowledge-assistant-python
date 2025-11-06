"""
Gemma Embedding Adapter.

Provides embeddings using Docker AI's embeddinggemma model.
This adapter implements the IEmbeddingProvider interface for local embeddings.
"""

import logging

import httpx

from app.interfaces.llm import EmbeddingResult, IEmbeddingProvider

logger = logging.getLogger(__name__)


class GemmaEmbeddingAdapter(IEmbeddingProvider):
    """
    Adapter for Docker AI's EmbeddingGemma model.

    Uses Docker Desktop AI feature with ai/embeddinggemma model
    for local embeddings without requiring external API calls.
    """

    def __init__(self, base_url: str, model_name: str = "ai/embeddinggemma"):
        """
        Initialize Gemma embedding adapter.

        Args:
            base_url: Base URL of Docker AI service
            model_name: Model name (default: ai/embeddinggemma)
        """
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"GemmaEmbeddingAdapter initialized with model {model_name} at {self.base_url}")

    async def embed_text(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding result with vector

        Raises:
            Exception: If embedding generation fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/engines/llama.cpp/v1/embeddings",
                json={
                    "model": self.model_name,
                    "input": text,
                },
            )
            response.raise_for_status()
            data = response.json()

            # Docker AI returns embeddings in OpenAI format
            embedding = data["data"][0]["embedding"]

            return EmbeddingResult(
                embedding=embedding,
                model=self.model_name,
                dimensions=len(embedding),
            )

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding results

        Raises:
            Exception: If embedding generation fails
        """
        try:
            # Docker AI supports batch embeddings with array input
            response = await self.client.post(
                f"{self.base_url}/engines/llama.cpp/v1/embeddings",
                json={
                    "model": self.model_name,
                    "input": texts,
                },
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data["data"]:
                results.append(
                    EmbeddingResult(
                        embedding=item["embedding"],
                        model=self.model_name,
                        dimensions=len(item["embedding"]),
                    )
                )

            logger.info(f"Generated {len(results)} embeddings using Docker AI")
            return results

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("GemmaEmbeddingAdapter closed")
