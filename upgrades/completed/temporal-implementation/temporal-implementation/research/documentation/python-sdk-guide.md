# Temporal Python SDK Guide

**Last Updated:** 2025-10-17
**SDK Version:** temporalio >= 1.11.0
**Source:** https://docs.temporal.io/develop/python

## Installation

```bash
# Install Temporal Python SDK
pip install temporalio

# With development dependencies
pip install temporalio[dev]

# Specific version (recommended for production)
pip install temporalio==1.11.0
```

**Requirements:**
- Python >= 3.10
- Temporal Server (local or cloud)

## Quick Reference

| Decorator/Function | Purpose | Example |
|-------------------|---------|---------|
| `@workflow.defn` | Define workflow | `@workflow.defn class MyWorkflow:` |
| `@workflow.run` | Workflow entry point | `@workflow.run async def run(self):` |
| `@activity.defn` | Define activity | `@activity.defn async def my_activity():` |
| `workflow.execute_activity()` | Execute activity | `await workflow.execute_activity(parse, timeout=...)` |
| `workflow.sleep()` | Durable sleep | `await workflow.sleep(60)` |
| `workflow.logger` | Workflow logging | `workflow.logger.info("message")` |
| `activity.heartbeat()` | Activity progress | `activity.heartbeat("50% complete")` |

## Workflow Development

### Basic Workflow Structure

```python
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class DocumentIngestionWorkflow:
    """Durable document ingestion workflow."""

    def __init__(self):
        # Workflow instance variables (automatically persisted)
        self.document_id = None
        self.status = "pending"

    @workflow.run
    async def run(self, document_id: str) -> dict:
        """Workflow entry point.

        Args:
            document_id: ID of document to ingest

        Returns:
            Ingestion result dictionary
        """
        self.document_id = document_id
        workflow.logger.info(f"Starting ingestion for {document_id}")

        # Execute activities
        parsed = await workflow.execute_activity(
            parse_document,
            document_id,
            start_to_close_timeout=timedelta(seconds=30)
        )

        self.status = "parsed"

        entities = await workflow.execute_activity(
            extract_entities,
            parsed,
            start_to_close_timeout=timedelta(minutes=2)
        )

        self.status = "entities_extracted"

        result = await workflow.execute_activity(
            write_to_databases,
            parsed, entities,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(max_attempts=5)
        )

        self.status = "completed"
        workflow.logger.info(f"Ingestion complete for {document_id}")

        return result
```

### Workflow Best Practices

**✅ DO:**
```python
@workflow.defn
class GoodWorkflow:
    @workflow.run
    async def run(self):
        # 1. Use workflow.logger (not print or standard logging)
        workflow.logger.info("Starting workflow")

        # 2. Use workflow.now() for current time (deterministic)
        current_time = workflow.now()

        # 3. Use workflow.random() for randomness (deterministic)
        jitter = workflow.random().randint(1, 10)

        # 4. Use workflow.sleep() for delays (durable)
        await workflow.sleep(30)

        # 5. Execute activities for non-deterministic operations
        result = await workflow.execute_activity(
            call_external_api,
            start_to_close_timeout=timedelta(seconds=10)
        )

        return result
```

**❌ DON'T:**
```python
@workflow.defn
class BadWorkflow:
    @workflow.run
    async def run(self):
        # ❌ DON'T use print (not persisted)
        print("Starting workflow")

        # ❌ DON'T use datetime.now() (non-deterministic)
        current_time = datetime.now()

        # ❌ DON'T use random.randint() (non-deterministic)
        jitter = random.randint(1, 10)

        # ❌ DON'T use asyncio.sleep() (not durable)
        await asyncio.sleep(30)

        # ❌ DON'T call external APIs directly (non-deterministic)
        response = await httpx.get("https://api.example.com")

        return response
```

### Workflow Signals and Queries

**Signals:** Send data to running workflows

```python
@workflow.defn
class OrderWorkflow:
    def __init__(self):
        self.status = "pending"
        self.cancelled = False

    @workflow.run
    async def run(self, order_id: str):
        # Wait for payment or cancellation
        await workflow.wait_condition(
            lambda: self.status == "paid" or self.cancelled
        )

        if self.cancelled:
            return "Order cancelled"

        # Process order...
        return "Order complete"

    @workflow.signal
    async def payment_received(self, payment_id: str):
        """Signal to mark payment received."""
        self.status = "paid"
        workflow.logger.info(f"Payment received: {payment_id}")

    @workflow.signal
    async def cancel_order(self):
        """Signal to cancel order."""
        self.cancelled = True
        workflow.logger.info("Order cancelled via signal")

# Client code to send signal
await client.get_workflow_handle("order-123").signal(
    OrderWorkflow.payment_received,
    "payment-abc-456"
)
```

**Queries:** Read workflow state without changing it

```python
@workflow.defn
class DataPipelineWorkflow:
    def __init__(self):
        self.processed_count = 0
        self.failed_count = 0
        self.current_stage = "initializing"

    @workflow.run
    async def run(self, batch_size: int):
        self.current_stage = "processing"
        for i in range(batch_size):
            try:
                await workflow.execute_activity(process_item, i)
                self.processed_count += 1
            except Exception:
                self.failed_count += 1

        self.current_stage = "completed"
        return {"processed": self.processed_count, "failed": self.failed_count}

    @workflow.query
    def get_progress(self) -> dict:
        """Query current progress."""
        return {
            "stage": self.current_stage,
            "processed": self.processed_count,
            "failed": self.failed_count
        }

# Client code to query
handle = client.get_workflow_handle("pipeline-123")
progress = await handle.query(DataPipelineWorkflow.get_progress)
print(progress)  # {"stage": "processing", "processed": 45, "failed": 2}
```

## Activity Development

### Basic Activity Structure

```python
from temporalio import activity
from datetime import timedelta

@activity.defn
async def parse_document(document_id: str) -> dict:
    """Parse document from storage.

    This activity is idempotent - can be safely retried.

    Args:
        document_id: ID of document to parse

    Returns:
        Parsed document dictionary

    Raises:
        ValidationError: If document format is invalid
    """
    activity.logger.info(f"Parsing document: {document_id}")

    # Get activity info
    info = activity.info()
    activity.logger.info(f"Attempt: {info.attempt}")

    try:
        # Heartbeat for long operations
        activity.heartbeat("Loading document")

        document = await load_document(document_id)

        activity.heartbeat("Parsing content")

        parsed = await parser.parse(document)

        activity.heartbeat("Parsing complete")

        return parsed

    except Exception as e:
        activity.logger.error(f"Parse failed: {str(e)}")
        raise
```

### Activity Configuration

```python
# In workflow
result = await workflow.execute_activity(
    parse_document,
    document_id,

    # Timeouts
    start_to_close_timeout=timedelta(minutes=5),
    schedule_to_close_timeout=timedelta(minutes=10),
    schedule_to_start_timeout=timedelta(minutes=1),
    heartbeat_timeout=timedelta(seconds=30),

    # Retry policy
    retry_policy=RetryPolicy(
        initial_interval=timedelta(seconds=1),
        backoff_coefficient=2.0,
        maximum_interval=timedelta(seconds=30),
        maximum_attempts=5,
        non_retryable_error_types=["ValidationError"]
    ),

    # Task queue (optional)
    task_queue="high-priority-queue"
)
```

### Activity Patterns

**1. Long-Running Activity with Heartbeat**

```python
@activity.defn
async def process_large_file(file_path: str) -> dict:
    """Process large file with progress reporting."""
    total_lines = await count_lines(file_path)
    processed = 0

    async for line in read_file(file_path):
        # Heartbeat every 100 lines
        if processed % 100 == 0:
            activity.heartbeat(f"Processed {processed}/{total_lines} lines")

        await process_line(line)
        processed += 1

        # Check for cancellation
        if activity.is_cancelled():
            activity.logger.info("Activity cancelled, cleaning up...")
            await cleanup()
            raise ActivityCancelledError()

    return {"processed": processed}
```

**2. Idempotent Activity**

```python
@activity.defn
async def write_to_database(record_id: str, data: dict) -> bool:
    """Idempotent database write.

    Uses record_id as idempotency key.
    """
    # Check if already written
    existing = await db.get(record_id)
    if existing:
        activity.logger.info(f"Record {record_id} already exists, skipping")
        return True

    # Write with idempotency key
    await db.insert(record_id, data)
    activity.logger.info(f"Record {record_id} written successfully")

    return True
```

**3. Activity with Async Completion**

```python
@activity.defn
async def start_external_job(job_config: dict) -> str:
    """Start long-running external job and return token for completion."""
    # Get async completion client
    async_complete = activity.get_async_complete_client()

    # Start external job
    job_id = await external_service.start_job(
        config=job_config,
        callback_token=async_complete.task_token
    )

    # Return immediately - job will complete asynchronously
    raise AsyncCompletion()

# External callback completes the activity
async def job_complete_webhook(job_id: str, result: dict, task_token: bytes):
    """Webhook called when external job completes."""
    client = await Client.connect("localhost:7233")
    await client.complete_async_activity(task_token, result)
```

## Worker Configuration

### Basic Worker

```python
from temporalio.client import Client
from temporalio.worker import Worker

async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="ingestion-queue",
        workflows=[DocumentIngestionWorkflow, OrderWorkflow],
        activities=[
            parse_document,
            extract_entities,
            write_to_databases
        ],
        max_concurrent_workflow_tasks=100,
        max_concurrent_activities=50,
        max_concurrent_local_activities=100,
    )

    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Worker Versioning (Production)

```python
from temporalio.common import WorkerDeploymentVersion, VersioningBehavior
from temporalio.worker import Worker, WorkerDeploymentConfig

worker = Worker(
    client,
    task_queue="ingestion-queue",
    workflows=[DocumentIngestionWorkflow],
    activities=[parse_document, extract_entities],
    deployment_config=WorkerDeploymentConfig(
        version=WorkerDeploymentVersion(
            deployment_name="ingestion-service",
            build_id="v2.3.0"  # From CI/CD
        ),
        use_worker_versioning=True,
        default_versioning_behavior=VersioningBehavior.PINNED
    )
)
```

## Testing

### Unit Testing Activities

```python
import pytest
from temporalio.testing import ActivityEnvironment

@pytest.mark.asyncio
async def test_parse_document():
    """Test parse_document activity in isolation."""
    activity_env = ActivityEnvironment()

    # Run activity
    result = await activity_env.run(parse_document, "doc-123")

    assert result["id"] == "doc-123"
    assert "content" in result
    assert len(result["content"]) > 0
```

### Unit Testing Workflows

```python
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

@pytest.mark.asyncio
async def test_ingestion_workflow():
    """Test complete ingestion workflow."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        # Start worker
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[parse_document, extract_entities, write_to_databases]
        ):
            # Execute workflow
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-123",
                id="test-workflow",
                task_queue="test-queue"
            )

            assert result["status"] == "success"
            assert result["document_id"] == "doc-123"
```

### Mocking Activities in Workflow Tests

```python
@pytest.mark.asyncio
async def test_workflow_with_mocked_activities():
    """Test workflow with mocked activities."""

    # Mock activities
    @activity.defn
    async def mock_parse(doc_id: str):
        return {"id": doc_id, "content": "mocked"}

    @activity.defn
    async def mock_extract(parsed: dict):
        return [{"entity": "test"}]

    @activity.defn
    async def mock_write(parsed: dict, entities: list):
        return {"status": "success"}

    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[DocumentIngestionWorkflow],
            activities=[mock_parse, mock_extract, mock_write]
        ):
            result = await env.client.execute_workflow(
                DocumentIngestionWorkflow.run,
                "doc-123",
                id="test-workflow",
                task_queue="test-queue"
            )

            assert result["status"] == "success"
```

## Error Handling

### Retry Policies

```python
from temporalio.common import RetryPolicy

# Conservative retry (for idempotent operations)
conservative_retry = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(minutes=5),
    maximum_attempts=10
)

# Aggressive retry (for transient failures)
aggressive_retry = RetryPolicy(
    initial_interval=timedelta(milliseconds=100),
    backoff_coefficient=1.5,
    maximum_interval=timedelta(seconds=10),
    maximum_attempts=50
)

# No retry (for operations that should fail fast)
no_retry = RetryPolicy(maximum_attempts=1)

# Selective retry (skip certain errors)
selective_retry = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_attempts=5,
    non_retryable_error_types=[
        "ValidationError",
        "PermissionError",
        "AuthenticationError"
    ]
)
```

### Activity Timeout Configuration

```python
# Short-running activity (API call)
await workflow.execute_activity(
    call_api,
    start_to_close_timeout=timedelta(seconds=10),
    heartbeat_timeout=timedelta(seconds=5)
)

# Long-running activity (file processing)
await workflow.execute_activity(
    process_file,
    start_to_close_timeout=timedelta(minutes=30),
    heartbeat_timeout=timedelta(minutes=1)
)

# Very long activity (batch processing)
await workflow.execute_activity(
    batch_process,
    start_to_close_timeout=timedelta(hours=2),
    schedule_to_close_timeout=timedelta(hours=3),
    heartbeat_timeout=timedelta(minutes=5)
)
```

## Advanced Patterns

### Child Workflows

```python
@workflow.defn
class ProcessBatchWorkflow:
    @workflow.run
    async def run(self, item_ids: list[str]):
        results = []

        # Spawn child workflow for each item
        for item_id in item_ids:
            result = await workflow.execute_child_workflow(
                ProcessItemWorkflow.run,
                item_id,
                id=f"process-{item_id}",
                task_queue="item-queue"
            )
            results.append(result)

        return results
```

### Continue As New (Long-Running Workflows)

```python
@workflow.defn
class PollingWorkflow:
    @workflow.run
    async def run(self, iteration: int = 0):
        # Poll external source
        items = await workflow.execute_activity(
            poll_source,
            start_to_close_timeout=timedelta(seconds=30)
        )

        # Process items
        for item in items:
            await workflow.execute_activity(process_item, item)

        # Sleep for polling interval
        await workflow.sleep(300)  # 5 minutes

        # Continue as new to prevent history from growing too large
        # Temporal recommendation: Continue as new every 10-50KB of history
        if iteration > 100:  # Or check workflow.info().get_history_size()
            workflow.logger.info(f"Continuing as new after {iteration} iterations")
            workflow.continue_as_new(iteration=0)
        else:
            workflow.continue_as_new(iteration=iteration + 1)
```

### Saga Pattern (Compensation)

```python
@workflow.defn
class OrderSagaWorkflow:
    @workflow.run
    async def run(self, order_id: str):
        compensations = []

        try:
            # Step 1: Reserve inventory
            await workflow.execute_activity(reserve_inventory, order_id)
            compensations.append(("release_inventory", order_id))

            # Step 2: Charge payment
            await workflow.execute_activity(charge_payment, order_id)
            compensations.append(("refund_payment", order_id))

            # Step 3: Ship order
            await workflow.execute_activity(ship_order, order_id)
            compensations.append(("cancel_shipment", order_id))

            return {"status": "success"}

        except Exception as e:
            workflow.logger.error(f"Order failed: {str(e)}, running compensations")

            # Run compensations in reverse order
            for compensation_activity, *args in reversed(compensations):
                try:
                    await workflow.execute_activity(
                        compensation_activity,
                        *args,
                        start_to_close_timeout=timedelta(minutes=5)
                    )
                except Exception as comp_error:
                    workflow.logger.error(f"Compensation failed: {comp_error}")

            raise
```

## Best Practices

### 1. Workflow Design

- ✅ Keep workflows deterministic
- ✅ Use workflow.sleep(), workflow.now(), workflow.random()
- ✅ Offload non-deterministic logic to activities
- ✅ Keep workflow logic simple and readable
- ✅ Use signals/queries for external communication

### 2. Activity Design

- ✅ Make activities idempotent
- ✅ Use heartbeats for long-running activities
- ✅ Set appropriate timeouts
- ✅ Handle cancellation gracefully
- ✅ Return serializable data (dict, list, primitive types)

### 3. Error Handling

- ✅ Use retry policies wisely
- ✅ Define non-retryable error types
- ✅ Log errors with context
- ✅ Implement compensation logic for distributed transactions

### 4. Performance

- ✅ Batch activity executions when possible
- ✅ Use local activities for lightweight operations
- ✅ Continue-as-new for long-running workflows
- ✅ Limit workflow history size (<50KB recommended)

### 5. Testing

- ✅ Unit test activities in isolation
- ✅ Use time-skipping for workflow tests
- ✅ Mock external dependencies
- ✅ Test error scenarios and retries

## Common Pitfalls

❌ **Using non-deterministic operations in workflows**
```python
# ❌ DON'T
current_time = datetime.now()  # Non-deterministic

# ✅ DO
current_time = workflow.now()  # Deterministic
```

❌ **Forgetting to set activity timeouts**
```python
# ❌ DON'T
await workflow.execute_activity(my_activity)  # No timeout!

# ✅ DO
await workflow.execute_activity(
    my_activity,
    start_to_close_timeout=timedelta(seconds=30)
)
```

❌ **Not making activities idempotent**
```python
# ❌ DON'T
@activity.defn
async def increment_counter():
    counter += 1  # Will increment multiple times on retry!

# ✅ DO
@activity.defn
async def set_counter(value: int):
    counter = value  # Idempotent
```

❌ **Catching all exceptions in workflows**
```python
# ❌ DON'T
try:
    await workflow.execute_activity(...)
except Exception:
    return "failed"  # Hides all errors!

# ✅ DO
try:
    await workflow.execute_activity(...)
except ApplicationError as e:
    workflow.logger.error(f"Application error: {e}")
    raise  # Re-raise to trigger retry or failure
```

## Resources

**Official Documentation:**
- Python SDK Guide: https://docs.temporal.io/develop/python
- API Reference: https://python.temporal.io
- Samples Repository: https://github.com/temporalio/samples-python

**Related Documentation:**
- [Temporal.io Overview](temporal-io-overview.md)
- [Deployment Guide](deployment-guide.md)
- [Testing Examples](../../examples/temporal/testing-example.py)
- [Integration Patterns](integration-patterns.md)
