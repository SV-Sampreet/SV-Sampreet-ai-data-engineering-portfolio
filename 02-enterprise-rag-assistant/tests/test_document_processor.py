"""Tests for document processor module."""
import pytest
import tempfile
import os
from src.document_processor import DocumentProcessor
from src.config import ProcessingConfig


@pytest.fixture
def processing_config():
    """Create processing config for testing."""
    return ProcessingConfig()


@pytest.fixture
def document_processor(processing_config):
    """Create document processor for testing."""
    return DocumentProcessor(processing_config)


def test_extract_text_from_txt(document_processor):
    """Test text extraction from TXT file."""
    # Create temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content for document processing.")
        temp_path = f.name

    try:
        pages = document_processor.extract_text_from_txt(temp_path)
        assert len(pages) == 1
        assert "Test content" in pages[0]["text"]
        assert pages[0]["page"] == 1
    finally:
        os.remove(temp_path)


def test_chunk_text(document_processor):
    """Test text chunking."""
    text = "This is a test document. " * 50  # Create longer text
    metadata = {"source": "test.txt", "page": 1}

    chunks = document_processor.chunk_text(text, metadata)

    assert len(chunks) > 1
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)
    assert chunks[0]["metadata"]["source"] == "test.txt"


def test_validate_file_size(document_processor):
    """Test file size validation."""
    # Create a small file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Small file")
        temp_path = f.name

    try:
        assert document_processor.validate_file_size(temp_path) is True
    finally:
        os.remove(temp_path)


def test_unsupported_format(document_processor):
    """Test error handling for unsupported formats."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
        f.write("Unsupported format")
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="Unsupported file format"):
            document_processor.extract_text(temp_path)
    finally:
        os.remove(temp_path)
