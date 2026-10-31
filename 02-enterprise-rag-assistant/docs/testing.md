# Testing Documentation

## Test Strategy

The Enterprise RAG Assistant uses a multi-layered testing approach focusing on component testing and deterministic behavior.

## Test Organization

```
tests/
├── __init__.py
├── test_config.py          # Configuration tests
└── test_document_processor.py  # Document processing tests
```

## Test Categories

### 1. Unit Tests

Unit tests validate individual components in isolation.

#### Configuration Tests (`test_config.py`)

**Purpose**: Verify configuration loading and default values

**Test Cases**:
- `test_llm_config_defaults`: Verify default LLM configuration
- `test_llm_config_from_env`: Verify environment variable overrides
- `test_embedding_config_defaults`: Verify default embedding configuration
- `test_processing_config_defaults`: Verify default processing configuration
- `test_retrieval_config_defaults`: Verify default retrieval configuration
- `test_vector_db_config_defaults`: Verify default vector database configuration

**Coverage**:
- Configuration dataclasses
- Environment variable parsing
- Default value handling

#### Document Processor Tests (`test_document_processor.py`)

**Purpose**: Verify document processing logic

**Test Cases**:
- `test_extract_text_from_txt`: Verify text extraction from TXT files
- `test_chunk_text`: Verify text chunking with overlap
- `test_validate_file_size`: Verify file size validation
- `test_unsupported_format`: Verify error handling for unsupported formats

**Fixtures**:
- `processing_config`: Creates ProcessingConfig instance
- `document_processor`: Creates DocumentProcessor instance

**Coverage**:
- Text extraction from different formats
- Chunking logic
- File validation
- Error handling

### 2. Integration Tests

Integration tests verify component interactions. Currently limited due to:

- Embedding model download time
- ChromaDB initialization overhead
- No external API keys for testing

**Planned Integration Tests** (future):
- End-to-end document ingestion
- End-to-end query processing
- Vector store operations
- LLM integration (with mock)

### 3. Manual Testing

Manual testing procedures for features not covered by automated tests.

#### Document Ingestion

**Procedure**:
1. Start API server: `python -m src.api`
2. Upload sample document via curl or Streamlit
3. Verify ingestion success
4. Check index status

**Expected Results**:
- Document accepted (if valid format and size)
- Chunks added to vector store
- Index count increases

#### Query Processing

**Procedure**:
1. Ingest sample documents
2. Ask a question via API or Streamlit
3. Verify answer generation
4. Check citations

**Expected Results**:
- Relevant chunks retrieved
- Answer generated (mock or real LLM)
- Citations displayed with sources

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_config.py -v
```

### Run Specific Test

```bash
pytest tests/test_document_processor.py::test_chunk_text -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

## Test Results

### Latest Test Run

```bash
pytest tests/ -v
```

**Expected Output**:
```
tests/test_config.py::test_llm_config_defaults PASSED
tests/test_config.py::test_llm_config_from_env PASSED
tests/test_config.py::test_embedding_config_defaults PASSED
tests/test_config.py::test_processing_config_defaults PASSED
tests/test_config.py::test_retrieval_config_defaults PASSED
tests/test_config.py::test_vector_db_config_defaults PASSED
tests/test_document_processor.py::test_extract_text_from_txt PASSED
tests/test_document_processor.py::test_chunk_text PASSED
tests/test_document_processor.py::test_validate_file_size PASSED
tests/test_document_processor.py::test_unsupported_format PASSED

============================== 10 passed in ~2s ==============================
```

**Note**: Actual test results will be generated when tests are run in the target environment.

## Test Coverage

### Current Coverage

Estimated coverage based on test implementation:

- `config.py`: ~100% (all configuration classes tested)
- `document_processor.py`: ~70% (main functions tested)
- `embedding_manager.py`: ~0% (no automated tests yet)
- `vector_store.py`: ~0% (no automated tests yet)
- `llm_manager.py`: ~0% (no automated tests yet)
- `rag_orchestrator.py`: ~0% (no automated tests yet)
- `api.py`: ~0% (no automated tests yet)
- `ui.py`: ~0% (no automated tests for UI)

### Coverage Goals

Target coverage for production-ready code:
- Core business logic: >80%
- Configuration: 100%
- I/O operations: >60%
- Overall: >70%

## Test Data

### Sample Data for Testing

**Company Policy**: Employee conduct policy with leave policies, code of conduct
**Product Guide**: Cloud storage features, pricing, best practices

### Test Fixtures

**Processing Config Fixture**:
```python
@pytest.fixture
def processing_config():
    return ProcessingConfig()
```

**Document Processor Fixture**:
```python
@pytest.fixture
def document_processor(processing_config):
    return DocumentProcessor(processing_config)
```

## Evaluation Framework

### Retrieval Quality Metrics

**Recall@k**: Fraction of relevant documents retrieved in top-k results

**Precision@k**: Fraction of retrieved documents that are relevant

**Implementation**:
```python
def recall_at_k(retrieved_ids, relevant_ids, k):
    retrieved_k = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)
    return len(retrieved_k & relevant_set) / len(relevant_set)
```

### Groundedness Evaluation

**Metric**: Does the answer stay grounded in retrieved context?

**Evaluation Method**:
- Manual review of sample queries
- Check if answer introduces information not in context
- Use LLM-as-judge for automated evaluation

### Citation Correctness

**Metric**: Do citations point to relevant passages?

**Evaluation Method**:
- Manual review of citations
- Check if cited passages support the answer
- Verify source and page numbers are correct

## Test Maintenance

### Adding New Tests

When adding new features:

1. Create test function following naming convention: `test_<feature>_<behavior>`
2. Add descriptive docstring
3. Use fixtures for common setup
4. Assert expected behavior
5. Run tests to verify
6. Update coverage documentation

### Updating Tests

When modifying existing code:

1. Run existing tests to identify failures
2. Update tests to reflect new behavior
3. Add new tests for new functionality
4. Verify all tests pass
5. Update documentation

## Continuous Integration

### CI Configuration (Future)

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v --cov=src
```

## Troubleshooting Tests

### Model Download Issues

**Problem**: Tests fail due to model download

**Solutions**:
- Pre-download models before running tests
- Use mocked embeddings for faster tests
- Increase test timeout

### Temporary File Issues

**Problem**: Tests fail due to temporary file cleanup

**Solutions**:
- Use proper try/finally blocks
- Use pytest tmp_path fixture
- Explicitly clean up in teardown

### ChromaDB Issues

**Problem**: Tests fail due to ChromaDB initialization

**Solutions**:
- Use in-memory ChromaDB for tests
- Clean up database between tests
- Mock vector store for unit tests

## Known Test Limitations

1. **No Embedding Tests**: Embedding generation not tested (requires model download)
2. **No Vector Store Tests**: ChromaDB operations not tested
3. **No LLM Tests**: LLM integration not tested (uses mock)
4. **No API Tests**: FastAPI endpoints not tested
5. **No End-to-End Tests**: Complete pipeline not tested
6. **No Evaluation Tests**: Retrieval quality metrics not automated

## Future Test Improvements

1. Add embedding manager tests with mocked model
2. Add vector store tests with in-memory ChromaDB
3. Add LLM manager tests with mock responses
4. Add API integration tests using TestClient
5. Add end-to-end pipeline tests
6. Add evaluation metric tests
7. Add retrieval quality benchmarks
8. Add performance tests for large document sets
