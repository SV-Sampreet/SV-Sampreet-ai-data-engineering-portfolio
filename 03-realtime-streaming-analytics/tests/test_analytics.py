"""Tests for analytics module."""
import pytest
from pyspark.sql import SparkSession
from src.analytics.aggregator import AnalyticsAggregator
from src.analytics.anomaly_detector import AnomalyDetector


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
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
    schema = StructType([
        StructField("event_id", StringType(), False),
        StructField("timestamp", TimestampType(), False),
        StructField("user_id", StringType(), False),
        StructField("amount", DoubleType(), False),
        StructField("category", StringType(), False),
    ])
    data = [
        ("evt1", "2024-01-01 10:00:00", "user1", 100.0, "electronics"),
        ("evt2", "2024-01-01 10:01:00", "user2", 200.0, "clothing"),
        ("evt3", "2024-01-01 10:02:00", "user3", 150.0, "electronics"),
    ]
    return spark.createDataFrame(data, schema)


def test_calculate_metrics(spark, sample_df):
    """Test metrics calculation."""
    aggregator = AnalyticsAggregator()
    result = aggregator.calculate_metrics(sample_df)
    assert result.count() > 0


def test_anomaly_detection(spark, sample_df):
    """Test anomaly detection."""
    detector = AnomalyDetector(threshold_multiplier=3.0)
    result = detector.detect_anomalies_with_reason(sample_df)
    assert result.count() == 3  # All records should have anomaly_reason column
