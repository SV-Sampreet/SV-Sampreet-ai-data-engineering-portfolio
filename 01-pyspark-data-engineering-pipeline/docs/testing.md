# Testing Documentation

## Test Strategy

The PySpark Data Engineering Pipeline uses a multi-layered testing approach to ensure code quality, correctness, and reliability.

## Test Organization

```
tests/
├── __init__.py
├── test_config.py          # Configuration tests
├── test_transformation.py  # Data transformation tests
└── test_analytics.py       # Analytics calculation tests
```

## Test Categories

### 1. Unit Tests

Unit tests validate individual components in isolation.

#### Configuration Tests (`test_config.py`)

**Purpose**: Verify configuration loading and default values

**Test Cases**:
- `test_spark_config_defaults`: Verify default Spark configuration values
- `test_spark_config_from_env`: Verify environment variable overrides
- `test_storage_config_defaults`: Verify default storage configuration
- `test_storage_config_hdfs_url`: Verify HDFS URL generation
- `test_validation_config_defaults`: Verify default validation configuration
- `test_validation_config_from_env`: Verify validation environment overrides
- `test_logging_config_defaults`: Verify default logging configuration

**Coverage**:
- Configuration dataclasses
- Environment variable parsing
- Default value handling
- HDFS URL construction

#### Transformation Tests (`test_transformation.py`)

**Purpose**: Verify data transformation logic

**Test Cases**:
- `test_clean_text_columns`: Verify text trimming and uppercasing
- `test_derive_date_parts`: Verify date part extraction (year, month, day)
- `test_calculate_revenue_metrics`: Verify revenue column creation
- `test_add_derived_columns`: Verify calculated total column

**Fixtures**:
- `spark`: Creates a local Spark session for testing
- `sample_df`: Creates a sample DataFrame with test data

**Coverage**:
- Text cleaning functions
- Date standardization
- Derived column calculation
- Revenue metric calculation

#### Analytics Tests (`test_analytics.py`)

**Purpose**: Verify analytics calculations

**Test Cases**:
- `test_calculate_revenue_by_region`: Verify regional revenue aggregation
- `test_calculate_revenue_by_product`: Verify product revenue aggregation
- `test_calculate_monthly_trends`: Verify monthly trend calculation
- `test_calculate_customer_metrics`: Verify customer-level metrics
- `test_calculate_summary_metrics`: Verify overall summary metrics
- `test_generate_analytics_report`: Verify comprehensive report generation

**Fixtures**:
- `spark`: Creates a local Spark session for testing
- `sample_sales_df`: Creates a sample sales DataFrame with realistic data

**Coverage**:
- Revenue aggregations
- Time-based analytics
- Customer analytics
- Summary metrics
- Report generation

### 2. Integration Tests

Integration tests verify component interactions. Currently, integration tests are limited due to:

- No HDFS cluster available in development environment
- Pipeline end-to-end test would require full data flow
- Integration tests marked as conditional in design

**Planned Integration Tests** (when infrastructure available):
- End-to-end pipeline execution
- HDFS read/write operations
- Multi-file directory ingestion
- Quarantine record persistence

### 3. Manual Testing

Manual testing procedures for features not covered by automated tests:

#### Pipeline Execution

**Procedure**:
1. Navigate to project directory
2. Activate virtual environment
3. Run pipeline: `python src/pipeline.py`
4. Verify output files in `data/output/`
5. Verify quarantine records in `data/quarantine/` (if any)
6. Check console output for execution summary

**Expected Results**:
- All input records processed
- Output files created in correct locations
- Execution summary printed to console
- No errors in logs

#### Data Quality Verification

**Procedure**:
1. Load output Parquet files
2. Verify record counts match expectations
3. Check for null values in required columns
4. Verify derived columns are calculated correctly
5. Validate business rules (positive quantities, consistent prices)

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
pytest tests/test_analytics.py::test_calculate_summary_metrics -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

### Run with Verbose Output

```bash
pytest tests/ -vv -s
```

## Test Results

### Latest Test Run

```bash
pytest tests/ -v
```

**Expected Output**:
```
tests/test_config.py::test_spark_config_defaults PASSED
tests/test_config.py::test_spark_config_from_env PASSED
tests/test_config.py::test_storage_config_defaults PASSED
tests/test_config.py::test_storage_config_hdfs_url PASSED
tests/test_config.py::test_validation_config_defaults PASSED
tests/test_config.py::test_validation_config_from_env PASSED
tests/test_config.py::test_logging_config_defaults PASSED
tests/test_transformation.py::test_clean_text_columns PASSED
tests/test_transformation.py::test_derive_date_parts PASSED
tests/test_transformation.py::test_calculate_revenue_metrics PASSED
tests/test_transformation.py::test_add_derived_columns PASSED
tests/test_analytics.py::test_calculate_revenue_by_region PASSED
tests/test_analytics.py::test_calculate_revenue_by_product PASSED
tests/test_analytics.py::test_calculate_monthly_trends PASSED
tests/test_analytics.py::test_calculate_customer_metrics PASSED
tests/test_analytics.py::test_calculate_summary_metrics PASSED
tests/test_analytics.py::test_generate_analytics_report PASSED

============================== 17 passed in 15.23s ==============================
```

**Note**: Actual test results will be generated when tests are run in the target environment.

## Test Coverage

### Current Coverage

Estimated coverage based on test implementation:

- `config.py`: ~100% (all configuration classes tested)
- `transformation.py`: ~80% (main transformation functions tested)
- `analytics.py`: ~90% (all analytics functions tested)
- `ingestion.py`: ~0% (no automated tests yet)
- `validation.py`: ~0% (no automated tests yet)
- `storage.py`: ~0% (no automated tests yet)
- `pipeline.py`: ~0% (no automated tests yet)

### Coverage Goals

Target coverage for production-ready code:
- Core business logic: >90%
- Configuration: 100%
- I/O operations: >70%
- Overall: >80%

## Test Data

### Sample Data for Testing

**Sales Data** (`data/sample/sample_sales.csv`):
- 30 realistic sales records
- Multiple regions (North, South, East, West)
- Various product categories
- Date range: January-March 2024
- Valid business data (positive quantities, consistent prices)

**Customer Data** (`data/sample/sample_customers.csv`):
- 15 customer records
- Various regions and segments
- Realistic signup dates
- Valid email formats

### Test Fixtures

**Spark Session Fixture**:
```python
@pytest.fixture
def spark():
    spark = SparkSession.builder \
        .master("local[1]") \
        .appName("test") \
        .getOrCreate()
    yield spark
    spark.stop()
```

**Sample DataFrame Fixture**:
```python
@pytest.fixture
def sample_df(spark):
    data = [("  north  ", "  electronics  ", "2024-01-15", 2, 99.99)]
    return spark.createDataFrame(data, ["region", "category", "order_date", "quantity", "unit_price"])
```

## Test Maintenance

### Adding New Tests

When adding new features:

1. Create test function following naming convention: `test_<feature>_<behavior>`
2. Add descriptive docstring explaining what is being tested
3. Use fixtures for common setup (Spark session, test data)
4. Assert expected behavior with clear assertions
5. Run tests to verify they pass
6. Update coverage documentation

### Updating Tests

When modifying existing code:

1. Run existing tests to identify failures
2. Update tests to reflect new behavior
3. Add new tests for new functionality
4. Verify all tests pass
5. Update documentation if test behavior changes

### Test Data Management

- Keep test data small and focused
- Use deterministic data (no random generation)
- Store test data in `tests/fixtures/` if complex
- Document test data assumptions
- Clean up test data after tests if creating temporary files

## Continuous Integration

### CI Configuration (Future)

When setting up CI/CD:

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

### Test Gates

Recommended test gates:
- All tests must pass before merging
- Coverage must not decrease
- New features must include tests
- Critical bugs must include regression tests

## Troubleshooting Tests

### Spark Session Issues

**Problem**: Tests fail with Spark session errors

**Solutions**:
- Ensure Java is installed and JAVA_HOME is set
- Check that PySpark is installed correctly
- Verify sufficient memory is available
- Try reducing parallelism: `master("local[1]")`

### Fixture Issues

**Problem**: Fixtures not found or fail to initialize

**Solutions**:
- Check fixture is defined in `conftest.py` or test file
- Verify fixture name matches usage
- Check fixture yields and cleans up correctly

### Timeout Issues

**Problem**: Tests timeout on slow systems

**Solutions**:
- Increase pytest timeout: `pytest --timeout=300`
- Reduce test data size
- Use `local[1]` instead of `local[*]`
- Close Spark sessions explicitly in fixtures

### Path Issues

**Problem**: Tests fail due to incorrect file paths

**Solutions**:
- Use absolute paths or relative to test file
- Use `os.path.dirname(__file__)` for test directory
- Create temporary directories for file I/O tests
- Clean up temporary files in teardown

## Known Test Limitations

1. **HDFS Integration**: Tests for HDFS storage backend are skipped when cluster unavailable
2. **End-to-End Pipeline**: No automated test for complete pipeline execution
3. **Performance**: No performance or scalability tests
4. **Recovery**: No tests for Spark recovery behavior
5. **Large Datasets**: Tests use small datasets; large dataset behavior untested

## Future Test Improvements

1. Add integration tests for ingestion module
2. Add unit tests for validation module
3. Add unit tests for storage module
4. Add end-to-end pipeline test
5. Add HDFS integration tests (conditional)
6. Add performance benchmarks
7. Add tests for error scenarios
8. Add tests for edge cases (empty data, all invalid data, etc.)
