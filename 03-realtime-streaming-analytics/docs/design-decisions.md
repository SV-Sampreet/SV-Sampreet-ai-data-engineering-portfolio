# Design Decisions

## Technology Choices

### PySpark Structured Streaming vs Spark Streaming (DStreams)

**Decision**: Use PySpark Structured Streaming

**Rationale**:
- Modern API built on DataFrame/Dataset
- Better integration with SQL
- Event time processing built-in
- Easier to debug and maintain
- Better fault tolerance with exactly-once support

**Trade-offs**:
- Slightly more complex for simple use cases
- Requires understanding of Spark SQL

### Local Files vs Kafka for Development

**Decision**: Support both with local files as primary

**Rationale**:
- Local files work without Docker/infrastructure
- Faster development iteration
- Lower barrier to entry
- Kafka integration added when needed

**Trade-offs**:
- Local files don't demonstrate true streaming
- Not suitable for production deployment
- Kafka integration incomplete in this version

### SQLite vs PostgreSQL

**Decision**: Support both with SQLite as fallback

**Rationale**:
- SQLite works without external database
- Self-contained, no setup required
- Good for development and testing
- PostgreSQL available for production-like scenarios

**Trade-offs**:
- SQLite not suitable for high-concurrency
- PostgreSQL integration incomplete in this version
- Different SQL dialects to handle

### Statistical Threshold vs ML for Anomaly Detection

**Decision**: Use statistical threshold (z-score based)

**Rationale**:
- Simple to implement and explain
- No training data required
- Configurable threshold
- Suitable for demonstration

**Trade-offs**:
- Less sophisticated than ML methods
- May not capture complex patterns
- Higher false positive rate

### Streamlit vs Custom Dashboard

**Decision**: Use Streamlit

**Rationale**:
- Pure Python, no frontend skills needed
- Built-in charts and components
- Easy to develop and iterate
- Good for data visualization

**Trade-offs**:
- Less customization than custom UI
- Performance limitations for real-time
- Limited component library

## Architecture Decisions

### Modular Component Design

**Decision**: Separate modules for each processing stage

**Rationale**:
- Single Responsibility Principle
- Easy testing of individual components
- Reusable components
- Clear data flow

**Trade-offs**:
- More files and boilerplate
- Slightly more complex initialization

### Memory Sink for Metrics

**Decision**: Write metrics to Spark memory tables

**Rationale**:
- Fast access for dashboard
- No database latency
- Simple implementation
- Good for development

**Trade-offs**:
- Data lost on restart
- Not suitable for production
- Limited memory capacity

### File-Based Checkpointing

**Decision**: Use local directory for checkpoints

**Rationale**:
- Spark default behavior
- Simple configuration
- Works without external storage
- Sufficient for development

**Trade-offs**:
- Not distributed
- Single point of failure
- Not suitable for production clusters

## Data Processing Decisions

### Tumbling Windows

**Decision**: Use tumbling (non-overlapping) windows

**Rationale**:
- Simple to understand
- Clear boundaries
- Good for time-based aggregations
- Easy to implement

**Trade-offs**:
- May miss events at boundaries
- Sliding windows would capture more context

### JSONL Format for Events

**Decision**: Use JSON Lines (one JSON per line)

**Rationale**:
- Simple to parse
- Human-readable
- Easy to append
- Works well with Spark

**Trade-offs**:
- Less efficient than binary formats
- No schema enforcement in file
- Larger file size

## Anomaly Detection Decisions

### Z-Score Based Threshold

**Decision**: Use mean + (multiplier × std_dev)

**Rationale**:
- Standard statistical method
- Easy to understand and tune
- Works without training data
- Configurable sensitivity

**Trade-offs**:
- Assumes normal distribution
- Sensitive to outliers in training
- May not work for all data patterns

### Per-Batch Calculation

**Decision**: Calculate statistics per batch

**Rationale**:
- Adapts to changing data patterns
- No separate training phase
- Simpler implementation
- Real-time adaptation

**Trade-offs**:
- May be unstable with small batches
- No historical context
- Higher variance in thresholds

## Testing Decisions

### Unit Tests for Components

**Decision**: Test each component independently

**Rationale**:
- Fast feedback
- Isolates failures
- Documents component behavior
- No external dependencies

**Trade-offs**:
- May miss integration issues
- Requires test fixtures

### Mock Spark for Tests

**Decision**: Use actual Spark but with local mode

**Rationale**:
- Tests actual Spark behavior
- No mock complexity
- More realistic testing
- Better coverage

**Trade-offs**:
- Slower than pure mocks
- Requires Java and Spark installation
- Some tests skip if Java incompatible

## Security Decisions

### Environment Variables for Configuration

**Decision**: Use python-dotenv for all sensitive config

**Rationale**:
- No credentials in code
- Standard practice
- Easy to configure per environment
- Supports .gitignore

**Trade-offs**:
- Requires documentation of all variables
- Easy to miss configuration

### No Data Encryption

**Decision**: No encryption at rest or in transit

**Rationale**:
- Uses synthetic/sample data
- No real personal or financial data
- Simpler implementation
- Suitable for portfolio project

**Trade-offs**:
- Not production-ready
- Would need encryption for real data

## Future Considerations

These decisions may be revisited:

1. **Kafka Integration**: If production deployment needed, complete Kafka producer/consumer
2. **PostgreSQL**: If multi-user or high-concurrency needed, complete PostgreSQL integration
3. **ML Anomaly Detection**: If accuracy insufficient, implement ML-based detection
4. **Dashboard Framework**: If customization needed, switch to React or custom UI
5. **Window Strategy**: If boundary events important, implement sliding windows
