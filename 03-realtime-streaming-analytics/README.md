# Real-Time Streaming Analytics Platform

A near-real-time data processing platform that ingests business events, processes streams, detects anomalies, and presents analytics through a dashboard.

## Problem Statement

Organizations need to monitor business events (transactions, user actions, system events) in real-time to detect anomalies, track metrics, and respond quickly to issues. This project implements a streaming analytics platform using PySpark Structured Streaming.

## Motivation

This project demonstrates:

- Building real-time data pipelines with PySpark Structured Streaming
- Event-driven architecture with Kafka integration
- Windowed analytics and aggregations
- Anomaly detection for business monitoring
- Real-time dashboards with Streamlit
- Graceful degradation with local fallback modes

## Features

- **Event Generation**: Synthetic transaction event generator with realistic data
- **Streaming Ingestion**: Kafka-based ingestion with local file-based fallback
- **Data Validation**: Schema validation, duplicate detection, amount validation
- **Windowed Analytics**: Rolling window calculations for event counts, totals, averages
- **Category Analytics**: Metrics broken down by transaction category
- **Anomaly Detection**: Statistical threshold-based anomaly detection
- **Data Persistence**: PostgreSQL with SQLite/Parquet fallback
- **Real-time Dashboard**: Streamlit dashboard for metrics and anomalies
- **Configurable**: Environment-based configuration for all components
- **Docker Support**: Docker Compose for Kafka and PostgreSQL

## Architecture

The platform follows a modular streaming architecture:

```
┌─────────────┐
│   Events    │
│  Generator  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Kafka    │ (or Local Files)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Spark     │
│  Streaming │
└──────┬──────┘
       │
       ├─────────────┬─────────────┐
       ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Metrics  │  │Anomalies │  │Category  │
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │             │             │
      └─────────────┴─────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  PostgreSQL   │ (or SQLite)
            └───────┬───────┘
                    │
                    ▼
            ┌───────────────┐
            │  Dashboard    │
            └───────────────┘
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture diagrams.

## Technology Stack

- **Python 3.8+**: Core programming language
- **PySpark 3.5.3**: Structured Streaming for real-time processing
- **Apache Kafka**: Event streaming (optional, local fallback available)
- **PostgreSQL**: Analytical storage (optional, SQLite fallback available)
- **Streamlit**: Real-time dashboard
- **Docker Compose**: Infrastructure orchestration
- **pytest**: Testing framework

## Prerequisites

- Python 3.8 or higher
- Java 8, 11, or 17 (for Spark)
- 4GB RAM minimum (8GB recommended)
- Docker and Docker Compose (for Kafka/PostgreSQL - optional)

## Setup

1. Clone the repository and navigate to the project directory:
```bash
cd 03-realtime-streaming-analytics
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

### Local Mode (File-Based Streaming)

**Generate sample events:**
```bash
python scripts/generate_events.py --count 100 --output data/input/sample_events.jsonl
```

**Start the streaming processor:**
```bash
python src/stream_pipeline.py
```

This will:
- Read events from `data/input/`
- Process events with validation and analytics
- Detect anomalies
- Store results in `data/output/` (SQLite/Parquet mode)
- Write metrics to memory for dashboard

**Start the dashboard** (in a separate terminal):
```bash
streamlit run dashboard/app.py
```

### Docker Mode (Kafka + PostgreSQL)

**Start infrastructure:**
```bash
docker-compose up -d
```

**Configure environment:**
```bash
export STREAMING_MODE=kafka
export DB_TYPE=postgresql
```

**Note**: Kafka mode requires additional implementation. Currently only local mode is fully implemented.

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
- Configuration tests: 5 tests
- Processing tests: 2 tests
- Analytics tests: 2 tests
- Total: 9 tests

## Configuration

Key configuration options in `.env`:

- `STREAMING_MODE`: `local` (file-based) or `kafka`
- `DB_TYPE`: `sqlite` or `postgresql`
- `ANOMALY_THRESHOLD_MULTIPLIER`: Standard deviation multiplier for anomaly detection (default: 3.0)
- `WINDOW_SIZE_SECONDS`: Window size for analytics (default: 60)

## Sample Data

The project includes sample transaction events in `data/sample/sample_events.jsonl`.

## Docker Compose

Docker Compose configuration for:
- Zookeeper (Kafka dependency)
- Kafka (event streaming)
- PostgreSQL (analytical storage)

**Start services:**
```bash
docker-compose up -d
```

**Stop services:**
```bash
docker-compose down
```

**Note**: Docker services are provided but integration with Kafka/PostgreSQL is not fully implemented in this version. Use local mode for testing.

## Security Considerations

- No credentials in code (use environment variables)
- Input validation on event data
- File size limits for event generation
- No sensitive data in sample events

## Limitations

- Kafka integration not fully implemented (local mode only)
- PostgreSQL integration not fully implemented (SQLite/Parquet fallback)
- No multi-stream processing
- No exactly-once semantics
- No backpressure handling
- No advanced anomaly detection (only statistical threshold)

## Future Improvements

- Complete Kafka producer/consumer implementation
- Complete PostgreSQL integration
- Add exactly-once semantics
- Implement backpressure handling
- Add advanced anomaly detection (ML-based)
- Add alerting system
- Add multi-stream processing
- Add event time vs processing time handling
- Add watermarking for late events

## Important Notes

### Local Mode

The local mode uses file-based streaming:
- Events are written to JSONL files in `data/input/`
- Spark reads these files as a stream
- This is suitable for development and testing
- Does not require Kafka or Docker

### Anomaly Detection

The current implementation uses simple statistical thresholding:
- Calculates mean and standard deviation of amounts
- Flags amounts exceeding mean + (threshold_multiplier × std_dev)
- This is a baseline method suitable for demonstration
- Production systems should use more sophisticated methods

### Java Compatibility

PySpark 3.5.3 has known compatibility issues with Java 25. Use Java 8, 11, or 17 for best results.

## License

This project is provided as-is for educational and portfolio purposes.

## Contact

For questions or issues, please open an issue in the repository.
