"""LLM interaction module with mock mode for testing."""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MockLLM:
    """Mock LLM for testing without API keys."""

    def __init__(self, config):
        """Initialize mock LLM.

        Args:
            config: LLMConfig instance
        """
        self.config = config
        logger.info("Using Mock LLM (no API calls)")

    def generate_response(self, prompt: str) -> str:
        """Generate a mock response.

        Args:
            prompt: Input prompt

        Returns:
            Mock response
        """
        logger.info("Generating mock LLM response")

        # Simple mock response based on context presence
        if "context" in prompt.lower() and len(prompt) > 500:
            return ("Based on the provided documents, I can answer your question. "
                   "The retrieved context contains relevant information about your query. "
                   "However, this is a mock response. In production, a real LLM would "
                   "synthesize a more detailed answer based on the retrieved context.")
        else:
            return ("I don't have enough context from the indexed documents to answer "
                   "your question accurately. Please try rephrasing your question or "
                   "upload more relevant documents. This is a mock response.")


class OpenAILLM:
    """OpenAI LLM wrapper."""

    def __init__(self, config):
        """Initialize OpenAI LLM.

        Args:
            config: LLMConfig instance
        """
        self.config = config
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.openai_api_key)
            logger.info("OpenAI LLM initialized")
        except ImportError:
            logger.error("OpenAI package not installed")
            raise ImportError("Install openai package: pip install openai")

    def generate_response(self, prompt: str) -> str:
        """Generate response using OpenAI API.

        Args:
            prompt: Input prompt

        Returns:
            Generated response
        """
        logger.info("Generating OpenAI response")

        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class LLMManager:
    """Manages LLM interactions."""

    def __init__(self, config):
        """Initialize LLM manager.

        Args:
            config: LLMConfig instance
        """
        self.config = config
        self.llm = self._create_llm()

    def _create_llm(self):
        """Create LLM instance based on provider."""
        if self.config.provider == "mock":
            return MockLLM(self.config)
        elif self.config.provider == "openai":
            if not self.config.openai_api_key:
                logger.warning("OpenAI API key not provided, falling back to mock mode")
                return MockLLM(self.config)
            return OpenAILLM(self.config)
        else:
            logger.warning(f"Unknown provider {self.config.provider}, using mock mode")
            return MockLLM(self.config)

    def generate_response(self, prompt: str) -> str:
        """Generate LLM response.

        Args:
            prompt: Input prompt

        Returns:
            Generated response
        """
        return self.llm.generate_response(prompt)
