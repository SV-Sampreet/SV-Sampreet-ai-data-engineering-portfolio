"""Embedding generation and management."""
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages embedding generation using sentence-transformers."""

    def __init__(self, config):
        """Initialize embedding manager.

        Args:
            config: EmbeddingConfig instance
        """
        self.config = config
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the embedding model."""
        logger.info(f"Loading embedding model: {self.config.model_name}")
        self.model = SentenceTransformer(self.config.model_name, device=self.config.device)
        logger.info("Embedding model loaded successfully")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=False)
        logger.info("Embeddings generated successfully")
        return embeddings.tolist()

    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a query.

        Args:
            query: Query string

        Returns:
            Embedding vector
        """
        logger.info("Generating query embedding")
        embedding = self.model.encode(query, show_progress_bar=False)
        return embedding.tolist()
