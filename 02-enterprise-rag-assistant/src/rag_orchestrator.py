"""RAG orchestrator that coordinates document processing, retrieval, and generation."""
import logging
from typing import List, Dict, Any

from src.document_processor import DocumentProcessor
from src.embedding_manager import EmbeddingManager
from src.vector_store import VectorStore
from src.llm_manager import LLMManager
from src.config import ProcessingConfig, RetrievalConfig, LLMConfig, EmbeddingConfig, VectorDBConfig

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """Orchestrates the RAG pipeline."""

    def __init__(self, processing_config: ProcessingConfig,
                 retrieval_config: RetrievalConfig,
                 llm_config: LLMConfig,
                 embedding_config: EmbeddingConfig,
                 vector_db_config: VectorDBConfig):
        """Initialize RAG orchestrator.

        Args:
            processing_config: Document processing configuration
            retrieval_config: Retrieval configuration
            llm_config: LLM configuration
            embedding_config: Embedding configuration
            vector_db_config: Vector database configuration
        """
        self.processing_config = processing_config
        self.retrieval_config = retrieval_config

        # Initialize components
        self.document_processor = DocumentProcessor(processing_config)
        self.embedding_manager = EmbeddingManager(embedding_config)
        self.vector_store = VectorStore(vector_db_config, self.embedding_manager)
        self.llm_manager = LLMManager(llm_config)

        logger.info("RAG Orchestrator initialized")

    def ingest_document(self, file_path: str) -> Dict[str, Any]:
        """Ingest a document into the RAG system.

        Args:
            file_path: Path to document

        Returns:
            Ingestion result with status and details
        """
        logger.info(f"Ingesting document: {file_path}")

        try:
            # Validate file size
            if not self.document_processor.validate_file_size(file_path):
                return {
                    "status": "error",
                    "message": f"File size exceeds limit of {self.processing_config.max_file_size_mb}MB"
                }

            # Process document
            chunks = self.document_processor.process_document(file_path)

            # Add to vector store
            num_added = self.vector_store.add_documents(chunks)

            return {
                "status": "success",
                "message": f"Successfully ingested document",
                "chunks_added": num_added,
                "total_chunks": self.vector_store.get_collection_size()
            }
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system with a question.

        Args:
            question: User question

        Returns:
            Query result with answer and sources
        """
        logger.info(f"Processing query: {question}")

        try:
            # Retrieve relevant chunks
            results = self.vector_store.search(question, top_k=self.retrieval_config.top_k)

            if not results:
                return {
                    "status": "no_context",
                    "answer": "I don't have enough context from the indexed documents to answer your question.",
                    "sources": []
                }

            # Build context
            context = "\n\n".join([
                f"[Source: {r['metadata'].get('source', 'Unknown')}, Page: {r['metadata'].get('page', 'N/A')}]\n{r['text']}"
                for r in results
            ])

            # Build prompt
            prompt = f"""Use the following context to answer the question. If the context doesn't contain enough information to answer the question, say so explicitly.

Context:
{context}

Question: {question}

Answer:"""

            # Generate answer
            answer = self.llm_manager.generate_response(prompt)

            # Format sources
            sources = [
                {
                    "source": r['metadata'].get('source', 'Unknown'),
                    "page": r['metadata'].get('page', 'N/A'),
                    "chunk_id": r['metadata'].get('chunk_id', 'N/A'),
                    "score": r['score'],
                    "text": r['text'][:200] + "..." if len(r['text']) > 200 else r['text']
                }
                for r in results
            ]

            return {
                "status": "success",
                "answer": answer,
                "sources": sources,
                "context_used": len(results)
            }
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "status": "error",
                "answer": f"An error occurred while processing your query: {str(e)}",
                "sources": []
            }

    def get_index_status(self) -> Dict[str, Any]:
        """Get the current index status.

        Returns:
            Index status information
        """
        return {
            "total_chunks": self.vector_store.get_collection_size(),
            "llm_provider": self.llm_manager.config.provider,
            "embedding_model": self.embedding_manager.config.model_name
        }

    def clear_index(self) -> Dict[str, Any]:
        """Clear the document index.

        Returns:
            Clear operation result
        """
        logger.info("Clearing document index")
        self.vector_store.clear_collection()
        return {
            "status": "success",
            "message": "Index cleared successfully"
        }
