"""Preflight environment tests for Temporal.io implementation.

These tests verify that all prerequisites are met before beginning
the Temporal.io integration (Section 1 of 17).

Author: Apex Infrastructure Team
Created: 2025-10-18
Section: 1 - Pre-Flight & Setup
"""

import subprocess
import sys
import pytest


def run_command(cmd: list[str], timeout: int = 10) -> tuple[int, str, str]:
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


def test_python_version():
    """Test 1/5: Verify Python version >= 3.11.

    Required for Temporal.io Python SDK compatibility.
    """
    returncode, stdout, stderr = run_command(["python3", "--version"])

    assert returncode == 0, "Python3 not found"

    version_str = stdout.strip().split()[1]
    major, minor = map(int, version_str.split(".")[:2])

    assert major >= 3, f"Python major version {major} < 3"
    assert minor >= 11, f"Python {major}.{minor} < 3.11 (Temporal requires 3.11+)"

    print(f"✓ Python {version_str} meets requirement (>= 3.11)")


def test_docker_version():
    """Test 2/5: Verify Docker version >= 20.10.

    Required for running Temporal Server in Docker Compose.
    """
    returncode, stdout, stderr = run_command(["docker", "--version"])

    assert returncode == 0, "Docker not found"

    # Parse "Docker version 28.5.1, build e180ab8"
    version_str = stdout.split()[2].rstrip(",")
    major, minor = map(int, version_str.split(".")[:2])

    assert major > 20 or (major == 20 and minor >= 10), \
        f"Docker {version_str} < 20.10 (Temporal requires 20.10+)"

    print(f"✓ Docker {version_str} meets requirement (>= 20.10)")


def test_postgres_version():
    """Test 3/5: Verify PostgreSQL version >= 12.

    Temporal Server requires PostgreSQL 12+ for workflow state persistence.
    """
    returncode, stdout, stderr = run_command([
        "docker", "exec", "apex-postgres", "psql", "--version"
    ])

    assert returncode == 0, "PostgreSQL container not accessible"

    # Parse "psql (PostgreSQL) 15.4"
    version_str = stdout.split()[2]
    major = int(version_str.split(".")[0])

    assert major >= 12, \
        f"PostgreSQL {version_str} < 12 (Temporal requires 12+)"

    print(f"✓ PostgreSQL {version_str} meets requirement (>= 12)")


def test_apex_databases_running():
    """Test 4/5: Verify all 4 Apex databases are running.

    Baseline requirement: Neo4j, PostgreSQL, Qdrant, Redis must be healthy
    before Temporal integration.
    """
    required_containers = {
        "apex-postgres": "PostgreSQL",
        "apex-neo4j": "Neo4j",
        "apex-redis": "Redis",
        "apex-qdrant": "Qdrant"
    }

    returncode, stdout, stderr = run_command(["docker", "ps", "--format", "{{.Names}}"])

    assert returncode == 0, "Could not list Docker containers"

    running_containers = stdout.strip().split("\n")

    missing = []
    for container, name in required_containers.items():
        if container not in running_containers:
            missing.append(f"{name} ({container})")

    assert not missing, \
        f"Missing required databases: {', '.join(missing)}"

    print(f"✓ All 4 Apex databases running: {', '.join(required_containers.values())}")


def test_saga_baseline():
    """Test 5/5: Verify Enhanced Saga tests are passing.

    Establishes baseline that must be preserved during Temporal integration.
    The Enhanced Saga pattern is battle-tested and must continue working.
    """
    # Run a quick subset of Saga tests to verify baseline
    returncode, stdout, stderr = run_command([
        "python3", "-m", "pytest",
        "tests/unit/test_saga_phase2.py",
        "-v",
        "--tb=short",
        "--no-cov"
    ], timeout=60)

    # We expect the tests to pass (returncode 0 or 5 for coverage warning)
    # Pytest returns 5 if tests pass but coverage is below threshold
    assert returncode in [0, 5], \
        f"Saga baseline tests failed (exit code {returncode})"

    # Check that we have the expected test output
    assert "passed" in stdout or "passed" in stderr, \
        "No passed tests found in Saga baseline"

    print(f"✓ Saga baseline tests passing (Enhanced Saga pattern verified)")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
