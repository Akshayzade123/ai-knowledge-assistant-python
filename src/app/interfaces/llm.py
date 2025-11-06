"""
LLM Interface - Defines contract for language model operations.

SOLID Principles Applied:
- Interface Segregation (I): Focused interface for LLM operations
- Dependency Inversion (D): RAG service depends on abstraction, not concrete LLM
- Open/Closed (O): Easy to add new LLM providers without modifying services
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EmbeddingResult:
    """Result of text embedding operation."""

    embedding: list[float]
    model: str
    dimensions: int


@dataclass
class GenerationResult:
    """Result of text generation operation."""

    text: str
    model: str
    tokens_used: int
    finish_reason: str


class IEmbeddingProvider(ABC):
    """Interface for text embedding operations."""

    @abstractmethod
    async def embed_text(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            EmbeddingResult with vector and metadata
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of input texts

        Returns:
            List of embedding results
        """
        pass


class IGenerationProvider(ABC):
    """Interface for text generation operations."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: str | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs,
    ) -> GenerationResult:
        """
        Generate text based on prompt and optional context.

        Args:
            prompt: User query or instruction
            context: Optional context (e.g., retrieved documents)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Provider-specific parameters

        Returns:
            GenerationResult with text and metadata
        """
        pass

    @abstractmethod
    async def generate_with_system(
        self, system_prompt: str, user_prompt: str, context: str | None = None, **kwargs
    ) -> GenerationResult:
        """
        Generate text with system instructions.

        Args:
            system_prompt: System-level instructions
            user_prompt: User query
            context: Optional context
            **kwargs: Provider-specific parameters

        Returns:
            GenerationResult with text and metadata
        """
        pass
