"""FastAPI application for RAG assistant."""
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from src.config import (
    ProcessingConfig, RetrievalConfig, LLMConfig,
    EmbeddingConfig, VectorDBConfig, APIConfig
)
from src.rag_orchestrator import RAGOrchestrator

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Enterprise RAG Assistant API", version="1.0.0")

# Initialize configurations
processing_config = ProcessingConfig()
retrieval_config = RetrievalConfig()
llm_config = LLMConfig()
embedding_config = EmbeddingConfig()
vector_db_config = VectorDBConfig()

# Initialize RAG orchestrator
rag = RAGOrchestrator(
    processing_config=processing_config,
    retrieval_config=retrieval_config,
    llm_config=llm_config,
    embedding_config=embedding_config,
    vector_db_config=vector_db_config
)


# Pydantic models
class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    status: str
    answer: str
    sources: List[dict]
    context_used: int


class StatusResponse(BaseModel):
    status: str
    total_chunks: int
    llm_provider: str
    embedding_model: str


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get index status."""
    status = rag.get_index_status()
    return StatusResponse(**status)


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Ingest a document into the RAG system."""
    # Validate file type
    allowed_extensions = {'.pdf', '.txt', '.md'}
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )

    # Save uploaded file
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # Ingest document
        result = rag.ingest_document(temp_file_path)
        return JSONResponse(content=result)
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    result = rag.query(request.question)
    return QueryResponse(**result)


@app.post("/clear")
async def clear_index():
    """Clear the document index."""
    result = rag.clear_index()
    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn
    api_config = APIConfig()
    uvicorn.run(app, host=api_config.host, port=api_config.port)
