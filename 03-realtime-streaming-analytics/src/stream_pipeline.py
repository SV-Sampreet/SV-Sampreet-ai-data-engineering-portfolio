"""Main streaming pipeline orchestrator."""
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import (
    SparkConfig, StreamingConfig, DatabaseConfig,
    AnomalyConfig, LoggingConfig
)
from src.streaming.stream_processor import StreamProcessor
from src.producer.event_generator import EventGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for streaming pipeline."""
    logger.info("=" * 80)
    logger.info("Starting Real-Time Streaming Analytics Platform")
    logger.info("=" * 80)

    # Initialize configurations
    spark_config = SparkConfig()
    streaming_config = StreamingConfig()
    db_config = DatabaseConfig()
    anomaly_config = AnomalyConfig()
    logging_config = LoggingConfig()

    logger.info(f"Streaming mode: {streaming_config.mode}")
    logger.info(f"Database type: {db_config.db_type}")

    if streaming_config.mode == "local":
        logger.info("Running in local file-based streaming mode")

        # Generate sample events
        generator = EventGenerator(seed=42)
        sample_file = os.path.join(streaming_config.input_dir, "sample_events.jsonl")

        # Create input directory
        os.makedirs(streaming_config.input_dir, exist_ok=True)

        # Generate initial batch of events
        logger.info("Generating initial sample events...")
        generator.generate_sample_file(sample_file, count=50)

        # Initialize stream processor
        processor = StreamProcessor(
            spark_config=spark_config,
            streaming_config=streaming_config,
            anomaly_config=anomaly_config,
            db_config=db_config
        )

        try:
            # Start processing
            processor.start_local_processing()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            processor.stop()
    else:
        logger.error("Kafka mode not implemented in this version")
        logger.info("Use STREAMING_MODE=local for file-based streaming")
        sys.exit(1)


if __name__ == "__main__":
    main()
