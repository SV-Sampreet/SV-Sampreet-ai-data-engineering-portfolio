# Design Decisions

## Technology Choices

### sentence-transformers vs OpenAI Embeddings

**Decision**: Use sentence-transformers (local)

**Rationale**:
- No API key required for development
- Lower cost for production
- Better privacy (data stays local)
- Sufficient quality for most use cases
- Fast inference on CPU

**Trade-offs**:
- Slower than OpenAI embeddings
- Requires model download (~500MB)
- Less customization than API-based embeddings

### ChromaDB vs Pinecone/Weaviate

**Decision**: Use ChromaDB (local)

**Rationale**:
- Open-source and free
- Easy local development
- No external dependencies
- Simple API
- Persistent storage out of the box

**Trade-offs**:
- Single-machine only
- Less scalable than cloud options
- No managed service
- Limited advanced features

### Mock LLM vs OpenAI-Only

**Decision**: Support both with mock fallback

**Rationale**:
- Enables testing without API keys
- Lower barrier to entry
- Demonstrates fallback strategy
- Production-ready with API key

**Trade-offs**:
- Mock responses are simplistic
- Two code paths to maintain
- Mock doesn't demonstrate real LLM capabilities

### FastAPI vs Flask

**Decision**: Use FastAPI

**Rationale**:
- Built-in data validation with Pydantic
- Automatic API documentation
- Async support
- Type hints
- Modern and fast

**Trade-offs**:
- Slightly more complex than Flask
- Newer ecosystem (though mature now)

### Streamlit vs Custom React App

**Decision**: Use Streamlit

**Rationale**:
- Pure Python, no frontend skills needed
- Rapid development
- Built-in components
- Easy deployment

**Trade-offs**:
- Less customization than custom UI
- Performance limitations for complex apps
- Limited component library

## Architecture Decisions

### Modular Component Design

**Decision**: Separate components for each stage

**Rationale**:
- Single Responsibility Principle
- Easy testing
- Reusable components
- Clear data flow

**Trade-offs**:
- More files and boilerplate
- Slightly more complex initialization

### Configurable Chunking

**Decision**: Make chunk size and overlap configurable

**Rationale**:
- Different documents require different chunk sizes
- Optimization for different use cases
- Research and experimentation

**Trade-offs**:
- Configuration complexity
- Need to tune for best results

### Persistent Vector Store

**Decision**: Use persistent ChromaDB storage

**Rationale**:
- Survives application restarts
- No need to re-embed documents
- Faster startup
- Better user experience

**Trade-offs**:
- Disk space usage
- Need to manage storage
- Potential for stale data

## Data Processing Decisions

### Page-Level Metadata

**Decision**: Track page numbers and source files

**Rationale**:
- Enables precise citations
- Helps users locate information
- Improves trust in answers
- Useful for debugging

**Trade-offs**:
- Slightly more storage
- Only applies to PDFs (not TXT/MD)

### Chunk Overlap

**Decision**: Use overlapping chunks (default 50 characters)

**Rationale**:
- Prevents context loss at chunk boundaries
- Improves retrieval for questions spanning chunks
- Better answer quality

**Trade-offs**:
- More chunks to store
- More storage and computation
- Potential redundancy

### Cosine Similarity

**Decision**: Use cosine similarity for vector search

**Rationale**:
- Standard for semantic search
- Works well with sentence-transformers
- Angle-based (magnitude-independent)
- Good performance

**Trade-offs**:
- May not be optimal for all use cases
- Other options: dot product, Euclidean distance

## LLM Integration Decisions

### Context Window Handling

**Decision**: Simple concatenation of top-k chunks

**Rationale**:
- Simple implementation
- Works for small to medium contexts
- Easy to understand

**Trade-offs**:
- May exceed context window for large k
- No intelligent context selection
- May include irrelevant chunks

### Prompt Engineering

**Decision**: Use explicit instruction in prompt

**Rationale**:
- Guides LLM behavior
- Explicitly states to use context
- Asks for refusal if insufficient context

**Trade-offs**:
- LLM may still hallucinate
- No chain-of-thought or advanced prompting
- May need tuning for different models

## Security Decisions

### File Upload Validation

**Decision**: Validate file type and size

**Rationale**:
- Prevents abuse
- Limits resource usage
- Security best practice

**Trade-offs**:
- May block legitimate edge cases
- Configuration complexity

### No Document Logging

**Decision**: Don't log document contents

**Rationale**:
- Privacy protection
- Reduces log size
- Security best practice

**Trade-offs**:
- Harder debugging
- No audit trail of content

## Testing Decisions

### Unit Tests for Components

**Decision**: Test each component independently

**Rationale**:
- Fast feedback
- Isolates failures
- Documents component behavior

**Trade-offs**:
- May miss integration issues
- Requires test fixtures

### Mock LLM for Tests

**Decision**: Use mock LLM in all tests

**Rationale**:
- No API key required
- Faster tests
- Deterministic behavior
- No cost

**Trade-offs**:
- Doesn't test real LLM integration
- May miss API-specific issues

## Future Considerations

These decisions may be revisited:

1. **Vector Database**: If scaling needed, migrate to Pinecone or Weaviate
2. **Embedding Model**: If quality insufficient, try OpenAI embeddings
3. **LLM Provider**: Add support for Anthropic, Google, local models
4. **Retrieval Strategy**: Add hybrid search, re-ranking
5. **UI Framework**: If customization needed, switch to React
