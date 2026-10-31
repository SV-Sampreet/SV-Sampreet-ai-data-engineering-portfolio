"""Tests for configuration module."""
import pytest
import os
from src.config import (
    SparkConfig, StreamingConfig, DatabaseConfig,
    AnomalyConfig, DashboardConfig, LoggingConfig
)


def test_spark_config_defaults():
    """Test SparkConfig default values."""
    config = SparkConfig()
    assert config.master == "local[*]"
    assert config.app_name == "StreamingAnalytics"


def test_streaming_config_defaults():
    """Test StreamingConfig default values."""
    config = StreamingConfig()
    assert config.mode == "local"
    assert config.kafka_topic == "transactions"


def test_database_config_defaults():
    """Test DatabaseConfig default values."""
    config = DatabaseConfig()
    assert config.db_type == "sqlite"
    assert config.sqlite_path == "data/analytics.db"


def test_database_config_connection_string():
    """Test database connection string generation."""
    config = DatabaseConfig()
    conn_str = config.get_connection_string()
    assert "sqlite:///" in conn_str


def test_anomaly_config_defaults():
    """Test AnomalyConfig default values."""
    config = AnomalyConfig()
    assert config.threshold_multiplier == 3.0
    assert config.window_size_seconds == 60
