"""Data validation module for quality checks."""
from typing import Tuple, List
from functools import reduce
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, count, when, isnan, isnull, to_date, lit, current_timestamp, struct
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates data quality and separates valid from invalid records."""

    def __init__(self, spark: SparkSession, config):
        """Initialize the data validator.

        Args:
            spark: SparkSession instance
            config: ValidationConfig instance
        """
        self.spark = spark
        self.config = config

    def validate_schema(self, df: DataFrame, required_columns: List[str]) -> Tuple[DataFrame, DataFrame]:
        """Check for required columns and separate records with missing columns.

        Args:
            df: Input DataFrame
            required_columns: List of column names that must be present

        Returns:
            Tuple of (valid_df, invalid_df) DataFrames
        """
        logger.info(f"Validating schema for required columns: {required_columns}")

        # Check which required columns are missing
        missing_columns = [col_name for col_name in required_columns if col_name not in df.columns]

        if missing_columns:
            error_msg = f"Missing required columns: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Check for null values in required columns
        null_conditions = [col(c).isNull() for c in required_columns]
        null_check = when(reduce(lambda x, y: x | y, null_conditions), True).otherwise(False)

        valid_df = df.filter(~null_check)
        invalid_df = df.filter(null_check)

        logger.info(f"Schema validation: {valid_df.count()} valid, {invalid_df.count()} invalid")

        return valid_df, invalid_df

    def check_null_threshold(self, df: DataFrame) -> bool:
        """Check if null values exceed the configured threshold.

        Args:
            df: Input DataFrame

        Returns:
            True if null values are within threshold, False otherwise
        """
        total_count = df.count()
        if total_count == 0:
            return True

        null_counts = df.select([count(when(isnull(c) | isnan(c), c)).alias(c) for c in df.columns])
        null_counts_dict = null_counts.first().asDict()
        total_nulls = sum(null_counts_dict.values())

        null_ratio = total_nulls / (total_count * len(df.columns))
        logger.info(f"Null ratio: {null_ratio:.3f}, threshold: {self.config.max_null_threshold}")

        return null_ratio <= self.config.max_null_threshold

    def remove_duplicates(self, df: DataFrame, key_columns: List[str]) -> DataFrame:
        """Remove duplicate records based on key columns.

        Args:
            df: Input DataFrame
            key_columns: Columns to use for duplicate detection

        Returns:
            DataFrame with duplicates removed
        """
        if not self.config.duplicate_check:
            logger.info("Duplicate check disabled, skipping")
            return df

        logger.info(f"Removing duplicates based on columns: {key_columns}")
        original_count = df.count()
        deduped_df = df.dropDuplicates(subset=key_columns)
        final_count = deduped_df.count()

        logger.info(f"Removed {original_count - final_count} duplicate records")
        return deduped_df

    def validate_dates(self, df: DataFrame, date_columns: List[str]) -> Tuple[DataFrame, DataFrame]:
        """Validate date columns and separate invalid dates.

        Args:
            df: Input DataFrame
            date_columns: List of date column names to validate

        Returns:
            Tuple of (valid_df, invalid_df) DataFrames
        """
        logger.info(f"Validating date columns: {date_columns}")

        date_conditions = []
        for date_col in date_columns:
            if date_col in df.columns:
                # Try to parse the date; if it fails, the record is invalid
                date_conditions.append(col(date_col).isNull())

        if not date_conditions:
            logger.info("No date columns to validate")
            return df, self.spark.createDataFrame(df.schema)

        # Combine all date conditions
        if len(date_conditions) == 1:
            invalid_date_check = date_conditions[0]
        else:
            from functools import reduce
            invalid_date_check = reduce(lambda x, y: x | y, date_conditions)

        valid_df = df.filter(~invalid_date_check)
        invalid_df = df.filter(invalid_date_check)

        logger.info(f"Date validation: {valid_df.count()} valid, {invalid_df.count()} invalid")

        return valid_df, invalid_df

    def validate_business_rules(self, df: DataFrame) -> Tuple[DataFrame, DataFrame]:
        """Validate business rules and separate invalid records.

        Args:
            df: Input DataFrame

        Returns:
            Tuple of (valid_df, invalid_df) DataFrames
        """
        logger.info("Validating business rules")

        # Example business rules:
        # - quantity must be positive
        # - unit_price must be positive
        # - total_price should equal quantity * unit_price (within tolerance)
        invalid_conditions = []

        if "quantity" in df.columns:
            invalid_conditions.append((col("quantity") <= 0, "quantity must be positive"))

        if "unit_price" in df.columns:
            invalid_conditions.append((col("unit_price") <= 0, "unit_price must be positive"))

        if "total_price" in df.columns and "quantity" in df.columns and "unit_price" in df.columns:
            # Check if total_price matches quantity * unit_price (allow 1% tolerance)
            expected_total = col("quantity") * col("unit_price")
            invalid_conditions.append((
                (col("total_price") < expected_total * 0.99) | (col("total_price") > expected_total * 1.01),
                "total_price does not match quantity * unit_price"
            ))

        if not invalid_conditions:
            logger.info("No business rules to validate")
            return df, self.spark.createDataFrame(df.schema)

        # Combine all invalid conditions
        invalid_check = invalid_conditions[0][0]
        for condition, _ in invalid_conditions[1:]:
            invalid_check = invalid_check | condition

        valid_df = df.filter(~invalid_check)
        invalid_df = df.filter(invalid_check)

        logger.info(f"Business rule validation: {valid_df.count()} valid, {invalid_df.count()} invalid")

        return valid_df, invalid_df

    def create_quarantine_record(self, invalid_df: DataFrame, error_type: str,
                                 error_message: str, source_file: str) -> DataFrame:
        """Create quarantine records from invalid data.

        Args:
            invalid_df: DataFrame with invalid records
            error_type: Type of error (e.g., "SCHEMA_ERROR", "DATE_ERROR")
            error_message: Descriptive error message
            source_file: Source file name

        Returns:
            DataFrame in quarantine schema format
        """
        from pyspark.sql.functions import to_json

        # Convert invalid records to JSON strings
        invalid_json = invalid_df.select(to_json(struct([col(c) for c in invalid_df.columns])).alias("original_data"))

        # Add metadata
        quarantine_df = invalid_json.withColumn("error_type", lit(error_type)) \
                                    .withColumn("error_message", lit(error_message)) \
                                    .withColumn("timestamp", current_timestamp()) \
                                    .withColumn("source_file", lit(source_file))

        return quarantine_df
