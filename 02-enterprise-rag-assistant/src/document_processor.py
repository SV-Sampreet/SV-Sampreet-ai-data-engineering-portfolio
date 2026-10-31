"""Document processing module for text extraction and chunking."""
import os
from typing import List, Dict, Any
from pathlib import Path
import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes documents for RAG system."""

    def __init__(self, config):
        """Initialize document processor.

        Args:
            config: ProcessingConfig instance
        """
        self.config = config
        self.supported_formats = {'.pdf', '.txt', '.md'}

    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF file with page metadata.

        Args:
            file_path: Path to PDF file

        Returns:
            List of pages with text and metadata
        """
        logger.info(f"Extracting text from PDF: {file_path}")
        reader = PdfReader(file_path)
        pages = []

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                pages.append({
                    "text": text,
                    "page": page_num,
                    "source": os.path.basename(file_path)
                })

        logger.info(f"Extracted {len(pages)} pages from PDF")
        return pages

    def extract_text_from_txt(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from plain text file.

        Args:
            file_path: Path to text file

        Returns:
            List with text and metadata
        """
        logger.info(f"Extracting text from TXT: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        return [{
            "text": text,
            "page": 1,
            "source": os.path.basename(file_path)
        }]

    def extract_text_from_md(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from Markdown file.

        Args:
            file_path: Path to Markdown file

        Returns:
            List with text and metadata
        """
        logger.info(f"Extracting text from Markdown: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        return [{
            "text": text,
            "page": 1,
            "source": os.path.basename(file_path)
        }]

    def extract_text(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract text from supported file formats.

        Args:
            file_path: Path to file

        Returns:
            List of pages/sections with text and metadata

        Raises:
            ValueError: If file format is not supported
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_ext == '.txt':
            return self.extract_text_from_txt(file_path)
        elif file_ext == '.md':
            return self.extract_text_from_md(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into chunks with overlap.

        Args:
            text: Text to chunk
            metadata: Metadata to include with each chunk

        Returns:
            List of text chunks with metadata
        """
        chunks = []
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap

        for i in range(0, len(text), chunk_size - overlap):
            chunk_text = text[i:i + chunk_size]
            if chunk_text.strip():
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_id"] = len(chunks)
                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })

        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks

    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a document: extract text and chunk it.

        Args:
            file_path: Path to document

        Returns:
            List of chunks with metadata
        """
        # Extract text
        pages = self.extract_text(file_path)

        # Chunk each page
        all_chunks = []
        for page in pages:
            chunks = self.chunk_text(page["text"], {
                "source": page["source"],
                "page": page["page"]
            })
            all_chunks.extend(chunks)

        logger.info(f"Processed {file_path}: {len(all_chunks)} chunks")
        return all_chunks

    def validate_file_size(self, file_path: str) -> bool:
        """Validate file size is within limits.

        Args:
            file_path: Path to file

        Returns:
            True if file size is valid, False otherwise
        """
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            logger.warning(f"File too large: {file_size_mb:.2f}MB (max: {self.config.max_file_size_mb}MB)")
            return False
        return True
