"""PySpark Structured Streaming processor."""
import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, current_timestamp
from pyspark.sql.types import StructType

from src.config import SparkConfig, StreamingConfig, AnomalyConfig
from src.schemas import TRANSACTION_SCHEMA
from src.processing.validator import EventValidator
from src.analytics.aggregator import AnalyticsAggregator
from src.analytics.anomaly_detector import AnomalyDetector
from src.storage.database import DatabaseStorage

logger = logging.getLogger(__name__)


class StreamProcessor:
    """Processes streaming transaction data."""

    def __init__(self, spark_config: SparkConfig, streaming_config: StreamingConfig,
                 anomaly_config: AnomalyConfig, db_config):
        """Initialize stream processor.

        Args:
            spark_config: Spark configuration
            streaming_config: Streaming configuration
            anomaly_config: Anomaly detection configuration
            db_config: Database configuration
        """
        self.spark_config = spark_config
        self.streaming_config = streaming_config
        self.anomaly_config = anomaly_config
        self.db_config = db_config

        # Initialize Spark session
        self.spark = self._create_spark_session()

        # Initialize components
        self.validator = EventValidator()
        self.aggregator = AnalyticsAggregator()
        self.anomaly_detector = AnomalyDetector(anomaly_config.threshold_multiplier)
        self.storage = DatabaseStorage(self.spark, db_config)

    def _create_spark_session(self) -> SparkSession:
        """Create Spark session.

        Returns:
            SparkSession instance
        """
        logger.info(f"Creating Spark session: {self.spark_config.app_name}")

        spark = SparkSession.builder \
            .master(self.spark_config.master) \
            .appName(self.spark_config.app_name) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.streaming.checkpointLocation", self.streaming_config.checkpoint_dir) \
            .getOrCreate()

        logger.info("Spark session created")
        return spark

    def create_local_stream(self) -> DataFrame:
        """Create a local file-based stream.

        Returns:
            Streaming DataFrame
        """
        logger.info(f"Creating local stream from: {self.streaming_config.input_dir}")

        # Create input directory if it doesn't exist
        import os
        os.makedirs(self.streaming_config.input_dir, exist_ok=True)

        # Read stream from directory
        stream_df = self.spark.readStream \
            .schema(TRANSACTION_SCHEMA) \
            .option("maxFilesPerTrigger", 1) \
            .json(self.streaming_config.input_dir)

        logger.info("Local stream created")
        return stream_df

    def process_stream(self, stream_df: DataFrame):
        """Process the streaming data.

        Args:
            stream_df: Input streaming DataFrame
        """
        logger.info("Starting stream processing")

        # Validate and clean
        validated_df = self.validator.validate(stream_df)

        # Detect anomalies
        anomaly_df = self.anomaly_detector.detect_anomalies_with_reason(validated_df)

        # Extract anomalies
        anomalies_only = anomaly_df.filter(col("anomaly_reason").isNotNull())

        # Calculate metrics
        metrics_df = self.aggregator.calculate_metrics(validated_df, "1 minute")
        category_metrics_df = self.aggregator.calculate_category_metrics(validated_df, "1 minute")

        # Write output
        query1 = metrics_df.writeStream \
            .outputMode("complete") \
            .format("memory") \
            .queryName("metrics") \
            .start()

        query2 = category_metrics_df.writeStream \
            .outputMode("complete") \
            .format("memory") \
            .queryName("category_metrics") \
            .start()

        # Write anomalies to storage
        def write_anomalies_batch(df, batch_id):
            """Write anomalies in batch."""
            if df.count() > 0:
                self.storage.write_anomalies(df)
                logger.info(f"Batch {batch_id}: Written {df.count()} anomalies")

        query3 = anomalies_only.writeStream \
            .foreachBatch(write_anomalies_batch) \
            .outputMode("append") \
            .start()

        logger.info("Stream processing started")

        return query1, query2, query3

    def start_local_processing(self):
        """Start local file-based streaming processing."""
        logger.info("Starting local streaming processing")

        stream_df = self.create_local_stream()
        query1, query2, query3 = self.process_stream(stream_df)

        logger.info("Waiting for stream termination...")
        query3.awaitTermination()

    def stop(self):
        """Stop the Spark session."""
        logger.info("Stopping Spark session")
        self.spark.stop()
