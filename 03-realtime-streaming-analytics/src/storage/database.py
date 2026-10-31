"""Database storage module for metrics and anomalies."""
import os
import logging
from typing import Optional
from pyspark.sql import DataFrame, SparkSession

logger = logging.getLogger(__name__)


class DatabaseStorage:
    """Handles database storage for analytics data."""

    def __init__(self, spark: SparkSession, config):
        """Initialize database storage.

        Args:
            spark: SparkSession instance
            config: DatabaseConfig instance
        """
        self.spark = spark
        self.config = config
        self.connection_string = config.get_connection_string()

    def write_metrics(self, df: DataFrame, table_name: str = "metrics", mode: str = "append"):
        """Write metrics to database.

        Args:
            df: DataFrame with metrics
            table_name: Target table name
            mode: Write mode (append, overwrite)
        """
        logger.info(f"Writing metrics to {table_name}")

        if self.config.db_type == "sqlite":
            # For SQLite, write to Parquet as fallback
            output_path = f"data/output/{table_name}"
            df.write.mode(mode).parquet(output_path)
            logger.info(f"Written metrics to Parquet: {output_path}")
        else:
            # For PostgreSQL, write directly
            df.write \
                .format("jdbc") \
                .option("url", self.connection_string) \
                .option("dbtable", table_name) \
                .mode(mode) \
                .save()
            logger.info(f"Written metrics to PostgreSQL table: {table_name}")

    def write_anomalies(self, df: DataFrame, table_name: str = "anomalies", mode: str = "append"):
        """Write anomalies to database.

        Args:
            df: DataFrame with anomalies
            table_name: Target table name
            mode: Write mode
        """
        logger.info(f"Writing anomalies to {table_name}")

        if self.config.db_type == "sqlite":
            output_path = f"data/output/{table_name}"
            df.write.mode(mode).parquet(output_path)
            logger.info(f"Written anomalies to Parquet: {output_path}")
        else:
            df.write \
                .format("jdbc") \
                .option("url", self.connection_string) \
                .option("dbtable", table_name) \
                .mode(mode) \
                .save()
            logger.info(f"Written anomalies to PostgreSQL table: {table_name}")

    def read_metrics(self, table_name: str = "metrics") -> Optional[DataFrame]:
        """Read metrics from database.

        Args:
            table_name: Table name to read

        Returns:
            DataFrame with metrics or None if not found
        """
        logger.info(f"Reading metrics from {table_name}")

        if self.config.db_type == "sqlite":
            output_path = f"data/output/{table_name}"
            if os.path.exists(output_path):
                return self.spark.read.parquet(output_path)
            else:
                logger.warning(f"Metrics file not found: {output_path}")
                return None
        else:
            try:
                return self.spark.read \
                    .format("jdbc") \
                    .option("url", self.connection_string) \
                    .option("dbtable", table_name) \
                    .load()
            except Exception as e:
                logger.error(f"Failed to read from PostgreSQL: {e}")
                return None

    def read_anomalies(self, table_name: str = "anomalies") -> Optional[DataFrame]:
        """Read anomalies from database.

        Args:
            table_name: Table name to read

        Returns:
            DataFrame with anomalies or None if not found
        """
        logger.info(f"Reading anomalies from {table_name}")

        if self.config.db_type == "sqlite":
            output_path = f"data/output/{table_name}"
            if os.path.exists(output_path):
                return self.spark.read.parquet(output_path)
            else:
                logger.warning(f"Anomalies file not found: {output_path}")
                return None
        else:
            try:
                return self.spark.read \
                    .format("jdbc") \
                    .option("url", self.connection_string) \
                    .option("dbtable", table_name) \
                    .load()
            except Exception as e:
                logger.error(f"Failed to read from PostgreSQL: {e}")
                return None
