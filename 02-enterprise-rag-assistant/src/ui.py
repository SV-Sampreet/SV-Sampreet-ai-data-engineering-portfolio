"""Streamlit UI for RAG assistant."""
import streamlit as st
import logging
from typing import List, Dict

from src.config import (
    ProcessingConfig, RetrievalConfig, LLMConfig,
    EmbeddingConfig, VectorDBConfig
)
from src.rag_orchestrator import RAGOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Enterprise RAG Assistant",
    page_icon="📚",
    layout="wide"
)

# Initialize configurations
@st.cache_resource
def initialize_rag():
    """Initialize RAG orchestrator with caching."""
    processing_config = ProcessingConfig()
    retrieval_config = RetrievalConfig()
    llm_config = LLMConfig()
    embedding_config = EmbeddingConfig()
    vector_db_config = VectorDBConfig()

    return RAGOrchestrator(
        processing_config=processing_config,
        retrieval_config=retrieval_config,
        llm_config=llm_config,
        embedding_config=embedding_config,
        vector_db_config=vector_db_config
    )

# Initialize RAG
rag = initialize_rag()

def main():
    """Main Streamlit application."""
    st.title("📚 Enterprise RAG Assistant")
    st.markdown("Upload documents and ask questions grounded in your knowledge base.")

    # Sidebar
    with st.sidebar:
        st.header("Index Status")
        status = rag.get_index_status()
        st.metric("Total Chunks", status["total_chunks"])
        st.info(f"LLM Provider: {status['llm_provider']}")
        st.info(f"Embedding Model: {status['embedding_model']}")

        st.header("Actions")
        if st.button("Clear Index", type="secondary"):
            result = rag.clear_index()
            st.success(result["message"])
            st.rerun()

        st.header("Configuration")
        st.info(f"Chunk Size: {ProcessingConfig().chunk_size}")
        st.info(f"Top-K Results: {RetrievalConfig().top_k}")

    # Main content
    tab1, tab2 = st.tabs(["Query Documents", "Ingest Documents"])

    with tab1:
        st.header("Ask a Question")
        question = st.text_input("Enter your question:", placeholder="e.g., What is the company's sick leave policy?")

        if st.button("Ask", type="primary"):
            if question:
                with st.spinner("Searching documents and generating answer..."):
                    result = rag.query(question)

                if result["status"] == "success":
                    st.success("Answer generated successfully!")
                    st.markdown(f"### Answer\n\n{result['answer']}")

                    if result["sources"]:
                        st.markdown("### Sources")
                        for i, source in enumerate(result["sources"], 1):
                            with st.expander(f"Source {i}: {source['source']} (Page {source['page']})"):
                                st.write(f"**Score:** {source['score']:.4f}")
                                st.write(f"**Chunk ID:** {source['chunk_id']}")
                                st.write(f"**Text:** {source['text']}")
                else:
                    st.error(result["answer"])
            else:
                st.warning("Please enter a question.")

    with tab2:
        st.header("Upload Documents")
        st.info("Supported formats: PDF, TXT, MD")
        st.info(f"Maximum file size: {ProcessingConfig().max_file_size_mb}MB")

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'txt', 'md'],
            accept_multiple_files=False
        )

        if uploaded_file:
            st.write(f"**File name:** {uploaded_file.name}")
            st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")

            if st.button("Ingest", type="primary"):
                with st.spinner("Processing document..."):
                    # Save uploaded file temporarily
                    import tempfile
                    import os

                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                        temp_file.write(uploaded_file.getbuffer())
                        temp_file_path = temp_file.name

                    try:
                        result = rag.ingest_document(temp_file_path)

                        if result["status"] == "success":
                            st.success(f"✅ {result['message']}")
                            st.metric("Chunks Added", result["chunks_added"])
                            st.metric("Total Chunks", result["total_chunks"])
                        else:
                            st.error(f"❌ {result['message']}")
                    finally:
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)

if __name__ == "__main__":
    main()
