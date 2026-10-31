"""Configuration management for the data pipeline."""
import os
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class SparkConfig:
    """Spark configuration parameters."""
    master: str = field(default_factory=lambda: os.getenv("SPARK_MASTER", "local[*]"))
    app_name: str = field(default_factory=lambda: os.getenv("SPARK_APP_NAME", "DataEngineeringPipeline"))
    driver_memory: str = "2g"
    executor_memory: str = "2g"

    def get_extra_config(self) -> dict:
        """Get extra Spark configuration for compatibility."""
        return {
            "spark.hadoop.security.authentication": "simple",
            "spark.hadoop.hadoop.security.authentication": "simple",
            "spark.hadoop.security.util.simplename": "true",
        }


@dataclass
class StorageConfig:
    """Storage configuration parameters."""
    backend: str = field(default_factory=lambda: os.getenv("STORAGE_BACKEND", "local"))
    input_dir: str = field(default_factory=lambda: os.getenv("INPUT_DIR", "data/sample"))
    output_dir: str = field(default_factory=lambda: os.getenv("OUTPUT_DIR", "data/output"))
    quarantine_dir: str = field(default_factory=lambda: os.getenv("QUARANTINE_DIR", "data/quarantine"))
    hdfs_namenode: Optional[str] = field(default_factory=lambda: os.getenv("HDFS_NAMENODE", "localhost"))
    hdfs_port: Optional[str] = field(default_factory=lambda: os.getenv("HDFS_PORT", "9000"))
    hdfs_user: Optional[str] = field(default_factory=lambda: os.getenv("HDFS_USER", "hdfs"))

    def get_hdfs_url(self) -> str:
        """Get HDFS URL if backend is HDFS."""
        if self.backend == "hdfs":
            return f"hdfs://{self.hdfs_namenode}:{self.hdfs_port}"
        return ""


@dataclass
class ValidationConfig:
    """Data validation configuration parameters."""
    enable_validation: bool = field(default_factory=lambda: os.getenv("ENABLE_VALIDATION", "true").lower() == "true")
    max_null_threshold: float = field(default_factory=lambda: float(os.getenv("MAX_NULL_THRESHOLD", "0.5")))
    duplicate_check: bool = field(default_factory=lambda: os.getenv("DUPLICATE_CHECK", "true").lower() == "true")


@dataclass
class LoggingConfig:
    """Logging configuration parameters."""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
