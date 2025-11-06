"""Configuration tests for Temporal.io integration.

These tests verify that the TemporalConfig dataclass correctly loads
configuration from environment variables and validates settings (Section 3 of 17).

Tests verify:
- Environment variable loading
- Default values
- Validation (rollout percentage, ports, concurrency)
- Feature flag logic
- .gitignore configuration

Author: Apex Infrastructure Team
Created: 2025-10-18
Section: 3 - Python SDK & Configuration
"""

import os
import pytest
from pathlib import Path
from apex_memory.config import TemporalConfig


def test_config_loads_from_env(monkeypatch):
    """Test 1/5: Verify configuration loads from environment variables.

    Tests that TemporalConfig.from_env() correctly reads all environment
    variables and populates the dataclass.
    """
    # Set environment variables
    monkeypatch.setenv("TEMPORAL_HOST", "temporal.example.com")
    monkeypatch.setenv("TEMPORAL_PORT", "7234")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "production")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "prod-ingestion-queue")
    monkeypatch.setenv("TEMPORAL_WORKER_BUILD_ID", "v2.0.0")
    monkeypatch.setenv("TEMPORAL_MAX_WORKFLOW_TASKS", "200")
    monkeypatch.setenv("TEMPORAL_MAX_ACTIVITIES", "400")
    monkeypatch.setenv("TEMPORAL_ROLLOUT", "50")
    monkeypatch.setenv("TEMPORAL_METRICS_PORT", "9078")
    monkeypatch.setenv("TEMPORAL_ENABLE_TRACING", "true")
    monkeypatch.setenv("TEMPORAL_TRACING_ENDPOINT", "http://localhost:4317")

    # Load config from environment
    config = TemporalConfig.from_env()

    # Verify all values loaded correctly
    assert config.host == "temporal.example.com"
    assert config.port == 7234
    assert config.namespace == "production"
    assert config.task_queue == "prod-ingestion-queue"
    assert config.worker_build_id == "v2.0.0"
    assert config.max_concurrent_workflow_tasks == 200
    assert config.max_concurrent_activities == 400
    assert config.rollout_percentage == 50
    assert config.metrics_port == 9078
    assert config.enable_tracing is True
    assert config.tracing_endpoint == "http://localhost:4317"

    print("✓ All environment variables loaded correctly")


def test_config_defaults():
    """Test 2/5: Verify default values when environment variables are missing.

    Tests that TemporalConfig provides sensible defaults for development
    when environment variables are not set.
    """
    # Create config with no environment variables (use defaults)
    config = TemporalConfig()

    # Verify default values
    assert config.host == "localhost"
    assert config.port == 7233
    assert config.namespace == "default"
    assert config.task_queue == "apex-ingestion-queue"
    assert config.worker_build_id == "v1.0.0"
    assert config.max_concurrent_workflow_tasks == 100
    assert config.max_concurrent_activities == 200
    assert config.rollout_percentage == 0
    assert config.metrics_port == 8078
    assert config.enable_tracing is False
    assert config.tracing_endpoint is None

    print(f"✓ Default configuration: {config}")


def test_rollout_percentage_validation():
    """Test 3/5: Verify rollout percentage validation (0-100 range).

    Tests that TemporalConfig enforces the 0-100% range for gradual rollout
    and raises ValueError for invalid values.
    """
    # Valid rollout percentages
    for percentage in [0, 10, 50, 100]:
        config = TemporalConfig(rollout_percentage=percentage)
        assert config.rollout_percentage == percentage

    # Invalid rollout percentages (below 0)
    with pytest.raises(ValueError, match="TEMPORAL_ROLLOUT must be 0-100"):
        TemporalConfig(rollout_percentage=-1)

    with pytest.raises(ValueError, match="TEMPORAL_ROLLOUT must be 0-100"):
        TemporalConfig(rollout_percentage=-50)

    # Invalid rollout percentages (above 100)
    with pytest.raises(ValueError, match="TEMPORAL_ROLLOUT must be 0-100"):
        TemporalConfig(rollout_percentage=101)

    with pytest.raises(ValueError, match="TEMPORAL_ROLLOUT must be 0-100"):
        TemporalConfig(rollout_percentage=150)

    print("✓ Rollout percentage validation enforced (0-100)")


def test_use_temporal_property():
    """Test 4/5: Verify use_temporal feature flag logic.

    Tests that the use_temporal property correctly indicates whether
    Temporal should be used based on rollout_percentage.
    """
    # rollout_percentage = 0 → use_temporal = False
    config = TemporalConfig(rollout_percentage=0)
    assert config.use_temporal is False

    # rollout_percentage = 1 → use_temporal = True
    config = TemporalConfig(rollout_percentage=1)
    assert config.use_temporal is True

    # rollout_percentage = 50 → use_temporal = True
    config = TemporalConfig(rollout_percentage=50)
    assert config.use_temporal is True

    # rollout_percentage = 100 → use_temporal = True
    config = TemporalConfig(rollout_percentage=100)
    assert config.use_temporal is True

    print("✓ use_temporal property working correctly")


def test_env_temporal_gitignored():
    """Test 5/5: Verify .env.temporal is in .gitignore.

    Tests that the .env.temporal file is gitignored to prevent committing
    sensitive configuration to version control.
    """
    gitignore_path = Path("/Users/richardglaubitz/Projects/apex-memory-system/.gitignore")

    assert gitignore_path.exists(), ".gitignore file not found"

    # Read .gitignore
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()

    # Verify .env.temporal is gitignored
    assert ".env.temporal" in gitignore_content, \
        ".env.temporal not found in .gitignore"

    print("✓ .env.temporal is gitignored (security verified)")


# Additional validation tests

def test_port_validation():
    """Bonus test: Verify port number validation.

    Tests that invalid port numbers are rejected.
    """
    # Valid ports
    config = TemporalConfig(port=1, metrics_port=1)
    assert config.port == 1

    config = TemporalConfig(port=65535, metrics_port=65535)
    assert config.port == 65535

    # Invalid port (below 1)
    with pytest.raises(ValueError, match="TEMPORAL_PORT must be 1-65535"):
        TemporalConfig(port=0)

    # Invalid port (above 65535)
    with pytest.raises(ValueError, match="TEMPORAL_PORT must be 1-65535"):
        TemporalConfig(port=65536)

    # Invalid metrics port
    with pytest.raises(ValueError, match="TEMPORAL_METRICS_PORT must be 1-65535"):
        TemporalConfig(metrics_port=0)

    print("✓ Port validation enforced (1-65535)")


def test_concurrency_validation():
    """Bonus test: Verify concurrency settings validation.

    Tests that concurrency must be >= 1.
    """
    # Valid concurrency
    config = TemporalConfig(max_concurrent_workflow_tasks=1, max_concurrent_activities=1)
    assert config.max_concurrent_workflow_tasks == 1

    # Invalid workflow task concurrency
    with pytest.raises(ValueError, match="max_concurrent_workflow_tasks must be >= 1"):
        TemporalConfig(max_concurrent_workflow_tasks=0)

    # Invalid activity concurrency
    with pytest.raises(ValueError, match="max_concurrent_activities must be >= 1"):
        TemporalConfig(max_concurrent_activities=0)

    print("✓ Concurrency validation enforced (>= 1)")


def test_server_url_property():
    """Bonus test: Verify server_url property.

    Tests that server_url correctly formats host:port.
    """
    config = TemporalConfig(host="localhost", port=7233)
    assert config.server_url == "localhost:7233"

    config = TemporalConfig(host="temporal.example.com", port=7234)
    assert config.server_url == "temporal.example.com:7234"

    print("✓ server_url property working correctly")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
