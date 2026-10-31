"""Storage module for writing processed data."""
import os
from typing import Optional
from pyspark.sql import DataFrame, SparkSession
import logging

logger = logging.getLogger(__name__)


class DataStorage:
    """Handles storage of processed data to various backends."""

    def __init__(self, spark: SparkSession, config):
        """Initialize the storage component.

        Args:
            spark: SparkSession instance
            config: StorageConfig instance
        """
        self.spark = spark
        self.config = config

    def _ensure_directory(self, directory: str) -> None:
        """Ensure a directory exists (for local filesystem).

        Args:
            directory: Directory path
        """
        if self.config.backend == "local":
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")

    def write_parquet(self, df: DataFrame, output_path: str, mode: str = "overwrite",
                      partition_by: Optional[list] = None) -> None:
        """Write a DataFrame to Parquet format.

        Args:
            df: DataFrame to write
            output_path: Output directory path
            mode: Write mode (overwrite, append, etc.)
            partition_by: Optional list of columns to partition by
        """
        if self.config.backend == "local":
            self._ensure_directory(output_path)
            full_path = output_path
        elif self.config.backend == "hdfs":
            full_path = f"{self.config.get_hdfs_url()}/{output_path}"
        else:
            raise ValueError(f"Unsupported storage backend: {self.config.backend}")

        logger.info(f"Writing Parquet to {full_path} with mode={mode}")

        writer = df.write.mode(mode)
        if partition_by:
            writer = writer.partitionBy(*partition_by)

        writer.parquet(full_path)
        logger.info(f"Successfully wrote {df.count()} records to Parquet")

    def write_csv(self, df: DataFrame, output_path: str, mode: str = "overwrite",
                  header: bool = True) -> None:
        """Write a DataFrame to CSV format.

        Args:
            df: DataFrame to write
            output_path: Output directory path
            mode: Write mode (overwrite, append, etc.)
            header: Whether to include header row
        """
        if self.config.backend == "local":
            self._ensure_directory(output_path)
            full_path = output_path
        elif self.config.backend == "hdfs":
            full_path = f"{self.config.get_hdfs_url()}/{output_path}"
        else:
            raise ValueError(f"Unsupported storage backend: {self.config.backend}")

        logger.info(f"Writing CSV to {full_path} with mode={mode}")

        df.write.mode(mode).option("header", header).csv(full_path)
        logger.info(f"Successfully wrote {df.count()} records to CSV")

    def write_quarantine(self, df: DataFrame, output_path: str) -> None:
        """Write quarantine records to storage.

        Args:
            df: DataFrame with quarantine records
            output_path: Output directory path
        """
        if df.count() == 0:
            logger.info("No quarantine records to write")
            return

        logger.info(f"Writing {df.count()} quarantine records to {output_path}")
        self.write_parquet(df, output_path, mode="append")

    def read_parquet(self, input_path: str) -> DataFrame:
        """Read a Parquet file into a DataFrame.

        Args:
            input_path: Input file or directory path

        Returns:
            DataFrame containing the Parquet data
        """
        if self.config.backend == "local":
            full_path = input_path
        elif self.config.backend == "hdfs":
            full_path = f"{self.config.get_hdfs_url()}/{input_path}"
        else:
            raise ValueError(f"Unsupported storage backend: {self.config.backend}")

        logger.info(f"Reading Parquet from {full_path}")
        df = self.spark.read.parquet(full_path)
        logger.info(f"Successfully read {df.count()} records from Parquet")

        return df
