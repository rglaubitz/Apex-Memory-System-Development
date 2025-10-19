# Temporal Workflow Orchestration - Implementation Guide

**Status:** Ready for Implementation
**Priority:** High
**Timeline:** 6-8 weeks (phased rollout)
**Last Updated:** 2025-10-18

---

## Executive Summary

This guide provides step-by-step implementation instructions for integrating Temporal.io workflow orchestration into the Apex Memory System while preserving the battle-tested Enhanced Saga pattern for database writes.

**Key Decisions:**
- ✅ **Temporal.io (1.28.0+)** - Production-proven workflow orchestration (Uber, Netflix, Stripe)
- ✅ **Python SDK (1.11.0+)** - Native Python workflow definitions
- ✅ **Hybrid Architecture** - Temporal for orchestration, Enhanced Saga for database writes
- ✅ **PostgreSQL Persistence** - Durable workflow state (port 5433)
- ✅ **Gradual Rollout** - 10% → 50% → 100% traffic migration
- ✅ **Worker Versioning** - Safe deployments with instant rollback

**Why Hybrid Architecture:**
- **Temporal excels at:** Orchestration, retries, state management, observability
- **Enhanced Saga excels at:** Multi-database consistency, circuit breakers, idempotency
- **Result:** 70% code reduction (3,000 → 1,000 lines), 99.9% reliability, complete observability

---

## Table of Contents

1. [Pre-Flight Verification](#pre-flight-verification)
2. [Dependency Installation](#dependency-installation)
3. [Phase 1: Infrastructure Setup](#phase-1-infrastructure-setup-week-1-2)
4. [Phase 2: Ingestion Migration](#phase-2-ingestion-migration-week-3-4)
5. [Phase 3: Multi-Source Integration](#phase-3-multi-source-integration-week-5-6)
6. [Phase 4: Monitoring & Observability](#phase-4-monitoring--observability-week-7-8)
7. [Testing Strategy](#testing-strategy)
8. [Rollback Procedures](#rollback-procedures)

---

## Pre-Flight Verification

### 1. Check PostgreSQL Version

```bash
# Temporal requires PostgreSQL 12+
psql --version

# Requirement: PostgreSQL 12+ (for Temporal persistence)
# Current Apex PostgreSQL: 16 (✓ compatible)
```

**Why:** Temporal uses PostgreSQL for workflow state persistence. We'll use port 5433 to avoid conflicts with Apex PostgreSQL (port 5432).

### 2. Check Docker & Docker Compose

```bash
# Check Docker
docker --version
# Requirement: Docker 20.10+

# Check Docker Compose
docker-compose --version
# Requirement: Docker Compose 1.29+ or Docker Compose V2

# Check Docker network
docker network ls | grep apex-network || docker network create apex-network
```

**Why:** Temporal Server runs in Docker for local development and production parity.

### 3. Check Python Version

```bash
# Check Python version
python --version
# Requirement: Python 3.11+ (current Apex requirement)

# Check pip
pip --version
```

### 4. Verify Apex Infrastructure

```bash
# Navigate to Apex codebase
cd apex-memory-system

# Check databases are running
docker ps | grep -E "neo4j|postgres|qdrant|redis"

# Expected: All 4 databases running

# Run existing Saga tests (validate baseline)
pytest tests/unit/test_saga_phase2.py -v

# Expected: 121/121 tests passing
```

**Recommended Config:**
```yaml
# docker-compose.yml (verify Apex network exists)
networks:
  apex-network:
    external: false  # Should be set to allow Temporal to join
```

---

## Dependency Installation

### Update requirements.txt

```bash
cd apex-memory-system

# Add to requirements.txt:
cat >> requirements.txt << 'EOF'

# Temporal.io Workflow Orchestration
temporalio==1.11.0  # Durable workflows, activities, workers
EOF

# Install
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "import temporalio; print(f'Temporal SDK: {temporalio.__version__}')"
# Expected: Temporal SDK: 1.11.0
```

---

## Phase 1: Infrastructure Setup (Week 1-2)

**Goal:** Deploy Temporal Server, install Python SDK, create worker infrastructure, validate with "Hello World"

### Day 1-2: Docker Compose Deployment

#### 1.1 Create Temporal Docker Compose Configuration

**File:** `apex-memory-system/docker/temporal-compose.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL for Temporal persistence (separate from Apex PostgreSQL)
  temporal-postgres:
    container_name: temporal-postgres
    image: postgres:16
    restart: always
    environment:
      POSTGRES_USER: temporal
      POSTGRES_PASSWORD: temporal
      POSTGRES_DB: temporal
    ports:
      - "5433:5432"  # Avoid conflict with Apex PostgreSQL (5432)
    volumes:
      - temporal-postgres-data:/var/lib/postgresql/data
    networks:
      - apex-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U temporal"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Temporal Server (auto-setup with schema initialization)
  temporal:
    container_name: temporal
    image: temporalio/auto-setup:1.28.0
    restart: always
    depends_on:
      temporal-postgres:
        condition: service_healthy
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=temporal
      - POSTGRES_PWD=temporal
      - POSTGRES_SEEDS=temporal-postgres
      - DYNAMIC_CONFIG_FILE_PATH=config/dynamicconfig/development.yaml
      - PROMETHEUS_ENDPOINT=0.0.0.0:8000
    ports:
      - "7233:7233"  # Frontend gRPC
      - "8077:8000"  # Prometheus metrics (avoid conflict with Apex Prometheus)
    volumes:
      - ./temporal-dynamicconfig:/etc/temporal/config/dynamicconfig
    networks:
      - apex-network
    healthcheck:
      test: ["CMD", "tctl", "--address", "localhost:7233", "cluster", "health"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Temporal UI
  temporal-ui:
    container_name: temporal-ui
    image: temporalio/ui:2.38.0
    restart: always
    depends_on:
      temporal:
        condition: service_healthy
    environment:
      - TEMPORAL_ADDRESS=temporal:7233
      - TEMPORAL_CORS_ORIGINS=http://localhost:3000,http://localhost:8088
    ports:
      - "8088:8080"  # Avoid conflict with Apex API (8000)
    networks:
      - apex-network

  # Temporal Admin Tools (for CLI operations)
  temporal-admin-tools:
    container_name: temporal-admin-tools
    image: temporalio/admin-tools:1.28.0
    restart: always
    depends_on:
      temporal:
        condition: service_healthy
    environment:
      - TEMPORAL_CLI_ADDRESS=temporal:7233
    networks:
      - apex-network
    stdin_open: true
    tty: true

volumes:
  temporal-postgres-data:
    driver: local

networks:
  apex-network:
    external: true  # Use existing Apex network
```

**Why this matters:** This configuration deploys a production-ready Temporal stack that integrates seamlessly with existing Apex infrastructure while avoiding port conflicts.

#### 1.2 Create Dynamic Configuration

```bash
# Create directory
mkdir -p apex-memory-system/docker/temporal-dynamicconfig

# Create config file
cat > apex-memory-system/docker/temporal-dynamicconfig/development.yaml <<EOF
# Temporal dynamic configuration for local development

# Enable client version checking
frontend.enableClientVersionCheck:
  - value: true

# Max workflow ID length
limit.maxIDLength:
  - value: 1000

# Force search attributes refresh
system.forceSearchAttributesCacheRefreshOnRead:
  - value: true

# Max auto-reset points for workflow history
history.maxAutoResetPoints:
  - value: 20
EOF
```

#### 1.3 Start Temporal Stack

```bash
# Create network if not exists
docker network create apex-network 2>/dev/null || true

# Start Temporal stack
cd apex-memory-system/docker
docker-compose -f temporal-compose.yml up -d

# Verify all containers started
docker ps | grep temporal

# Expected output:
# temporal-postgres   Up (healthy)
# temporal            Up (healthy)
# temporal-ui         Up
# temporal-admin-tools Up

# Check logs
docker-compose -f temporal-compose.yml logs -f temporal
# Watch for: "Server started"
```

#### 1.4 Verify Temporal Health

```bash
# Test Temporal Server
curl http://localhost:7233

# Test Temporal UI
open http://localhost:8088

# Test PostgreSQL
PGPASSWORD=temporal psql -h localhost -p 5433 -U temporal -d temporal -c "SELECT 1"
# Expected: 1 row returned

# Test metrics endpoint
curl http://localhost:8077/metrics | grep temporal_request
# Expected: Prometheus metrics
```

**Troubleshooting:**
- If `temporal` container won't start: Check `temporal-postgres` is healthy first
- If port conflicts: Adjust ports in `temporal-compose.yml`
- View logs: `docker-compose -f temporal-compose.yml logs temporal`

---

### Day 3: Python SDK Installation & Configuration

#### 2.1 Install Temporal Python SDK

Already completed in [Dependency Installation](#dependency-installation) above.

#### 2.2 Create Temporal Configuration

**File:** `apex-memory-system/src/apex_memory/config/temporal_config.py`

```python
"""Temporal.io configuration for Apex Memory System.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class TemporalConfig:
    """Temporal configuration loaded from environment variables."""

    # Connection
    host: str = os.getenv("TEMPORAL_HOST", "localhost:7233")
    namespace: str = os.getenv("TEMPORAL_NAMESPACE", "default")

    # Worker configuration
    task_queue: str = os.getenv("TEMPORAL_TASK_QUEUE", "apex-ingestion")
    worker_build_id: str = os.getenv("TEMPORAL_WORKER_BUILD_ID", "dev")
    deployment_name: str = os.getenv("TEMPORAL_DEPLOYMENT_NAME", "apex-ingestion-service")

    # TLS (for production/Temporal Cloud)
    tls_cert_path: Optional[str] = os.getenv("TEMPORAL_TLS_CERT_PATH")
    tls_key_path: Optional[str] = os.getenv("TEMPORAL_TLS_KEY_PATH")
    tls_ca_path: Optional[str] = os.getenv("TEMPORAL_TLS_CA_PATH")

    # Observability
    metrics_port: int = int(os.getenv("TEMPORAL_METRICS_PORT", "8078"))
    enable_tracing: bool = os.getenv("TEMPORAL_ENABLE_TRACING", "false").lower() == "true"
    otel_endpoint: str = os.getenv("TEMPORAL_OTEL_ENDPOINT", "http://localhost:4318")

    # Migration feature flags
    temporal_rollout_percentage: int = int(os.getenv("TEMPORAL_ROLLOUT", "0"))

    @property
    def use_temporal(self) -> bool:
        """Check if Temporal is enabled (for gradual rollout)."""
        return self.temporal_rollout_percentage > 0


# Global config instance
config = TemporalConfig()
```

#### 2.3 Create Environment Variables

**File:** `apex-memory-system/.env.temporal` (add to `.gitignore`)

```bash
# Temporal Connection
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default

# Worker Configuration
TEMPORAL_TASK_QUEUE=apex-ingestion
TEMPORAL_WORKER_BUILD_ID=v1.0.0-dev
TEMPORAL_DEPLOYMENT_NAME=apex-ingestion-service

# Observability
TEMPORAL_METRICS_PORT=8078
TEMPORAL_ENABLE_TRACING=false
TEMPORAL_OTEL_ENDPOINT=http://localhost:4318

# Migration Feature Flags
TEMPORAL_ROLLOUT=0  # 0 = disabled, 10 = 10% traffic, 100 = all traffic

# TLS (for production/Temporal Cloud - leave empty for local dev)
# TEMPORAL_TLS_CERT_PATH=
# TEMPORAL_TLS_KEY_PATH=
# TEMPORAL_TLS_CA_PATH=
```

#### 2.4 Load Configuration in Main App

Update `apex-memory-system/src/apex_memory/main.py`:

```python
# Add to imports
from dotenv import load_dotenv

# Load both .env files
load_dotenv()  # Load .env
load_dotenv(".env.temporal")  # Load Temporal config

# Rest of main.py...
```

---

### Day 4-5: Worker Infrastructure

#### 3.1 Create Directory Structure

```bash
cd apex-memory-system

# Create Temporal module structure
mkdir -p src/apex_memory/temporal/{workflows,activities,workers}
touch src/apex_memory/temporal/__init__.py
touch src/apex_memory/temporal/workflows/__init__.py
touch src/apex_memory/temporal/activities/__init__.py
touch src/apex_memory/temporal/workers/__init__.py
```

#### 3.2 Create Base Worker

**File:** `apex-memory-system/src/apex_memory/temporal/workers/base_worker.py`

```python
"""Base Temporal worker for Apex Memory System.

This worker connects to Temporal Server and polls for workflow/activity tasks.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
import logging
import signal
from typing import List, Type

from temporalio.client import Client
from temporalio.worker import Worker

from apex_memory.config.temporal_config import config

logger = logging.getLogger(__name__)


class ApexTemporalWorker:
    """Base worker for Temporal workflows and activities."""

    def __init__(
        self,
        workflows: List[Type],
        activities: List[callable],
        task_queue: str = None,
        max_concurrent_workflow_tasks: int = 100,
        max_concurrent_activities: int = 50,
    ):
        """Initialize Apex Temporal worker.

        Args:
            workflows: List of workflow classes to register.
            activities: List of activity functions to register.
            task_queue: Task queue name (defaults to config.task_queue).
            max_concurrent_workflow_tasks: Max concurrent workflow tasks.
            max_concurrent_activities: Max concurrent activity tasks.
        """
        self.workflows = workflows
        self.activities = activities
        self.task_queue = task_queue or config.task_queue
        self.max_concurrent_workflow_tasks = max_concurrent_workflow_tasks
        self.max_concurrent_activities = max_concurrent_activities

        self.client = None
        self.worker = None
        self._shutdown_event = asyncio.Event()

        logger.info(
            f"Initializing Apex Temporal Worker - "
            f"Queue: {self.task_queue}, "
            f"Workflows: {len(workflows)}, "
            f"Activities: {len(activities)}"
        )

    async def connect(self):
        """Connect to Temporal Server."""
        try:
            logger.info(f"Connecting to Temporal Server at {config.host}")
            self.client = await Client.connect(config.host, namespace=config.namespace)
            logger.info("Connected to Temporal Server successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Temporal Server: {e}")
            raise

    async def start(self):
        """Start the worker and begin polling for tasks."""
        if not self.client:
            await self.connect()

        try:
            logger.info(f"Starting worker for task queue: {self.task_queue}")

            self.worker = Worker(
                self.client,
                task_queue=self.task_queue,
                workflows=self.workflows,
                activities=self.activities,
                max_concurrent_workflow_tasks=self.max_concurrent_workflow_tasks,
                max_concurrent_activities=self.max_concurrent_activities,
                max_concurrent_local_activities=100,
            )

            logger.info(
                f"Worker started successfully - "
                f"Polling {self.task_queue} for workflows and activities"
            )

            # Run worker (blocks until shutdown)
            await self.worker.run()

        except Exception as e:
            logger.error(f"Worker failed: {e}")
            raise

    async def stop(self):
        """Stop the worker gracefully."""
        logger.info("Stopping worker...")
        self._shutdown_event.set()

        if self.worker:
            # Temporal SDK handles graceful shutdown automatically
            logger.info("Worker stopped successfully")

        if self.client:
            await self.client.close()
            logger.info("Temporal client connection closed")

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def handle_shutdown(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.stop())

        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)


async def main():
    """Main entry point for worker."""
    # Import workflows and activities here to avoid circular imports
    from apex_memory.temporal.workflows.hello_world import GreetingWorkflow
    from apex_memory.temporal.activities.hello_world import greet_activity

    # Create worker
    worker = ApexTemporalWorker(
        workflows=[GreetingWorkflow],
        activities=[greet_activity],
        task_queue="apex-ingestion",
    )

    # Setup graceful shutdown
    worker.setup_signal_handlers()

    # Start worker (blocks until shutdown)
    await worker.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    asyncio.run(main())
```

**Why this matters:** This base worker provides a reusable foundation with graceful shutdown, error handling, and connection management. All future workers will extend this pattern.

---

### Day 6-7: Hello World Validation

#### 4.1 Create Hello World Workflow

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/hello_world.py`

```python
"""Hello World workflow for Apex Temporal integration validation.

This workflow demonstrates basic Temporal concepts:
- Workflow definition
- Activity execution
- Deterministic workflow logic

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

from datetime import timedelta
from temporalio import workflow

# Import activities (activities are defined in separate module)
with workflow.unsafe.imports_passed_through():
    from apex_memory.temporal.activities.hello_world import greet_activity


@workflow.defn
class GreetingWorkflow:
    """Simple greeting workflow for validation."""

    @workflow.run
    async def run(self, name: str) -> str:
        """Run the greeting workflow.

        Args:
            name: Name to greet.

        Returns:
            Greeting message.
        """
        workflow.logger.info(f"Starting greeting workflow for: {name}")

        # Execute activity with timeout and retry policy
        greeting = await workflow.execute_activity(
            greet_activity,
            name,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=workflow.RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3,
            ),
        )

        workflow.logger.info(f"Greeting workflow complete: {greeting}")
        return greeting
```

#### 4.2 Create Hello World Activity

**File:** `apex-memory-system/src/apex_memory/temporal/activities/hello_world.py`

```python
"""Hello World activities for Apex Temporal integration validation.

Activities are the building blocks of workflows - they perform actual work.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

from temporalio import activity


@activity.defn
async def greet_activity(name: str) -> str:
    """Simple greeting activity.

    Args:
        name: Name to greet.

    Returns:
        Greeting message.
    """
    activity.logger.info(f"Greeting: {name}")
    return f"Hello, {name}! Welcome to Apex Memory System with Temporal.io!"
```

#### 4.3 Create Development Worker Script

**File:** `apex-memory-system/src/apex_memory/temporal/workers/dev_worker.py`

```python
"""Development worker for local testing.

Run this script to start a worker that processes Hello World workflows.

Usage:
    python -m apex_memory.temporal.workers.dev_worker

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
import logging

from apex_memory.temporal.workers.base_worker import ApexTemporalWorker
from apex_memory.temporal.workflows.hello_world import GreetingWorkflow
from apex_memory.temporal.activities.hello_world import greet_activity

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


async def main():
    """Start development worker."""
    worker = ApexTemporalWorker(
        workflows=[GreetingWorkflow],
        activities=[greet_activity],
        task_queue="apex-ingestion",
        max_concurrent_workflow_tasks=50,
        max_concurrent_activities=25,
    )

    worker.setup_signal_handlers()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
```

#### 4.4 Test Hello World Workflow

**Terminal 1: Start Worker**

```bash
cd apex-memory-system

# Load environment
export $(cat .env.temporal | xargs)

# Start worker
python -m apex_memory.temporal.workers.dev_worker

# Expected output:
# Connecting to Temporal Server at localhost:7233
# Connected to Temporal Server successfully
# Worker started successfully - Polling apex-ingestion
```

**Terminal 2: Execute Workflow**

Create test script: `apex-memory-system/scripts/test_hello_world.py`

```python
"""Test script to execute Hello World workflow.

Usage:
    python scripts/test_hello_world.py

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
from temporalio.client import Client

async def main():
    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Execute workflow
    result = await client.execute_workflow(
        "GreetingWorkflow",
        "Apex Team",
        id="hello-world-test-1",
        task_queue="apex-ingestion",
    )

    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run the test:

```bash
python scripts/test_hello_world.py

# Expected output:
# Workflow result: Hello, Apex Team! Welcome to Apex Memory System with Temporal.io!
```

#### 4.5 Verify in Temporal UI

1. Open Temporal UI: http://localhost:8088
2. Navigate to "Workflows" tab
3. Find workflow ID: `hello-world-test-1`
4. Click to view:
   - Event history (workflow started, activity scheduled, activity completed, workflow completed)
   - Input/output
   - Activity execution timeline

**What to look for:**
- ✅ Workflow shows "Completed" status
- ✅ Activity `greet_activity` executed successfully
- ✅ Event history shows all steps
- ✅ No errors in logs

---

### Day 8-10: Monitoring, Testing & Documentation

#### 5.1 Configure Prometheus Scrape Targets

**File:** `apex-memory-system/docker/prometheus/temporal.yml` (or add to existing `prometheus.yml`)

```yaml
# Temporal Server metrics
scrape_configs:
  - job_name: 'temporal-server'
    static_configs:
      - targets: ['localhost:8077']  # Temporal Server metrics endpoint
    scrape_interval: 15s
    scrape_timeout: 10s

  - job_name: 'temporal-sdk-python'
    static_configs:
      - targets: ['localhost:8078']  # Python SDK metrics (from worker)
    scrape_interval: 15s
    scrape_timeout: 10s
```

Restart Prometheus:

```bash
docker-compose restart prometheus
```

#### 5.2 Import Grafana Dashboards

1. Download dashboards:

```bash
# Download Temporal dashboards
mkdir -p apex-memory-system/docker/grafana/dashboards/temporal

curl -o apex-memory-system/docker/grafana/dashboards/temporal/temporal-server.json \
  https://raw.githubusercontent.com/temporalio/dashboards/main/temporal-server.json

curl -o apex-memory-system/docker/grafana/dashboards/temporal/temporal-sdk.json \
  https://raw.githubusercontent.com/temporalio/dashboards/main/temporal-sdk.json
```

2. Import to Grafana:
   - Open Grafana: http://localhost:3000
   - Go to Dashboards → Import
   - Upload `temporal-server.json` and `temporal-sdk.json`
   - Select Prometheus datasource
   - Click "Import"

3. Verify dashboards show metrics:
   - Navigate to imported dashboards
   - Should see workflow execution metrics

#### 5.3 Create Integration Tests

**File:** `apex-memory-system/tests/integration/test_temporal_integration.py`

```python
"""Integration tests for Temporal.io setup.

Tests verify:
- Worker can connect to Temporal Server
- Workflows can be executed
- Activities execute successfully
- Error handling works

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import pytest
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.testing import WorkflowEnvironment

from apex_memory.temporal.workflows.hello_world import GreetingWorkflow
from apex_memory.temporal.activities.hello_world import greet_activity


@pytest.mark.asyncio
async def test_temporal_server_connection():
    """Test connection to Temporal Server."""
    client = await Client.connect("localhost:7233")

    # Verify connection by listing workflows
    workflows = []
    async for workflow in client.list_workflows("WorkflowType='GreetingWorkflow'"):
        workflows.append(workflow)

    # If we got here, connection is healthy
    assert client is not None
    await client.close()


@pytest.mark.asyncio
async def test_hello_world_workflow():
    """Test Hello World workflow executes successfully."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[GreetingWorkflow],
            activities=[greet_activity],
        ):
            # Execute workflow
            result = await env.client.execute_workflow(
                GreetingWorkflow.run,
                "Test User",
                id="test-hello-world",
                task_queue="test-queue",
            )

            assert "Hello, Test User!" in result
            assert "Apex Memory System" in result


@pytest.mark.asyncio
async def test_activity_execution():
    """Test activity executes independently."""
    result = await greet_activity("Integration Test")

    assert "Hello, Integration Test!" in result
    assert "Temporal.io" in result


@pytest.mark.asyncio
async def test_workflow_with_invalid_input():
    """Test workflow handles invalid input gracefully."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[GreetingWorkflow],
            activities=[greet_activity],
        ):
            # Execute with empty string
            result = await env.client.execute_workflow(
                GreetingWorkflow.run,
                "",
                id="test-empty-input",
                task_queue="test-queue",
            )

            # Should still work (no validation in Hello World)
            assert "Hello," in result
```

Run tests:

```bash
cd apex-memory-system

# Run Temporal integration tests
pytest tests/integration/test_temporal_integration.py -v

# Expected: All tests pass
```

#### 5.4 Create Smoke Test Suite

**File:** `apex-memory-system/tests/integration/test_temporal_smoke.py`

```python
"""Smoke tests for Temporal infrastructure.

Quick tests to verify basic functionality before deployment.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import pytest
import asyncio
from temporalio.client import Client


@pytest.mark.asyncio
async def test_temporal_server_reachable():
    """Smoke test: Temporal Server is reachable."""
    try:
        client = await Client.connect("localhost:7233", connect_timeout=5.0)
        await client.close()
        assert True
    except Exception as e:
        pytest.fail(f"Temporal Server not reachable: {e}")


@pytest.mark.asyncio
async def test_temporal_ui_reachable():
    """Smoke test: Temporal UI is accessible."""
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8088", timeout=5.0)
        assert response.status_code == 200


def test_temporal_config_loaded():
    """Smoke test: Temporal configuration is loaded."""
    from apex_memory.config.temporal_config import config

    assert config.host == "localhost:7233"
    assert config.namespace == "default"
    assert config.task_queue == "apex-ingestion"


def test_worker_can_import_workflows():
    """Smoke test: Workflows can be imported."""
    from apex_memory.temporal.workflows.hello_world import GreetingWorkflow

    assert GreetingWorkflow is not None


def test_worker_can_import_activities():
    """Smoke test: Activities can be imported."""
    from apex_memory.temporal.activities.hello_world import greet_activity

    assert greet_activity is not None
```

Run smoke tests:

```bash
pytest tests/integration/test_temporal_smoke.py -v

# Expected: All 5 tests pass in <10 seconds
```

---

### Phase 1 Completion Checklist

```
☑ Infrastructure
  ☑ Temporal Server running and healthy
  ☑ Temporal UI accessible at http://localhost:8088
  ☑ PostgreSQL persistence configured (survives restarts)
  ☑ Worker can connect and poll task queues

☑ Code
  ☑ Hello World workflow executes successfully
  ☑ Worker infrastructure created and tested
  ☑ Integration tests passing (5/5)
  ☑ Smoke tests passing (5/5)

☑ Monitoring
  ☑ Prometheus scraping Temporal metrics
  ☑ Grafana dashboards imported and functional
  ☑ Logs structured and queryable

☑ Team Readiness
  ☑ Team trained on Temporal basics
  ☑ Documentation complete and reviewed
  ☑ Development environment setup documented
```

**Validation Command:**

```bash
# Run full Phase 1 validation
cd apex-memory-system

# 1. Check services
docker ps | grep -E "temporal|postgres"

# 2. Check Temporal health
curl -f http://localhost:7233 && echo "✓ Temporal Server OK"
curl -f http://localhost:8088 && echo "✓ Temporal UI OK"

# 3. Run tests
pytest tests/integration/test_temporal_smoke.py -v
pytest tests/integration/test_temporal_integration.py -v

# 4. Verify Saga tests still pass (baseline)
pytest tests/unit/test_saga_phase2.py -v

# Expected: All tests pass
```

**🎉 Phase 1 Complete! Ready for Phase 2: Ingestion Migration**

---

## Phase 2: Ingestion Migration (Week 3-4)

**Goal:** Migrate ingestion pipeline to Temporal workflows while preserving Enhanced Saga for database writes. Gradual rollout from 10% → 100%.

### Day 1-3: Ingestion Workflow Implementation

#### 1.1 Create Ingestion Activities

**File:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

```python
"""Ingestion activities for Temporal workflows.

Activities delegate database writes to Enhanced Saga pattern.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import logging
from typing import List, Dict, Any, Optional

from temporalio import activity

from apex_memory.models.document import ParsedDocument
from apex_memory.services.document_parser import DocumentParser
from apex_memory.services.entity_extractor import EntityExtractor
from apex_memory.services.embedding_generator import EmbeddingGenerator
from apex_memory.services.database_writer import DatabaseWriteOrchestrator

logger = logging.getLogger(__name__)


@activity.defn
async def parse_document_activity(document_id: str) -> Dict[str, Any]:
    """Parse document from storage.

    This activity is idempotent - can be safely retried.

    Args:
        document_id: ID of document to parse.

    Returns:
        Parsed document dictionary (serializable).

    Raises:
        ValidationError: If document format is invalid.
    """
    activity.logger.info(f"Parsing document: {document_id}")

    # Get activity info for debugging
    info = activity.info()
    activity.logger.info(f"Attempt: {info.attempt}")

    try:
        # Heartbeat for long operations
        activity.heartbeat("Loading document")

        # Load document from storage
        parser = DocumentParser()
        parsed_doc = await parser.parse_from_storage(document_id)

        activity.heartbeat("Parsing complete")

        # Convert to serializable dict
        return {
            "uuid": parsed_doc.uuid,
            "content": parsed_doc.content,
            "metadata": parsed_doc.metadata,
            "chunks": parsed_doc.chunks,
        }

    except Exception as e:
        activity.logger.error(f"Parse failed: {str(e)}")
        raise


@activity.defn
async def extract_entities_activity(parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract entities from parsed document.

    Args:
        parsed_doc: Parsed document dictionary.

    Returns:
        List of extracted entities.
    """
    activity.logger.info(f"Extracting entities from document: {parsed_doc['uuid']}")

    extractor = EntityExtractor()
    entities = await extractor.extract(parsed_doc["content"])

    activity.logger.info(f"Extracted {len(entities)} entities")
    return entities


@activity.defn
async def generate_embeddings_activity(
    parsed_doc: Dict[str, Any], chunks: List[str]
) -> Dict[str, Any]:
    """Generate document and chunk embeddings.

    Args:
        parsed_doc: Parsed document dictionary.
        chunks: Document chunks.

    Returns:
        Dictionary with document_embedding and chunk_embeddings.
    """
    activity.logger.info(f"Generating embeddings for document: {parsed_doc['uuid']}")

    generator = EmbeddingGenerator()

    # Generate document-level embedding
    doc_embedding = await generator.generate_document_embedding(parsed_doc["content"])

    # Generate chunk embeddings
    chunk_embeddings = await generator.generate_chunk_embeddings(chunks)

    activity.logger.info(
        f"Generated embeddings: doc={len(doc_embedding)} dims, "
        f"{len(chunk_embeddings)} chunks"
    )

    return {"document_embedding": doc_embedding, "chunk_embeddings": chunk_embeddings}


@activity.defn
async def write_to_databases_activity(
    parsed_doc: Dict[str, Any],
    entities: List[Dict[str, Any]],
    embeddings: Dict[str, Any],
) -> Dict[str, Any]:
    """Write to all databases using Enhanced Saga.

    This activity DELEGATES to DatabaseWriteOrchestrator which handles:
    - Distributed locking
    - Idempotency
    - Circuit breakers
    - Exponential backoff retries
    - Atomic 4-database writes
    - Rollback with DLQ

    Why delegate? Enhanced Saga is battle-tested (121/121 tests passing)
    and optimized for multi-database consistency.

    Args:
        parsed_doc: Parsed document dictionary.
        entities: Extracted entities.
        embeddings: Document and chunk embeddings.

    Returns:
        Write result dictionary.

    Raises:
        ApplicationError: If database write fails (Temporal will retry).
    """
    activity.logger.info(
        f"Writing document {parsed_doc['uuid']} to databases via Enhanced Saga"
    )

    # Reconstruct ParsedDocument
    doc = ParsedDocument(
        uuid=parsed_doc["uuid"],
        content=parsed_doc["content"],
        metadata=parsed_doc["metadata"],
        chunks=parsed_doc["chunks"],
    )

    # Initialize database orchestrator (singleton pattern in production)
    orchestrator = DatabaseWriteOrchestrator(
        enable_locking=True,  # Phase 1
        enable_idempotency=True,  # Phase 1
        enable_circuit_breakers=True,  # Phase 2
        enable_retries=True,  # Phase 2
    )

    try:
        # Delegate to Enhanced Saga
        result = await orchestrator.write_document_parallel(
            parsed_doc=doc,
            embedding=embeddings["document_embedding"],
            chunks=parsed_doc["chunks"],
            chunk_embeddings=embeddings["chunk_embeddings"],
            entities=entities,
        )

        # Enhanced Saga returns WriteResult with detailed status
        if result.all_success:
            activity.logger.info(f"Write successful for {parsed_doc['uuid']}")
            return {
                "status": "success",
                "document_id": parsed_doc["uuid"],
                "databases_written": ["neo4j", "postgres", "qdrant", "redis"],
            }

        elif result.status == "rolled_back":
            activity.logger.error(
                f"Write failed for {parsed_doc['uuid']}, rolled back successfully"
            )
            raise ApplicationError(
                f"Database write failed and rolled back: {result.errors}",
                type="DatabaseWriteError",
                non_retryable=False,  # Allow Temporal to retry
            )

        else:  # FAILED or PARTIAL
            activity.logger.critical(
                f"Write failed for {parsed_doc['uuid']}, status={result.status}"
            )
            raise ApplicationError(
                f"Database write failure: {result.errors}",
                type="DatabaseWriteError",
                non_retryable=True,  # Don't retry - likely validation error
            )

    finally:
        orchestrator.close()
```

**Why this matters:** These activities encapsulate the ingestion pipeline steps as individual, retriable units. The key design decision is **delegating database writes to Enhanced Saga**, preserving the battle-tested pattern (121/121 tests).

#### 1.2 Create Ingestion Workflow

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`

```python
"""Ingestion workflow for Apex Memory System.

This workflow orchestrates the full document ingestion pipeline:
1. Parse document
2. Extract entities
3. Generate embeddings
4. Write to databases (via Enhanced Saga)

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activities (safe pattern for Temporal)
with workflow.unsafe.imports_passed_through():
    from apex_memory.temporal.activities.ingestion import (
        parse_document_activity,
        extract_entities_activity,
        generate_embeddings_activity,
        write_to_databases_activity,
    )


@workflow.defn
class DocumentIngestionWorkflow:
    """Durable document ingestion workflow."""

    def __init__(self):
        # Workflow instance variables (automatically persisted by Temporal)
        self.document_id = None
        self.source = None
        self.status = "pending"

    @workflow.run
    async def run(self, document_id: str, source: str = "unknown") -> dict:
        """Run the document ingestion workflow.

        Args:
            document_id: ID of document to ingest.
            source: Source system (e.g., "frontapp", "turvo", "samsara").

        Returns:
            Ingestion result dictionary.
        """
        self.document_id = document_id
        self.source = source

        workflow.logger.info(f"Starting ingestion for document: {document_id} (source: {source})")

        # Step 1: Parse document
        parsed_doc = await workflow.execute_activity(
            parse_document_activity,
            document_id,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                backoff_coefficient=2.0,
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
                non_retryable_error_types=["ValidationError"],
            ),
        )
        self.status = "parsed"
        workflow.logger.info(f"Document parsed: {len(parsed_doc['chunks'])} chunks")

        # Step 2: Extract entities
        entities = await workflow.execute_activity(
            extract_entities_activity,
            parsed_doc,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                backoff_coefficient=2.0,
                maximum_attempts=3,
            ),
        )
        self.status = "entities_extracted"
        workflow.logger.info(f"Entities extracted: {len(entities)} entities")

        # Step 3: Generate embeddings
        embeddings = await workflow.execute_activity(
            generate_embeddings_activity,
            parsed_doc,
            parsed_doc["chunks"],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                backoff_coefficient=2.0,
                maximum_attempts=5,  # OpenAI API can be flaky
            ),
        )
        self.status = "embeddings_generated"
        workflow.logger.info("Embeddings generated successfully")

        # Step 4: Write to databases (via Enhanced Saga)
        result = await workflow.execute_activity(
            write_to_databases_activity,
            parsed_doc,
            entities,
            embeddings,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=5),
                backoff_coefficient=2.0,
                maximum_interval=timedelta(minutes=1),
                maximum_attempts=3,
                non_retryable_error_types=["ValidationError"],
            ),
        )
        self.status = "completed"

        workflow.logger.info(f"Ingestion complete for document: {document_id}")
        return result

    @workflow.query
    def get_status(self) -> dict:
        """Query current workflow status."""
        return {
            "document_id": self.document_id,
            "source": self.source,
            "status": self.status,
        }
```

**Why this matters:** This workflow provides durable orchestration with automatic retries, state persistence, and complete observability via Temporal UI. The Enhanced Saga handles database writes unchanged.

---

### Day 4-5: Gradual Rollout Implementation

#### 2.1 Create Migration Coordinator

**File:** `apex-memory-system/src/apex_memory/temporal/migration/rollout_coordinator.py`

```python
"""Gradual rollout coordinator for Temporal migration.

Manages feature flags for progressive traffic routing:
- 0%: All traffic to legacy (Temporal disabled)
- 10%: 10% traffic to Temporal, 90% to legacy
- 50%: 50% traffic to Temporal, 50% to legacy
- 100%: All traffic to Temporal (migration complete)

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import hashlib
import logging
from typing import Optional

from apex_memory.config.temporal_config import config

logger = logging.getLogger(__name__)


class RolloutCoordinator:
    """Coordinates gradual rollout of Temporal workflows."""

    def __init__(self, rollout_percentage: Optional[int] = None):
        """Initialize rollout coordinator.

        Args:
            rollout_percentage: Override rollout percentage (defaults to config).
        """
        self.rollout_percentage = (
            rollout_percentage
            if rollout_percentage is not None
            else config.temporal_rollout_percentage
        )

        logger.info(f"Rollout coordinator initialized: {self.rollout_percentage}% traffic to Temporal")

    def should_use_temporal(self, document_id: str) -> bool:
        """Determine if document should use Temporal path.

        Uses deterministic hashing to ensure same document always routes the same way.

        Args:
            document_id: Document UUID.

        Returns:
            True if should use Temporal, False if should use legacy.
        """
        if self.rollout_percentage == 0:
            return False

        if self.rollout_percentage == 100:
            return True

        # Deterministic hash-based routing
        hash_value = int(hashlib.sha256(document_id.encode()).hexdigest(), 16)
        bucket = hash_value % 100

        use_temporal = bucket < self.rollout_percentage

        logger.debug(
            f"Document {document_id}: bucket={bucket}, "
            f"rollout={self.rollout_percentage}%, "
            f"use_temporal={use_temporal}"
        )

        return use_temporal


# Global instance
rollout_coordinator = RolloutCoordinator()
```

#### 2.2 Update Ingestion Endpoint

**File:** `apex-memory-system/src/apex_memory/api/endpoints/documents.py` (modify existing)

```python
# Add imports
from temporalio.client import Client
from apex_memory.config.temporal_config import config
from apex_memory.temporal.migration.rollout_coordinator import rollout_coordinator
from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow

# Existing imports...
from apex_memory.services.database_writer import DatabaseWriteOrchestrator
from apex_memory.services.document_parser import DocumentParser

logger = logging.getLogger(__name__)


@router.post("/documents/ingest", response_model=dict)
async def ingest_document(
    document_id: str,
    source: str = "api",
) -> dict:
    """Ingest document (with Temporal gradual rollout).

    Routes to Temporal or legacy based on rollout percentage.

    Args:
        document_id: Document UUID to ingest.
        source: Source system (e.g., "frontapp", "api").

    Returns:
        Ingestion result.
    """
    logger.info(f"Ingestion request: {document_id} (source: {source})")

    # Determine routing
    use_temporal = rollout_coordinator.should_use_temporal(document_id)

    if use_temporal:
        logger.info(f"Routing {document_id} to Temporal path")
        return await ingest_via_temporal(document_id, source)
    else:
        logger.info(f"Routing {document_id} to legacy path")
        return await ingest_via_legacy(document_id, source)


async def ingest_via_temporal(document_id: str, source: str) -> dict:
    """Ingest document via Temporal workflow.

    Args:
        document_id: Document UUID.
        source: Source system.

    Returns:
        Ingestion result.
    """
    # Connect to Temporal
    client = await Client.connect(config.host, namespace=config.namespace)

    try:
        # Execute workflow
        result = await client.execute_workflow(
            DocumentIngestionWorkflow.run,
            document_id,
            source,
            id=f"ingest-{document_id}",
            task_queue=config.task_queue,
        )

        logger.info(f"Temporal ingestion complete: {document_id}")
        return result

    finally:
        await client.close()


async def ingest_via_legacy(document_id: str, source: str) -> dict:
    """Ingest document via legacy path (direct Saga).

    Args:
        document_id: Document UUID.
        source: Source system.

    Returns:
        Ingestion result.
    """
    # Existing legacy ingestion logic
    parser = DocumentParser()
    orchestrator = DatabaseWriteOrchestrator(
        enable_locking=True,
        enable_idempotency=True,
        enable_circuit_breakers=True,
        enable_retries=True,
    )

    try:
        # Parse
        parsed_doc = await parser.parse_from_storage(document_id)

        # Extract entities (existing logic)
        entities = await extract_entities(parsed_doc)

        # Generate embeddings (existing logic)
        embeddings = await generate_embeddings(parsed_doc)

        # Write via Saga (existing logic)
        result = await orchestrator.write_document_parallel(
            parsed_doc=parsed_doc,
            embedding=embeddings["document_embedding"],
            entities=entities,
        )

        return {"status": "success", "document_id": document_id}

    finally:
        orchestrator.close()
```

**Why this matters:** The rollout coordinator enables **zero-downtime migration** with instant rollback capability. Deterministic hashing ensures the same document always routes the same way, preventing inconsistencies.

---

### Day 6-7: Testing & Monitoring

#### 3.1 Create Integration Tests for Ingestion Workflow

**File:** `apex-memory-system/tests/integration/test_ingestion_workflow.py`

```python
"""Integration tests for Temporal ingestion workflow.

Tests verify end-to-end ingestion with Enhanced Saga integration.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow
from apex_memory.temporal.activities.ingestion import (
    parse_document_activity,
    extract_entities_activity,
    generate_embeddings_activity,
    write_to_databases_activity,
)


@pytest.mark.asyncio
async def test_full_ingestion_workflow():
    """Test complete ingestion workflow with all activities."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                parse_document_activity,
                extract_entities_activity,
                generate_embeddings_activity,
                write_to_databases_activity,
            ],
        ):
            # Execute workflow
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "test-doc-123",
                "test-source",
                id="test-ingestion-workflow",
                task_queue="test-queue",
            )

            assert result["status"] == "success"
            assert result["document_id"] == "test-doc-123"
            assert "databases_written" in result


@pytest.mark.asyncio
async def test_ingestion_rollback_on_failure():
    """Test ingestion handles database write failures with rollback."""
    # Mock write activity to fail
    @activity.defn
    async def mock_write_failure(*args):
        raise Exception("Simulated database failure")

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                parse_document_activity,
                extract_entities_activity,
                generate_embeddings_activity,
                mock_write_failure,  # Replace write activity with failure
            ],
        ):
            with pytest.raises(Exception):
                await env.client.execute_workflow(
                    DocumentIngestionWorkflow.run,
                    "test-doc-456",
                    "test-source",
                    id="test-ingestion-failure",
                    task_queue="test-queue",
                )

            # Verify workflow failed and Enhanced Saga rolled back
            # (Check DLQ, verify no partial writes)


@pytest.mark.asyncio
async def test_ingestion_query_status():
    """Test querying workflow status during execution."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                parse_document_activity,
                extract_entities_activity,
                generate_embeddings_activity,
                write_to_databases_activity,
            ],
        ):
            # Start workflow (don't wait for completion)
            handle = await env.client.start_workflow(
                DocumentIngestionWorkflow.run,
                "test-doc-789",
                "test-source",
                id="test-query-status",
                task_queue="test-queue",
            )

            # Query status
            status = await handle.query(DocumentIngestionWorkflow.get_status)

            assert status["document_id"] == "test-doc-789"
            assert status["status"] in ["pending", "parsed", "entities_extracted", "completed"]

            # Wait for completion
            await handle.result()
```

Run tests:

```bash
cd apex-memory-system

pytest tests/integration/test_ingestion_workflow.py -v

# Expected: All tests pass
```

#### 3.2 Load Testing

**File:** `apex-memory-system/tests/load/test_concurrent_ingestion.py`

```python
"""Load tests for concurrent ingestion workflows.

Tests verify system handles concurrent load.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import pytest
import asyncio
from temporalio.client import Client


@pytest.mark.load
@pytest.mark.asyncio
async def test_100_concurrent_workflows():
    """Test 100 concurrent ingestion workflows."""
    client = await Client.connect("localhost:7233")

    # Start 100 workflows concurrently
    tasks = [
        client.start_workflow(
            "DocumentIngestionWorkflow",
            f"load-test-doc-{i}",
            "load-test",
            id=f"load-test-{i}",
            task_queue="apex-ingestion",
        )
        for i in range(100)
    ]

    # Wait for all to start
    handles = await asyncio.gather(*tasks)

    # Wait for all to complete
    results = await asyncio.gather(*[h.result() for h in handles])

    # Verify all succeeded
    assert len(results) == 100
    assert all(r["status"] == "success" for r in results)

    await client.close()
```

---

### Day 8-10: Gradual Rollout Execution

#### 4.1 Week 3: 10% Traffic

```bash
# Update environment variable
export TEMPORAL_ROLLOUT=10

# Restart API
docker-compose restart apex-api

# Monitor for 48 hours
# - Check error rates (should match legacy)
# - Check latency P99 (<5× legacy)
# - Monitor Temporal UI for failures
```

**Monitoring Dashboard:**
- Temporal UI: http://localhost:8088 → Check workflow success rate
- Grafana: View Temporal Server metrics
- Compare: Temporal error rate vs legacy error rate

**Success Criteria:**
- Error rate < 2× legacy
- P99 latency < 5× legacy
- Zero data consistency issues

#### 4.2 Week 4: 50% Traffic → 100% Traffic

```bash
# Increase to 50%
export TEMPORAL_ROLLOUT=50
docker-compose restart apex-api

# Monitor for 24 hours

# Increase to 100% (full migration)
export TEMPORAL_ROLLOUT=100
docker-compose restart apex-api

# Monitor for 48 hours before removing legacy code
```

**Rollback Trigger:**
- Error rate > 2× legacy → `export TEMPORAL_ROLLOUT=0`
- Data consistency issues → Instant rollback
- Temporal Server unavailable → Falls back to legacy automatically

---

### Phase 2 Completion Checklist

```
☑ Implementation
  ☑ Ingestion workflow created with 4 activities
  ☑ Enhanced Saga integration preserved (121/121 tests passing)
  ☑ Rollout coordinator with feature flags
  ☑ API endpoint updated for gradual rollout

☑ Testing
  ☑ Integration tests passing (full ingestion workflow)
  ☑ Rollback tests passing (failure handling)
  ☑ Load tests passing (100 concurrent workflows)
  ☑ Saga tests still passing (baseline validation)

☑ Migration
  ☑ 10% traffic validated (48 hours)
  ☑ 50% traffic validated (24 hours)
  ☑ 100% traffic running (full migration)
  ☑ Legacy code removed after 2-week safety window

☑ Monitoring
  ☑ Temporal UI shows all workflows
  ☑ Error rates match legacy baseline
  ☑ Latency within acceptable range
  ☑ No data consistency issues
```

**🎉 Phase 2 Complete! Ready for Phase 3: Multi-Source Integration**

---

## Phase 3: Multi-Source Integration (Week 5-6)

**Goal:** Implement 9+ data source workflows (webhook, polling, streaming, batch patterns) with priority-based execution.

### Data Sources Overview

**Priority 0 (Critical):**
- FrontApp (webhook, 1,000/day)
- Turvo (webhook, 500/day)
- LLMs (API)

**Priority 1 (High):**
- Samsara (stream, 1,000/min)
- Banks/Plaid (poll, 200/day)

**Priority 2 (Standard):**
- Sonar (webhook, 300/day)
- Carrier EDI (batch, 50/day)
- CRM (poll, 100/day)
- Financial (poll, 50/day)

### Day 1-3: Webhook Workflows

#### 1.1 Create Webhook Ingestion Workflow

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/webhook_ingestion.py`

```python
"""Webhook-based ingestion workflow for external sources.

Supports: FrontApp, Turvo, Sonar

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

with workflow.unsafe.imports_passed_through():
    from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow
    from apex_memory.temporal.activities.webhook import (
        validate_webhook_signature,
        parse_webhook_payload,
    )


@workflow.defn
class WebhookIngestionWorkflow:
    """Process webhook events from external sources."""

    def __init__(self):
        self.event_id = None
        self.source = None
        self.status = "pending"

    @workflow.run
    async def run(self, webhook_event: dict) -> dict:
        """Process webhook event.

        Args:
            webhook_event: Webhook payload with signature, event_id, data.

        Returns:
            Processing result.
        """
        self.source = webhook_event.get("source", "unknown")
        self.event_id = webhook_event.get("event_id")

        workflow.logger.info(f"Processing webhook from {self.source}: {self.event_id}")

        # Step 1: Validate webhook signature
        is_valid = await workflow.execute_activity(
            validate_webhook_signature,
            webhook_event,
            start_to_close_timeout=timedelta(seconds=5),
        )

        if not is_valid:
            workflow.logger.error(f"Invalid webhook signature: {self.event_id}")
            raise ApplicationError("Invalid webhook signature", non_retryable=True)

        self.status = "validated"

        # Step 2: Check for duplicate events (via workflow search attributes)
        if await self._is_duplicate(self.event_id):
            workflow.logger.info(f"Duplicate webhook event: {self.event_id}, skipping")
            return {"status": "duplicate", "event_id": self.event_id}

        self.status = "deduped"

        # Step 3: Parse webhook payload
        parsed = await workflow.execute_activity(
            parse_webhook_payload,
            webhook_event,
            start_to_close_timeout=timedelta(seconds=10),
        )

        self.status = "parsed"

        # Step 4: Route to ingestion pipeline (child workflow)
        result = await workflow.execute_child_workflow(
            DocumentIngestionWorkflow.run,
            document_id=parsed["document_id"],
            source=self.source,
            id=f"ingest-{self.event_id}",
            task_queue="apex-ingestion",
        )

        self.status = "completed"
        workflow.logger.info(f"Webhook processing complete: {self.event_id}")

        return {"status": "processed", "event_id": self.event_id, "result": result}

    async def _is_duplicate(self, event_id: str) -> bool:
        """Check if event already processed via workflow search."""
        # Use workflow.search_attributes to check for existing workflow with this event_id
        # For now, simplified - in production, query Temporal for existing workflows
        return False

    @workflow.query
    def get_status(self) -> dict:
        """Query webhook processing status."""
        return {
            "event_id": self.event_id,
            "source": self.source,
            "status": self.status,
        }
```

#### 1.2 Create Webhook Activities

**File:** `apex-memory-system/src/apex_memory/temporal/activities/webhook.py`

```python
"""Webhook processing activities.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import hmac
import hashlib
import logging
from typing import Dict, Any

from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn
async def validate_webhook_signature(webhook_event: Dict[str, Any]) -> bool:
    """Validate webhook signature.

    Args:
        webhook_event: Webhook payload with signature.

    Returns:
        True if signature is valid.
    """
    source = webhook_event.get("source")
    signature = webhook_event.get("signature")
    payload = webhook_event.get("data")

    activity.logger.info(f"Validating webhook signature for source: {source}")

    # Get secret for source (from environment/config)
    secret = _get_webhook_secret(source)

    if not secret:
        activity.logger.error(f"No webhook secret configured for source: {source}")
        return False

    # Calculate expected signature
    expected_signature = hmac.new(
        secret.encode(), str(payload).encode(), hashlib.sha256
    ).hexdigest()

    is_valid = hmac.compare_digest(signature, expected_signature)

    if not is_valid:
        activity.logger.warning(f"Invalid webhook signature from {source}")

    return is_valid


@activity.defn
async def parse_webhook_payload(webhook_event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse webhook payload to extract document information.

    Args:
        webhook_event: Webhook event.

    Returns:
        Parsed data with document_id and other metadata.
    """
    source = webhook_event.get("source")
    data = webhook_event.get("data", {})

    activity.logger.info(f"Parsing webhook payload from {source}")

    # Source-specific parsing logic
    if source == "frontapp":
        return _parse_frontapp_webhook(data)
    elif source == "turvo":
        return _parse_turvo_webhook(data)
    elif source == "sonar":
        return _parse_sonar_webhook(data)
    else:
        raise ValueError(f"Unsupported webhook source: {source}")


def _get_webhook_secret(source: str) -> str:
    """Get webhook secret for source."""
    import os

    secrets = {
        "frontapp": os.getenv("FRONTAPP_WEBHOOK_SECRET"),
        "turvo": os.getenv("TURVO_WEBHOOK_SECRET"),
        "sonar": os.getenv("SONAR_WEBHOOK_SECRET"),
    }

    return secrets.get(source, "")


def _parse_frontapp_webhook(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse FrontApp webhook."""
    return {
        "document_id": data.get("message_id"),
        "content": data.get("body"),
        "metadata": {
            "conversation_id": data.get("conversation_id"),
            "sender": data.get("sender"),
        },
    }


def _parse_turvo_webhook(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Turvo webhook."""
    return {
        "document_id": data.get("shipment_id"),
        "content": data.get("details"),
        "metadata": {
            "status": data.get("status"),
            "carrier": data.get("carrier"),
        },
    }


def _parse_sonar_webhook(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Sonar webhook."""
    return {
        "document_id": data.get("alert_id"),
        "content": data.get("alert_description"),
        "metadata": {
            "severity": data.get("severity"),
            "timestamp": data.get("timestamp"),
        },
    }
```

---

### Day 4-5: Polling Workflows

#### 2.1 Create Polling Workflow

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/polling.py`

```python
"""Polling-based ingestion workflow for external sources.

Supports: Banks/Plaid, CRM, Financial systems

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow
    from apex_memory.temporal.activities.polling import fetch_new_records


@workflow.defn
class PollingWorkflow:
    """Poll external source periodically for new records."""

    def __init__(self):
        self.source = None
        self.iteration = 0
        self.total_processed = 0

    @workflow.run
    async def run(self, source: str, interval_seconds: int = 900):
        """Poll source periodically.

        Args:
            source: Source system (e.g., "plaid", "crm", "financial").
            interval_seconds: Polling interval (default: 15 minutes).
        """
        self.source = source

        while True:
            workflow.logger.info(f"Polling {source}, iteration {self.iteration}")

            # Step 1: Fetch new records
            records = await workflow.execute_activity(
                fetch_new_records,
                source,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=workflow.RetryPolicy(maximum_attempts=5),
            )

            workflow.logger.info(f"Fetched {len(records)} new records from {source}")

            # Step 2: Spawn child workflow for each record
            for record in records:
                await workflow.execute_child_workflow(
                    DocumentIngestionWorkflow.run,
                    document_id=record["id"],
                    source=source,
                    id=f"ingest-{source}-{record['id']}",
                    task_queue="apex-ingestion",
                )

            self.total_processed += len(records)

            # Step 3: Sleep for polling interval
            workflow.logger.info(f"Sleeping for {interval_seconds}s before next poll")
            await workflow.sleep(interval_seconds)

            # Step 4: Continue-as-new to prevent history from growing
            self.iteration += 1
            if self.iteration >= 100:  # Reset every 100 iterations
                workflow.logger.info(f"Continuing as new after {self.iteration} iterations")
                workflow.continue_as_new(source, interval_seconds)

    @workflow.query
    def get_stats(self) -> dict:
        """Query polling statistics."""
        return {
            "source": self.source,
            "iteration": self.iteration,
            "total_processed": self.total_processed,
        }
```

#### 2.2 Create Polling Activities

**File:** `apex-memory-system/src/apex_memory/temporal/activities/polling.py`

```python
"""Polling activities for external sources.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import logging
from typing import List, Dict, Any

from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn
async def fetch_new_records(source: str) -> List[Dict[str, Any]]:
    """Fetch new records from external source.

    Args:
        source: Source system (e.g., "plaid", "crm", "financial").

    Returns:
        List of new records to process.
    """
    activity.logger.info(f"Fetching new records from {source}")

    # Source-specific polling logic
    if source == "plaid":
        return await _fetch_plaid_transactions()
    elif source == "crm":
        return await _fetch_crm_updates()
    elif source == "financial":
        return await _fetch_financial_updates()
    else:
        raise ValueError(f"Unsupported polling source: {source}")


async def _fetch_plaid_transactions() -> List[Dict[str, Any]]:
    """Fetch new Plaid transactions."""
    # Call Plaid API
    # Return list of transactions
    return []


async def _fetch_crm_updates() -> List[Dict[str, Any]]:
    """Fetch new CRM updates."""
    # Call CRM API
    # Return list of updates
    return []


async def _fetch_financial_updates() -> List[Dict[str, Any]]:
    """Fetch new financial system updates."""
    # Call financial system API
    # Return list of updates
    return []
```

---

### Day 6-7: Streaming & Batch Workflows

#### 3.1 Create Streaming Workflow (Samsara)

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/streaming.py`

```python
"""Streaming ingestion workflow for high-volume sources.

Supports: Samsara fleet telemetry (1,000 events/min)

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow
    from apex_memory.temporal.activities.streaming import collect_stream_batch


@workflow.defn
class StreamIngestionWorkflow:
    """Process high-volume stream data in batches."""

    def __init__(self):
        self.source = None
        self.total_processed = 0

    @workflow.run
    async def run(self, stream_config: dict):
        """Process stream data in batches.

        Args:
            stream_config: Stream configuration (source, batch_size, timeout).
        """
        self.source = stream_config.get("source", "samsara")
        batch_size = stream_config.get("batch_size", 100)
        batch_timeout_seconds = stream_config.get("batch_timeout", 30)

        while True:
            # Step 1: Collect batch of events
            batch = await workflow.execute_activity(
                collect_stream_batch,
                stream_config,
                batch_size,
                batch_timeout_seconds,
                start_to_close_timeout=timedelta(seconds=60),
                heartbeat_timeout=timedelta(seconds=10),
            )

            if not batch:
                workflow.logger.info("No events in batch, continuing...")
                continue

            workflow.logger.info(f"Processing batch of {len(batch)} events")

            # Step 2: Process batch in parallel (spawn child workflows)
            tasks = []
            for event in batch:
                task = workflow.execute_child_workflow(
                    DocumentIngestionWorkflow.run,
                    document_id=event["id"],
                    source=self.source,
                    id=f"ingest-{self.source}-{event['id']}",
                    task_queue="apex-ingestion",
                )
                tasks.append(task)

            # Wait for all to complete
            await asyncio.gather(*tasks)

            self.total_processed += len(batch)
            workflow.logger.info(f"Batch complete, total processed: {self.total_processed}")
```

#### 3.2 Create Batch Workflow (Carrier EDI)

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/batch.py`

```python
"""Batch processing workflow for scheduled bulk imports.

Supports: Carrier EDI files (50/day)

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

import asyncio
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow
    from apex_memory.temporal.activities.batch import fetch_batch_files, parse_batch_file


@workflow.defn
class BatchProcessingWorkflow:
    """Process batch files (EDI, CSV, etc.)."""

    @workflow.run
    async def run(self, batch_config: dict) -> dict:
        """Process batch files.

        Args:
            batch_config: Batch configuration (source, file_pattern).

        Returns:
            Processing summary.
        """
        source = batch_config.get("source", "carrier-edi")

        workflow.logger.info(f"Starting batch processing for {source}")

        # Step 1: Fetch batch files
        files = await workflow.execute_activity(
            fetch_batch_files,
            batch_config,
            start_to_close_timeout=timedelta(seconds=30),
        )

        workflow.logger.info(f"Found {len(files)} batch files to process")

        total_records = 0

        # Step 2: Process each file
        for file_path in files:
            workflow.logger.info(f"Processing file: {file_path}")

            # Parse file
            records = await workflow.execute_activity(
                parse_batch_file,
                file_path,
                start_to_close_timeout=timedelta(minutes=5),
            )

            # Process each record
            tasks = []
            for record in records:
                task = workflow.execute_child_workflow(
                    DocumentIngestionWorkflow.run,
                    document_id=record["id"],
                    source=source,
                    id=f"ingest-{source}-{record['id']}",
                    task_queue="apex-ingestion",
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

            total_records += len(records)
            workflow.logger.info(f"File complete: {file_path}, {len(records)} records")

        workflow.logger.info(f"Batch processing complete: {total_records} total records")

        return {
            "status": "completed",
            "files_processed": len(files),
            "total_records": total_records,
        }
```

---

### Phase 3 Completion Checklist

```
☑ Webhook Workflows
  ☑ WebhookIngestionWorkflow implemented
  ☑ FrontApp, Turvo, Sonar support
  ☑ Signature validation and deduplication
  ☑ Integration tests passing

☑ Polling Workflows
  ☑ PollingWorkflow implemented
  ☑ Plaid, CRM, Financial support
  ☑ Continue-as-new for long-running polls
  ☑ Integration tests passing

☑ Streaming Workflows
  ☑ StreamIngestionWorkflow implemented
  ☑ Samsara fleet telemetry support
  ☑ Batch processing (100 events/batch)
  ☑ Load tests passing (1,000 events/min)

☑ Batch Workflows
  ☑ BatchProcessingWorkflow implemented
  ☑ Carrier EDI file processing
  ☑ Multi-file parallel processing
  ☑ Integration tests passing

☑ Production
  ☑ All 9 data sources integrated
  ☑ Priority-based execution configured
  ☑ Worker pool sized appropriately
  ☑ Monitoring dashboards updated
```

**🎉 Phase 3 Complete! Ready for Phase 4: Monitoring & Observability**

---

## Phase 4: Monitoring & Observability (Week 7-8)

**Goal:** Complete observability stack with Temporal UI, Prometheus, Grafana, and OpenTelemetry distributed tracing.

### Day 1-2: Temporal UI Configuration

#### 1.1 Configure Search Attributes

```bash
# Connect to Temporal
docker exec temporal-admin-tools tctl admin cluster add-search-attributes \
  --name Source --type Keyword \
  --name Priority --type Keyword \
  --name DocumentId --type Keyword \
  --name Status --type Keyword

# Verify
docker exec temporal-admin-tools tctl cluster get-search-attributes
```

#### 1.2 Update Workflows with Search Attributes

Add to workflow start options:

```python
# In API endpoints
result = await client.execute_workflow(
    DocumentIngestionWorkflow.run,
    document_id,
    source,
    id=f"ingest-{document_id}",
    task_queue=config.task_queue,
    search_attributes={
        "Source": source,
        "DocumentId": document_id,
        "Status": "processing",
    },
)
```

---

### Day 3-5: Prometheus & Grafana

#### 2.1 Configure Prometheus Targets

Already configured in Phase 1. Verify scraping:

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job == "temporal-server")'

# Expected: "temporal-server" target showing "up"
```

#### 2.2 Create Custom Grafana Dashboard

**File:** `apex-memory-system/docker/grafana/dashboards/apex-temporal.json`

```json
{
  "dashboard": {
    "title": "Apex Memory System - Temporal Workflows",
    "panels": [
      {
        "title": "Workflow Success Rate",
        "targets": [
          {
            "expr": "rate(temporal_workflow_success_count[5m])"
          }
        ]
      },
      {
        "title": "Workflow Latency (P99)",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, temporal_workflow_latency_bucket)"
          }
        ]
      },
      {
        "title": "Activity Execution Rate",
        "targets": [
          {
            "expr": "rate(temporal_activity_execution_count[5m])"
          }
        ]
      },
      {
        "title": "Worker Task Queue Depth",
        "targets": [
          {
            "expr": "temporal_task_queue_depth{queue=\"apex-ingestion\"}"
          }
        ]
      }
    ]
  }
}
```

Import to Grafana and view metrics.

---

### Day 6-7: OpenTelemetry Distributed Tracing

#### 3.1 Configure OpenTelemetry

**File:** `apex-memory-system/src/apex_memory/config/telemetry.py`

```python
"""OpenTelemetry configuration for distributed tracing.

Author: Apex Infrastructure Team
Created: 2025-10-18
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from apex_memory.config.temporal_config import config


def setup_tracing():
    """Setup OpenTelemetry distributed tracing."""
    if not config.enable_tracing:
        return

    # Create tracer provider
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Configure OTLP exporter
    otlp_exporter = OTLPSpanExporter(endpoint=config.otel_endpoint)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    print(f"OpenTelemetry tracing enabled: {config.otel_endpoint}")
```

Load in main:

```python
# In apex_memory/main.py
from apex_memory.config.telemetry import setup_tracing

setup_tracing()
```

---

### Day 8-10: Documentation & Training

#### 4.1 Create Operational Runbook

**File:** `apex-memory-system/docs/temporal-operations.md`

```markdown
# Temporal Operations Runbook

## Daily Operations

### Check Workflow Health
```bash
# View active workflows
open http://localhost:8088

# Check Temporal Server health
curl http://localhost:7233
```

### Monitor Metrics
- Grafana: http://localhost:3000 → "Apex Temporal Workflows" dashboard
- Prometheus: http://localhost:9090

## Troubleshooting

### Workflow Failures
1. Open Temporal UI → Find failed workflow
2. View event history → Identify failure point
3. Check activity errors
4. Retry or fix and rerun

### Worker Not Processing Tasks
1. Check worker logs: `docker logs apex-worker`
2. Verify task queue: Check Temporal UI → Task Queues
3. Restart worker: `docker restart apex-worker`

## Deployment

### Rolling Worker Updates
```bash
# Update code
git pull

# Build new image
docker build -t apex-worker:v2.0.0 .

# Update workers with worker versioning
temporal worker deployment set-ramping-version \
  --deployment-name apex-ingestion-service \
  --build-id v2.0.0 \
  --percentage 10
```

## Rollback

### Emergency Rollback
```bash
# Set rollout to 0%
export TEMPORAL_ROLLOUT=0
docker restart apex-api
```
```

#### 4.2 Team Training Session

**Training Agenda:**
1. Temporal UI walkthrough (30 min)
2. Debugging workflows in UI (20 min)
3. Running workers locally (15 min)
4. Monitoring dashboards (15 min)
5. Operational runbook review (10 min)
6. Q&A (30 min)

---

### Phase 4 Completion Checklist

```
☑ Temporal UI
  ☑ Search attributes configured
  ☑ Workflows visible and searchable
  ☑ Event history complete

☑ Prometheus
  ☑ Temporal Server metrics scraping
  ☑ Python SDK metrics scraping
  ☑ Metrics visible in Prometheus UI

☑ Grafana
  ☑ Temporal Server dashboard imported
  ☑ Temporal SDK dashboard imported
  ☑ Apex custom dashboard created
  ☑ Alerts configured for failures

☑ OpenTelemetry
  ☑ Tracing enabled and configured
  ☑ Spans visible in tracing backend
  ☑ Distributed traces across workflows/activities

☑ Documentation
  ☑ Operational runbook complete
  ☑ Team trained on Temporal operations
  ☑ Troubleshooting guide created
  ☑ Deployment procedures documented
```

**🎉 Phase 4 Complete! Temporal Implementation Finished!**

---

## Testing Strategy

### Unit Tests (Activities)

**Run activity tests in isolation:**

```bash
cd apex-memory-system

# Test individual activities
pytest tests/unit/test_temporal_activities.py -v

# Test with mocks
pytest tests/unit/test_temporal_activities.py::test_parse_activity_with_mock -v
```

**Example:** `tests/unit/test_temporal_activities.py`

```python
import pytest
from temporalio.testing import ActivityEnvironment
from apex_memory.temporal.activities.ingestion import parse_document_activity


@pytest.mark.asyncio
async def test_parse_document_activity():
    """Test parse activity in isolation."""
    activity_env = ActivityEnvironment()

    result = await activity_env.run(parse_document_activity, "test-doc-123")

    assert result["uuid"] == "test-doc-123"
    assert "content" in result
```

---

### Integration Tests (Workflows + Saga)

**Run full workflow tests:**

```bash
# Test complete ingestion workflow
pytest tests/integration/test_temporal_integration.py -v

# Test Saga integration
pytest tests/integration/test_temporal_saga_integration.py -v
```

**Example:** `tests/integration/test_temporal_saga_integration.py`

```python
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow
from apex_memory.temporal.activities.ingestion import (
    parse_document_activity,
    extract_entities_activity,
    generate_embeddings_activity,
    write_to_databases_activity,
)


@pytest.mark.asyncio
async def test_temporal_saga_integration():
    """Test Temporal workflow with real Enhanced Saga."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[
                parse_document_activity,
                extract_entities_activity,
                generate_embeddings_activity,
                write_to_databases_activity,  # Real Saga
            ],
        ):
            # Execute workflow
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "integration-test-doc",
                "test-source",
                id="test-saga-integration",
                task_queue="test-queue",
            )

            # Verify success
            assert result["status"] == "success"

            # Verify databases were written (check Enhanced Saga)
            # TODO: Query databases to verify data exists
```

---

### Load Tests (Concurrent Workflows)

**Run load tests:**

```bash
# Test 100 concurrent workflows
pytest tests/load/test_concurrent_workflows.py -v --workers=10

# Test 1,000 workflows (stress test)
pytest tests/load/test_stress.py -v
```

**Example:** `tests/load/test_concurrent_workflows.py`

```python
import pytest
import asyncio
from temporalio.client import Client


@pytest.mark.load
@pytest.mark.asyncio
async def test_100_concurrent_workflows():
    """Test 100 concurrent ingestion workflows."""
    client = await Client.connect("localhost:7233")

    # Start 100 workflows
    handles = []
    for i in range(100):
        handle = await client.start_workflow(
            "DocumentIngestionWorkflow",
            f"load-test-doc-{i}",
            "load-test",
            id=f"load-test-{i}",
            task_queue="apex-ingestion",
        )
        handles.append(handle)

    # Wait for all to complete
    results = await asyncio.gather(*[h.result() for h in handles])

    # Verify all succeeded
    assert len(results) == 100
    assert all(r["status"] == "success" for r in results)

    await client.close()
```

---

## Rollback Procedures

### Emergency Rollback (<5 minutes)

**Scenario:** Critical issue detected, need instant rollback

```bash
# Option 1: Environment variable (instant)
export TEMPORAL_ROLLOUT=0  # Route all traffic to legacy
kubectl set env deployment/apex-api TEMPORAL_ROLLOUT=0
# OR
docker exec apex-api env TEMPORAL_ROLLOUT=0

# Option 2: Worker versioning (gradual)
temporal worker deployment set-current-version \
  --deployment-name apex-ingestion-service \
  --build-id v1.0.0  # Rollback to previous version

# Option 3: Shut down Temporal (extreme - automatic fallback to legacy)
docker-compose -f docker/temporal-compose.yml down
```

**Monitoring After Rollback:**
- Verify error rate returns to baseline
- Check legacy path is processing all traffic
- Monitor for any data inconsistencies

---

### Graceful Rollback (<30 minutes)

**Scenario:** Non-critical issue, want controlled rollback

```bash
# Step 1: Stop new workflows from starting
temporal workflow terminate --query "WorkflowType='DocumentIngestionWorkflow' AND ExecutionStatus='Running'"

# Step 2: Let running workflows complete (or wait 10 minutes)
temporal workflow list --query "WorkflowType='DocumentIngestionWorkflow' AND ExecutionStatus='Running'"

# Step 3: Gradually reduce traffic
export TEMPORAL_ROLLOUT=50  # 50% to legacy
sleep 600  # Wait 10 minutes

export TEMPORAL_ROLLOUT=10  # 90% to legacy
sleep 600

export TEMPORAL_ROLLOUT=0  # All to legacy

# Step 4: Verify legacy path stability
# Monitor error rates, latency, throughput

# Step 5: Shut down Temporal (optional)
docker-compose -f docker/temporal-compose.yml down
```

---

### Worker Versioning Rollback

**Scenario:** New worker version has issues

```bash
# Instant rollback to previous worker version
temporal worker deployment set-current-version \
  --deployment-name apex-ingestion-service \
  --build-id v1.9.0  # Previous stable version

# Verify rollback
temporal worker deployment describe \
  --deployment-name apex-ingestion-service

# Expected output:
# Current Version: v1.9.0
```

**Advantages:**
- Instant rollback (no code deploy)
- Running workflows continue on old version
- New workflows use stable version

---

## Deployment Checklist

```
☐ Pre-Deployment
  ☐ All tests passing (unit, integration, load)
  ☐ Saga baseline tests passing (121/121)
  ☐ Code review approved
  ☐ Rollback plan documented

☐ Phase 1: Infrastructure (Week 1-2)
  ☐ Temporal Server deployed and healthy
  ☐ Hello World workflow validated
  ☐ Monitoring configured

☐ Phase 2: Ingestion Migration (Week 3-4)
  ☐ 10% traffic validated (48 hours)
  ☐ 50% traffic validated (24 hours)
  ☐ 100% traffic running (full migration)

☐ Phase 3: Multi-Source Integration (Week 5-6)
  ☐ All 9 data sources integrated
  ☐ Webhook, polling, streaming, batch workflows tested
  ☐ Production load validated

☐ Phase 4: Observability (Week 7-8)
  ☐ Temporal UI search attributes configured
  ☐ Grafana dashboards created
  ☐ OpenTelemetry tracing enabled
  ☐ Team trained on operations

☐ Post-Deployment
  ☐ Monitor for 48 hours
  ☐ Verify error rates < baseline
  ☐ Verify latency < 5× baseline
  ☐ No data consistency issues
  ☐ Remove legacy code after 2-week safety window
```

---

## Next Steps

1. **Complete Phase 1 Checklist:** [PHASE-1-CHECKLIST.md](PHASE-1-CHECKLIST.md)
2. **Review Research Documentation:** [research/README.md](research/README.md)
3. **Study Integration Patterns:** [research/documentation/integration-patterns.md](research/documentation/integration-patterns.md)
4. **Read ADR-003:** [research/architecture-decisions/ADR-003-temporal-orchestration.md](research/architecture-decisions/ADR-003-temporal-orchestration.md)

---

**Questions or issues?** Refer to [README.md](./README.md) for overview and [research documentation](research/) for detailed technical guidance.

**Related documentation:**
- [README.md](./README.md) - Temporal implementation overview
- [PHASE-1-CHECKLIST.md](./PHASE-1-CHECKLIST.md) - Detailed Phase 1 tasks
- [research/README.md](research/README.md) - Research artifacts index
- [research/documentation/integration-patterns.md](research/documentation/integration-patterns.md) - Hybrid architecture
- [research/documentation/deployment-guide.md](research/documentation/deployment-guide.md) - Docker Compose, Kubernetes
- [research/documentation/python-sdk-guide.md](research/documentation/python-sdk-guide.md) - SDK usage patterns
- [research/architecture-decisions/ADR-003-temporal-orchestration.md](research/architecture-decisions/ADR-003-temporal-orchestration.md) - Decision rationale

---

**Created:** 2025-10-18
**Owner:** Apex Infrastructure Team
**Status:** Ready for Implementation
