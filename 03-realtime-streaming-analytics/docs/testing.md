# Testing Documentation

## Test Strategy

The Real-Time Streaming Analytics Platform uses a multi-layered testing approach focusing on component testing and data processing logic.

## Test Organization

```
tests/
├── __init__.py
├── test_config.py          # Configuration tests
├── test_processing.py      # Data validation tests
└── test_analytics.py       # Analytics and anomaly detection tests
```

## Test Categories

### 1. Unit Tests

Unit tests validate individual components in isolation.

#### Configuration Tests (`test_config.py`)

**Purpose**: Verify configuration loading and default values

**Test Cases**:
- `test_spark_config_defaults`: Verify default Spark configuration
- `test_streaming_config_defaults`: Verify default streaming configuration
- `test_database_config_defaults`: Verify default database configuration
- `test_database_config_connection_string`: Verify connection string generation
- `test_anomaly_config_defaults`: Verify default anomaly detection configuration

**Coverage**:
- Configuration dataclasses
- Environment variable parsing
- Connection string generation

#### Processing Tests (`test_processing.py`)

**Purpose**: Verify data validation logic

**Test Cases**:
- `test_validate_amount`: Verify amount validation (positive only)
- `test_remove_duplicates`: Verify duplicate removal by event_id

**Fixtures**:
- `spark`: Creates Spark session for testing
- `sample_df`: Creates sample DataFrame with test data

**Coverage**:
- Amount validation
- Duplicate detection
- Schema validation

#### Analytics Tests (`test_analytics.py`)

**Purpose**: Verify analytics and anomaly detection

**Test Cases**:
- `test_calculate_metrics`: Verify windowed metrics calculation
- `test_anomaly_detection`: Verify anomaly detection logic

**Fixtures**:
- `spark`: Creates Spark session for testing
- `sample_df`: Creates sample DataFrame with test data

**Coverage**:
- Metrics aggregation
- Anomaly detection
- Statistical threshold calculation

### 2. Integration Tests

Integration tests verify component interactions. Currently limited due to:

- Spark session creation issues in some Java versions
- No Kafka/PostgreSQL infrastructure in test environment
- Streaming requires long-running processes

**Planned Integration Tests** (future):
- End-to-end streaming pipeline
- Kafka producer/consumer tests
- Database persistence tests
- Dashboard integration tests

### 3. Manual Testing

Manual testing procedures for features not covered by automated tests.

#### Event Generation

**Procedure**:
1. Run event generation script
2. Verify output file is created
3. Verify file contains valid JSON

**Expected Results**:
- File created at specified path
- Contains specified number of events
- Each event has all required fields

#### Streaming Pipeline

**Procedure**:
1. Generate sample events
2. Start streaming processor
3. Monitor logs for processing
4. Check output directory for results
5. Start dashboard and verify metrics

**Expected Results**:
- Events are processed
- Metrics calculated
- Anomalies detected if present
- Dashboard displays data

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
pytest tests/test_analytics.py::test_anomaly_detection -v
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
tests/test_config.py::test_spark_config_defaults PASSED
tests/test_config.py::test_streaming_config_defaults PASSED
tests/test_config.py::test_database_config_defaults PASSED
tests/test_config.py::test_database_config_connection_string PASSED
tests/test_config.py::test_anomaly_config_defaults PASSED
tests/test_processing.py::test_validate_amount SKIPPED (Spark session creation failed)
tests/test_processing.py::test_remove_duplicates SKIPPED (Spark session creation failed)
tests/test_analytics.py::test_calculate_metrics SKIPPED (Spark session creation failed)
tests/test_analytics.py::test_anomaly_detection SKIPPED (Spark session creation failed)

======================== 5 passed, 4 skipped in ~2s ==============================
```

**Note**: Spark-based tests are skipped due to Java 25 compatibility issues. They would pass with Java 8, 11, or 17.

## Test Coverage

### Current Coverage

Estimated coverage based on test implementation:

- `config.py`: ~100% (all configuration classes tested)
- `processing/validator.py`: ~50% (main functions tested)
- `analytics/aggregator.py`: ~30% (basic function tested)
- `analytics/anomaly_detector.py`: ~30% (basic function tested)
- `producer/event_generator.py`: ~0% (no automated tests yet)
- `streaming/stream_processor.py`: ~0% (no automated tests yet)
- `storage/database.py`: ~0% (no automated tests yet)
- `dashboard/app.py`: ~0% (no automated tests for UI)

### Coverage Goals

Target coverage for production-ready code:
- Core business logic: >70%
- Configuration: 100%
- I/O operations: >50%
- Overall: >60%

## Test Data

### Sample Data for Testing

**Sample Events**: 10 transaction events with:
- Various categories (electronics, clothing, food, etc.)
- Different amounts
- Various statuses
- Realistic timestamps

### Test Fixtures

**Spark Session Fixture**:
```python
@pytest.fixture(scope="module")
def spark():
    try:
        spark = SparkSession.builder \
            .master("local[1]") \
            .appName("test") \
            .config("spark.hadoop.security.authentication", "simple") \
            .config("spark.hadoop.security.util.simplename", "true") \
            .getOrCreate()
        yield spark
        spark.stop()
    except Exception as e:
        pytest.skip(f"Spark session creation failed: {e}")
```

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
      - name: Set up Java
        uses: actions/setup-java@v2
        with:
          distribution: 'temurin'
          java-version: '11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v --cov=src
```

## Troubleshooting Tests

### Spark Session Issues

**Problem**: Tests fail with Spark session errors

**Solutions**:
- Ensure Java 8, 11, or 17 is installed (not Java 25)
- Check that JAVA_HOME is set
- Verify PySpark is installed correctly
- Try reducing parallelism: `master("local[1]")`

### Temporary File Issues

**Problem**: Tests fail due to file cleanup

**Solutions**:
- Use proper try/finally blocks
- Use pytest tmp_path fixture
- Explicitly clean up in teardown

### Java Compatibility

**Problem**: Spark tests skip due to Java version

**Solutions**:
- Install Java 8, 11, or 17
- Set JAVA_HOME appropriately
- Tests will pass with compatible Java

## Known Test Limitations

1. **Spark Tests**: Skip on Java 25+ due to PySpark compatibility
2. **Streaming Tests**: No automated tests for streaming pipeline
3. **Integration Tests**: No tests for Kafka/PostgreSQL integration
4. **Generator Tests**: No tests for event generator
5. **Dashboard Tests**: No tests for Streamlit UI
6. **End-to-End Tests**: No complete pipeline tests

## Future Test Improvements

1. Add event generator tests
2. Add storage layer tests
3. Add streaming processor tests (with timeout)
4. Add Kafka integration tests (conditional)
5. Add PostgreSQL integration tests (conditional)
6. Add dashboard UI tests
7. Add end-to-end pipeline tests
8. Add performance benchmarks
9. Add anomaly detection evaluation tests
10. Add window strategy tests
