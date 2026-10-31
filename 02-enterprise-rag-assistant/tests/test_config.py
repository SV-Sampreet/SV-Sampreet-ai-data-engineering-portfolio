"""Tests for configuration module."""
import pytest
import os
from src.config import (
    LLMConfig, EmbeddingConfig, VectorDBConfig,
    ProcessingConfig, RetrievalConfig, APIConfig, StreamlitConfig, LoggingConfig
)


def test_llm_config_defaults():
    """Test LLMConfig default values."""
    config = LLMConfig()
    assert config.provider == "mock"
    assert config.openai_model == "gpt-3.5-turbo"
    assert config.temperature == 0.7


def test_llm_config_from_env():
    """Test LLMConfig reads from environment variables."""
    os.environ.pop("LLM_PROVIDER", None)
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["OPENAI_API_KEY"] = "test_key"
    config = LLMConfig()
    assert config.provider == "openai"
    assert config.openai_api_key == "test_key"
    del os.environ["LLM_PROVIDER"]
    del os.environ["OPENAI_API_KEY"]


def test_embedding_config_defaults():
    """Test EmbeddingConfig default values."""
    config = EmbeddingConfig()
    assert "sentence-transformers" in config.model_name
    assert config.device == "cpu"


def test_processing_config_defaults():
    """Test ProcessingConfig default values."""
    config = ProcessingConfig()
    assert config.chunk_size == 500
    assert config.chunk_overlap == 50
    assert config.max_file_size_mb == 10


def test_retrieval_config_defaults():
    """Test RetrievalConfig default values."""
    config = RetrievalConfig()
    assert config.top_k == 5
    assert config.score_threshold == 0.5


def test_vector_db_config_defaults():
    """Test VectorDBConfig default values."""
    config = VectorDBConfig()
    assert config.persist_dir == "data/index"
    assert config.collection_name == "documents"
