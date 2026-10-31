"""Configuration management for RAG assistant."""
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """LLM configuration parameters."""
    provider: str = os.getenv("LLM_PROVIDER", "mock")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))


@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""
    model_name: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    device: str = os.getenv("EMBEDDING_DEVICE", "cpu")


@dataclass
class VectorDBConfig:
    """Vector database configuration."""
    persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "data/index")
    collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "documents")


@dataclass
class ProcessingConfig:
    """Document processing configuration."""
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))


@dataclass
class RetrievalConfig:
    """Retrieval configuration."""
    top_k: int = int(os.getenv("TOP_K", "5"))
    score_threshold: float = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.5"))


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))


@dataclass
class StreamlitConfig:
    """Streamlit UI configuration."""
    host: str = os.getenv("STREAMLIT_HOST", "localhost")
    port: int = int(os.getenv("STREAMLIT_PORT", "8501"))


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = os.getenv("LOG_LEVEL", "INFO")
