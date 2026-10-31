"""Vector database management using ChromaDB."""
import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""

    def __init__(self, config, embedding_manager):
        """Initialize vector store.

        Args:
            config: VectorDBConfig instance
            embedding_manager: EmbeddingManager instance
        """
        self.config = config
        self.embedding_manager = embedding_manager
        self.client = None
        self.collection = None
        self._initialize_store()

    def _initialize_store(self):
        """Initialize ChromaDB client and collection."""
        logger.info(f"Initializing ChromaDB with persist directory: {self.config.persist_dir}")

        # Create persist directory if it doesn't exist
        os.makedirs(self.config.persist_dir, exist_ok=True)

        # Initialize client
        self.client = chromadb.PersistentClient(
            path=self.config.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.config.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"ChromaDB initialized. Collection size: {self.collection.count()}")

    def add_documents(self, chunks: List[Dict[str, Any]]) -> int:
        """Add document chunks to the vector store.

        Args:
            chunks: List of chunks with text and metadata

        Returns:
            Number of chunks added
        """
        if not chunks:
            logger.warning("No chunks to add")
            return 0

        logger.info(f"Adding {len(chunks)} chunks to vector store")

        # Extract texts and metadata
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [f"{meta['source']}_page{meta['page']}_chunk{meta['chunk_id']}" for meta in metadatas]

        # Generate embeddings
        embeddings = self.embedding_manager.generate_embeddings(texts)

        # Add to collection
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )

        logger.info(f"Successfully added {len(chunks)} chunks")
        return len(chunks)

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for relevant chunks.

        Args:
            query: Search query
            top_k: Number of results to return (uses config default if None)

        Returns:
            List of relevant chunks with scores
        """
        if top_k is None:
            top_k = self.config.top_k

        logger.info(f"Searching for top {top_k} results for query: {query}")

        # Generate query embedding
        query_embedding = self.embedding_manager.generate_query_embedding(query)

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "score": results['distances'][0][i] if results['distances'] else 0.0,
                    "id": results['ids'][0][i] if results['ids'] else ""
                })

        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results

    def clear_collection(self):
        """Clear all documents from the collection."""
        logger.info("Clearing collection")
        self.client.delete_collection(self.config.collection_name)
        self.collection = self.client.create_collection(
            name=self.config.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Collection cleared")

    def get_collection_size(self) -> int:
        """Get the number of documents in the collection.

        Returns:
            Number of documents
        """
        return self.collection.count()

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from the collection.

        Returns:
            List of all documents with metadata
        """
        results = self.collection.get()
        formatted_results = []

        if results['documents']:
            for i, doc in enumerate(results['documents']):
                formatted_results.append({
                    "text": doc,
                    "metadata": results['metadatas'][i] if results['metadatas'] else {},
                    "id": results['ids'][i] if results['ids'] else ""
                })

        return formatted_results
