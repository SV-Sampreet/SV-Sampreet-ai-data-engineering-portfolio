# PySpark Data Engineering Pipeline

A production-style batch data engineering pipeline that transforms raw business data into validated, analytics-ready datasets using Apache PySpark.

## Problem Statement

Organizations need reliable data pipelines to process raw business data into clean, validated datasets for analytics and reporting. This project implements a complete end-to-end data pipeline with ingestion, validation, transformation, analytics, and storage capabilities.

## Motivation

This project demonstrates:

- Building modular, maintainable data pipelines with PySpark
- Implementing data quality checks and error handling
- Working with distributed data processing at scale
- Using Parquet for efficient columnar storage
- Designing idempotent, rerunnable pipelines
- Handling both local filesystem and HDFS storage backends

## Features

- **Data Ingestion**: Read CSV and JSON files from local or HDFS storage
- **Schema Validation**: Enforce required columns and data types
- **Data Quality Checks**: Null thresholds, duplicate detection, date validation, business rule validation
- **Quarantine System**: Separate invalid records with error explanations
- **Data Transformation**: Clean text, standardize dates, derive columns, join datasets
- **Business Analytics**: Revenue by region/product, monthly trends, customer metrics
- **Storage Options**: Write to local filesystem or HDFS in Parquet format
- **Idempotent Design**: Safe to rerun without double-counting
- **Comprehensive Logging**: Track pipeline execution and data quality metrics

## Architecture

The pipeline follows a modular architecture with separate components for each stage:

```
┌─────────────┐
│   Ingestion │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Validation  │───► Quarantine
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Transform    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Analytics  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Storage   │
└─────────────┘
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture diagrams.

## Technology Stack

- **Python 3.8+**: Core programming language
- **PySpark 3.5.3**: Distributed data processing framework
- **Apache Spark**: Unified analytics engine
- **Parquet**: Columnar storage format
- **pytest**: Testing framework
- **python-dotenv**: Environment variable management

## Prerequisites

- Python 3.8 or higher
- Java 8, 11, or 17 (required for Spark)
  - **Note**: Java 25+ has known compatibility issues with PySpark 3.5.3
- 4GB RAM minimum (8GB recommended for larger datasets)
- Optional: Hadoop HDFS cluster for HDFS backend

## Setup

1. Clone the repository and navigate to the project directory:
```bash
cd 01-pyspark-data-engineering-pipeline
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

## Execution

### Run the complete pipeline:

```bash
python src/pipeline.py
```

### Run with custom input files:

```python
from src.pipeline import DataPipeline

pipeline = DataPipeline()
result = pipeline.run(
    sales_file="data/sample/sample_sales.csv",
    customers_file="data/sample/sample_customers.csv"
)
pipeline.stop()
```

### Expected output:

The pipeline will:
1. Read sample data from `data/sample/`
2. Validate and clean the data
3. Calculate analytics metrics
4. Write curated datasets to `data/output/`
5. Write quarantine records to `data/quarantine/` (if any)
6. Print an execution summary

Output directories:
- `data/output/sales_curated/`: Cleaned and enriched sales data
- `data/output/revenue_by_region/`: Revenue aggregated by region
- `data/output/revenue_by_product/`: Revenue aggregated by product
- `data/output/monthly_trends/`: Monthly revenue trends
- `data/output/customer_metrics/`: Customer-level metrics
- `data/quarantine/`: Invalid records with error explanations

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
- Configuration tests: 7 tests
- Transformation tests: 4 tests
- Analytics tests: 6 tests
- Total: 17 tests

## Example Output

```
================================================================================
PIPELINE EXECUTION SUMMARY
================================================================================
Status: SUCCESS
Input Records: 30
Valid Records: 30
Invalid Records: 0
Quarantine Records: 0
Output Records: 30

Analytics Summary:
  total_orders: 30
  total_revenue: 4299.3
  avg_order_value: 143.31
  unique_customers: 15
  unique_products: 30
================================================================================
```

## Data Quality Report

The pipeline tracks:
- Input record count
- Valid record count
- Invalid record count (with reasons)
- Quarantine record count
- Output record count

Invalid records are categorized by:
- Schema errors (missing required columns)
- Date errors (invalid date formats)
- Business rule errors (negative quantities, price mismatches)

## Configuration

Key configuration options in `.env`:

- `STORAGE_BACKEND`: `local` or `hdfs`
- `INPUT_DIR`: Input data directory
- `OUTPUT_DIR`: Output data directory
- `QUARANTINE_DIR`: Quarantine data directory
- `ENABLE_VALIDATION`: Enable/disable data validation
- `MAX_NULL_THRESHOLD`: Maximum allowed null ratio (0.0-1.0)
- `DUPLICATE_CHECK`: Enable/disable duplicate removal
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## HDFS Integration

To use HDFS storage:

1. Set `STORAGE_BACKEND=hdfs` in `.env`
2. Configure HDFS connection parameters:
   - `HDFS_NAMENODE`: HDFS namenode hostname
   - `HDFS_PORT`: HDFS port (default: 9000)
   - `HDFS_USER`: HDFS username

**Note**: HDFS integration requires a running Hadoop cluster. Integration tests for HDFS are skipped when the cluster is unavailable.

## Troubleshooting

### Java not found
Ensure Java is installed and JAVA_HOME is set:
```bash
java -version
echo $JAVA_HOME
```

### Out of memory errors
Increase Spark memory in `src/config.py`:
```python
driver_memory: str = "4g"
executor_memory: str = "4g"
```

### File not found errors
Check that input files exist in the configured directory:
```bash
ls data/sample/
```

### PySpark import errors
Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

## Limitations

- HDFS integration not tested in environments without Hadoop clusters
- Streaming mode not implemented (batch-only)
- No automatic schema evolution for changing data structures
- No built-in data lineage tracking
- Local mode only (no cluster deployment configuration)

## Future Improvements

- Add support for streaming data with Spark Structured Streaming
- Implement schema registry integration
- Add data lineage and metadata tracking
- Support for additional file formats (Avro, ORC)
- Implement incremental processing for large datasets
- Add Airflow or similar orchestration integration
- Add automated data quality monitoring and alerting
- Support for cloud storage (S3, GCS, Azure Blob)

## License

This project is provided as-is for educational and portfolio purposes.

## Contact

For questions or issues, please open an issue in the repository.
