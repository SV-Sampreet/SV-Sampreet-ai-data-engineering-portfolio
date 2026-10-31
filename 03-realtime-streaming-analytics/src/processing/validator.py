"""Data validation module for streaming events."""
from functools import reduce
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, when, isnan, isnull, to_timestamp
import logging

logger = logging.getLogger(__name__)


class EventValidator:
    """Validates streaming event data."""

    def __init__(self):
        """Initialize event validator."""
        pass

    def validate_schema(self, df: DataFrame, required_columns: list) -> DataFrame:
        """Validate schema and filter invalid records.

        Args:
            df: Input DataFrame
            required_columns: List of required column names

        Returns:
            Validated DataFrame
        """
        logger.info(f"Validating schema for required columns: {required_columns}")

        # Check for null values in required columns
        null_conditions = [col(c).isNull() for c in required_columns]
        null_check = when(reduce(lambda x, y: x | y, null_conditions), True).otherwise(False)

        valid_df = df.filter(~null_check)
        invalid_count = df.count() - valid_df.count()

        if invalid_count > 0:
            logger.warning(f"Filtered {invalid_count} invalid records due to null values")

        return valid_df

    def validate_amount(self, df: DataFrame) -> DataFrame:
        """Validate amount field (must be positive).

        Args:
            df: Input DataFrame

        Returns:
            Validated DataFrame
        """
        logger.info("Validating amount field")

        valid_df = df.filter(col("amount") > 0)
        invalid_count = df.count() - valid_df.count()

        if invalid_count > 0:
            logger.warning(f"Filtered {invalid_count} records with non-positive amounts")

        return valid_df

    def parse_timestamp(self, df: DataFrame, timestamp_col: str = "timestamp") -> DataFrame:
        """Parse timestamp column.

        Args:
            df: Input DataFrame
            timestamp_col: Timestamp column name

        Returns:
            DataFrame with parsed timestamp
        """
        logger.info(f"Parsing timestamp column: {timestamp_col}")

        df = df.withColumn(timestamp_col, to_timestamp(col(timestamp_col)))

        return df

    def remove_duplicates(self, df: DataFrame, key_column: str = "event_id") -> DataFrame:
        """Remove duplicate events based on event_id.

        Args:
            df: Input DataFrame
            key_column: Column to use for duplicate detection

        Returns:
            DataFrame with duplicates removed
        """
        logger.info(f"Removing duplicates based on {key_column}")

        original_count = df.count()
        deduped_df = df.dropDuplicates([key_column])
        final_count = deduped_df.count()

        removed = original_count - final_count
        if removed > 0:
            logger.warning(f"Removed {removed} duplicate records")

        return deduped_df

    def validate(self, df: DataFrame) -> DataFrame:
        """Run all validations.

        Args:
            df: Input DataFrame

        Returns:
            Validated DataFrame
        """
        required_columns = ["event_id", "timestamp", "user_id", "amount", "category", "status"]

        df = self.validate_schema(df, required_columns)
        df = self.parse_timestamp(df)
        df = self.validate_amount(df)
        df = self.remove_duplicates(df)

        return df
