"""Main pipeline orchestrator."""
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp

from src.config import SparkConfig, StorageConfig, ValidationConfig, LoggingConfig
from src.ingestion import DataIngestion
from src.validation import DataValidator
from src.transformation import DataTransformer
from src.analytics import DataAnalytics
from src.storage import DataStorage


def setup_logging(config: LoggingConfig) -> None:
    """Configure logging for the pipeline.

    Args:
        config: LoggingConfig instance
    """
    logging.basicConfig(
        level=getattr(logging, config.level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_spark_session(config: SparkConfig) -> SparkSession:
    """Create and configure a Spark session.

    Args:
        config: SparkConfig instance

    Returns:
        Configured SparkSession
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Creating Spark session: {config.app_name}")

    builder = SparkSession.builder \
        .master(config.master) \
        .appName(config.app_name) \
        .config("spark.driver.memory", config.driver_memory) \
        .config("spark.executor.memory", config.executor_memory) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")

    # Add extra configuration for Java compatibility
    extra_config = config.get_extra_config()
    for key, value in extra_config.items():
        builder = builder.config(key, value)

    spark = builder.getOrCreate()

    logger.info("Spark session created successfully")
    return spark


class DataPipeline:
    """Main data pipeline orchestrator."""

    def __init__(self):
        """Initialize the pipeline with all components."""
        self.spark_config = SparkConfig()
        self.storage_config = StorageConfig()
        self.validation_config = ValidationConfig()
        self.logging_config = LoggingConfig()

        setup_logging(self.logging_config)
        self.logger = logging.getLogger(__name__)

        self.spark = create_spark_session(self.spark_config)

        # Initialize components
        self.ingestion = DataIngestion(self.spark, self.storage_config)
        self.validator = DataValidator(self.spark, self.validation_config)
        self.transformer = DataTransformer(self.spark)
        self.analytics = DataAnalytics(self.spark)
        self.storage = DataStorage(self.spark, self.storage_config)

        # Track pipeline metrics
        self.metrics = {
            "input_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "quarantine_records": 0,
            "output_records": 0
        }

    def run(self, sales_file: str = None, customers_file: str = None) -> dict:
        """Run the complete data pipeline.

        Args:
            sales_file: Path to sales data file (optional)
            customers_file: Path to customers data file (optional)

        Returns:
            Dictionary with pipeline results and analytics
        """
        self.logger.info("=" * 80)
        self.logger.info("Starting Data Engineering Pipeline")
        self.logger.info("=" * 80)

        try:
            # Step 1: Ingest data
            self.logger.info("Step 1: Data Ingestion")
            if sales_file:
                sales_df = self.ingestion.read_csv(sales_file)
            else:
                sales_df = self.ingestion.read_directory(
                    self.storage_config.input_dir,
                    file_format="csv"
                )

            self.metrics["input_records"] = sales_df.count()
            self.logger.info(f"Ingested {self.metrics['input_records']} sales records")

            if customers_file:
                customers_df = self.ingestion.read_csv(customers_file)
            else:
                # Try to read customers from the same directory
                customers_df = self.ingestion.read_directory(
                    self.storage_config.input_dir,
                    file_format="csv"
                ).filter("customer_id is not null and product_id is null")

            # Step 2: Validate data
            self.logger.info("Step 2: Data Validation")
            if self.validation_config.enable_validation:
                # Schema validation
                required_sales_columns = ["order_id", "customer_id", "product_id", "quantity", "unit_price", "total_price", "order_date"]
                valid_sales, invalid_sales = self.validator.validate_schema(sales_df, required_sales_columns)

                # Date validation
                valid_sales, invalid_dates = self.validator.validate_dates(valid_sales, ["order_date"])

                # Business rule validation
                valid_sales, invalid_business = self.validator.validate_business_rules(valid_sales)

                # Combine all invalid records
                all_invalid = invalid_sales.union(invalid_dates).union(invalid_business)
                all_invalid = all_invalid.dropDuplicates()

                # Remove duplicates
                valid_sales = self.validator.remove_duplicates(valid_sales, ["order_id"])

                self.metrics["valid_records"] = valid_sales.count()
                self.metrics["invalid_records"] = all_invalid.count()

                self.logger.info(f"Validation complete: {self.metrics['valid_records']} valid, {self.metrics['invalid_records']} invalid")

                # Write quarantine records
                if all_invalid.count() > 0:
                    quarantine_df = self.validator.create_quarantine_record(
                        all_invalid,
                        error_type="VALIDATION_ERROR",
                        error_message="Failed schema, date, or business rule validation",
                        source_file=sales_file or "data/sample"
                    )
                    self.storage.write_quarantine(quarantine_df, self.storage_config.quarantine_dir)
                    self.metrics["quarantine_records"] = quarantine_df.count()
            else:
                valid_sales = sales_df
                self.metrics["valid_records"] = valid_sales.count()
                self.logger.info("Validation disabled, skipping")

            # Step 3: Transform data
            self.logger.info("Step 3: Data Transformation")
            valid_sales = self.transformer.clean_text_columns(valid_sales, ["region", "category", "payment_method"])
            valid_sales = self.transformer.calculate_revenue_metrics(valid_sales)
            valid_sales = self.transformer.derive_date_parts(valid_sales, "order_date")

            # Join with customer data if available
            if customers_df.count() > 0:
                valid_sales = self.transformer.join_customers(valid_sales, customers_df)

            self.logger.info("Transformation complete")

            # Step 4: Calculate analytics
            self.logger.info("Step 4: Analytics Calculation")
            analytics_report = self.analytics.generate_analytics_report(valid_sales)

            self.logger.info("Analytics calculated:")
            for key, value in analytics_report["summary"].items():
                self.logger.info(f"  {key}: {value}")

            # Step 5: Store results
            self.logger.info("Step 5: Storage")
            self.storage.write_parquet(valid_sales, f"{self.storage_config.output_dir}/sales_curated")
            self.storage.write_parquet(analytics_report["revenue_by_region"], f"{self.storage_config.output_dir}/revenue_by_region")
            self.storage.write_parquet(analytics_report["revenue_by_product"], f"{self.storage_config.output_dir}/revenue_by_product")
            self.storage.write_parquet(analytics_report["monthly_trends"], f"{self.storage_config.output_dir}/monthly_trends")
            self.storage.write_parquet(analytics_report["customer_metrics"], f"{self.storage_config.output_dir}/customer_metrics")

            self.metrics["output_records"] = valid_sales.count()
            self.logger.info(f"Storage complete: {self.metrics['output_records']} records written")

            # Step 6: Generate execution summary
            summary = {
                "pipeline_metrics": self.metrics,
                "analytics_summary": analytics_report["summary"],
                "status": "SUCCESS"
            }

            self.logger.info("=" * 80)
            self.logger.info("Pipeline completed successfully")
            self.logger.info("=" * 80)

            return summary

        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return {
                "pipeline_metrics": self.metrics,
                "status": "FAILED",
                "error": str(e)
            }

    def stop(self):
        """Stop the Spark session."""
        self.logger.info("Stopping Spark session")
        self.spark.stop()


def main():
    """Main entry point for the pipeline."""
    pipeline = DataPipeline()
    try:
        result = pipeline.run()
        print("\n" + "=" * 80)
        print("PIPELINE EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Input Records: {result['pipeline_metrics']['input_records']}")
        print(f"Valid Records: {result['pipeline_metrics']['valid_records']}")
        print(f"Invalid Records: {result['pipeline_metrics']['invalid_records']}")
        print(f"Quarantine Records: {result['pipeline_metrics']['quarantine_records']}")
        print(f"Output Records: {result['pipeline_metrics']['output_records']}")

        if result['status'] == 'SUCCESS':
            print("\nAnalytics Summary:")
            for key, value in result['analytics_summary'].items():
                print(f"  {key}: {value}")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")

        print("=" * 80)
    finally:
        pipeline.stop()


if __name__ == "__main__":
    main()
