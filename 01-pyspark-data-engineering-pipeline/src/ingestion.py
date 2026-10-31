"""Data ingestion module for reading raw data files."""
import os
from typing import Optional
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType
import logging

logger = logging.getLogger(__name__)


class DataIngestion:
    """Handles ingestion of raw data files into Spark DataFrames."""

    def __init__(self, spark: SparkSession, config):
        """Initialize the data ingestion component.

        Args:
            spark: SparkSession instance
            config: StorageConfig instance
        """
        self.spark = spark
        self.config = config

    def read_csv(self, file_path: str, schema: Optional[StructType] = None, header: bool = True) -> DataFrame:
        """Read a CSV file into a DataFrame.

        Args:
            file_path: Path to the CSV file
            schema: Optional schema to enforce
            header: Whether the file has a header row

        Returns:
            DataFrame containing the CSV data

        Raises:
            FileNotFoundError: If the file does not exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")

        logger.info(f"Reading CSV file: {file_path}")

        reader = self.spark.read
        if schema:
            reader = reader.schema(schema)

        df = reader.csv(file_path, header=header, mode="PERMISSIVE")
        logger.info(f"Successfully read {df.count()} records from {file_path}")
        return df

    def read_json(self, file_path: str, schema: Optional[StructType] = None) -> DataFrame:
        """Read a JSON file into a DataFrame.

        Args:
            file_path: Path to the JSON file
            schema: Optional schema to enforce

        Returns:
            DataFrame containing the JSON data

        Raises:
            FileNotFoundError: If the file does not exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")

        logger.info(f"Reading JSON file: {file_path}")

        reader = self.spark.read
        if schema:
            reader = reader.schema(schema)

        df = reader.json(file_path)
        logger.info(f"Successfully read {df.count()} records from {file_path}")
        return df

    def read_directory(self, directory_path: str, file_format: str = "csv",
                       schema: Optional[StructType] = None, header: bool = True) -> DataFrame:
        """Read all files of a specific format from a directory.

        Args:
            directory_path: Path to the directory
            file_format: File format (csv, json, parquet)
            schema: Optional schema to enforce
            header: Whether files have header rows (for CSV)

        Returns:
            DataFrame containing combined data from all files

        Raises:
            FileNotFoundError: If the directory does not exist
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Input directory not found: {directory_path}")

        logger.info(f"Reading {file_format} files from directory: {directory_path}")

        # Find files matching the format
        if file_format == "csv":
            files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
        elif file_format == "json":
            files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
        elif file_format == "parquet":
            files = [f for f in os.listdir(directory_path) if f.endswith('.parquet')]
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

        if not files:
            logger.warning(f"No {file_format} files found in {directory_path}")
            return self.spark.createDataFrame([], schema or StructType())

        logger.info(f"Found {len(files)} {file_format} files")

        # Read and combine all files
        dfs = []
        for file in files:
            file_path = os.path.join(directory_path, file)
            if file_format == "csv":
                df = self.read_csv(file_path, schema, header)
            elif file_format == "json":
                df = self.read_json(file_path, schema)
            elif file_format == "parquet":
                df = self.spark.read.parquet(file_path)
            dfs.append(df)

        if dfs:
            combined_df = dfs[0]
            for df in dfs[1:]:
                combined_df = combined_df.union(df)
            logger.info(f"Combined total: {combined_df.count()} records")
            return combined_df
        else:
            return self.spark.createDataFrame([], schema or StructType())
