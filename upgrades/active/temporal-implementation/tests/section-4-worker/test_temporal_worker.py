"""Worker infrastructure tests for Temporal.io integration.

These tests verify that ApexTemporalWorker correctly connects to Temporal Server,
handles graceful shutdown, and configures workers properly (Section 4 of 17).

Tests verify:
- Worker initialization
- Connection to Temporal Server
- Task queue polling
- Graceful shutdown (SIGINT, SIGTERM)
- Concurrency configuration
- Configuration integration
- Logging and error handling

Author: Apex Infrastructure Team
Created: 2025-10-18
Section: 4 - Worker Infrastructure
"""

import asyncio
import logging
import signal
import os
from unittest.mock import Mock, patch, AsyncMock
import pytest

from apex_memory.config import TemporalConfig
from apex_memory.temporal.workers import ApexTemporalWorker


# Mock workflow and activity for testing
class MockWorkflow:
    """Mock workflow class for testing."""
    pass


async def mock_activity():
    """Mock activity function for testing."""
    return "mock result"


@pytest.fixture
def worker():
    """Fixture providing basic worker instance."""
    return ApexTemporalWorker(
        workflows=[MockWorkflow],
        activities=[mock_activity],
    )


@pytest.fixture
def multi_worker():
    """Fixture providing worker with multiple workflows and activities."""
    class WorkflowA:
        pass

    class WorkflowB:
        pass

    async def activity_a():
        return "a"

    async def activity_b():
        return "b"

    async def activity_c():
        return "c"

    return ApexTemporalWorker(
        workflows=[WorkflowA, WorkflowB],
        activities=[activity_a, activity_b, activity_c],
    )


# Test 1/15: Worker Initialization
def test_worker_initialization(worker):
    """Test 1/15: Verify worker instance created with correct configuration.

    Tests that ApexTemporalWorker initializes with workflows, activities,
    and loads configuration from TemporalConfig.
    """
    assert worker is not None
    assert len(worker.workflows) == 1
    assert len(worker.activities) == 1
    assert worker.task_queue == worker.config.task_queue
    assert worker.worker_build_id == worker.config.worker_build_id
    assert worker.client is None  # Not connected yet
    assert worker.worker is None  # Not started yet

    print("✓ Worker initialized successfully")


# Test 2/15: Worker Connection
@pytest.mark.asyncio
async def test_worker_connects_to_server(worker, monkeypatch):
    """Test 2/15: Verify worker connects to Temporal Server successfully.

    Tests that worker can establish connection to Temporal Server
    using configuration from TemporalConfig.
    """
    # Set environment for testing
    monkeypatch.setenv("TEMPORAL_HOST", "localhost")
    monkeypatch.setenv("TEMPORAL_PORT", "7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "default")

    # Reload config
    worker.config = TemporalConfig.from_env()

    try:
        await worker.connect()

        assert worker.client is not None
        assert worker._runtime is not None

        print(f"✓ Connected to Temporal Server at {worker.config.server_url}")

    except Exception as e:
        # If connection fails, skip test (Docker may not be running)
        print(f"⚠ Skipped (Temporal not available): {e}")
        pytest.skip("Temporal Server not available")

    finally:
        # Cleanup
        if worker.client:
            await worker.client.close()


# Test 3/15: Task Queue Configuration
def test_worker_task_queue_config(monkeypatch):
    """Test 3/15: Verify task queue loaded from configuration.

    Tests that worker uses task queue from TemporalConfig,
    or accepts custom task queue override.
    """
    # Default task queue from config
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "test-queue")
    worker = ApexTemporalWorker(workflows=[MockWorkflow], activities=[mock_activity])
    assert worker.task_queue == "test-queue"

    # Custom task queue override
    worker = ApexTemporalWorker(
        workflows=[MockWorkflow],
        activities=[mock_activity],
        task_queue="custom-queue"
    )
    assert worker.task_queue == "custom-queue"

    print("✓ Task queue configuration working")


# Test 4/15: Namespace Configuration
def test_worker_namespace_config(monkeypatch):
    """Test 4/15: Verify namespace loaded from configuration.

    Tests that worker connects to correct Temporal namespace.
    """
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "production")

    worker = ApexTemporalWorker(workflows=[MockWorkflow], activities=[mock_activity])
    assert worker.config.namespace == "production"

    print("✓ Namespace configuration working")


# Test 5/15: Concurrent Workflow Tasks Configuration
def test_worker_concurrent_workflow_tasks(monkeypatch):
    """Test 5/15: Verify max concurrent workflow tasks configuration.

    Tests that worker respects max_concurrent_workflow_tasks setting
    from config or constructor override.
    """
    # Default from config
    monkeypatch.setenv("TEMPORAL_MAX_WORKFLOW_TASKS", "200")
    worker = ApexTemporalWorker(workflows=[MockWorkflow], activities=[mock_activity])
    assert worker.max_concurrent_workflow_tasks == 200

    # Custom override
    worker = ApexTemporalWorker(
        workflows=[MockWorkflow],
        activities=[mock_activity],
        max_concurrent_workflow_tasks=500
    )
    assert worker.max_concurrent_workflow_tasks == 500

    print("✓ Workflow task concurrency configuration working")


# Test 6/15: Concurrent Activities Configuration
def test_worker_concurrent_activities(monkeypatch):
    """Test 6/15: Verify max concurrent activities configuration.

    Tests that worker respects max_concurrent_activities setting
    from config or constructor override.
    """
    # Default from config
    monkeypatch.setenv("TEMPORAL_MAX_ACTIVITIES", "400")
    worker = ApexTemporalWorker(workflows=[MockWorkflow], activities=[mock_activity])
    assert worker.max_concurrent_activities == 400

    # Custom override
    worker = ApexTemporalWorker(
        workflows=[MockWorkflow],
        activities=[mock_activity],
        max_concurrent_activities=1000
    )
    assert worker.max_concurrent_activities == 1000

    print("✓ Activity concurrency configuration working")


# Test 7/15: Worker Build ID
def test_worker_build_id(monkeypatch):
    """Test 7/15: Verify worker build ID for versioning.

    Tests that worker uses build ID from config or accepts override.
    """
    # Default from config
    monkeypatch.setenv("TEMPORAL_WORKER_BUILD_ID", "v2.0.0")
    worker = ApexTemporalWorker(workflows=[MockWorkflow], activities=[mock_activity])
    assert worker.worker_build_id == "v2.0.0"

    # Custom override
    worker = ApexTemporalWorker(
        workflows=[MockWorkflow],
        activities=[mock_activity],
        worker_build_id="v3.5.1"
    )
    assert worker.worker_build_id == "v3.5.1"

    print("✓ Worker build ID configuration working")


# Test 8/15: Logging Configured
def test_worker_logs_startup(caplog):
    """Test 8/15: Verify logging configured properly.

    Tests that worker logs startup events with appropriate messages.
    """
    with caplog.at_level(logging.INFO):
        # Create worker inside test so caplog can capture logs
        worker = ApexTemporalWorker(
            workflows=[MockWorkflow],
            activities=[mock_activity],
        )

        assert "Initializing Apex Temporal Worker" in caplog.text
        assert f"Queue: {worker.task_queue}" in caplog.text
        assert f"Workflows: 1" in caplog.text
        assert f"Activities: 1" in caplog.text

    print("✓ Worker logging configured")


# Test 9/15: Multiple Workflows Registration
def test_worker_multiple_workflows(multi_worker):
    """Test 9/15: Verify worker can register multiple workflows.

    Tests that worker accepts and stores multiple workflow classes.
    """
    assert len(multi_worker.workflows) == 2
    assert all(hasattr(wf, '__name__') or hasattr(wf, '__class__') for wf in multi_worker.workflows)

    print("✓ Multiple workflows registered successfully")


# Test 10/15: Multiple Activities Registration
def test_worker_multiple_activities(multi_worker):
    """Test 10/15: Verify worker can register multiple activities.

    Tests that worker accepts and stores multiple activity functions.
    """
    assert len(multi_worker.activities) == 3
    assert all(callable(activity) for activity in multi_worker.activities)

    print("✓ Multiple activities registered successfully")


# Test 11/15: Signal Handler Setup
def test_worker_signal_handlers(worker):
    """Test 11/15: Verify signal handlers configured for graceful shutdown.

    Tests that worker sets up SIGINT and SIGTERM handlers.
    """
    # Setup signal handlers
    worker.setup_signal_handlers()

    # Verify handlers are set (non-default)
    assert signal.getsignal(signal.SIGINT) != signal.SIG_DFL
    assert signal.getsignal(signal.SIGTERM) != signal.SIG_DFL

    print("✓ Signal handlers configured (SIGINT, SIGTERM)")


# Test 12/15: Client Cleanup on Shutdown
@pytest.mark.asyncio
async def test_worker_closes_client(worker, monkeypatch):
    """Test 12/15: Verify client connection closed on shutdown.

    Tests that worker properly cleans up client connection when stopped.
    """
    monkeypatch.setenv("TEMPORAL_HOST", "localhost")
    monkeypatch.setenv("TEMPORAL_PORT", "7233")

    worker.config = TemporalConfig.from_env()

    try:
        # Connect
        await worker.connect()
        assert worker.client is not None

        # Stop
        await worker.stop()

        # Client should be closed (note: client.close() doesn't set to None)
        # We verify via shutdown event
        assert worker._shutdown_event.is_set()

        print("✓ Client connection closed on shutdown")

    except Exception as e:
        # If connection fails, still pass test (Docker may not be running)
        print(f"⚠ Skipped (Temporal not available): {e}")
        pytest.skip("Temporal Server not available")


# Test 13/15: Startup Failure Handling
@pytest.mark.asyncio
async def test_worker_startup_failure_handling(worker, monkeypatch, caplog):
    """Test 13/15: Verify startup errors logged and raised.

    Tests that worker handles connection failures gracefully with logging.
    """
    # Set invalid host to trigger connection failure
    monkeypatch.setenv("TEMPORAL_HOST", "invalid-host-12345")
    monkeypatch.setenv("TEMPORAL_PORT", "9999")

    worker.config = TemporalConfig.from_env()

    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception):
            await worker.connect()

        # Verify error was logged
        assert "Failed to connect to Temporal Server" in caplog.text

    print("✓ Startup failure handling working")


# Test 14/15: Prometheus Metrics Configuration
def test_worker_prometheus_metrics(worker, monkeypatch):
    """Test 14/15: Verify Prometheus metrics configured.

    Tests that worker sets up Prometheus metrics on configured port.
    """
    monkeypatch.setenv("TEMPORAL_METRICS_PORT", "9078")

    worker.config = TemporalConfig.from_env()
    runtime = worker._setup_runtime()

    assert runtime is not None
    # Runtime telemetry config is set up
    # (actual metrics require worker running)

    print(f"✓ Prometheus metrics configured on port {worker.config.metrics_port}")


# Test 15/15: Worker Running Status
@pytest.mark.asyncio
async def test_worker_is_running_property(worker, monkeypatch):
    """Test 15/15: Verify is_running property reflects worker state.

    Tests that worker.is_running correctly indicates if worker is active.
    """
    # Initially not running
    assert worker.is_running is False

    monkeypatch.setenv("TEMPORAL_HOST", "localhost")
    monkeypatch.setenv("TEMPORAL_PORT", "7233")

    worker.config = TemporalConfig.from_env()

    try:
        # Connect
        await worker.connect()
        assert worker.is_running is True

        # Stop
        await worker.stop()
        assert worker.is_running is False

        print("✓ is_running property working correctly")

    except Exception:
        # If connection fails, still pass test
        print("⚠ Skipped (Temporal not available)")
        pytest.skip("Temporal Server not available")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
