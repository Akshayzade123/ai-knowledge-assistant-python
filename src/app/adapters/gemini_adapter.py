"""
Google Gemini Generation Adapter.

SOLID Principles Applied:
- Single Responsibility (S): Only handles Gemini text generation
- Dependency Inversion (D): Implements IGenerationProvider
- Open/Closed (O): New generation providers can be added without changing services
"""

import logging

from google import genai
from google.genai import types

from app.interfaces.llm import GenerationResult, IGenerationProvider

logger = logging.getLogger(__name__)


class GeminiAdapter(IGenerationProvider):
    """
    Concrete implementation for Google Gemini API (generation only).

    Implements generation interface for answer generation.
    Embeddings are handled by Docker AI's EmbeddingGemma.
    """

    def __init__(
        self,
        api_key: str,
        generation_model: str = "gemini-2.5-flash",
    ):
        """
        Initialize Gemini adapter for generation.

        Args:
            api_key: Google AI API key
            generation_model: Model for text generation
        """
        self.api_key = api_key
        self.generation_model_name = generation_model

        # Initialize client with new google-genai SDK
        self.client = genai.Client(api_key=api_key)

        logger.info(f"Initialized Gemini generation with model: {generation_model}")

    async def generate(
        self,
        prompt: str,
        context: str | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs,
    ) -> GenerationResult:
        """Generate text using Gemini."""
        try:
            # Construct full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

            # Generate response with new SDK
            response = self.client.models.generate_content(
                model=self.generation_model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )

            return GenerationResult(
                text=response.text,
                model=self.generation_model_name,
                tokens_used=response.usage_metadata.total_token_count,
                finish_reason=str(response.candidates[0].finish_reason),
            )

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    async def generate_with_system(
        self, system_prompt: str, user_prompt: str, context: str | None = None, **kwargs
    ) -> GenerationResult:
        """Generate text with system instructions."""
        try:
            # Construct user prompt with context
            full_user_prompt = user_prompt
            if context:
                full_user_prompt = f"Context:\n{context}\n\nQuestion: {user_prompt}"

            # Generate response with system instruction using new SDK
            response = self.client.models.generate_content(
                model=self.generation_model_name,
                contents=full_user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=kwargs.get("max_tokens", 1000),
                    temperature=kwargs.get("temperature", 0.7),
                ),
            )

            return GenerationResult(
                text=response.text,
                model=self.generation_model_name,
                tokens_used=response.usage_metadata.total_token_count,
                finish_reason=str(response.candidates[0].finish_reason),
            )

        except Exception as e:
            logger.error(f"Error generating with system prompt: {e}")
            raise
