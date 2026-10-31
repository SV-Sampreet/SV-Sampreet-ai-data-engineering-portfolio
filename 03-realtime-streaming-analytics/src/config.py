"""Configuration management for streaming analytics platform."""
import os
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class StreamingConfig:
    """Streaming configuration parameters."""
    mode: str = field(default_factory=lambda: os.getenv("STREAMING_MODE", "local"))
    kafka_bootstrap_servers: str = field(default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
    kafka_topic: str = field(default_factory=lambda: os.getenv("KAFKA_TOPIC", "transactions"))
    input_dir: str = field(default_factory=lambda: os.getenv("INPUT_DIR", "data/input"))
    checkpoint_dir: str = field(default_factory=lambda: os.getenv("CHECKPOINT_DIR", "data/checkpoint"))


@dataclass
class DatabaseConfig:
    """Database configuration parameters."""
    db_type: str = field(default_factory=lambda: os.getenv("DB_TYPE", "sqlite"))
    postgres_host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    postgres_port: int = field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    postgres_db: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "streaming_analytics"))
    postgres_user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "postgres"))
    postgres_password: Optional[str] = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD"))
    sqlite_path: str = field(default_factory=lambda: os.getenv("SQLITE_PATH", "data/analytics.db"))

    def get_connection_string(self) -> str:
        """Get database connection string."""
        if self.db_type == "postgresql":
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        else:
            return f"sqlite:///{self.sqlite_path}"


@dataclass
class SparkConfig:
    """Spark configuration parameters."""
    master: str = field(default_factory=lambda: os.getenv("SPARK_MASTER", "local[*]"))
    app_name: str = field(default_factory=lambda: os.getenv("SPARK_APP_NAME", "StreamingAnalytics"))


@dataclass
class AnomalyConfig:
    """Anomaly detection configuration."""
    threshold_multiplier: float = field(default_factory=lambda: float(os.getenv("ANOMALY_THRESHOLD_MULTIPLIER", "3.0")))
    window_size_seconds: int = field(default_factory=lambda: int(os.getenv("WINDOW_SIZE_SECONDS", "60")))


@dataclass
class DashboardConfig:
    """Dashboard configuration parameters."""
    host: str = field(default_factory=lambda: os.getenv("DASHBOARD_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DASHBOARD_PORT", "8501")))


@dataclass
class LoggingConfig:
    """Logging configuration parameters."""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
