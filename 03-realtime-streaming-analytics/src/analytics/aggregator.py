"""Windowed analytics aggregation module."""
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, sum as _sum, avg, window
import logging

logger = logging.getLogger(__name__)


class AnalyticsAggregator:
    """Calculates windowed analytics on streaming data."""

    def __init__(self):
        """Initialize analytics aggregator."""
        pass

    def calculate_metrics(self, df: DataFrame, window_duration: str = "1 minute") -> DataFrame:
        """Calculate windowed metrics.

        Args:
            df: Input DataFrame
            window_duration: Window duration (e.g., "1 minute", "5 minutes")

        Returns:
            DataFrame with windowed metrics
        """
        logger.info(f"Calculating metrics with window: {window_duration}")

        # Add window column
        windowed_df = df.groupBy(
            window(col("timestamp"), window_duration)
        ).agg(
            count("event_id").alias("event_count"),
            _sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount")
        )

        # Extract window start/end
        windowed_df = windowed_df.select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("event_count"),
            col("total_amount"),
            col("avg_amount")
        )

        return windowed_df

    def calculate_category_metrics(self, df: DataFrame, window_duration: str = "1 minute") -> DataFrame:
        """Calculate windowed metrics by category.

        Args:
            df: Input DataFrame
            window_duration: Window duration

        Returns:
            DataFrame with category-level metrics
        """
        logger.info(f"Calculating category metrics with window: {window_duration}")

        windowed_df = df.groupBy(
            window(col("timestamp"), window_duration),
            col("category")
        ).agg(
            count("event_id").alias("event_count"),
            _sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount")
        )

        windowed_df = windowed_df.select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("category"),
            col("event_count"),
            col("total_amount"),
            col("avg_amount")
        )

        return windowed_df

    def calculate_status_metrics(self, df: DataFrame, window_duration: str = "1 minute") -> DataFrame:
        """Calculate metrics by transaction status.

        Args:
            df: Input DataFrame
            window_duration: Window duration

        Returns:
            DataFrame with status metrics
        """
        logger.info(f"Calculating status metrics with window: {window_duration}")

        windowed_df = df.groupBy(
            window(col("timestamp"), window_duration),
            col("status")
        ).agg(
            count("event_id").alias("event_count"),
            _sum("amount").alias("total_amount")
        )

        windowed_df = windowed_df.select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("status"),
            col("event_count"),
            col("total_amount")
        )

        return windowed_df
