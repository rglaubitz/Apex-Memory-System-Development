# Multi-Database Coordination - Quick Reference

**Status:** ✅ Research Complete
**Date:** 2025-11-01
**For Full Details:** See [RESEARCH-SUMMARY.md](../RESEARCH-SUMMARY.md#5-multi-database-coordination)

---

## Executive Summary

**Coordinating 5 Databases: Neo4j, PostgreSQL, Qdrant, Redis, Graphiti**

- ✅ **ID Mapping** - UUID v7 for time-ordered, collision-proof distributed IDs
- ✅ **Saga Pattern** - Orchestrated multi-database transactions with compensation
- ✅ **Cache Invalidation** - TTL-based + event-driven patterns
- ✅ **Cross-DB Consistency** - Eventually consistent with idempotency
- ✅ **Temporal Coordination** - Graphiti as source of truth for time-aware entities

**Current Apex State:**
- UUID v4 for IDs (no time ordering)
- Saga pattern implemented (DocumentIngestionWorkflow)
- Redis cache (TTL-based, no event-driven invalidation)
- Graphiti integration incomplete

---

## ID Mapping Strategy

### UUID v7 (Recommended for Apex)

**Why UUID v7 over UUID v4:**
- ✅ **Time-ordered** - Sortable by creation time (no separate timestamp needed)
- ✅ **Index-friendly** - Sequential IDs improve B-tree performance (Neo4j, PostgreSQL)
- ✅ **Collision-proof** - 122 bits of randomness (same as v4)
- ✅ **Distributed-safe** - No coordination needed across services

**UUID v7 Format:**
```
xxxxxxxx-xxxx-7xxx-xxxx-xxxxxxxxxxxx
|      |    |    |    |
|      |    |    |    └─ 62 bits random
|      |    |    └────── 2 bits variant (10)
|      |    └─────────── 4 bits version (0111 = 7)
|      └──────────────── 12 bits random
└─────────────────────── 48 bits timestamp (milliseconds since epoch)
```

**Python Implementation:**

```python
import uuid
import time

def generate_uuid7() -> str:
    """Generate UUID v7 (time-ordered)."""
    timestamp_ms = int(time.time() * 1000)  # 48 bits
    random_bits = uuid.uuid4().int & ((1 << 74) - 1)  # 74 bits

    # Combine: 48-bit timestamp + 4-bit version (7) + 2-bit variant (10) + 74-bit random
    uuid_int = (timestamp_ms << 80) | (7 << 76) | (2 << 74) | random_bits
    return str(uuid.UUID(int=uuid_int))

# Example
doc_id = generate_uuid7()
print(doc_id)  # 018c1a2e-3f4b-7d8e-9a1c-2b3d4e5f6a7b
#                ^^^^^^^^ (timestamp sortable)
```

**Comparison:**

| Feature | UUID v4 | UUID v7 |
|---------|---------|---------|
| **Time-ordered** | ❌ No | ✅ Yes |
| **Index performance** | ⚠️ Random (fragmented) | ✅ Sequential (optimized) |
| **Sortable** | ❌ No | ✅ Yes (by creation time) |
| **Collision probability** | 1 in 2^122 | 1 in 2^122 (same) |
| **Distributed-safe** | ✅ Yes | ✅ Yes |

**Apex Migration Path:**
1. Add `generate_uuid7()` utility
2. Use for new documents/chunks/entities (dual-write phase)
3. Backfill existing UUIDs (optional, non-breaking)
4. Add sort-by-creation queries (leverage time ordering)

---

## Cross-Database ID Propagation

### Consistent ID Usage

**Single Source of Truth** - Document UUID assigned once, propagated everywhere:

```python
from uuid import UUID

class DocumentIngestionCoordinator:
    """Coordinates document ingestion across 5 databases."""

    async def ingest_document(self, content: str, metadata: dict) -> UUID:
        # 1. Generate UUID v7 (source of truth)
        document_id = generate_uuid7()

        try:
            # 2. Write to PostgreSQL (metadata + pgvector)
            await self.postgres_service.insert_document(
                document_id=document_id,
                content=content,
                metadata=metadata
            )

            # 3. Write to Qdrant (vector embeddings)
            embedding = await self.embedding_service.generate(content)
            await self.qdrant_service.upsert_document(
                document_id=document_id,
                vector=embedding,
                payload=metadata
            )

            # 4. Write to Neo4j (graph relationships)
            await self.neo4j_service.create_document_node(
                document_id=document_id,
                title=metadata["title"],
                created_at=metadata["created_at"]
            )

            # 5. Write to Graphiti (temporal episode)
            await self.graphiti_service.add_document_episode(
                document_id=document_id,
                content=content,
                reference_time=metadata["created_at"]
            )

            # 6. Cache in Redis (3600s TTL)
            await self.redis_service.cache_document(
                document_id=document_id,
                data={"id": document_id, "title": metadata["title"]},
                ttl=3600
            )

            return document_id

        except Exception as e:
            # Saga compensation (rollback all writes)
            await self.rollback_ingestion(document_id)
            raise
```

**Key Pattern**: UUID generated once, propagated to all 5 databases with same ID.

---

## Saga Pattern (Orchestrated)

### Transaction Coordination Without 2PC

**Why Saga over Two-Phase Commit (2PC):**
- ✅ **No coordinator bottleneck** - Each database commits independently
- ✅ **Partition-tolerant** - Works during network splits
- ✅ **Failure-resilient** - Compensation activities for rollback
- ❌ **Eventually consistent** - Not strongly consistent (acceptable for Apex)

**Saga Implementation Pattern:**

```python
from temporal import workflow
from dataclasses import dataclass
from typing import List, Callable

@dataclass
class SagaStep:
    """Single step in saga with compensation."""
    action: Callable  # Forward action
    compensation: Callable  # Rollback action
    description: str

@workflow.defn
class DocumentIngestionSaga:
    """Orchestrated saga for multi-database writes."""

    @workflow.run
    async def run(self, document_id: str, content: str, metadata: dict) -> dict:
        saga_log = []

        # Define saga steps (order matters)
        steps = [
            SagaStep(
                action=lambda: self.write_postgres(document_id, content, metadata),
                compensation=lambda: self.delete_postgres(document_id),
                description="PostgreSQL write"
            ),
            SagaStep(
                action=lambda: self.write_qdrant(document_id, content),
                compensation=lambda: self.delete_qdrant(document_id),
                description="Qdrant write"
            ),
            SagaStep(
                action=lambda: self.write_neo4j(document_id, metadata),
                compensation=lambda: self.delete_neo4j(document_id),
                description="Neo4j write"
            ),
            SagaStep(
                action=lambda: self.write_graphiti(document_id, content, metadata),
                compensation=lambda: self.delete_graphiti(document_id),
                description="Graphiti write"
            ),
            SagaStep(
                action=lambda: self.cache_redis(document_id, metadata),
                compensation=lambda: self.invalidate_redis(document_id),
                description="Redis cache"
            )
        ]

        # Execute saga
        for i, step in enumerate(steps):
            try:
                result = await step.action()
                saga_log.append({"step": i, "status": "success", "description": step.description})
            except Exception as e:
                # Compensate (rollback all previous steps)
                workflow.logger.error(f"Saga failed at step {i}: {step.description} - {e}")

                for j in range(i - 1, -1, -1):
                    try:
                        await steps[j].compensation()
                        saga_log.append({"step": j, "status": "compensated", "description": steps[j].description})
                    except Exception as comp_error:
                        workflow.logger.error(f"Compensation failed for step {j}: {comp_error}")
                        saga_log.append({"step": j, "status": "compensation_failed", "description": steps[j].description})

                raise Exception(f"Saga failed: {saga_log}")

        return {"status": "success", "saga_log": saga_log}

    async def write_postgres(self, document_id: str, content: str, metadata: dict):
        """Write to PostgreSQL."""
        await workflow.execute_activity(
            insert_document_activity,
            args=[document_id, content, metadata],
            start_to_close_timeout=timedelta(seconds=30)
        )

    async def delete_postgres(self, document_id: str):
        """Compensate: Delete from PostgreSQL."""
        await workflow.execute_activity(
            delete_document_activity,
            args=[document_id],
            start_to_close_timeout=timedelta(seconds=10)
        )

    # Similar methods for Qdrant, Neo4j, Graphiti, Redis...
```

### Compensation Activities

**Design Principles:**
1. **Idempotent** - Safe to retry (DELETE WHERE id=X works even if already deleted)
2. **Fast** - Target <10s per compensation
3. **Logged** - Record all compensation attempts
4. **Best-effort** - Log failures but don't block (eventual consistency acceptable)

**Example Compensation (Neo4j):**

```python
from temporal import activity

@activity.defn
async def delete_neo4j_document(document_id: str) -> dict:
    """Compensate: Delete document node from Neo4j."""
    driver = get_neo4j_driver()

    with driver.session() as session:
        result = session.run("""
            MATCH (d:Document {uuid: $document_id})
            DETACH DELETE d
            RETURN count(d) AS deleted_count
        """, document_id=document_id)

        deleted_count = result.single()["deleted_count"]

        if deleted_count == 0:
            activity.logger.warning(f"Neo4j compensation: Document {document_id} not found (already deleted)")

        return {
            "status": "compensated",
            "deleted_count": deleted_count,
            "idempotent": True
        }
```

---

## Cache Invalidation Strategies

### Redis Cache Patterns

**Current Apex Pattern** - TTL-based expiration:

```python
# Write-through cache
async def cache_document(document_id: str, data: dict, ttl: int = 3600):
    """Cache document metadata (3600s = 1 hour)."""
    key = f"doc:{document_id}"
    await redis_client.setex(key, ttl, json.dumps(data))

# Read-through cache
async def get_document(document_id: str) -> dict:
    """Get document from cache or database."""
    key = f"doc:{document_id}"

    # 1. Check cache
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)

    # 2. Cache miss - query PostgreSQL
    doc = await postgres_service.get_document(document_id)

    # 3. Write to cache (3600s TTL)
    await redis_client.setex(key, 3600, json.dumps(doc))

    return doc
```

**Problem**: Stale data until TTL expires (1 hour).

### Event-Driven Cache Invalidation (Recommended)

**Pattern**: Invalidate cache on write operations:

```python
from enum import Enum

class CacheEvent(str, Enum):
    """Cache invalidation events."""
    DOCUMENT_UPDATED = "document_updated"
    DOCUMENT_DELETED = "document_deleted"
    ENTITY_UPDATED = "entity_updated"

async def update_document(document_id: str, updates: dict):
    """Update document and invalidate cache."""
    # 1. Update PostgreSQL
    await postgres_service.update_document(document_id, updates)

    # 2. Update Qdrant (if embedding changed)
    if "content" in updates:
        embedding = await embedding_service.generate(updates["content"])
        await qdrant_service.update_vector(document_id, embedding)

    # 3. Update Neo4j (if metadata changed)
    if "title" in updates or "tags" in updates:
        await neo4j_service.update_document_node(document_id, updates)

    # 4. Invalidate Redis cache
    await invalidate_cache(document_id, CacheEvent.DOCUMENT_UPDATED)

async def invalidate_cache(document_id: str, event: CacheEvent):
    """Invalidate cache for document and related entities."""
    keys_to_delete = [
        f"doc:{document_id}",           # Document cache
        f"query:*{document_id}*",       # Query results containing this doc
        f"user:docs:{user_id}",         # User's document list
    ]

    # Wildcard delete
    for pattern in keys_to_delete:
        if "*" in pattern:
            keys = await redis_client.keys(pattern)
            if keys:
                await redis_client.delete(*keys)
        else:
            await redis_client.delete(pattern)

    # Publish event for distributed invalidation (if using Redis Cluster)
    await redis_client.publish("cache_invalidation", json.dumps({
        "document_id": document_id,
        "event": event.value,
        "timestamp": datetime.now().isoformat()
    }))
```

**Benefits:**
- ✅ No stale data (immediate invalidation)
- ✅ Distributed coordination via pub/sub
- ✅ Selective invalidation (only affected keys)

**Trade-offs:**
- ⚠️ More complex (event handlers needed)
- ⚠️ Potential cache stampede (many queries after invalidation)

### Cache Stampede Mitigation

**Problem**: 1000 requests hit cache miss simultaneously, all query database.

**Solution 1: Request Coalescing**

```python
import asyncio
from typing import Dict

# In-memory request deduplication
_pending_requests: Dict[str, asyncio.Future] = {}

async def get_document_with_coalescing(document_id: str) -> dict:
    """Get document with request coalescing."""
    key = f"doc:{document_id}"

    # 1. Check cache
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)

    # 2. Cache miss - check if request already pending
    if document_id in _pending_requests:
        return await _pending_requests[document_id]

    # 3. Create new request
    future = asyncio.Future()
    _pending_requests[document_id] = future

    try:
        # Query database
        doc = await postgres_service.get_document(document_id)

        # Write to cache
        await redis_client.setex(key, 3600, json.dumps(doc))

        # Resolve future
        future.set_result(doc)
        return doc

    finally:
        # Cleanup
        del _pending_requests[document_id]
```

**Result**: 1000 requests → 1 database query (other 999 wait for first result).

**Solution 2: Probabilistic Early Expiration (PER)**

```python
import random

async def get_document_with_per(document_id: str) -> dict:
    """Get document with probabilistic early refresh."""
    key = f"doc:{document_id}"

    cached_data = await redis_client.get(key)
    if not cached_data:
        # Cache miss - query database
        return await refresh_cache(document_id)

    data = json.loads(cached_data)
    ttl = await redis_client.ttl(key)

    # Probabilistic early refresh (10% chance if TTL < 10% remaining)
    if ttl > 0:
        refresh_probability = max(0, 1 - (ttl / 3600))  # Higher prob as TTL decreases
        if random.random() < refresh_probability:
            # Asynchronously refresh cache (return stale data immediately)
            asyncio.create_task(refresh_cache(document_id))

    return data

async def refresh_cache(document_id: str) -> dict:
    """Refresh cache from database."""
    doc = await postgres_service.get_document(document_id)
    await redis_client.setex(f"doc:{document_id}", 3600, json.dumps(doc))
    return doc
```

---

## Temporal Coordination (Graphiti as Source of Truth)

### Entity Lifecycle Management

**Pattern**: Graphiti tracks entity evolution over time, other databases store point-in-time snapshots.

```python
from datetime import datetime, timedelta

async def query_entity_at_time(entity_name: str, reference_time: datetime) -> dict:
    """Get entity state at specific point in time."""

    # 1. Query Graphiti for temporal entity
    graphiti_entity = await graphiti_service.search_entities(
        query=entity_name,
        reference_time=reference_time  # As of this time
    )

    if not graphiti_entity:
        return None

    entity_uuid = graphiti_entity["uuid"]

    # 2. Query Neo4j for relationships (at that time)
    relationships = await neo4j_service.get_relationships(
        entity_uuid=entity_uuid,
        valid_at=reference_time  # Temporal filter
    )

    # 3. Query PostgreSQL for metadata
    metadata = await postgres_service.get_entity(entity_uuid)

    # 4. Combine results
    return {
        "uuid": entity_uuid,
        "name": graphiti_entity["name"],
        "entity_type": graphiti_entity["entity_type"],
        "relationships": relationships,
        "metadata": metadata,
        "reference_time": reference_time.isoformat(),
        "source": "graphiti"  # Graphiti = source of truth
    }
```

### Temporal Query Patterns

**Example: "What did we know about ACME Corporation on October 1, 2025?"**

```python
async def temporal_snapshot(entity_name: str, snapshot_date: datetime) -> dict:
    """Get complete entity snapshot at specific date."""

    # 1. Graphiti: Entity state at snapshot_date
    entity = await graphiti_service.search_entities(
        query=entity_name,
        reference_time=snapshot_date,
        limit=1
    )

    if not entity:
        return {"error": f"{entity_name} not found at {snapshot_date}"}

    entity_uuid = entity["uuid"]

    # 2. Neo4j: Relationships valid at snapshot_date
    cypher = """
        MATCH (e:Entity {uuid: $entity_uuid})-[r:RELATED_TO]-(other:Entity)
        WHERE r.valid_from <= $snapshot_date
          AND (r.invalid_at IS NULL OR r.invalid_at > $snapshot_date)
        RETURN other.name AS related_entity,
               r.relationship_type AS relationship,
               r.valid_from AS since
    """
    relationships = await neo4j_service.query(cypher, {
        "entity_uuid": entity_uuid,
        "snapshot_date": snapshot_date
    })

    # 3. PostgreSQL: Documents mentioning entity (created before snapshot_date)
    documents = await postgres_service.query("""
        SELECT document_id, title, created_at
        FROM documents
        WHERE entity_mentions @> ARRAY[$1]::uuid[]
          AND created_at <= $2
        ORDER BY created_at DESC
        LIMIT 10
    """, [entity_uuid, snapshot_date])

    return {
        "entity": entity,
        "relationships": relationships,
        "documents": documents,
        "snapshot_date": snapshot_date.isoformat()
    }
```

**Use Case**: "Show me what our relationship with this customer looked like 6 months ago" (for dispute resolution, compliance audits).

---

## Consistency Guarantees

### Eventually Consistent (Acceptable for Apex)

**Trade-offs:**

| Consistency Model | Latency | Availability | Complexity | Apex Fit |
|-------------------|---------|--------------|------------|----------|
| **Strong** (2PC) | High (100-500ms) | Low (single failure = abort) | High | ❌ Too slow |
| **Eventual** (Saga) | Low (10-50ms) | High (partition-tolerant) | Medium | ✅ Acceptable |
| **Causal** | Medium (50-100ms) | Medium | Very High | ❌ Overkill |

**Apex Decision**: Eventually consistent with saga compensation is sufficient.

**Why:**
- Read-heavy workload (90% reads, 10% writes)
- Short inconsistency window (typically <100ms)
- Compensation handles failures (no data loss)
- User-facing queries tolerant of stale data (cached for 1 hour anyway)

### Idempotency Requirements

**All write operations must be idempotent** (safe to retry):

```python
@activity.defn
async def insert_document_activity(document_id: str, content: str, metadata: dict):
    """Insert document (idempotent)."""
    # Use INSERT ... ON CONFLICT DO NOTHING (PostgreSQL)
    await postgres_service.execute("""
        INSERT INTO documents (document_id, content, title, created_at)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (document_id) DO NOTHING
    """, [document_id, content, metadata["title"], metadata["created_at"]])

    # Idempotency: If document_id already exists, no-op (no error)
```

**Benefits:**
- Temporal workflow retries are safe
- Network failures don't cause duplicates
- Saga compensation can retry without side effects

---

## Cross-Database Query Patterns

### Federated Queries (Avoid)

**Anti-Pattern**: Join across databases in application code

```python
# ❌ BAD: N+1 queries (slow for 100+ documents)
async def get_documents_with_relationships(user_id: str) -> List[dict]:
    # 1. Query PostgreSQL for user's documents
    docs = await postgres_service.query(
        "SELECT * FROM documents WHERE user_id = $1",
        [user_id]
    )

    # 2. For each document, query Neo4j for relationships (N queries)
    for doc in docs:
        doc["relationships"] = await neo4j_service.get_relationships(doc["document_id"])

    return docs
```

**Better Pattern**: Query router selects optimal database

```python
# ✅ GOOD: Route to optimal database based on query intent
async def search_documents(query: str, user_id: str) -> List[dict]:
    # 1. Classify query intent
    intent = await query_router.classify(query)

    if intent == QueryIntent.SEMANTIC:
        # Qdrant: Vector similarity search
        return await qdrant_service.search(query, user_id)

    elif intent == QueryIntent.RELATIONSHIP:
        # Neo4j: Graph traversal
        return await neo4j_service.traverse(query, user_id)

    elif intent == QueryIntent.TEMPORAL:
        # Graphiti: Time-aware entity search
        return await graphiti_service.search_temporal(query, user_id)

    else:
        # PostgreSQL: Metadata/hybrid search
        return await postgres_service.search(query, user_id)
```

### Result Aggregation (When Necessary)

**Pattern**: Parallel queries + merge results

```python
async def multi_database_search(query: str, user_id: str) -> dict:
    """Search across multiple databases (parallel)."""

    # Execute queries in parallel
    qdrant_task = qdrant_service.search(query, user_id, limit=10)
    neo4j_task = neo4j_service.search(query, user_id, limit=10)
    postgres_task = postgres_service.search(query, user_id, limit=10)

    qdrant_results, neo4j_results, postgres_results = await asyncio.gather(
        qdrant_task, neo4j_task, postgres_task
    )

    # Merge results (de-duplicate by document_id)
    merged = {}
    for result in qdrant_results + neo4j_results + postgres_results:
        doc_id = result["document_id"]
        if doc_id not in merged:
            merged[doc_id] = result
        else:
            # Merge metadata (prefer higher scores)
            if result.get("score", 0) > merged[doc_id].get("score", 0):
                merged[doc_id].update(result)

    # Sort by score and return top 10
    sorted_results = sorted(merged.values(), key=lambda x: x.get("score", 0), reverse=True)
    return {"results": sorted_results[:10], "total": len(merged)}
```

---

## Monitoring and Observability

### Cross-Database Metrics

**Key Metrics to Track:**

1. **Saga Success Rate** - Target: >99.9%
   ```python
   saga_success_rate = Gauge('saga_success_rate', 'Saga success rate')
   saga_failure_count = Counter('saga_failures_total', 'Total saga failures')
   ```

2. **Compensation Latency** - Target: <10s P90
   ```python
   compensation_latency = Histogram(
       'compensation_latency_seconds',
       'Compensation latency',
       buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0]
   )
   ```

3. **Cache Hit Rate** - Target: >70%
   ```python
   cache_hit_rate = Gauge('redis_cache_hit_rate', 'Cache hit rate')
   ```

4. **Cross-DB Query Latency** - Target: <200ms P90
   ```python
   cross_db_query_latency = Histogram(
       'cross_db_query_latency_seconds',
       'Cross-database query latency',
       buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
   )
   ```

5. **Consistency Lag** - Target: <100ms
   ```python
   consistency_lag = Histogram(
       'consistency_lag_seconds',
       'Time between primary write and replica consistency',
       buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
   )
   ```

---

## Apex-Specific Recommendations

### Short-Term (Phase 3)

1. **Migrate to UUID v7** 🆔
   - Replace UUID v4 with time-ordered UUID v7
   - Improve Neo4j/PostgreSQL index performance
   - Enable sort-by-creation queries

2. **Add Event-Driven Cache Invalidation** ⚡
   - Invalidate Redis cache on document updates
   - Use pub/sub for distributed coordination
   - Reduce stale data window (1 hour → immediate)

3. **Saga Improvements** 🔄
   - Add retry logic to compensation activities
   - Log saga execution timeline (Temporal UI)
   - Alert on compensation failures

### Long-Term (Phase 4+)

4. **Graphiti Temporal Integration** 🕐
   - Use Graphiti as source of truth for entity evolution
   - Implement "as-of" queries (entity state at past time)
   - Sync Neo4j relationships with Graphiti episodes

5. **Distributed Tracing** 🔍
   - OpenTelemetry spans for cross-database queries
   - Trace saga execution across all 5 databases
   - Identify bottlenecks (slowest database writes)

6. **Consistency Monitoring** 📊
   - Measure time between PostgreSQL write and Qdrant consistency
   - Alert on consistency lag >1s (outliers)
   - Dashboard: Saga success rate, compensation rate, consistency lag

---

## Critical Gaps (Current State)

From current-state-analysis.md:

**Graphiti Entity Types Not Passed** ❌ Priority 1
- `GraphitiService.add_document_episode()` missing `entity_types` parameter
- Impact: Only 60% accuracy instead of 90%
- **Fix**: Add `entity_types=ENTITY_TYPES` parameter

**Redis Schema Documentation Only** ⚠️ Priority 2
- No enforcement of key naming conventions
- No validation layer
- Impact: Potential key collisions, inconsistent patterns
- **Fix**: Create validation layer (optional) or comprehensive docs

**DLQ Schema Usage Unclear** ⚠️ Priority 3
- `postgres_dlq.sql` exists but not referenced
- No documented retry/failure handling
- Impact: Dead letter queue may not be operational
- **Fix**: Document DLQ workflow, add retry logic

---

## References

**Official Documentation (Tier 1):**
- Temporal Sagas: https://docs.temporal.io/workflows#saga-pattern
- Redis Cache Patterns: https://redis.io/docs/manual/patterns/
- UUID v7 Spec: https://datatracker.ietf.org/doc/html/draft-peabody-dispatch-new-uuid-format

**Verified Examples (Tier 2):**
- Python UUID v7: https://github.com/uuid6/uuid6-python (200+ stars)
- Saga Pattern (Microsoft): https://docs.microsoft.com/en-us/azure/architecture/reference-architectures/saga/saga

**Current Apex Implementation:**
- Saga: `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`
- Redis Cache: `apex-memory-system/src/apex_memory/services/redis_service.py`
- ID Generation: `apex-memory-system/src/apex_memory/utils/id_generator.py`

**Research Summary:**
- Complete Multi-DB findings: [RESEARCH-SUMMARY.md](../RESEARCH-SUMMARY.md#5-multi-database-coordination)
- Neo4j patterns: [neo4j-research.md](./neo4j-research.md)
- PostgreSQL patterns: [postgresql-research.md](./postgresql-research.md)

---

**Next**: All research complete! See [../IMPLEMENTATION.md](../IMPLEMENTATION.md) for step-by-step implementation guide (coming next)
