# Temporal Integration Patterns for Apex Memory System

**Last Updated:** 2025-10-17
**Context:** Integrating Temporal.io with existing Enhanced Saga pattern
**Status:** Research Complete → Implementation Planning

## Overview

This document describes integration patterns for adopting Temporal.io workflow orchestration while preserving our battle-tested Enhanced Saga pattern for database writes.

**Key Principle:** Temporal for orchestration, Enhanced Saga for data consistency.

## Hybrid Architecture

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    External Data Sources (9+)                    │
│  FrontApp │ Turvo │ Samsara │ Banks │ Sonar │ EDI │ CRM │ LLMs  │
└─────────────┬────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────────┐
│               Temporal.io Orchestration Layer                     │
│  • Workflow State Management                                      │
│  • Retry Logic & Exponential Backoff                             │
│  • Activity Scheduling                                            │
│  • Compensation Coordination                                      │
│  • Observability (Temporal UI)                                   │
└─────────────┬────────────────────────────────────────────────────┘
              │
              ├─> WebhookWorkflow (FrontApp, Turvo, Sonar)
              ├─> PollingWorkflow (Banks, CRM, Financial)
              ├─> StreamWorkflow (Samsara)
              └─> BatchWorkflow (Carrier EDI)
              │
              ▼
┌──────────────────────────────────────────────────────────────────┐
│                 Ingestion Pipeline Activities                      │
│  • parse_document                                                 │
│  • extract_entities                                               │
│  • generate_embeddings                                            │
│  • write_to_databases ← DELEGATES TO ENHANCED SAGA               │
└─────────────┬────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────────┐
│          Enhanced Saga (KEPT AS-IS - 121/121 tests passing)      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ DatabaseWriteOrchestrator                                   │  │
│  │  Phase 1:                                                   │  │
│  │    • Distributed Locking (Redis Redlock)                   │  │
│  │    • Idempotency Cache (SHA256 keys)                       │  │
│  │    • Parallel DB Writes (asyncio.gather)                   │  │
│  │  Phase 2:                                                   │  │
│  │    • Circuit Breakers (5 failures → OPEN)                  │  │
│  │    • Exponential Backoff Retry (1s → 2s → 4s)             │  │
│  │    • Dead Letter Queue (PostgreSQL)                        │  │
│  │  Rollback Logic:                                            │  │
│  │    • Atomic Compensation                                    │  │
│  │    • DLQ for Failed Rollbacks                              │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────┬────────────────────────────────────────────────────┘
              │
              ├─> Neo4j (Entities, Relationships)
              ├─> PostgreSQL + pgvector (Metadata, Chunks, Embeddings)
              ├─> Qdrant (Vector Search)
              └─> Redis (Cache)
```

### Responsibility Separation

| Layer | Responsibilities | Why |
|-------|-----------------|-----|
| **Temporal Workflows** | • Multi-source orchestration<br>• Long-running processes<br>• Workflow-level retries<br>• Compensation coordination<br>• State management | Temporal excels at durable execution across hours/days |
| **Temporal Activities** | • Single operations<br>• Parsing, extraction, embedding<br>• API calls to external services<br>• Delegating to Enhanced Saga | Activities are atomic, retriable units |
| **Enhanced Saga** | • 4-database atomic writes<br>• Distributed locking<br>• Idempotency enforcement<br>• Circuit breaker protection<br>• Rollback with DLQ | Saga is battle-tested (121/121 tests), optimized for multi-DB consistency |

## Integration Pattern: Temporal Activity → Enhanced Saga

### Pattern Implementation

```python
from temporalio import activity, workflow
from datetime import timedelta
from apex_memory.services.database_writer import DatabaseWriteOrchestrator
from apex_memory.models.document import ParsedDocument

# ============================================================================
# Temporal Workflow (Orchestration)
# ============================================================================

@workflow.defn
class DocumentIngestionWorkflow:
    """Orchestrates multi-step ingestion using Temporal."""

    @workflow.run
    async def run(self, document_id: str, source: str) -> dict:
        workflow.logger.info(f"Ingesting document {document_id} from {source}")

        # Step 1: Parse document (Temporal Activity)
        parsed = await workflow.execute_activity(
            parse_document_activity,
            document_id,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_attempts=3
            )
        )

        # Step 2: Extract entities (Temporal Activity)
        entities = await workflow.execute_activity(
            extract_entities_activity,
            parsed,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_attempts=3
            )
        )

        # Step 3: Generate embeddings (Temporal Activity)
        embeddings = await workflow.execute_activity(
            generate_embeddings_activity,
            parsed,
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_attempts=5
            )
        )

        # Step 4: Write to databases (DELEGATE TO ENHANCED SAGA)
        result = await workflow.execute_activity(
            write_to_databases_activity,
            parsed, entities, embeddings,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=5),
                maximum_attempts=3,
                non_retryable_error_types=["ValidationError"]
            )
        )

        workflow.logger.info(f"Ingestion complete: {result}")
        return result


# ============================================================================
# Temporal Activities (Individual Operations)
# ============================================================================

@activity.defn
async def parse_document_activity(document_id: str) -> ParsedDocument:
    """Parse document (idempotent, no database writes)."""
    activity.logger.info(f"Parsing document: {document_id}")

    # Load from storage
    document = await storage.load(document_id)

    # Parse content
    parser = DocumentParser()
    parsed = await parser.parse(document)

    activity.logger.info(f"Parsed {len(parsed.chunks)} chunks")
    return parsed


@activity.defn
async def extract_entities_activity(parsed: ParsedDocument) -> list:
    """Extract entities (idempotent, no database writes)."""
    activity.logger.info(f"Extracting entities from {parsed.uuid}")

    extractor = EntityExtractor()
    entities = await extractor.extract(parsed.content)

    activity.logger.info(f"Extracted {len(entities)} entities")
    return entities


@activity.defn
async def generate_embeddings_activity(parsed: ParsedDocument) -> list[float]:
    """Generate embeddings (idempotent, calls OpenAI API)."""
    activity.logger.info(f"Generating embeddings for {parsed.uuid}")

    # This activity handles OpenAI API calls with retries
    embeddings = await openai_client.embed(parsed.content)

    activity.logger.info(f"Generated {len(embeddings)} dimension embedding")
    return embeddings


@activity.defn
async def write_to_databases_activity(
    parsed: ParsedDocument,
    entities: list,
    embeddings: list[float]
) -> dict:
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
    """
    activity.logger.info(f"Writing {parsed.uuid} to databases via Enhanced Saga")

    # Initialize database writers (singleton pattern in production)
    orchestrator = DatabaseWriteOrchestrator(
        neo4j_writer=neo4j_writer,
        postgres_writer=postgres_writer,
        qdrant_writer=qdrant_writer,
        redis_writer=redis_writer,
        enable_locking=True,          # Phase 1
        enable_idempotency=True,      # Phase 1
        enable_circuit_breakers=True, # Phase 2
        enable_retries=True,          # Phase 2
    )

    # Delegate to Enhanced Saga
    result = await orchestrator.write_document_parallel(
        document=parsed,
        embedding=embeddings
    )

    # Enhanced Saga returns WriteResult with detailed status
    if result.status == WriteStatus.SUCCESS:
        activity.logger.info(f"Write successful for {parsed.uuid}")
        return {
            "status": "success",
            "document_id": parsed.uuid,
            "databases_written": ["neo4j", "postgres", "qdrant", "redis"]
        }

    elif result.status == WriteStatus.ROLLED_BACK:
        activity.logger.error(f"Write failed for {parsed.uuid}, rolled back")
        raise ApplicationError(
            f"Database write failed: {result.errors}",
            type="DatabaseWriteError",
            non_retryable=False  # Allow Temporal to retry
        )

    elif result.status == WriteStatus.FAILED:
        activity.logger.critical(f"Write failed for {parsed.uuid}, no rollback")
        raise ApplicationError(
            f"Complete write failure: {result.errors}",
            type="DatabaseWriteError",
            non_retryable=True  # Don't retry - likely validation error
        )
```

### Why This Pattern Works

**1. Clear Separation of Concerns**
- Temporal: "What should happen and in what order?"
- Enhanced Saga: "How do I write to 4 databases atomically?"

**2. Leverages Strengths**
- Temporal: Durable execution, workflow visibility, long-running processes
- Enhanced Saga: Multi-database consistency, circuit breakers, idempotency

**3. Battle-Tested Components**
- Enhanced Saga: 121/121 tests passing, 88-96% coverage
- Temporal: Production-proven at Uber, Netflix, Stripe

**4. Incremental Adoption**
- Keep Enhanced Saga for database writes (no changes needed)
- Add Temporal for orchestration (new layer on top)
- Gradual migration of workflows to Temporal

## Integration Pattern: Multi-Source Workflows

### Webhook-Based Integration (FrontApp, Turvo, Sonar)

```python
@workflow.defn
class WebhookIngestionWorkflow:
    """Process webhook events from external sources."""

    @workflow.run
    async def run(self, webhook_event: dict) -> dict:
        # 1. Validate webhook signature
        is_valid = await workflow.execute_activity(
            validate_webhook_signature,
            webhook_event,
            start_to_close_timeout=timedelta(seconds=5)
        )

        if not is_valid:
            raise ApplicationError("Invalid webhook signature", non_retryable=True)

        # 2. Deduplicate using idempotency key
        event_id = webhook_event["event_id"]
        if await self.is_duplicate(event_id):
            workflow.logger.info(f"Duplicate event {event_id}, skipping")
            return {"status": "duplicate"}

        # 3. Parse webhook payload
        parsed = await workflow.execute_activity(
            parse_webhook_payload,
            webhook_event,
            start_to_close_timeout=timedelta(seconds=10)
        )

        # 4. Route to ingestion pipeline
        result = await workflow.execute_child_workflow(
            DocumentIngestionWorkflow.run,
            document_id=parsed["document_id"],
            source=webhook_event["source"],
            id=f"ingest-{event_id}",
            task_queue="ingestion-queue"
        )

        return {"status": "processed", "result": result}

    @workflow.query
    def is_duplicate(self, event_id: str) -> bool:
        """Check if event already processed (via workflow search)."""
        # Query Temporal for existing workflow with this event_id
        # Implementation detail: Use workflow.search_attributes
        return False  # Simplified
```

### Polling-Based Integration (Banks, CRM, Financial)

```python
@workflow.defn
class PollingWorkflow:
    """Poll external source periodically."""

    @workflow.run
    async def run(self, source: str, interval_seconds: int = 900):
        iteration = 0

        while True:
            workflow.logger.info(f"Polling {source}, iteration {iteration}")

            # 1. Fetch new records
            records = await workflow.execute_activity(
                fetch_new_records,
                source,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=5)
            )

            workflow.logger.info(f"Fetched {len(records)} records from {source}")

            # 2. Spawn child workflow for each record
            for record in records:
                await workflow.execute_child_workflow(
                    DocumentIngestionWorkflow.run,
                    document_id=record["id"],
                    source=source,
                    id=f"ingest-{source}-{record['id']}",
                    task_queue="ingestion-queue"
                )

            # 3. Sleep for polling interval
            await workflow.sleep(interval_seconds)

            # 4. Continue-as-new to prevent history from growing
            iteration += 1
            if iteration >= 100:
                workflow.continue_as_new(source, interval_seconds)
```

### Stream-Based Integration (Samsara Fleet Telemetry)

```python
@workflow.defn
class StreamIngestionWorkflow:
    """Process high-volume stream data."""

    @workflow.run
    async def run(self, stream_config: dict):
        batch_size = 100
        batch_timeout_seconds = 30

        while True:
            # 1. Collect batch of events
            batch = await workflow.execute_activity(
                collect_stream_batch,
                stream_config,
                batch_size,
                batch_timeout_seconds,
                start_to_close_timeout=timedelta(seconds=60),
                heartbeat_timeout=timedelta(seconds=10)
            )

            if not batch:
                workflow.logger.info("No events in batch, continuing...")
                continue

            workflow.logger.info(f"Processing batch of {len(batch)} events")

            # 2. Process batch in parallel
            tasks = []
            for event in batch:
                task = workflow.execute_child_workflow(
                    DocumentIngestionWorkflow.run,
                    document_id=event["id"],
                    source="samsara",
                    id=f"ingest-samsara-{event['id']}",
                    task_queue="ingestion-queue"
                )
                tasks.append(task)

            # Wait for all to complete
            await asyncio.gather(*tasks)

            workflow.logger.info(f"Batch complete, processed {len(batch)} events")
```

## Error Handling Strategy

### Multi-Level Error Handling

```
Level 1: Enhanced Saga Internal Retries
└─> Circuit breakers, exponential backoff, DLQ

Level 2: Temporal Activity Retries
└─> RetryPolicy on activities (write_to_databases_activity)

Level 3: Temporal Workflow Compensation
└─> Saga pattern at workflow level for multi-step compensation
```

### Example: Complete Error Flow

```python
@workflow.defn
class ResilientIngestionWorkflow:
    """Workflow with complete error handling."""

    @workflow.run
    async def run(self, document_id: str):
        compensations = []

        try:
            # Step 1: Validate document
            await workflow.execute_activity(
                validate_document,
                document_id,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    non_retryable_error_types=["ValidationError"]
                )
            )

            # Step 2: Parse (with compensation)
            parsed = await workflow.execute_activity(
                parse_document_activity,
                document_id,
                start_to_close_timeout=timedelta(seconds=30)
            )
            compensations.append(("cleanup_parsed_data", parsed.uuid))

            # Step 3: Extract entities (with compensation)
            entities = await workflow.execute_activity(
                extract_entities_activity,
                parsed
            )
            compensations.append(("cleanup_entities", entities))

            # Step 4: Write to databases (Enhanced Saga handles its own retries/rollback)
            result = await workflow.execute_activity(
                write_to_databases_activity,
                parsed, entities,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=5),
                    backoff_coefficient=2.0,
                    maximum_attempts=3
                )
            )

            return {"status": "success", "result": result}

        except Exception as e:
            workflow.logger.error(f"Workflow failed: {str(e)}, running compensations")

            # Run compensations in reverse order
            for compensation_activity, *args in reversed(compensations):
                try:
                    await workflow.execute_activity(
                        compensation_activity,
                        *args,
                        start_to_close_timeout=timedelta(minutes=1)
                    )
                except Exception as comp_error:
                    workflow.logger.error(f"Compensation failed: {comp_error}")
                    # Compensation failures go to DLQ (handled by Enhanced Saga)

            # Re-raise to mark workflow as failed
            raise
```

## Performance Considerations

### Latency Analysis

```
Traditional Approach (Direct Saga):
├─> Lock acquisition: ~10ms
├─> Idempotency check: ~5ms
├─> 4-DB parallel writes: ~150ms
├─> Rollback (if needed): ~100ms
└─> Total: ~165-265ms

Temporal + Saga Approach:
├─> Temporal workflow start: ~50ms
├─> Activity scheduling: ~20ms
├─> Activity execution (calls Saga):
│   ├─> Lock acquisition: ~10ms
│   ├─> Idempotency check: ~5ms
│   ├─> 4-DB parallel writes: ~150ms
│   └─> Rollback (if needed): ~100ms
├─> Activity completion: ~10ms
└─> Total: ~245-345ms

Overhead: ~80ms (30-50% increase)
```

**Mitigation Strategies:**

1. **Use Local Activities for Lightweight Operations:**
```python
# Regular activity: ~50ms overhead
await workflow.execute_activity(parse_small_doc, ...)

# Local activity: ~5ms overhead
await workflow.execute_local_activity(parse_small_doc, ...)
```

2. **Batch Operations:**
```python
# Bad: 100 activities = 100 × 50ms = 5,000ms overhead
for item in items:
    await workflow.execute_activity(process_item, item)

# Good: 1 activity = 1 × 50ms = 50ms overhead
await workflow.execute_activity(process_batch, items)
```

3. **Optimize Critical Path:**
```python
# Use Temporal for orchestration (non-latency-critical)
@workflow.defn
class BatchIngestionWorkflow:  # Run nightly, latency doesn't matter
    ...

# Keep direct Saga calls for real-time operations
async def realtime_ingest(doc_id: str):
    # <100ms requirement → Skip Temporal, call Saga directly
    orchestrator = DatabaseWriteOrchestrator(...)
    return await orchestrator.write_document_parallel(...)
```

## Migration Strategy

### Phase 1: Parallel Execution (Week 1-2)

```python
@workflow.defn
class MigrationWorkflow:
    """Run both paths in parallel, compare results."""

    @workflow.run
    async def run(self, document_id: str):
        # Execute both paths
        temporal_result, direct_result = await asyncio.gather(
            workflow.execute_activity(ingest_via_temporal, document_id),
            workflow.execute_activity(ingest_via_direct_saga, document_id)
        )

        # Compare results
        if temporal_result != direct_result:
            workflow.logger.error(f"Results mismatch: {temporal_result} vs {direct_result}")

        return temporal_result  # Use Temporal result
```

### Phase 2: Gradual Rollout (Week 3-4)

```python
@workflow.defn
class GradualRolloutWorkflow:
    """Route % traffic to Temporal, rest to direct Saga."""

    @workflow.run
    async def run(self, document_id: str):
        # Determine routing (10% → 50% → 100%)
        rollout_percentage = 50  # From feature flag
        use_temporal = workflow.random().randint(1, 100) <= rollout_percentage

        if use_temporal:
            workflow.logger.info(f"Routing {document_id} to Temporal path")
            return await workflow.execute_activity(ingest_via_temporal, document_id)
        else:
            workflow.logger.info(f"Routing {document_id} to direct Saga path")
            return await workflow.execute_activity(ingest_via_direct_saga, document_id)
```

### Phase 3: Full Migration (Week 5-6)

```python
# All ingestion goes through Temporal
@workflow.defn
class ProductionIngestionWorkflow:
    """Production workflow using Temporal + Enhanced Saga."""

    @workflow.run
    async def run(self, document_id: str):
        # Full Temporal orchestration
        # Enhanced Saga handles database writes
        ...
```

## Related Documentation

- [Temporal.io Overview](temporal-io-overview.md)
- [Python SDK Guide](python-sdk-guide.md)
- [Deployment Guide](deployment-guide.md)
- [Migration Strategy](migration-strategy.md)
- [Monitoring & Observability](monitoring-observability.md)

## Resources

- Enhanced Saga Documentation: `upgrades/completed/saga-pattern-enhancement/README.md`
- Saga Test Suite: `apex-memory-system/tests/unit/test_saga_phase2.py`
- Temporal Samples: https://github.com/temporalio/samples-python
