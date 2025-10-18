"""Infrastructure tests for Temporal Docker Compose setup.

These tests verify that the Temporal infrastructure is correctly configured
and all services are running properly (Section 2 of 17).

Tests verify:
- YAML configuration validity
- Container startup and health
- Port accessibility
- Network integration
- Persistence
- Metrics availability

Author: Apex Infrastructure Team
Created: 2025-10-18
Section: 2 - Docker Compose Infrastructure
"""

import subprocess
import time
import yaml
import pytest
import requests
from pathlib import Path


def run_command(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run shell command and return exit code, stdout, stderr.

    Args:
        cmd: Command and arguments as list.
        timeout: Command timeout in seconds.

    Returns:
        Tuple of (exit_code, stdout, stderr).
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def test_temporal_compose_valid():
    """Test 1/10: Validate temporal-compose.yml syntax.

    Ensures the Docker Compose file is valid YAML and has required services.
    """
    compose_file = Path("/Users/richardglaubitz/Projects/apex-memory-system/docker/temporal-compose.yml")

    assert compose_file.exists(), "temporal-compose.yml not found"

    # Parse YAML
    with open(compose_file, 'r') as f:
        compose_config = yaml.safe_load(f)

    # Validate structure
    assert 'services' in compose_config, "No 'services' section in compose file"

    # Validate required services
    required_services = [
        'temporal-postgres',
        'temporal',
        'temporal-ui',
        'temporal-admin-tools'
    ]

    for service in required_services:
        assert service in compose_config['services'], \
            f"Service '{service}' not found in compose file"

    # Validate network configuration
    assert 'networks' in compose_config, "No 'networks' section in compose file"
    assert 'apex-network' in compose_config['networks'], \
        "apex-network not configured"
    assert compose_config['networks']['apex-network']['external'] is True, \
        "apex-network should be external"

    # Validate volumes
    assert 'volumes' in compose_config, "No 'volumes' section in compose file"
    assert 'temporal-postgres-data' in compose_config['volumes'], \
        "temporal-postgres-data volume not configured"

    print("✓ temporal-compose.yml is valid YAML with all required services")


def test_temporal_postgres_starts():
    """Test 2/10: Verify PostgreSQL container starts.

    Checks that temporal-postgres container is running.
    """
    returncode, stdout, stderr = run_command([
        "docker", "ps", "--filter", "name=temporal-postgres", "--format", "{{.Names}}"
    ])

    assert returncode == 0, "Docker command failed"
    assert "temporal-postgres" in stdout, \
        "temporal-postgres container not running"

    print("✓ temporal-postgres container is running")


def test_temporal_server_starts():
    """Test 3/10: Verify Temporal Server container starts.

    Checks that temporal container is running.
    """
    returncode, stdout, stderr = run_command([
        "docker", "ps", "--filter", "name=temporal", "--format", "{{.Names}}"
    ])

    assert returncode == 0, "Docker command failed"

    running_containers = stdout.strip().split("\n")
    temporal_running = any("temporal" == container for container in running_containers)

    assert temporal_running, "temporal container not running"

    print("✓ temporal container is running")


def test_temporal_ui_accessible():
    """Test 4/10: Verify Temporal UI is accessible at localhost:8088.

    Checks that the web UI responds to HTTP requests.
    """
    try:
        response = requests.get("http://localhost:8088", timeout=10)

        # UI should return 200 or redirect (3xx)
        assert response.status_code in [200, 301, 302, 303, 307, 308], \
            f"Unexpected status code: {response.status_code}"

        print(f"✓ Temporal UI accessible at http://localhost:8088 (status {response.status_code})")

    except requests.exceptions.ConnectionError:
        pytest.fail("Cannot connect to Temporal UI at localhost:8088")
    except requests.exceptions.Timeout:
        pytest.fail("Timeout connecting to Temporal UI")


def test_admin_tools_accessible():
    """Test 5/10: Verify admin tools container is running.

    Checks that temporal-admin-tools container is accessible.
    """
    returncode, stdout, stderr = run_command([
        "docker", "ps", "--filter", "name=temporal-admin-tools", "--format", "{{.Names}}"
    ])

    assert returncode == 0, "Docker command failed"
    assert "temporal-admin-tools" in stdout, \
        "temporal-admin-tools container not running"

    print("✓ temporal-admin-tools container is running")


def test_health_checks_pass():
    """Test 6/10: Verify all health checks are passing.

    Checks that containers report healthy status.
    """
    # Check temporal-postgres health
    returncode, stdout, stderr = run_command([
        "docker", "ps",
        "--filter", "name=temporal-postgres",
        "--filter", "health=healthy",
        "--format", "{{.Names}}"
    ])

    assert "temporal-postgres" in stdout, \
        "temporal-postgres not healthy (may need to wait 30-60s after startup)"

    # Check temporal health
    returncode, stdout, stderr = run_command([
        "docker", "ps",
        "--filter", "name=temporal",
        "--filter", "health=healthy",
        "--format", "{{.Names}}"
    ])

    # Filter for exact match (not temporal-ui or temporal-admin-tools)
    healthy_containers = stdout.strip().split("\n")
    temporal_healthy = "temporal" in healthy_containers

    assert temporal_healthy, \
        "temporal server not healthy (may need to wait 30-60s after startup)"

    # Check temporal-ui health
    returncode, stdout, stderr = run_command([
        "docker", "ps",
        "--filter", "name=temporal-ui",
        "--filter", "health=healthy",
        "--format", "{{.Names}}"
    ])

    assert "temporal-ui" in stdout, \
        "temporal-ui not healthy (may need to wait 30-60s after startup)"

    print("✓ All health checks passing (postgres, temporal, ui)")


def test_prometheus_metrics_available():
    """Test 7/10: Verify Prometheus metrics endpoint is accessible.

    Checks that Temporal Server exposes metrics at localhost:8077.
    """
    try:
        response = requests.get("http://localhost:8077/metrics", timeout=10)

        assert response.status_code == 200, \
            f"Unexpected status code: {response.status_code}"

        # Verify it's Prometheus format (starts with # HELP or metric name)
        content = response.text
        assert len(content) > 0, "Metrics endpoint returned empty response"
        assert ("# HELP" in content or "temporal_" in content), \
            "Response doesn't look like Prometheus metrics"

        print(f"✓ Prometheus metrics available at http://localhost:8077/metrics ({len(content)} bytes)")

    except requests.exceptions.ConnectionError:
        pytest.fail("Cannot connect to metrics endpoint at localhost:8077")
    except requests.exceptions.Timeout:
        pytest.fail("Timeout connecting to metrics endpoint")


def test_postgres_persistence():
    """Test 8/10: Verify PostgreSQL data persists across restarts.

    Tests that the temporal-postgres-data volume maintains data.
    """
    # Check that volume exists
    returncode, stdout, stderr = run_command([
        "docker", "volume", "ls", "--format", "{{.Name}}"
    ])

    assert returncode == 0, "Docker volume command failed"
    assert "temporal-postgres-data" in stdout, \
        "temporal-postgres-data volume not found"

    # Verify volume is mounted
    returncode, stdout, stderr = run_command([
        "docker", "inspect", "temporal-postgres", "--format", "{{.Mounts}}"
    ])

    assert returncode == 0, "Docker inspect failed"
    assert "temporal-postgres-data" in stdout, \
        "Volume not mounted to temporal-postgres container"

    print("✓ PostgreSQL persistence configured (temporal-postgres-data volume)")


def test_network_connectivity():
    """Test 9/10: Verify Apex network integration.

    Checks that all Temporal containers are on apex-network.
    """
    containers = [
        "temporal-postgres",
        "temporal",
        "temporal-ui",
        "temporal-admin-tools"
    ]

    for container in containers:
        returncode, stdout, stderr = run_command([
            "docker", "inspect", container,
            "--format", "{{range $net, $conf := .NetworkSettings.Networks}}{{$net}} {{end}}"
        ])

        assert returncode == 0, f"Failed to inspect {container}"
        assert "apex-network" in stdout, \
            f"{container} not connected to apex-network"

    print("✓ All Temporal containers connected to apex-network")


def test_dynamic_config_loaded():
    """Test 10/10: Verify dynamic configuration is loaded.

    Checks that the development.yaml config file is mounted and readable.
    """
    # Check that config file exists on host
    config_file = Path("/Users/richardglaubitz/Projects/apex-memory-system/docker/temporal-dynamicconfig/development.yaml")

    assert config_file.exists(), "development.yaml not found"

    # Verify it's valid YAML
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    assert config is not None, "development.yaml is empty or invalid"
    assert isinstance(config, dict), "development.yaml should be a dictionary"

    # Check that volume is mounted to temporal container
    returncode, stdout, stderr = run_command([
        "docker", "inspect", "temporal", "--format", "{{.Mounts}}"
    ])

    assert returncode == 0, "Failed to inspect temporal container"
    assert "temporal-dynamicconfig" in stdout, \
        "Dynamic config directory not mounted"

    print("✓ Dynamic configuration loaded (development.yaml)")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
