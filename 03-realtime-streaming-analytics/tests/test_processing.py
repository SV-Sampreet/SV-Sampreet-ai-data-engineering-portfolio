"""Tests for data processing module."""
import pytest
from pyspark.sql import SparkSession
from src.processing.validator import EventValidator
from src.schemas import TRANSACTION_SCHEMA


@pytest.fixture(scope="module")
def spark():
    """Create Spark session for testing."""
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
    """Create sample DataFrame for testing."""
    data = [
        ("evt1", "2024-01-01 10:00:00", "user1", 100.0, "electronics", "credit_card", "completed"),
        ("evt2", "2024-01-01 10:01:00", "user2", 200.0, "clothing", "debit_card", "completed"),
        ("evt3", "2024-01-01 10:02:00", "user3", -50.0, "food", "paypal", "completed"),  # Invalid amount
        ("evt1", "2024-01-01 10:03:00", "user4", 150.0, "travel", "credit_card", "completed"),  # Duplicate
    ]
    return spark.createDataFrame(data, TRANSACTION_SCHEMA)


def test_validate_amount(spark, sample_df):
    """Test amount validation."""
    validator = EventValidator()
    result = validator.validate_amount(sample_df)
    assert result.count() == 3  # Should filter out negative amount


def test_remove_duplicates(spark, sample_df):
    """Test duplicate removal."""
    validator = EventValidator()
    result = validator.remove_duplicates(sample_df)
    assert result.count() == 3  # Should remove duplicate event_id
