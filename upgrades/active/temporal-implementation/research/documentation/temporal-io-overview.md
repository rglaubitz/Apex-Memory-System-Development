# Temporal.io Overview

**Last Updated:** 2025-10-17
**Source Tier:** Tier 1 (Official Documentation)
**Reference:** https://docs.temporal.io

## What is Temporal.io?

Temporal.io is a **durable execution platform** that guarantees workflow completion despite failures, process crashes, or infrastructure outages. It provides automatic state persistence, retry logic, and observability for distributed applications.

**Key Distinction:** Temporal.io is NOT a task queue or job scheduler. It's a workflow orchestration platform that models complex business logic as reliable, long-running processes that can survive any failure.

## Core Concepts

### 1. Workflows

**Definition:** Durable functions that orchestrate activities and maintain state across failures.

**Key Characteristics:**
- **Deterministic:** Must produce the same result when replayed
- **Durable:** State automatically persisted to database
- **Long-Running:** Can execute for days, months, or years
- **Fault-Tolerant:** Survive process crashes, restarts, and infrastructure failures

**Example Use Cases:**
- Multi-step data ingestion pipelines
- Long-running batch processing
- Order fulfillment workflows (days to weeks)
- User onboarding flows with emails, waits, and conditionals

**Python Example:**
```python
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class IngestionWorkflow:
    @workflow.run
    async def run(self, document_id: str) -> str:
        # Step 1: Parse document
        parsed = await workflow.execute_activity(
            parse_document,
            document_id,
            start_to_close_timeout=timedelta(seconds=30)
        )

        # Step 2: Extract entities
        entities = await workflow.execute_activity(
            extract_entities,
            parsed,
            start_to_close_timeout=timedelta(seconds=60)
        )

        # Step 3: Write to databases
        result = await workflow.execute_activity(
            write_to_databases,
            parsed, entities,
            start_to_close_timeout=timedelta(seconds=120)
        )

        return result
```

### 2. Activities

**Definition:** Individual units of work executed by workflows. Activities represent a single, well-defined action.

**Key Characteristics:**
- **Idempotent:** Can be safely retried without side effects
- **Timeout-Controlled:** Configurable timeouts for execution
- **Heartbeat-Enabled:** Can report progress for long-running tasks
- **Retry-Safe:** Automatic retries with exponential backoff

**Example Use Cases:**
- API calls to external services
- Database operations
- File I/O operations
- Email sending
- Image processing

**Python Example:**
```python
from temporalio import activity

@activity.defn
async def parse_document(document_id: str) -> dict:
    """Parse document from storage.

    This activity is idempotent and can be safely retried.
    """
    activity.logger.info(f"Parsing document: {document_id}")

    # Heartbeat for long operations
    activity.heartbeat("Starting parse")

    # Actual parsing logic
    document = await load_document(document_id)
    parsed = await parser.parse(document)

    activity.heartbeat("Parsing complete")
    return parsed
```

### 3. Workers

**Definition:** Processes that poll task queues and execute workflows and activities.

**Key Characteristics:**
- **Stateless:** Can be scaled horizontally
- **Specialized:** Can be configured to handle specific workflows/activities
- **Version-Aware:** Support versioned deployments for safe upgrades
- **Resilient:** Automatic reconnection on network failures

**Architecture:**
```
┌─────────────────────────────────────┐
│       Temporal Server               │
│  - Workflow History Storage         │
│  - Task Queue Management            │
│  - Scheduling & Timing              │
└───────────┬─────────────────────────┘
            │
            ├─> Task Queue: "ingestion-queue"
            ├─> Task Queue: "query-queue"
            └─> Task Queue: "webhook-queue"
                    │
                    ▼
            ┌───────────────────┐
            │   Worker Process  │
            │  - Polls queue    │
            │  - Executes code  │
            │  - Reports back   │
            └───────────────────┘
```

**Python Example:**
```python
from temporalio.client import Client
from temporalio.worker import Worker

async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="ingestion-queue",
        workflows=[IngestionWorkflow],
        activities=[parse_document, extract_entities, write_to_databases],
    )

    await worker.run()
```

### 4. Task Queues

**Definition:** Logical queues that route work from workflows to workers.

**Key Characteristics:**
- **Logical Routing:** Not a message queue, just a routing mechanism
- **Worker Affinity:** Specific workers poll specific queues
- **Load Balancing:** Temporal automatically distributes work
- **Priority Support:** Can configure different priorities

**Common Patterns:**
```python
# Different task queues for different workload types
INGESTION_QUEUE = "ingestion-queue"      # High-priority document ingestion
QUERY_QUEUE = "query-queue"              # User queries
WEBHOOK_QUEUE = "webhook-queue"          # External webhook processing
BATCH_QUEUE = "batch-queue"              # Low-priority batch processing
```

## Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Client Applications                     │
│  (Start workflows, send signals, query state)            │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                  Temporal Server                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Frontend Service (gRPC API)                       │  │
│  └──────────────┬─────────────────────────────────────┘  │
│                 │                                          │
│  ┌──────────────▼──────────────────────────────────────┐ │
│  │  History Service (Workflow execution state)         │ │
│  └──────────────┬──────────────────────────────────────┘ │
│                 │                                          │
│  ┌──────────────▼──────────────────────────────────────┐ │
│  │  Matching Service (Task queue routing)             │ │
│  └──────────────┬──────────────────────────────────────┘ │
│                 │                                          │
│  ┌──────────────▼──────────────────────────────────────┐ │
│  │  Persistence Layer (PostgreSQL, Cassandra, MySQL)  │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                      Workers                              │
│  - Poll task queues                                       │
│  - Execute workflow/activity code                         │
│  - Report results back to server                          │
└──────────────────────────────────────────────────────────┘
```

### State Persistence

**How Temporal Ensures Durability:**

1. **Event Sourcing:** Every workflow decision is recorded as an event
2. **Event History:** Immutable log of all workflow events
3. **Replay Mechanism:** Workflows reconstruct state by replaying events
4. **Automatic Checkpointing:** State persisted after each decision

**Example Event History:**
```
Event 1: WorkflowExecutionStarted
Event 2: ActivityTaskScheduled (parse_document)
Event 3: ActivityTaskCompleted (parse_document)
Event 4: ActivityTaskScheduled (extract_entities)
Event 5: ActivityTaskCompleted (extract_entities)
Event 6: ActivityTaskScheduled (write_to_databases)
Event 7: ActivityTaskCompleted (write_to_databases)
Event 8: WorkflowExecutionCompleted
```

## Benefits

### 1. Automatic Reliability

**Traditional Approach:**
```python
# Manual retry, state management, error handling
def process_document(doc_id):
    state = load_state(doc_id)

    if state.status != "parsed":
        for attempt in range(3):
            try:
                parsed = parse_document(doc_id)
                save_state(doc_id, "parsed", parsed)
                break
            except Exception as e:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)

    # Repeat for every step... 100s of lines of boilerplate
```

**Temporal Approach:**
```python
# Temporal handles ALL retry, state, error handling
@workflow.defn
class ProcessDocument:
    @workflow.run
    async def run(self, doc_id: str):
        parsed = await workflow.execute_activity(
            parse_document, doc_id,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(max_attempts=3)
        )
        return parsed  # That's it!
```

**Code Reduction:** 70% less code (3,000 → 1,000 lines estimated)

### 2. Complete Observability

**Built-in Visibility:**
- Temporal UI shows ALL workflow executions in real-time
- View event history for every workflow
- Query workflow state without modifying code
- Replay workflows for debugging

**Traditional Monitoring:**
```
Logs: "Step 1 complete" ... "Step 2 failed" (somewhere in thousands of log lines)
Metrics: Counter for success/failure
Tracing: Spans for individual operations
```

**Temporal Monitoring:**
```
- Workflow ID: doc-abc-123
- Status: Running
- Current Step: extract_entities (Activity 2 of 3)
- Retry Attempt: 1 of 3
- Started: 2025-10-17 10:30:00
- Duration: 45 seconds
- Full Event History: [Click to view 10 events]
```

### 3. Simplified State Management

**No External State Store Required:**
- Workflow state automatically persisted
- Survives process crashes
- No Redis, PostgreSQL, or external state store needed
- State is NEVER lost

**Example:**
```python
@workflow.defn
class OrderWorkflow:
    def __init__(self):
        self.order_state = "pending"
        self.payment_id = None
        self.shipment_id = None

    @workflow.run
    async def run(self, order_id: str):
        # State automatically persisted!
        self.payment_id = await workflow.execute_activity(process_payment, order_id)
        self.order_state = "paid"

        # Even if worker crashes here, state is preserved

        self.shipment_id = await workflow.execute_activity(ship_order, order_id)
        self.order_state = "shipped"

        return self.shipment_id
```

### 4. Production-Ready Error Handling

**Built-in Capabilities:**
- Exponential backoff retries (configurable)
- Circuit breaker patterns (via activity failures)
- Timeout handling (start-to-close, schedule-to-start, heartbeat)
- Dead letter queue (failed workflows queryable in Temporal UI)

**Retry Policy Example:**
```python
retry_policy = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=10,
    non_retryable_error_types=["ValidationError"]
)

await workflow.execute_activity(
    risky_operation,
    retry_policy=retry_policy
)
```

### 5. Versioning and Safe Deployment

**Worker Versioning (Since v1.11):**
- Deploy new workflow code without breaking running workflows
- Gradual rollout (10% → 50% → 100%)
- Instant rollback on issues
- Workflow pinning (workflow runs entirely on one version)

**Blue-Green and Rainbow Deployments:**
```python
worker = Worker(
    client,
    task_queue="ingestion-queue",
    workflows=[IngestionWorkflow],
    activities=[parse_document, extract_entities],
    deployment_config=WorkerDeploymentConfig(
        version=WorkerDeploymentVersion(
            deployment_name="ingestion-service",
            build_id="v2.3.0"
        ),
        use_worker_versioning=True,
        default_versioning_behavior=VersioningBehavior.PINNED
    )
)
```

## Use Cases

### Perfect For:

1. **Multi-Step Data Pipelines**
   - Ingest → Parse → Extract → Transform → Load
   - Webhooks → Validate → Process → Notify
   - Examples: Our 9+ data source integrations (FrontApp, Turvo, Samsara, etc.)

2. **Long-Running Business Processes**
   - User onboarding (send email → wait 3 days → send reminder)
   - Order fulfillment (place order → wait for payment → ship → wait for delivery)
   - Subscription renewals (charge → retry on failure → cancel after 3 failures)

3. **Human-in-the-Loop Workflows**
   - Approval workflows (submit → wait for approval → execute)
   - Review workflows (auto-review → manual review → publish)

4. **Distributed Transactions**
   - Saga pattern (book flight → book hotel → cancel both if either fails)
   - Cross-service coordination

### Not Ideal For:

1. **Sub-Second Latency Requirements**
   - Temporal adds ~50-100ms overhead per workflow
   - Better: Direct API calls for real-time operations

2. **Stateless Request/Response**
   - Simple REST endpoints that don't need durability
   - Better: Standard API frameworks (FastAPI, Flask)

3. **Pure Data Processing (No Orchestration)**
   - Batch ETL jobs with no coordination logic
   - Better: Apache Spark, Airflow

4. **Fire-and-Forget Tasks**
   - Background jobs that don't need tracking
   - Better: Celery, RabbitMQ

## Temporal vs Alternatives

| Feature | Temporal | Airflow | Celery | AWS Step Functions |
|---------|----------|---------|--------|-------------------|
| **Durable State** | ✅ Built-in | ❌ External DB | ❌ External broker | ✅ Built-in |
| **Automatic Retries** | ✅ Built-in | ⚠️ Manual | ✅ Built-in | ✅ Built-in |
| **Versioning** | ✅ Worker versioning | ❌ None | ❌ None | ❌ None |
| **Local Development** | ✅ Temporal CLI | ⚠️ Complex | ✅ Easy | ❌ Cloud only |
| **Language Support** | ✅ 7+ SDKs | ⚠️ Python only | ⚠️ Python only | ⚠️ JSON/YAML |
| **Debugging** | ✅ Temporal UI | ⚠️ Limited | ❌ Logs only | ⚠️ CloudWatch |
| **Code as Workflows** | ✅ Native Python | ⚠️ DAG definitions | ✅ Native Python | ❌ JSON/ASL |
| **Cost (Self-Hosted)** | Free | Free | Free | N/A |
| **Cost (Managed)** | $$$ Temporal Cloud | $$$ MWAA | N/A | $$ Step Functions |

## Temporal Guarantees

**What Temporal DOES Guarantee:**

1. **At-Least-Once Execution:** Activities execute at least once (may retry)
2. **Exactly-Once Workflow Decision:** Workflow logic runs exactly once per event
3. **State Durability:** Workflow state NEVER lost (survives all failures)
4. **Event Ordering:** Events in workflow history are strictly ordered

**What Temporal DOES NOT Guarantee:**

1. **Exactly-Once Activity Execution:** Activities may execute multiple times (must be idempotent)
2. **Real-Time Guarantees:** No SLA on latency (typical: 50-200ms)
3. **Data Consistency:** Application must handle distributed transactions

## Quick Start

### 1. Install Temporal CLI

```bash
# macOS
brew install temporal

# Linux/WSL
curl -sSf https://temporal.download/cli.sh | sh
```

### 2. Start Temporal Server

```bash
temporal server start-dev
```

This starts:
- Temporal Server on `localhost:7233`
- Temporal UI on `http://localhost:8233`

### 3. Install Python SDK

```bash
pip install temporalio
```

### 4. Write Your First Workflow

```python
# hello_workflow.py
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker
import asyncio

@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@workflow.defn
class HelloWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=10)
        )

async def main():
    client = await Client.connect("localhost:7233")

    # Start worker
    async with Worker(
        client,
        task_queue="hello-queue",
        workflows=[HelloWorkflow],
        activities=[say_hello]
    ):
        # Execute workflow
        result = await client.execute_workflow(
            HelloWorkflow.run,
            "World",
            id="hello-workflow-1",
            task_queue="hello-queue"
        )
        print(result)  # "Hello, World!"

if __name__ == "__main__":
    asyncio.run(main())
```

### 5. Run and View in UI

```bash
python hello_workflow.py

# Open browser: http://localhost:8233
# View workflow execution in real-time
```

## Resources

**Official Documentation:**
- Main Docs: https://docs.temporal.io
- Python SDK: https://docs.temporal.io/develop/python
- Python API Reference: https://python.temporal.io

**Learning Resources:**
- Temporal 101 (Free Course): https://learn.temporal.io/courses/temporal_101/python
- Python Samples: https://github.com/temporalio/samples-python
- Community Forum: https://community.temporal.io

**Production Resources:**
- Deployment Guide: https://docs.temporal.io/self-hosted-guide
- Helm Charts: https://github.com/temporalio/helm-charts
- Docker Compose: https://github.com/temporalio/docker-compose

## Related Documentation

**In This Repository:**
- [Python SDK Guide](python-sdk-guide.md) - Detailed SDK usage patterns
- [Deployment Guide](deployment-guide.md) - Docker Compose setup
- [Integration Patterns](integration-patterns.md) - Hybrid architecture with Enhanced Saga
- [Migration Strategy](migration-strategy.md) - Gradual rollout approach
- [Monitoring & Observability](monitoring-observability.md) - Prometheus, Grafana, OpenTelemetry

**Architecture Decisions:**
- [ADR-003: Temporal Orchestration](../../architecture-decisions/ADR-003-temporal-orchestration.md) - Why we chose Temporal

## Next Steps

1. **Read:** [Python SDK Guide](python-sdk-guide.md) for detailed SDK patterns
2. **Setup:** [Deployment Guide](deployment-guide.md) for local development
3. **Understand:** [Integration Patterns](integration-patterns.md) for hybrid architecture
4. **Plan:** Review `upgrades/active/temporal-implementation/` for our implementation roadmap
