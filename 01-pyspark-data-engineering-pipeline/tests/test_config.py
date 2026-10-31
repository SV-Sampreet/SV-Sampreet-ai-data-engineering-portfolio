"""Tests for configuration module."""
import pytest
import os
from src.config import SparkConfig, StorageConfig, ValidationConfig, LoggingConfig


def test_spark_config_defaults():
    """Test SparkConfig default values."""
    config = SparkConfig()
    assert config.master == "local[*]"
    assert config.app_name == "DataEngineeringPipeline"
    assert config.driver_memory == "2g"
    assert config.executor_memory == "2g"


def test_spark_config_from_env():
    """Test SparkConfig reads from environment variables."""
    # Clear existing values
    os.environ.pop("SPARK_MASTER", None)
    os.environ.pop("SPARK_APP_NAME", None)

    os.environ["SPARK_MASTER"] = "local[4]"
    os.environ["SPARK_APP_NAME"] = "TestApp"
    config = SparkConfig()
    assert config.master == "local[4]"
    assert config.app_name == "TestApp"
    # Clean up
    del os.environ["SPARK_MASTER"]
    del os.environ["SPARK_APP_NAME"]


def test_storage_config_defaults():
    """Test StorageConfig default values."""
    config = StorageConfig()
    assert config.backend == "local"
    assert config.input_dir == "data/sample"
    assert config.output_dir == "data/output"
    assert config.quarantine_dir == "data/quarantine"


def test_storage_config_hdfs_url():
    """Test HDFS URL generation."""
    config = StorageConfig()
    config.backend = "hdfs"
    config.hdfs_namenode = "namenode"
    config.hdfs_port = "8020"
    assert config.get_hdfs_url() == "hdfs://namenode:8020"


def test_validation_config_defaults():
    """Test ValidationConfig default values."""
    config = ValidationConfig()
    assert config.enable_validation is True
    assert config.max_null_threshold == 0.5
    assert config.duplicate_check is True


def test_validation_config_from_env():
    """Test ValidationConfig reads from environment variables."""
    # Clear existing values
    os.environ.pop("ENABLE_VALIDATION", None)
    os.environ.pop("MAX_NULL_THRESHOLD", None)
    os.environ.pop("DUPLICATE_CHECK", None)

    os.environ["ENABLE_VALIDATION"] = "false"
    os.environ["MAX_NULL_THRESHOLD"] = "0.8"
    os.environ["DUPLICATE_CHECK"] = "false"
    config = ValidationConfig()
    assert config.enable_validation is False
    assert config.max_null_threshold == 0.8
    assert config.duplicate_check is False
    # Clean up
    del os.environ["ENABLE_VALIDATION"]
    del os.environ["MAX_NULL_THRESHOLD"]
    del os.environ["DUPLICATE_CHECK"]


def test_logging_config_defaults():
    """Test LoggingConfig default values."""
    config = LoggingConfig()
    assert config.level == "INFO"
