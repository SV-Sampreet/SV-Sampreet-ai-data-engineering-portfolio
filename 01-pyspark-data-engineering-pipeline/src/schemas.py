"""Schema definitions for the data pipeline."""
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, DecimalType, TimestampType


# Sales data schema
SALES_SCHEMA = StructType([
    StructField("order_id", StringType(), nullable=False),
    StructField("customer_id", StringType(), nullable=False),
    StructField("product_id", StringType(), nullable=False),
    StructField("product_name", StringType(), nullable=False),
    StructField("category", StringType(), nullable=True),
    StructField("quantity", IntegerType(), nullable=False),
    StructField("unit_price", DecimalType(10, 2), nullable=False),
    StructField("total_price", DecimalType(10, 2), nullable=False),
    StructField("order_date", DateType(), nullable=False),
    StructField("region", StringType(), nullable=True),
    StructField("payment_method", StringType(), nullable=True),
])

# Customer data schema
CUSTOMER_SCHEMA = StructType([
    StructField("customer_id", StringType(), nullable=False),
    StructField("customer_name", StringType(), nullable=False),
    StructField("email", StringType(), nullable=True),
    StructField("signup_date", DateType(), nullable=False),
    StructField("region", StringType(), nullable=True),
    StructField("customer_segment", StringType(), nullable=True),
])

# Quarantine record schema (includes error information)
QUARANTINE_SCHEMA = StructType([
    StructField("original_data", StringType(), nullable=False),
    StructField("error_type", StringType(), nullable=False),
    StructField("error_message", StringType(), nullable=False),
    StructField("timestamp", TimestampType(), nullable=False),
    StructField("source_file", StringType(), nullable=False),
])
