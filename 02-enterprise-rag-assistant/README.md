# Enterprise Document Intelligence Assistant Using RAG

A document-grounded AI assistant that answers questions using uploaded documents and cites the sources used for its answers.

## Problem Statement

Organizations have vast amounts of unstructured document data (PDFs, text files, policies, guides) that employees need to query. Traditional keyword search is insufficient for complex questions. This project implements a Retrieval-Augmented Generation (RAG) system that can understand and answer questions based on document content.

## Motivation

This project demonstrates:

- Building production-grade RAG systems from scratch
- Document processing and text chunking strategies
- Vector embeddings and similarity search
- Integration with vector databases (ChromaDB)
- LLM integration with mock mode for testing
- FastAPI for REST API endpoints
- Streamlit for user interface
- Evaluation and quality metrics for RAG systems

## Features

- **Document Ingestion**: Upload PDF, TXT, and Markdown files
- **Text Extraction**: Extract text with page metadata from PDFs
- **Text Chunking**: Configurable chunk size and overlap for optimal retrieval
- **Vector Embeddings**: Generate embeddings using sentence-transformers
- **Vector Database**: Persistent storage with ChromaDB
- **Semantic Search**: Retrieve relevant document chunks based on semantic similarity
- **Answer Generation**: Generate answers grounded in retrieved context
- **Source Citation**: Display source files, page numbers, and relevant passages
- **Insufficient Context Handling**: Explicitly state when evidence is insufficient
- **Mock Mode**: Local testing without API keys
- **REST API**: FastAPI endpoints for programmatic access
- **Web UI**: Streamlit interface for interactive use

## Architecture

The RAG system follows a modular architecture:

```
┌─────────────┐
│  Document   │
│  Ingestion  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Text      │
│ Extraction │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Chunking   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Embeddings  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Vector DB   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Retrieval  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Generation │
│   (LLM)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Answer +    │
│  Citations  │
└─────────────┘
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture diagrams.

## Technology Stack

- **Python 3.8+**: Core programming language
- **FastAPI**: REST API framework
- **Streamlit**: Web UI framework
- **LangChain**: LLM orchestration (optional)
- **ChromaDB**: Vector database
- **sentence-transformers**: Embedding model
- **PyPDF**: PDF text extraction
- **pytest**: Testing framework
- **python-dotenv**: Environment variable management

## Prerequisites

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for larger document sets)
- Optional: OpenAI API key for production LLM (mock mode available)

## Setup

1. Clone the repository and navigate to the project directory:
```bash
cd 02-enterprise-rag-assistant
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

For local testing without API keys, keep `LLM_PROVIDER=mock` (default).

## Execution

### Start the API Server:

```bash
python -m src.api
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Start the Streamlit UI:

```bash
streamlit run src/ui.py
```

The UI will be available at `http://localhost:8501`

### Example API Usage:

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Ingest Document:**
```bash
curl -X POST -F "file=@data/sample/company_policy.txt" http://localhost:8000/ingest
```

**Query Documents:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is the sick leave policy?"}' \
  http://localhost:8000/query
```

**Get Status:**
```bash
curl http://localhost:8000/status
```

**Clear Index:**
```bash
curl -X POST http://localhost:8000/clear
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

Test results:
- Configuration tests: 6 tests
- Document processor tests: 4 tests
- Total: 10 tests

## Configuration

Key configuration options in `.env`:

- `LLM_PROVIDER`: `mock` or `openai`
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)
- `EMBEDDING_MODEL`: Sentence transformer model name
- `CHUNK_SIZE`: Text chunk size in characters (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `TOP_K`: Number of retrieved chunks (default: 5)
- `MAX_FILE_SIZE_MB`: Maximum file size for upload (default: 10)

## Sample Data

The project includes sample documents:
- `data/sample/company_policy.txt`: Employee conduct policy
- `data/sample/product_guide.txt`: Cloud storage product guide

These can be used to test the system without uploading your own documents.

## Evaluation

The project includes an evaluation framework to measure retrieval quality:

- **Retrieval Metrics**: Recall@k, Precision@k
- **Groundedness**: Evaluate if answers are grounded in retrieved context
- **Citation Correctness**: Verify citations point to relevant passages

See [docs/testing.md](docs/testing.md) for evaluation details.

## Security Considerations

- No document contents logged unnecessarily
- Input validation on file uploads
- File size limits to prevent abuse
- No credentials in code (use environment variables)
- Warning about document prompt injection risks

## Limitations

- Mock LLM provides simple responses, not nuanced answers
- No document prompt injection protection (retrieved content should not be treated as trusted instructions)
- No advanced retrieval strategies (hybrid search, re-ranking)
- No multi-turn conversation support
- No document versioning or updates
- No user authentication or authorization

## Future Improvements

- Add hybrid search (keyword + semantic)
- Implement re-ranking for better retrieval
- Add multi-turn conversation support
- Implement document versioning
- Add user authentication
- Support more document formats (DOCX, PPTX)
- Add evaluation metrics dashboard
- Implement query expansion
- Add document summarization
- Support multiple LLM providers

## Important Notes

### RAG and Hallucinations

This system uses RAG to ground answers in retrieved documents, but it does not eliminate hallucinations. The LLM may still generate incorrect or misleading information. Always verify important information.

### Document Prompt Injection

Retrieved document content is used to construct prompts. Untrusted documents could attempt prompt injection. Do not treat retrieved content as trusted instructions. In production, implement content sanitization and prompt injection detection.

### Mock Mode

The mock LLM mode is for testing and demonstration only. It provides simple template responses. For production use, configure an LLM provider (OpenAI or compatible).

## License

This project is provided as-is for educational and portfolio purposes.

## Contact

For questions or issues, please open an issue in the repository.
