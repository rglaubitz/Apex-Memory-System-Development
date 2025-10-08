# ADR-002: Saga Pattern for Distributed Writes

**Status:** Proposed

**Date:** 2025-10-06

**Deciders:** Architecture Team, CTO, CIO

---

## Context

The Apex Memory System implements a parallel multi-database architecture with four heterogeneous data stores:

1. **Neo4j** - Graph relationships and entity connections
2. **PostgreSQL + pgvector** - Metadata search and hybrid semantic queries
3. **Qdrant** - High-performance vector similarity search
4. **Redis** - Cache layer for <100ms repeat queries

When ingesting documents, we must write extracted entities, embeddings, and metadata to all four databases in a coordinated manner. **The challenge is maintaining data consistency across these heterogeneous systems where traditional ACID distributed transactions are not feasible.**

### The Problem

Traditional distributed transaction mechanisms like Two-Phase Commit (2PC) are not viable because:

1. **NoSQL database incompatibility:** Neo4j, Qdrant, and Redis do not support XA transactions or 2PC protocols
2. **Performance penalties:** 2PC requires holding locks across all databases, creating bottlenecks and reducing throughput
3. **Single point of failure:** The transaction coordinator becomes a critical failure point
4. **Scalability limitations:** Synchronous coordination does not scale well with high ingestion rates (target: 10+ documents/second)

### Business Requirements

- **Data consistency:** All four databases must eventually reflect the same logical state
- **Failure recovery:** Partial writes must be rolled back to prevent data corruption
- **Performance:** Ingestion latency must remain under 1 second (P90)
- **Observability:** Failed transactions must be detectable and debuggable
- **Idempotency:** Retries must not create duplicate data

---

## Options Considered

### Option A: Two-Phase Commit (2PC)

**Approach:** Use a distributed transaction coordinator to implement 2PC across all databases.

**Pros:**
- Strong consistency guarantees (ACID)
- Automatic rollback on failure
- Well-understood protocol

**Cons:**
- **Not supported by our database stack:** Neo4j, Qdrant, and Redis do not implement XA transactions
- **Performance bottleneck:** Requires holding locks across all databases during commit phase
- **Single point of failure:** Transaction coordinator failure blocks all writes
- **Scalability issues:** Synchronous coordination limits throughput

**Verdict:** ❌ **Not feasible** - Incompatible with NoSQL databases in our stack.

**Research Support:**
- "When building distributed systems, you would want to use different data stores like NoSQL databases (Mongo, Cassandra or Neo4J)... but none of these would support XA Transactions" ([Microservices.io](https://microservices.io/patterns/data/saga.html))
- Baeldung: "2PC is less scalable due to the need for coordination and the potential locks to be held across distributed nodes"

---

### Option B: Saga Pattern (Orchestration)

**Approach:** Implement an orchestrator service that coordinates sequential writes to each database with compensating transactions for rollback.

**Pros:**
- **Works with heterogeneous databases:** No XA transaction requirement
- **Centralized control flow:** Single orchestrator manages all steps
- **Explicit error handling:** Clear rollback semantics via compensating transactions
- **Observable:** Easy to debug and monitor transaction state
- **Better for complex workflows:** Supports conditional logic and branching

**Cons:**
- **Increased latency:** Sequential writes add ~200-400ms vs parallel
- **Single point of failure:** Orchestrator must be highly available
- **Implementation complexity:** Requires coding compensating transactions

**Performance Impact:**
- Sequential writes: ~800ms total (4 × 200ms average DB latency)
- Still within P90 target of <1s

**Verdict:** ✅ **Recommended** - Best balance of reliability, observability, and compatibility.

**Research Support:**
- Microsoft Azure Architecture: "The orchestrator performs saga requests, stores and interprets the states of each task, and handles failure recovery by using compensating transactions" ([Saga Design Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga))
- Chris Richardson: "An orchestrator tells the participants what local transactions to execute" ([Microservices.io](https://microservices.io/patterns/data/saga.html))

---

### Option C: Saga Pattern (Choreography)

**Approach:** Implement event-driven saga where each database write publishes an event to trigger the next write.

**Pros:**
- **Decoupled services:** No central coordinator dependency
- **Scalable:** Services react independently to events
- **Flexible evolution:** Easy to add new databases

**Cons:**
- **Difficult to debug:** Transaction flow distributed across event logs
- **Cyclic dependency risk:** Events can create complex dependency chains
- **Harder to implement compensations:** No central place to track state
- **Eventual consistency window:** Larger time window for inconsistency

**Verdict:** ❌ **Not recommended** - Too complex for our use case with only 4 databases.

**Research Support:**
- Microsoft Azure Architecture: "End-to-end monitoring and reporting are more difficult to achieve in saga choreography, compared with saga orchestration" ([Saga Design Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga))
- LinkedIn: "Orchestration: Ideal for complex workflows needing clear visibility and control. Choreography: Suited for simpler, loosely coupled systems"

---

### Option D: Best-Effort Writes (No Coordination)

**Approach:** Write to all databases in parallel without transaction coordination or rollback.

**Pros:**
- **Lowest latency:** Parallel writes complete in ~200ms (fastest database response)
- **Simple implementation:** No saga infrastructure needed
- **Maximum throughput:** No coordination overhead

**Cons:**
- **No consistency guarantees:** Partial writes leave databases in inconsistent state
- **Data corruption risk:** Failed writes create orphaned data
- **No rollback mechanism:** Cannot recover from failures
- **Debugging nightmare:** No audit trail of what succeeded vs failed

**Verdict:** ❌ **Not acceptable** - Violates data consistency requirements.

---

## Decision

**We will implement the Saga Pattern with Orchestration (Option B)** for the following reasons:

### 1. **Compatibility with Heterogeneous Databases**
The saga pattern works with any database (SQL, NoSQL, graph, vector, cache) because it relies on local ACID transactions within each database rather than distributed transactions across databases.

### 2. **Eventual Consistency with Compensating Transactions**
While we sacrifice strong consistency, we gain:
- **Guaranteed rollback:** Compensating transactions undo partial writes
- **Auditability:** Central orchestrator logs all steps and failures
- **Debugging:** Clear transaction state for troubleshooting

### 3. **Performance Within Requirements**
Sequential writes add latency (~800ms total) but remain within our P90 target of <1s for ingestion.

### 4. **Industry-Proven Pattern**
The orchestration-based saga pattern is widely used for distributed systems with heterogeneous databases, as documented by Microsoft, AWS, and microservices thought leaders.

---

## Research Support

### Tier 1: Official Documentation

**Microsoft Azure Architecture Center:**
- [Saga Design Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga) - Orchestration approach for distributed transactions
- [Compensating Transaction Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction) - Rollback semantics and idempotency

**AWS Prescriptive Guidance:**
- [Saga Pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-data-persistence/saga-pattern.html) - Implementation guidance for distributed data persistence

### Tier 2: Verified Technical Sources

**Chris Richardson - Microservices.io:**
- [Saga Pattern](https://microservices.io/patterns/data/saga.html) - Canonical definition and orchestration vs choreography comparison

**Temporal.io:**
- [Saga Compensating Transactions](https://temporal.io/blog/compensating-actions-part-of-a-complete-breakfast-with-sagas) - Python implementation patterns

**Baeldung Computer Science:**
- [Saga Pattern in Microservices](https://www.baeldung.com/cs/saga-pattern-microservices) - Best practices and trade-offs
- [Two-Phase Commit vs Saga Pattern](https://www.baeldung.com/cs/two-phase-commit-vs-saga-pattern) - Comparison and use cases

### Tier 3: GitHub Examples (1.5k+ stars)

**Python Saga Implementations:**
- [cdddg/py-saga-orchestration](https://github.com/cdddg/py-saga-orchestration) - Async saga builder pattern
- [serramatutu/py-saga](https://github.com/serramatutu/py-saga) - Asynchronous saga with compensations
- [absent1706/saga-framework](https://github.com/absent1706/saga-framework) - Production-ready saga framework

---

## Implementation Architecture

### Saga Orchestrator Design

```
┌─────────────────────────────────────────────────────┐
│          Ingestion API (FastAPI)                    │
│  POST /documents/ingest                             │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│          Saga Orchestrator                          │
│                                                      │
│  Steps:                                             │
│  1. Extract entities & embeddings                   │
│  2. Write to Neo4j (graph)           ──────────┐    │
│  3. Write to PostgreSQL (metadata)   ──────────┼──► │
│  4. Write to Qdrant (vectors)        ──────────┼──► │
│  5. Write to Redis (cache)           ──────────┘    │
│                                                      │
│  On Failure: Execute compensations in reverse       │
└─────────────────────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┬────────────┐
      ▼              ▼              ▼            ▼
   Neo4j        PostgreSQL       Qdrant        Redis
  (Graph)       (Metadata)      (Vectors)     (Cache)
```

### Compensating Transaction Flow

```
Success Path:          Failure Path (Step 3 fails):
1. Neo4j ✓            1. Neo4j ✓
2. PostgreSQL ✓       2. PostgreSQL ✓
3. Qdrant ✓           3. Qdrant ✗ [FAILURE]
4. Redis ✓
                      Compensate:
                      2. Delete from PostgreSQL ✓
                      1. Delete from Neo4j ✓
```

---

## Python Implementation Example

### Saga Orchestrator Core

```python
import asyncio
import logging
from typing import Callable, Awaitable, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SagaStatus(Enum):
    """Saga execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


@dataclass
class SagaStep:
    """Represents a single step in the saga"""
    name: str
    action: Callable[..., Awaitable[Any]]
    compensation: Callable[..., Awaitable[None]]
    result: Optional[Any] = None
    error: Optional[Exception] = None


class SagaOrchestrator:
    """
    Orchestrates distributed writes across multiple databases with compensating transactions.

    Based on:
    - Microsoft Saga Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/saga
    - Temporal Compensations: https://temporal.io/blog/compensating-actions-part-of-a-complete-breakfast-with-sagas
    """

    def __init__(self, saga_id: str):
        self.saga_id = saga_id
        self.steps: List[SagaStep] = []
        self.status = SagaStatus.PENDING
        self.completed_steps: List[SagaStep] = []

    def add_step(
        self,
        name: str,
        action: Callable[..., Awaitable[Any]],
        compensation: Callable[..., Awaitable[None]]
    ) -> 'SagaOrchestrator':
        """
        Add a step to the saga.

        Args:
            name: Step identifier for logging
            action: Async function to execute (forward transaction)
            compensation: Async function to undo action (rollback)
        """
        self.steps.append(SagaStep(name=name, action=action, compensation=compensation))
        return self

    async def execute(self) -> bool:
        """
        Execute saga steps sequentially.

        Returns:
            True if all steps completed successfully, False if compensated

        Raises:
            Exception if compensation fails (requires manual intervention)
        """
        self.status = SagaStatus.IN_PROGRESS
        logger.info(f"[Saga {self.saga_id}] Starting execution with {len(self.steps)} steps")

        try:
            # Execute steps sequentially
            for step in self.steps:
                logger.info(f"[Saga {self.saga_id}] Executing step: {step.name}")
                try:
                    step.result = await step.action()
                    self.completed_steps.append(step)
                    logger.info(f"[Saga {self.saga_id}] Step {step.name} completed successfully")
                except Exception as e:
                    step.error = e
                    logger.error(f"[Saga {self.saga_id}] Step {step.name} failed: {e}")
                    await self._compensate()
                    return False

            # All steps completed
            self.status = SagaStatus.COMPLETED
            logger.info(f"[Saga {self.saga_id}] Saga completed successfully")
            return True

        except Exception as e:
            logger.exception(f"[Saga {self.saga_id}] Unexpected error during execution: {e}")
            await self._compensate()
            return False

    async def _compensate(self):
        """
        Execute compensating transactions in reverse order.

        Based on Microsoft Compensating Transaction Pattern:
        https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction
        """
        self.status = SagaStatus.COMPENSATING
        logger.warning(f"[Saga {self.saga_id}] Starting compensation for {len(self.completed_steps)} completed steps")

        # Compensate in reverse order (LIFO)
        for step in reversed(self.completed_steps):
            try:
                logger.info(f"[Saga {self.saga_id}] Compensating step: {step.name}")
                await step.compensation()
                logger.info(f"[Saga {self.saga_id}] Compensation for {step.name} completed")
            except Exception as e:
                logger.exception(
                    f"[Saga {self.saga_id}] CRITICAL: Compensation failed for step {step.name}: {e}. "
                    "Manual intervention required!"
                )
                self.status = SagaStatus.FAILED
                raise  # Re-raise to alert monitoring systems

        self.status = SagaStatus.COMPENSATED
        logger.info(f"[Saga {self.saga_id}] Compensation completed successfully")


class IngestionSaga:
    """
    Saga implementation for document ingestion across multiple databases.
    """

    def __init__(
        self,
        neo4j_client,
        postgres_client,
        qdrant_client,
        redis_client
    ):
        self.neo4j = neo4j_client
        self.postgres = postgres_client
        self.qdrant = qdrant_client
        self.redis = redis_client

    async def ingest_document(self, document_id: str, entities: dict, embeddings: list) -> bool:
        """
        Ingest document data across all databases using saga pattern.

        Args:
            document_id: Unique document identifier
            entities: Extracted entities and relationships
            embeddings: Vector embeddings for semantic search

        Returns:
            True if ingestion succeeded, False if compensated
        """
        saga = SagaOrchestrator(saga_id=f"ingest_{document_id}")

        # Step 1: Write to Neo4j (graph relationships)
        saga.add_step(
            name="neo4j_write",
            action=lambda: self._write_to_neo4j(document_id, entities),
            compensation=lambda: self._delete_from_neo4j(document_id)
        )

        # Step 2: Write to PostgreSQL (metadata)
        saga.add_step(
            name="postgres_write",
            action=lambda: self._write_to_postgres(document_id, entities),
            compensation=lambda: self._delete_from_postgres(document_id)
        )

        # Step 3: Write to Qdrant (vectors)
        saga.add_step(
            name="qdrant_write",
            action=lambda: self._write_to_qdrant(document_id, embeddings),
            compensation=lambda: self._delete_from_qdrant(document_id)
        )

        # Step 4: Write to Redis (cache)
        saga.add_step(
            name="redis_write",
            action=lambda: self._write_to_redis(document_id, entities),
            compensation=lambda: self._delete_from_redis(document_id)
        )

        return await saga.execute()

    # Forward transactions (idempotent)

    async def _write_to_neo4j(self, document_id: str, entities: dict):
        """Write entities and relationships to Neo4j graph database"""
        # Idempotent: MERGE instead of CREATE
        await self.neo4j.merge_entities(document_id, entities)
        logger.info(f"Wrote {len(entities)} entities to Neo4j for document {document_id}")

    async def _write_to_postgres(self, document_id: str, entities: dict):
        """Write metadata to PostgreSQL with pgvector"""
        # Idempotent: INSERT ... ON CONFLICT DO UPDATE
        await self.postgres.upsert_metadata(document_id, entities)
        logger.info(f"Wrote metadata to PostgreSQL for document {document_id}")

    async def _write_to_qdrant(self, document_id: str, embeddings: list):
        """Write vector embeddings to Qdrant"""
        # Idempotent: Qdrant uses document_id as point ID
        await self.qdrant.upsert_vectors(document_id, embeddings)
        logger.info(f"Wrote {len(embeddings)} vectors to Qdrant for document {document_id}")

    async def _write_to_redis(self, document_id: str, entities: dict):
        """Write to Redis cache with TTL"""
        # Idempotent: SET overwrites existing key
        await self.redis.set_with_ttl(f"doc:{document_id}", entities, ttl=3600)
        logger.info(f"Cached document {document_id} in Redis")

    # Compensating transactions (idempotent)

    async def _delete_from_neo4j(self, document_id: str):
        """Compensate: Delete entities from Neo4j"""
        await self.neo4j.delete_document(document_id)
        logger.info(f"Compensated: Deleted from Neo4j for document {document_id}")

    async def _delete_from_postgres(self, document_id: str):
        """Compensate: Delete metadata from PostgreSQL"""
        await self.postgres.delete_document(document_id)
        logger.info(f"Compensated: Deleted from PostgreSQL for document {document_id}")

    async def _delete_from_qdrant(self, document_id: str):
        """Compensate: Delete vectors from Qdrant"""
        await self.qdrant.delete_document(document_id)
        logger.info(f"Compensated: Deleted from Qdrant for document {document_id}")

    async def _delete_from_redis(self, document_id: str):
        """Compensate: Delete from Redis cache"""
        await self.redis.delete(f"doc:{document_id}")
        logger.info(f"Compensated: Deleted from Redis for document {document_id}")


# Example usage in FastAPI endpoint
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/documents/ingest")
async def ingest_document(
    document_id: str,
    entities: dict,
    embeddings: list
):
    """
    Ingest document across all databases using saga pattern.
    """
    saga = IngestionSaga(
        neo4j_client=neo4j,
        postgres_client=postgres,
        qdrant_client=qdrant,
        redis_client=redis
    )

    success = await saga.ingest_document(document_id, entities, embeddings)

    if success:
        return {"status": "success", "document_id": document_id}
    else:
        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed and was compensated"
        )
```

---

## Consequences

### Positive

1. **Data Consistency Guarantees**
   - All-or-nothing semantics via compensating transactions
   - No orphaned data across databases
   - Auditability via centralized orchestrator logs

2. **Database Compatibility**
   - Works with heterogeneous databases (SQL, NoSQL, graph, vector, cache)
   - No XA transaction requirement

3. **Observable & Debuggable**
   - Single orchestrator tracks all transaction state
   - Clear logs for each step and compensation
   - Easy to identify failure points

4. **Proven Pattern**
   - Industry-standard approach (Microsoft, AWS, Google Cloud)
   - Multiple production-ready Python frameworks available

### Negative

1. **Increased Latency**
   - Sequential writes add ~600-800ms vs parallel (~200ms)
   - Still within P90 target but higher than theoretical minimum
   - **Mitigation:** Cache frequent queries in Redis; optimize DB client connection pooling

2. **Eventual Consistency Window**
   - Brief period where databases may be inconsistent (during saga execution)
   - ~800ms window where a read might return partial data
   - **Mitigation:** Use database-level transactions within each step; add "ingestion_status" field to track completion

3. **Implementation Complexity**
   - Must design and test compensating transactions for each step
   - Orchestrator becomes critical infrastructure component
   - **Mitigation:** Comprehensive unit tests for compensations; orchestrator health monitoring with auto-restart

4. **Compensating Transaction Limitations**
   - Cannot undo side effects visible to other processes ("dirty reads")
   - Compensations may not restore exact previous state
   - **Mitigation:** Design idempotent operations; use semantic locks where necessary

### Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Orchestrator Failure** | Saga stuck in inconsistent state | Deploy orchestrator with high availability; persist saga state to durable storage |
| **Compensation Failure** | Manual intervention required | Implement retry logic with exponential backoff; alert on-call engineer; maintain compensation audit log |
| **Concurrent Saga Conflicts** | Two sagas updating same entity | Use optimistic locking (version numbers); retry with latest version |
| **Long-Running Sagas** | Lock contention, timeouts | Set step timeouts (30s); use async patterns; avoid holding DB locks |

---

## Monitoring & Observability

### Key Metrics

1. **Saga Success Rate:** Percentage of sagas that complete without compensation
   - Target: >99.5%
   - Alert if <95%

2. **Compensation Rate:** Percentage of sagas requiring rollback
   - Target: <0.5%
   - Alert if >5%

3. **Saga Latency (P50, P90, P99):**
   - P90 target: <1s
   - Alert if P90 >2s

4. **Step Failure Distribution:** Which database step fails most often
   - Identify weakest link in the chain
   - Prioritize reliability improvements

### Logging Requirements

```python
# Log format for saga events
{
    "saga_id": "ingest_doc123",
    "event": "step_completed",
    "step_name": "neo4j_write",
    "duration_ms": 187,
    "status": "success",
    "timestamp": "2025-10-06T10:23:45Z"
}
```

### Alerting

- **Critical:** Compensation failure (manual intervention needed)
- **High:** Compensation rate >5% (indicates system instability)
- **Medium:** P90 latency >2s (performance degradation)
- **Low:** Individual step failures (transient issues)

---

## Testing Strategy

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_saga_success():
    """Test successful saga execution"""
    saga = SagaOrchestrator("test_saga")

    action1 = AsyncMock(return_value="result1")
    compensation1 = AsyncMock()

    saga.add_step("step1", action1, compensation1)

    success = await saga.execute()

    assert success is True
    assert saga.status == SagaStatus.COMPLETED
    action1.assert_awaited_once()
    compensation1.assert_not_awaited()


@pytest.mark.asyncio
async def test_saga_compensation():
    """Test compensation on failure"""
    saga = SagaOrchestrator("test_saga")

    action1 = AsyncMock(return_value="result1")
    compensation1 = AsyncMock()

    action2 = AsyncMock(side_effect=Exception("Database error"))
    compensation2 = AsyncMock()

    saga.add_step("step1", action1, compensation1)
    saga.add_step("step2", action2, compensation2)

    success = await saga.execute()

    assert success is False
    assert saga.status == SagaStatus.COMPENSATED
    action1.assert_awaited_once()
    action2.assert_awaited_once()
    compensation1.assert_awaited_once()  # Rollback step1
    compensation2.assert_not_awaited()   # Step2 didn't complete
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_ingestion_saga_rollback():
    """Test rollback when Qdrant write fails"""
    # Setup mock clients
    neo4j_mock = AsyncMock()
    postgres_mock = AsyncMock()
    qdrant_mock = AsyncMock()
    qdrant_mock.upsert_vectors.side_effect = Exception("Qdrant timeout")
    redis_mock = AsyncMock()

    saga = IngestionSaga(neo4j_mock, postgres_mock, qdrant_mock, redis_mock)

    success = await saga.ingest_document(
        "doc123",
        {"entities": []},
        [0.1, 0.2, 0.3]
    )

    assert success is False
    # Verify writes
    neo4j_mock.merge_entities.assert_awaited_once()
    postgres_mock.upsert_metadata.assert_awaited_once()
    qdrant_mock.upsert_vectors.assert_awaited_once()
    redis_mock.set_with_ttl.assert_not_awaited()  # Never reached

    # Verify compensations (reverse order)
    postgres_mock.delete_document.assert_awaited_once()
    neo4j_mock.delete_document.assert_awaited_once()
```

---

## Future Enhancements

### Phase 2: Parallel Compensations

For faster rollback, compensations can run in parallel (order doesn't matter for deletions):

```python
async def _compensate_parallel(self):
    """Execute compensations in parallel for faster rollback"""
    compensation_tasks = [
        step.compensation()
        for step in reversed(self.completed_steps)
    ]
    await asyncio.gather(*compensation_tasks, return_exceptions=True)
```

### Phase 3: Saga State Persistence

Persist saga state to PostgreSQL for recovery after orchestrator crashes:

```sql
CREATE TABLE saga_state (
    saga_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    current_step INTEGER,
    completed_steps JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Phase 4: Distributed Tracing

Integrate with OpenTelemetry for end-to-end saga tracing:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def execute(self):
    with tracer.start_as_current_span(f"saga.{self.saga_id}") as span:
        span.set_attribute("saga.steps", len(self.steps))
        # ... saga execution
```

---

## Related Decisions

- **ADR-001:** Multi-Database Architecture (defines the 4 databases requiring coordination)
- **ADR-003:** Query Router Design (planned - will use saga for write-heavy operations)
- **ADR-004:** Observability Stack (planned - will integrate saga metrics)

---

## References

### Official Documentation
- [Microsoft: Saga Design Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)
- [Microsoft: Compensating Transaction Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)
- [AWS: Saga Pattern for Distributed Transactions](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-data-persistence/saga-pattern.html)

### Technical Resources
- [Chris Richardson: Saga Pattern](https://microservices.io/patterns/data/saga.html)
- [Temporal: Saga Compensating Transactions](https://temporal.io/blog/compensating-actions-part-of-a-complete-breakfast-with-sagas)
- [Baeldung: Saga Pattern in Microservices](https://www.baeldung.com/cs/saga-pattern-microservices)
- [Baeldung: Two-Phase Commit vs Saga Pattern](https://www.baeldung.com/cs/two-phase-commit-vs-saga-pattern)

### Code Examples
- [cdddg/py-saga-orchestration](https://github.com/cdddg/py-saga-orchestration) - Python async saga builder
- [serramatutu/py-saga](https://github.com/serramatutu/py-saga) - Asynchronous saga implementation
- [absent1706/saga-framework](https://github.com/absent1706/saga-framework) - Production saga framework

---

**Review Required:** CIO (research quality), CTO (technical feasibility), COO (operational impact)
