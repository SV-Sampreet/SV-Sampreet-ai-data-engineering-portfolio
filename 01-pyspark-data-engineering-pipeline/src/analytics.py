"""Analytics module for calculating business metrics."""
from pyspark.sql import DataFrame
from pyspark.sql.functions import sum, count, avg, col, desc, asc, round
import logging

logger = logging.getLogger(__name__)


class DataAnalytics:
    """Calculates business metrics and aggregations."""

    def __init__(self, spark):
        """Initialize the analytics component.

        Args:
            spark: SparkSession instance
        """
        self.spark = spark

    def calculate_revenue_by_region(self, df: DataFrame) -> DataFrame:
        """Calculate total revenue by region.

        Args:
            df: Input DataFrame with sales data

        Returns:
            DataFrame with revenue by region
        """
        logger.info("Calculating revenue by region")

        if "region" not in df.columns or "revenue" not in df.columns:
            logger.warning("Required columns for revenue by region not found")
            return self.spark.createDataFrame()

        result = df.groupBy("region") \
                   .agg(
                       sum("revenue").alias("total_revenue"),
                       count("order_id").alias("order_count"),
                       avg("revenue").alias("avg_order_value")
                   ) \
                   .orderBy(desc("total_revenue"))

        return result

    def calculate_revenue_by_product(self, df: DataFrame) -> DataFrame:
        """Calculate total revenue by product.

        Args:
            df: Input DataFrame with sales data

        Returns:
            DataFrame with revenue by product
        """
        logger.info("Calculating revenue by product")

        if "product_name" not in df.columns or "revenue" not in df.columns:
            logger.warning("Required columns for revenue by product not found")
            return self.spark.createDataFrame()

        result = df.groupBy("product_id", "product_name", "category") \
                   .agg(
                       sum("revenue").alias("total_revenue"),
                       sum("quantity").alias("total_quantity"),
                       count("order_id").alias("order_count")
                   ) \
                   .orderBy(desc("total_revenue"))

        return result

    def calculate_monthly_trends(self, df: DataFrame) -> DataFrame:
        """Calculate monthly revenue trends.

        Args:
            df: Input DataFrame with sales data

        Returns:
            DataFrame with monthly trends
        """
        logger.info("Calculating monthly trends")

        if "year" not in df.columns or "month" not in df.columns or "revenue" not in df.columns:
            logger.warning("Required columns for monthly trends not found")
            return self.spark.createDataFrame()

        result = df.groupBy("year", "month") \
                   .agg(
                       sum("revenue").alias("total_revenue"),
                       count("order_id").alias("order_count"),
                       avg("revenue").alias("avg_order_value")
                   ) \
                   .orderBy("year", "month")

        return result

    def calculate_customer_metrics(self, df: DataFrame) -> DataFrame:
        """Calculate customer-level metrics.

        Args:
            df: Input DataFrame with sales data

        Returns:
            DataFrame with customer metrics
        """
        logger.info("Calculating customer metrics")

        if "customer_id" not in df.columns or "revenue" not in df.columns:
            logger.warning("Required columns for customer metrics not found")
            return self.spark.createDataFrame()

        result = df.groupBy("customer_id") \
                   .agg(
                       sum("revenue").alias("total_spent"),
                       count("order_id").alias("order_count"),
                       avg("revenue").alias("avg_order_value")
                   ) \
                   .orderBy(desc("total_spent"))

        return result

    def calculate_summary_metrics(self, df: DataFrame) -> dict:
        """Calculate overall summary metrics.

        Args:
            df: Input DataFrame with sales data

        Returns:
            Dictionary with summary metrics
        """
        logger.info("Calculating summary metrics")

        metrics = {}

        if "order_id" in df.columns:
            metrics["total_orders"] = df.count()

        if "revenue" in df.columns:
            revenue_result = df.agg(sum("revenue").alias("total_revenue")).collect()[0]
            metrics["total_revenue"] = float(revenue_result["total_revenue"]) if revenue_result["total_revenue"] else 0.0

            avg_result = df.agg(avg("revenue").alias("avg_order_value")).collect()[0]
            metrics["avg_order_value"] = float(avg_result["avg_order_value"]) if avg_result["avg_order_value"] else 0.0

        if "customer_id" in df.columns:
            metrics["unique_customers"] = df.select("customer_id").distinct().count()

        if "product_id" in df.columns:
            metrics["unique_products"] = df.select("product_id").distinct().count()

        return metrics

    def generate_analytics_report(self, df: DataFrame) -> dict:
        """Generate a comprehensive analytics report.

        Args:
            df: Input DataFrame with sales data

        Returns:
            Dictionary containing all analytics results
        """
        logger.info("Generating comprehensive analytics report")

        report = {
            "summary": self.calculate_summary_metrics(df),
            "revenue_by_region": self.calculate_revenue_by_region(df),
            "revenue_by_product": self.calculate_revenue_by_product(df),
            "monthly_trends": self.calculate_monthly_trends(df),
            "customer_metrics": self.calculate_customer_metrics(df)
        }

        return report
