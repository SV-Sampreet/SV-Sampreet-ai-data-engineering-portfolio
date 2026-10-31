"""Anomaly detection module for transaction events."""
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, stddev, avg, when, lit
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detects anomalies in transaction data."""

    def __init__(self, threshold_multiplier: float = 3.0):
        """Initialize anomaly detector.

        Args:
            threshold_multiplier: Number of standard deviations for threshold
        """
        self.threshold_multiplier = threshold_multiplier

    def detect_statistical_anomalies(self, df: DataFrame) -> DataFrame:
        """Detect anomalies using statistical threshold (z-score).

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with anomaly flag
        """
        logger.info("Detecting statistical anomalies")

        # Calculate mean and std dev
        stats = df.select(
            avg("amount").alias("mean_amount"),
            stddev("amount").alias("std_amount")
        ).collect()[0]

        mean_amount = stats["mean_amount"]
        std_amount = stats["std_amount"]

        if std_amount is None or std_amount == 0:
            logger.warning("Cannot calculate standard deviation (single value or null)")
            return df.withColumn("is_anomaly", lit(False))

        threshold = mean_amount + (self.threshold_multiplier * std_amount)
        logger.info(f"Anomaly threshold: {threshold:.2f} (mean: {mean_amount:.2f}, std: {std_amount:.2f})")

        # Flag anomalies
        anomaly_df = df.withColumn(
            "is_anomaly",
            col("amount") > threshold
        )

        # Extract anomalies
        anomalies = anomaly_df.filter(col("is_anomaly") == True)

        if anomalies.count() > 0:
            logger.warning(f"Detected {anomalies.count()} anomalies")

        return anomaly_df

    def detect_anomalies_with_reason(self, df: DataFrame) -> DataFrame:
        """Detect anomalies and provide reason.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with anomaly information
        """
        logger.info("Detecting anomalies with reason")

        # Calculate statistics
        stats = df.select(
            avg("amount").alias("mean_amount"),
            stddev("amount").alias("std_amount")
        ).collect()[0]

        mean_amount = stats["mean_amount"]
        std_amount = stats["std_amount"]

        if std_amount is None or std_amount == 0:
            logger.warning("Standard deviation is zero or null, using mean-based threshold")
            # Use mean * multiplier as threshold if std dev is zero
            threshold = mean_amount * self.threshold_multiplier
        else:
            threshold = mean_amount + (self.threshold_multiplier * std_amount)

        # Add anomaly information
        anomaly_df = df.withColumn(
            "anomaly_reason",
            when(col("amount") > threshold,
                 f"Amount exceeds threshold of {threshold:.2f}"
            ).otherwise(None)
        ).withColumn(
            "anomaly_threshold",
            lit(threshold)
        )

        return anomaly_df
