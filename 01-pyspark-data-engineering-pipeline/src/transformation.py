"""Data transformation module for cleaning and enriching data."""
from typing import Optional
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, upper, trim, regexp_replace, when, year, month, dayofmonth, to_date
import logging

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transforms and cleans data for downstream analytics."""

    def __init__(self, spark):
        """Initialize the data transformer.

        Args:
            spark: SparkSession instance
        """
        self.spark = spark

    def clean_text_columns(self, df: DataFrame, text_columns: list) -> DataFrame:
        """Clean text columns by trimming and standardizing case.

        Args:
            df: Input DataFrame
            text_columns: List of text column names to clean

        Returns:
            DataFrame with cleaned text columns
        """
        logger.info(f"Cleaning text columns: {text_columns}")

        for col_name in text_columns:
            if col_name in df.columns:
                df = df.withColumn(col_name, trim(col(col_name)))
                df = df.withColumn(col_name, upper(col(col_name)))

        return df

    def standardize_dates(self, df: DataFrame, date_columns: list, date_format: str = "yyyy-MM-dd") -> DataFrame:
        """Standardize date columns to a consistent format.

        Args:
            df: Input DataFrame
            date_columns: List of date column names to standardize
            date_format: Target date format

        Returns:
            DataFrame with standardized date columns
        """
        logger.info(f"Standardizing date columns: {date_columns}")

        for col_name in date_columns:
            if col_name in df.columns:
                df = df.withColumn(col_name, to_date(col(col_name), date_format))

        return df

    def derive_date_parts(self, df: DataFrame, date_column: str) -> DataFrame:
        """Derive year, month, and day from a date column.

        Args:
            df: Input DataFrame
            date_column: Date column name

        Returns:
            DataFrame with derived date part columns
        """
        logger.info(f"Deriving date parts from {date_column}")

        if date_column not in df.columns:
            logger.warning(f"Date column {date_column} not found")
            return df

        df = df.withColumn("year", year(col(date_column)))
        df = df.withColumn("month", month(col(date_column)))
        df = df.withColumn("day", dayofmonth(col(date_column)))

        return df

    def calculate_revenue_metrics(self, df: DataFrame) -> DataFrame:
        """Calculate revenue-related metrics.

        Args:
            df: Input DataFrame with sales data

        Returns:
            DataFrame with calculated revenue metrics
        """
        logger.info("Calculating revenue metrics")

        if "total_price" in df.columns:
            df = df.withColumn("revenue", col("total_price"))
        else:
            logger.warning("total_price column not found for revenue calculation")

        return df

    def join_customers(self, sales_df: DataFrame, customers_df: DataFrame,
                       join_key: str = "customer_id") -> DataFrame:
        """Join sales data with customer data.

        Args:
            sales_df: Sales DataFrame
            customers_df: Customer DataFrame
            join_key: Column name to join on

        Returns:
            Joined DataFrame
        """
        logger.info(f"Joining sales and customers on {join_key}")

        joined_df = sales_df.join(customers_df, on=join_key, how="left")
        logger.info(f"Joined DataFrame has {joined_df.count()} records")

        return joined_df

    def add_derived_columns(self, df: DataFrame) -> DataFrame:
        """Add commonly used derived columns.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with derived columns
        """
        logger.info("Adding derived columns")

        # Add a calculated column for average order value if applicable
        if "quantity" in df.columns and "unit_price" in df.columns:
            df = df.withColumn("calculated_total", col("quantity") * col("unit_price"))

        return df
