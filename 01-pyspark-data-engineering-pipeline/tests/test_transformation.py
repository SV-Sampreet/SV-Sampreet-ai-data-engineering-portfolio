"""Tests for data transformation module."""
import pytest
import sys
from pyspark.sql import SparkSession
from src.transformation import DataTransformer


@pytest.fixture(scope="module")
def spark():
    """Create a Spark session for testing."""
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


@pytest.fixture
def sample_df(spark):
    """Create a sample DataFrame for testing."""
    data = [
        ("  north  ", "  electronics  ", "2024-01-15", 2, 99.99),
        ("  south  ", "  furniture  ", "2024-01-16", 1, 199.99),
        ("  east  ", "  accessories  ", "2024-01-17", 3, 49.99),
    ]
    return spark.createDataFrame(data, ["region", "category", "order_date", "quantity", "unit_price"])


def test_clean_text_columns(spark, sample_df):
    """Test cleaning text columns."""
    transformer = DataTransformer(spark)
    result = transformer.clean_text_columns(sample_df, ["region", "category"])

    # Check that text is trimmed and uppercased
    regions = [row.region for row in result.collect()]
    assert all(r == r.upper() and not r.startswith(" ") for r in regions)


def test_derive_date_parts(spark, sample_df):
    """Test deriving date parts."""
    transformer = DataTransformer(spark)
    result = transformer.derive_date_parts(sample_df, "order_date")

    # Check that date part columns exist
    assert "year" in result.columns
    assert "month" in result.columns
    assert "day" in result.columns

    # Check values
    row = result.first()
    assert row.year == 2024
    assert row.month == 1


def test_calculate_revenue_metrics(spark):
    """Test revenue metrics calculation."""
    data = [("ORD001", 2, 99.99, 199.98)]
    df = spark.createDataFrame(data, ["order_id", "quantity", "unit_price", "total_price"])

    transformer = DataTransformer(spark)
    result = transformer.calculate_revenue_metrics(df)

    assert "revenue" in result.columns
    assert result.first().revenue == 199.98


def test_add_derived_columns(spark):
    """Test adding derived columns."""
    data = [("ORD001", 2, 99.99)]
    df = spark.createDataFrame(data, ["order_id", "quantity", "unit_price"])

    transformer = DataTransformer(spark)
    result = transformer.add_derived_columns(df)

    assert "calculated_total" in result.columns
    assert result.first().calculated_total == 199.98
