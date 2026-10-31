"""Tests for analytics module."""
import pytest
from pyspark.sql import SparkSession
from src.analytics import DataAnalytics


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
def sample_sales_df(spark):
    """Create a sample sales DataFrame for testing."""
    data = [
        ("ORD001", "CUST001", "PROD001", "Laptop", "Electronics", 2, 899.99, 1799.98, 2024, 1, 15, "North", 1799.98),
        ("ORD002", "CUST002", "PROD002", "Mouse", "Electronics", 5, 29.99, 149.95, 2024, 1, 16, "South", 149.95),
        ("ORD003", "CUST001", "PROD003", "Hub", "Electronics", 3, 49.99, 149.97, 2024, 1, 17, "East", 149.97),
        ("ORD004", "CUST003", "PROD004", "Keyboard", "Electronics", 1, 129.99, 129.99, 2024, 2, 18, "West", 129.99),
        ("ORD005", "CUST004", "PROD005", "Monitor", "Electronics", 1, 349.99, 349.99, 2024, 2, 19, "North", 349.99),
    ]
    return spark.createDataFrame(data, [
        "order_id", "customer_id", "product_id", "product_name", "category",
        "quantity", "unit_price", "total_price", "year", "month", "day",
        "region", "revenue"
    ])


def test_calculate_revenue_by_region(spark, sample_sales_df):
    """Test revenue calculation by region."""
    analytics = DataAnalytics(spark)
    result = analytics.calculate_revenue_by_region(sample_sales_df)

    assert result.count() > 0
    assert "total_revenue" in result.columns
    assert "order_count" in result.columns
    assert "avg_order_value" in result.columns


def test_calculate_revenue_by_product(spark, sample_sales_df):
    """Test revenue calculation by product."""
    analytics = DataAnalytics(spark)
    result = analytics.calculate_revenue_by_product(sample_sales_df)

    assert result.count() > 0
    assert "total_revenue" in result.columns
    assert "total_quantity" in result.columns


def test_calculate_monthly_trends(spark, sample_sales_df):
    """Test monthly trend calculation."""
    analytics = DataAnalytics(spark)
    result = analytics.calculate_monthly_trends(sample_sales_df)

    assert result.count() > 0
    assert "year" in result.columns
    assert "month" in result.columns
    assert "total_revenue" in result.columns


def test_calculate_customer_metrics(spark, sample_sales_df):
    """Test customer metrics calculation."""
    analytics = DataAnalytics(spark)
    result = analytics.calculate_customer_metrics(sample_sales_df)

    assert result.count() > 0
    assert "customer_id" in result.columns
    assert "total_spent" in result.columns
    assert "order_count" in result.columns


def test_calculate_summary_metrics(spark, sample_sales_df):
    """Test summary metrics calculation."""
    analytics = DataAnalytics(spark)
    result = analytics.calculate_summary_metrics(sample_sales_df)

    assert isinstance(result, dict)
    assert "total_orders" in result
    assert "total_revenue" in result
    assert "unique_customers" in result
    assert "unique_products" in result
    assert result["total_orders"] == 5
    assert result["unique_customers"] == 4
    assert result["unique_products"] == 5


def test_generate_analytics_report(spark, sample_sales_df):
    """Test comprehensive analytics report generation."""
    analytics = DataAnalytics(spark)
    result = analytics.generate_analytics_report(sample_sales_df)

    assert isinstance(result, dict)
    assert "summary" in result
    assert "revenue_by_region" in result
    assert "revenue_by_product" in result
    assert "monthly_trends" in result
    assert "customer_metrics" in result
