"""Schema definitions for streaming analytics."""
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, IntegerType, BooleanType


# Transaction event schema
TRANSACTION_SCHEMA = StructType([
    StructField("event_id", StringType(), nullable=False),
    StructField("timestamp", TimestampType(), nullable=False),
    StructField("user_id", StringType(), nullable=False),
    StructField("amount", DoubleType(), nullable=False),
    StructField("category", StringType(), nullable=False),
    StructField("payment_method", StringType(), nullable=True),
    StructField("status", StringType(), nullable=False),
])

# Processed metrics schema
METRICS_SCHEMA = StructType([
    StructField("window_start", TimestampType(), nullable=False),
    StructField("window_end", TimestampType(), nullable=False),
    StructField("event_count", IntegerType(), nullable=False),
    StructField("total_amount", DoubleType(), nullable=False),
    StructField("avg_amount", DoubleType(), nullable=False),
    StructField("category", StringType(), nullable=True),
])

# Anomaly schema
ANOMALY_SCHEMA = StructType([
    StructField("event_id", StringType(), nullable=False),
    StructField("timestamp", TimestampType(), nullable=False),
    StructField("user_id", StringType(), nullable=False),
    StructField("amount", DoubleType(), nullable=False),
    StructField("category", StringType(), nullable=False),
    StructField("reason", StringType(), nullable=False),
    StructField("threshold", DoubleType(), nullable=False),
])
