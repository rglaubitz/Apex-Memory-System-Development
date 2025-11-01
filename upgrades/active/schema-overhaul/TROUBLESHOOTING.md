# Schema Overhaul Troubleshooting Guide

**Status:** ✅ Complete
**Last Updated:** 2025-11-01
**Version:** 1.0

---

## Table of Contents

1. [Common Issues by Database](#1-common-issues-by-database)
2. [Seed Entity Management](#2-seed-entity-management)
3. [Multi-Database Coordination](#3-multi-database-coordination)
4. [Performance Issues](#4-performance-issues)
5. [Migration Problems](#5-migration-problems)
6. [Graphiti Integration](#6-graphiti-integration)
7. [Debugging Tools & Commands](#7-debugging-tools--commands)

---

## 1. Common Issues by Database

### 1.1 Neo4j Issues

#### Issue: Index Not Being Used

**Symptoms:**
- Slow queries (>1s)
- `PROFILE` shows `AllNodesScan` or `NodeByLabelScan`
- No `NodeIndexSeek` in query plan

**Diagnosis:**
```cypher
// Check if index exists
SHOW INDEXES
YIELD name, labelsOrTypes, properties, state
WHERE name CONTAINS 'your_index_name';

// Profile query to see execution plan
PROFILE
MATCH (e:Entity {name: 'test'})
RETURN e;
```

**Solutions:**

**Solution 1: Index doesn't exist**
```cypher
// Create missing index
CREATE INDEX entity_name_idx IF NOT EXISTS
FOR (e:Entity) ON (e.name);

// Wait for index to build
SHOW INDEXES
YIELD name, state, populationPercent
WHERE name = 'entity_name_idx';
```

**Solution 2: Query doesn't use index parameters**
```cypher
// BAD: Literal values prevent index usage
MATCH (e:Entity {name: 'ACME Corp'}) RETURN e;

// GOOD: Parameterized queries enable index
MATCH (e:Entity {name: $name}) RETURN e;
```

**Solution 3: Property mismatch**
```cypher
// Check actual property names
MATCH (e:Entity) RETURN properties(e) LIMIT 1;

// Ensure index property matches query
CREATE INDEX entity_correct_property IF NOT EXISTS
FOR (e:Entity) ON (e.actualPropertyName);
```

---

#### Issue: Temporal Queries Too Slow

**Symptoms:**
- Queries with `valid_from`/`invalid_at` filters >100ms
- Many `:Edge` nodes scanned

**Diagnosis:**
```cypher
// Profile temporal query
PROFILE
MATCH (e:Entity {name: 'ACME Corp'})-[:RELATES_TO]->(edge:Edge)-[:RELATES_TO]->(related)
WHERE edge.valid_from <= datetime('2025-10-15T00:00:00Z')
  AND (edge.invalid_at IS NULL OR edge.invalid_at > datetime('2025-10-15T00:00:00Z'))
RETURN related
LIMIT 10;

// Check for temporal index
SHOW INDEXES
YIELD name, labelsOrTypes, properties
WHERE 'Edge' IN labelsOrTypes;
```

**Solution: Create composite temporal index**
```cypher
// CRITICAL: Composite index on both temporal fields
CREATE INDEX edge_temporal_validity_idx IF NOT EXISTS
FOR (ed:Edge) ON (ed.valid_from, ed.invalid_at);

// Individual indexes also helpful
CREATE INDEX edge_valid_from_idx IF NOT EXISTS
FOR (ed:Edge) ON (ed.valid_from);

CREATE INDEX edge_invalid_at_idx IF NOT EXISTS
FOR (ed:Edge) ON (ed.invalid_at);
```

**Verification:**
```cypher
// Re-profile query - should now show NodeIndexSeek
PROFILE
MATCH (e:Entity {name: 'ACME Corp'})-[:RELATES_TO]->(edge:Edge)-[:RELATES_TO]->(related)
WHERE edge.valid_from <= datetime('2025-10-15T00:00:00Z')
  AND (edge.invalid_at IS NULL OR edge.invalid_at > datetime('2025-10-15T00:00:00Z'))
RETURN related
LIMIT 10;
```

---

#### Issue: Connection Pool Exhaustion

**Symptoms:**
- "Unable to acquire connection from pool"
- Timeouts on queries
- 503 errors from API

**Diagnosis:**
```python
# Check driver connection pool status
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
print(f"Max pool size: {driver._pool.max_connection_pool_size}")
print(f"Active connections: {driver._pool.in_use_connection_count()}")
```

**Solutions:**

**Solution 1: Increase pool size**
```python
# In Neo4jService __init__
driver = GraphDatabase.driver(
    uri="bolt://localhost:7687",
    auth=("neo4j", "password"),
    max_connection_pool_size=100,  # Default: 50
    connection_acquisition_timeout=60  # Default: 30s
)
```

**Solution 2: Ensure sessions are closed**
```python
# BAD: Session not closed
def bad_query():
    session = driver.session()
    result = session.run("MATCH (n) RETURN n LIMIT 10")
    return list(result)  # Session never closed!

# GOOD: Use context manager
def good_query():
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN n LIMIT 10")
        return list(result)
    # Session automatically closed
```

**Solution 3: Use connection pooling with limits**
```python
# In Temporal activities
@activity.defn
async def query_neo4j(query: str) -> list:
    async with async_timeout.timeout(30):  # Prevent hanging
        with driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]
```

---

### 1.2 PostgreSQL Issues

#### Issue: HNSW Index Build Taking Too Long

**Symptoms:**
- `CREATE INDEX` hanging for >10 minutes
- High CPU usage on PostgreSQL
- Blocking other queries

**Diagnosis:**
```sql
-- Check index build progress
SELECT
    now() - query_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE query LIKE '%CREATE INDEX%'
  AND state <> 'idle';

-- Check existing indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexname LIKE '%hnsw%';
```

**Solutions:**

**Solution 1: Use CONCURRENTLY**
```sql
-- Build index without locking table
CREATE INDEX CONCURRENTLY documents_embedding_hnsw_idx
ON documents USING hnsw (embedding vector_cosine_ops);

-- Check progress
SELECT * FROM pg_stat_progress_create_index;
```

**Solution 2: Adjust work_mem temporarily**
```sql
-- Increase memory for index build
SET work_mem = '256MB';  -- Default: 4MB

CREATE INDEX documents_embedding_hnsw_idx
ON documents USING hnsw (embedding vector_cosine_ops);

-- Reset to default
RESET work_mem;
```

**Solution 3: Build in maintenance window**
```sql
-- Schedule during low-traffic period
-- Use lower ef_construction for faster build
CREATE INDEX documents_embedding_hnsw_idx
ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);  -- Lower = faster (default: 200)
```

---

#### Issue: pgvector Query Not Using Index

**Symptoms:**
- Slow vector similarity queries (>1s)
- Sequential scan instead of index scan
- EXPLAIN shows "Seq Scan"

**Diagnosis:**
```sql
-- Check query plan
EXPLAIN ANALYZE
SELECT id, title, embedding <=> '[0.1, 0.2, ...]' AS distance
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 10;

-- Check if index exists and is valid
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'documents'
  AND indexname LIKE '%embedding%';

-- Check index statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexname LIKE '%embedding%';
```

**Solutions:**

**Solution 1: Create HNSW index**
```sql
-- HNSW is much faster than IVFFlat for small-medium datasets
CREATE INDEX documents_embedding_hnsw_idx
ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Solution 2: Adjust query parameters**
```sql
-- Increase ef_search for better recall (slower but more accurate)
SET hnsw.ef_search = 100;  -- Default: 40

SELECT id, title, embedding <=> $1 AS distance
FROM documents
ORDER BY embedding <=> $1
LIMIT 10;
```

**Solution 3: Use correct distance operator**
```sql
-- Ensure operator matches index
-- For cosine distance: <=>
-- For L2 distance: <->
-- For inner product: <#>

-- Match operator to index type
CREATE INDEX documents_embedding_hnsw_idx
ON documents USING hnsw (embedding vector_cosine_ops);  -- Use <=>

SELECT * FROM documents
ORDER BY embedding <=> $1  -- Must use <=> not <-> or <#>
LIMIT 10;
```

---

#### Issue: Alembic Migration Fails

**Symptoms:**
- `alembic upgrade head` fails midway
- "duplicate key value" or "relation already exists" errors
- Database in inconsistent state

**Diagnosis:**
```sql
-- Check current Alembic version
SELECT version_num FROM alembic_version;

-- Check what should be applied
-- alembic history --verbose

-- Check for conflicting objects
SELECT tablename FROM pg_tables WHERE tablename = 'your_table';
SELECT indexname FROM pg_indexes WHERE indexname = 'your_index';
```

**Solutions:**

**Solution 1: Rollback and retry**
```bash
# Downgrade to known good state
alembic downgrade -1

# Check database state
psql -U apex -d apex_memory -c "SELECT version_num FROM alembic_version;"

# Try upgrade again
alembic upgrade head
```

**Solution 2: Fix migration script**
```python
# In migration file - add IF NOT EXISTS checks
def upgrade():
    # BAD: Will fail if table exists
    op.create_table('documents', ...)

    # GOOD: Idempotent
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)

    if 'documents' not in inspector.get_table_names():
        op.create_table('documents', ...)

    # For indexes
    op.create_index('idx_name', 'table', ['column'], if_not_exists=True)
```

**Solution 3: Stamp current state**
```bash
# If migration already applied manually
alembic stamp head

# Or stamp specific revision
alembic stamp <revision_id>
```

---

### 1.3 Qdrant Issues

#### Issue: Collection Not Found

**Symptoms:**
- "Collection 'documents' not found" errors
- 404 responses from Qdrant API
- Empty collection list

**Diagnosis:**
```python
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)

# List all collections
collections = client.get_collections()
print("Existing collections:", [c.name for c in collections.collections])

# Try to get specific collection
try:
    info = client.get_collection("documents")
    print(f"Collection exists: {info.name}, vectors: {info.vectors_count}")
except Exception as e:
    print(f"Collection not found: {e}")
```

**Solutions:**

**Solution 1: Create collection**
```python
from qdrant_client.models import Distance, VectorParams

# Create missing collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1536,  # OpenAI text-embedding-3-small
        distance=Distance.COSINE
    )
)
```

**Solution 2: Run initialization script**
```bash
# Run Qdrant schema setup
python scripts/setup/create_qdrant_collections.py
```

**Solution 3: Check Docker container**
```bash
# Ensure Qdrant is running
docker ps | grep qdrant

# Check logs for errors
docker logs apex-qdrant

# Restart if needed
docker-compose restart qdrant
```

---

#### Issue: Point Upload Fails (UUID Format)

**Symptoms:**
- "Invalid UUID format" errors
- Points not uploaded to Qdrant
- 400 Bad Request responses

**Diagnosis:**
```python
# Check UUID format
import uuid

test_uuid = "some-uuid-string"
print(f"Is valid UUID? {is_valid_uuid(test_uuid)}")

def is_valid_uuid(uuid_string):
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False
```

**Solutions:**

**Solution 1: Use UUID strings, not objects**
```python
# BAD: UUID object
entity_id = uuid.uuid7()  # Returns UUID object
client.upsert(
    collection_name="entities",
    points=[{"id": entity_id, ...}]  # Will fail
)

# GOOD: UUID string
entity_id = str(uuid.uuid7())  # Convert to string
client.upsert(
    collection_name="entities",
    points=[{"id": entity_id, ...}]  # Works
)
```

**Solution 2: Validate before upload**
```python
def upsert_entity_safe(entity_id: str, vector: list, payload: dict):
    """Safe upsert with validation."""
    # Validate UUID
    try:
        uuid.UUID(entity_id)
    except ValueError:
        raise ValueError(f"Invalid UUID format: {entity_id}")

    # Upload
    client.upsert(
        collection_name="entities",
        points=[{
            "id": entity_id,
            "vector": vector,
            "payload": payload
        }]
    )
```

---

### 1.4 Redis Issues

#### Issue: Cache Hit Rate Too Low (<50%)

**Symptoms:**
- High database query load
- Slow repeat queries
- Cache hit rate <50% (target: >70%)

**Diagnosis:**
```bash
# Check Redis stats
redis-cli INFO stats | grep keyspace_hits
redis-cli INFO stats | grep keyspace_misses

# Calculate hit rate
redis-cli --eval hit_rate.lua
```

```lua
-- hit_rate.lua
local hits = redis.call('INFO', 'stats')
local misses = redis.call('INFO', 'stats')
-- Parse and calculate hit rate
```

**Solutions:**

**Solution 1: Increase TTL for stable data**
```python
# BAD: Too short TTL
redis.setex("entity:uuid", 60, json.dumps(data))  # 1 minute

# GOOD: Longer TTL for stable entities
redis.setex("entity:uuid", 86400, json.dumps(data))  # 24 hours
```

**Solution 2: Implement cache warming**
```python
async def warm_cache_on_startup():
    """Pre-populate cache with frequently accessed entities."""
    # Get top 100 most accessed entities
    top_entities = await pg_service.query("""
        SELECT id, data
        FROM entities
        ORDER BY access_count DESC
        LIMIT 100
    """)

    # Populate cache
    for entity in top_entities:
        redis.setex(
            f"entity:{entity['id']}",
            86400,
            json.dumps(entity['data'])
        )
```

**Solution 3: Add cache-aside pattern**
```python
async def get_entity(entity_id: str) -> dict:
    """Get entity with cache-aside pattern."""
    # Try cache first
    cached = redis.get(f"entity:{entity_id}")
    if cached:
        return json.loads(cached)

    # Cache miss - query database
    entity = await pg_service.query_one(
        "SELECT * FROM entities WHERE id = %s",
        (entity_id,)
    )

    # Populate cache for next time
    if entity:
        redis.setex(f"entity:{entity_id}", 86400, json.dumps(entity))

    return entity
```

---

## 2. Seed Entity Management

### 2.1 Issue: Duplicate Entities After Ingestion

**Symptoms:**
- Seed entity "G" + extracted entity "The G Companies"
- Multiple nodes for same real-world entity
- Inconsistent query results

**Diagnosis:**
```cypher
// Find potential duplicates
MATCH (e1:Entity), (e2:Entity)
WHERE e1.name CONTAINS e2.name
  AND e1.uuid <> e2.uuid
  AND (e1.source = 'seed_data' OR e2.source = 'seed_data')
RETURN
    e1.name AS entity1,
    e1.source AS source1,
    e2.name AS entity2,
    e2.source AS source2,
    e2.uuid AS duplicate_uuid
ORDER BY e1.name;
```

**Example output:**
```
entity1           source1     entity2              source2               duplicate_uuid
"G"               seed_data   "The G Companies"    graphiti_extraction   abc123...
"G"               seed_data   "G Transport"        graphiti_extraction   def456...
"Origin Transport" seed_data   "Origin"            graphiti_extraction   ghi789...
```

**Solutions:**

**Solution 1: Update seed entity aliases**
```json
// data/seed/entities.json
{
  "entities": [
    {
      "name": "G",
      "aliases": ["The G Companies", "G Transport", "G Logistics", "G Corp"],
      ...
    }
  ]
}
```

**Solution 2: Merge duplicate into seed entity**
```bash
# Use merge script
python scripts/maintenance/merge_entities.py <seed_uuid> <duplicate_uuid>
```

```cypher
// Manual merge in Neo4j
MATCH (seed:Entity {uuid: $seed_uuid, source: 'seed_data'})
MATCH (duplicate:Entity {uuid: $duplicate_uuid})

// Transfer all relationships from duplicate to seed
MATCH (duplicate)-[r]->(target)
WHERE NOT (seed)-[]->(target)
CREATE (seed)-[r2:${type(r)}]->(target)
SET r2 = properties(r)

MATCH (source)-[r]->(duplicate)
WHERE NOT (source)-[]->(seed)
CREATE (source)-[r2:${type(r)}]->(seed)
SET r2 = properties(r)

// Delete duplicate
DETACH DELETE duplicate

RETURN seed.name AS merged_into, count(r) AS relationships_transferred;
```

**Solution 3: Configure Graphiti deduplication**
```python
# In GraphitiService - add deduplication threshold
from graphiti_core import Graphiti

graphiti = Graphiti(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    entity_similarity_threshold=0.9  # Higher = more strict (prevent near-duplicates)
)
```

---

### 2.2 Issue: Seed Workflow Fails Midway

**Symptoms:**
- Some entities created, others missing
- Inconsistent state across databases
- Temporal workflow shows "Failed" status

**Diagnosis:**
```bash
# Check Temporal workflow history
temporal workflow describe --workflow-id seed-entities-<timestamp>

# Check which entities were created
psql -U apex -d apex_memory -c "SELECT name, created_at FROM entities WHERE source = 'seed_data';"
```

```cypher
// Neo4j - Check created entities
MATCH (e:Entity {source: 'seed_data'})
RETURN e.name, e.created_at
ORDER BY e.created_at;
```

**Solutions:**

**Solution 1: Compensations run automatically**
```
The SeedEntitiesWorkflow has built-in saga pattern with compensations.
If workflow fails, Temporal automatically calls compensate_entity_creation()
for any entities created before failure.

Check Temporal UI for compensation activity status.
```

**Solution 2: Manual cleanup if needed**
```bash
# If compensations didn't run, manually clean up
python scripts/maintenance/cleanup_seed_entities.py
```

```python
# cleanup_seed_entities.py
from apex_memory.services import *

def cleanup_partial_seed():
    """Remove all seed entities from all databases."""

    # PostgreSQL
    pg = PostgreSQLService()
    pg.execute("DELETE FROM entities WHERE source = 'seed_data'")

    # Neo4j
    neo4j = Neo4jService()
    neo4j.run("MATCH (e:Entity {source: 'seed_data'}) DETACH DELETE e")

    # Qdrant
    qdrant = QdrantService()
    qdrant.delete(
        collection_name="entities",
        points_selector={
            "filter": {
                "must": [{"key": "source", "match": {"value": "seed_data"}}]
            }
        }
    )

    # Redis
    redis = RedisService()
    for key in redis.scan_iter("entity:*"):
        cached = redis.get(key)
        if json.loads(cached).get("source") == "seed_data":
            redis.delete(key)

    print("✅ Cleanup complete - all seed entities removed")
```

**Solution 3: Fix seed data and retry**
```bash
# 1. Fix entities.json (add missing fields, correct UUIDs)
# 2. Re-run seed workflow
python scripts/seed/run_seed_entities.py data/seed/entities.json
```

---

### 2.3 Issue: Seed Entities Not Linking to Extracted Entities

**Symptoms:**
- Seed entity "G" exists
- Extracted entities (customers, products) exist
- But no relationships between them
- Queries return isolated seed entities

**Diagnosis:**
```cypher
// Check if seed entities have relationships
MATCH (seed:Entity {source: 'seed_data'})
OPTIONAL MATCH (seed)-[r]-(connected)
RETURN
    seed.name,
    count(r) AS relationship_count,
    collect(DISTINCT type(r)) AS relationship_types
ORDER BY relationship_count;
```

**Example bad output:**
```
name                relationship_count   relationship_types
"G"                 5                    [OWNS, HAS_DEPARTMENT]  // Only seed→seed
"Origin Transport"  3                    [OPERATES, DEVELOPS]    // No links to extracted
"Fleet"             1                    [USES]
```

**Solutions:**

**Solution 1: Ensure document mentions seed entities**
```
Documents must explicitly mention seed entity names (or aliases) for Graphiti
to create relationships.

Example good document:
"ACME Corporation placed a $50,000 order with Origin Transport for fleet services."
             ↓
Graphiti creates: (ACME Corp)-[:CUSTOMER_OF]->(Origin Transport)
                                                  ↑ Links to seed entity
```

**Solution 2: Manual relationship creation**
```python
# scripts/maintenance/link_extracted_to_seed.py
from apex_memory.services.neo4j_service import Neo4jService

def link_customers_to_seed():
    """Link extracted customer entities to seed 'Origin Transport' entity."""

    neo4j = Neo4jService()

    # Find customers and link to Origin Transport
    neo4j.run("""
        MATCH (customer:Entity {entity_type: 'Customer'})
        MATCH (origin:Entity {name: 'Origin Transport', source: 'seed_data'})
        WHERE NOT (customer)-[:CUSTOMER_OF]->(origin)
        CREATE (customer)-[:CUSTOMER_OF {
            created_at: datetime(),
            confidence: 0.8,
            source: 'manual_link'
        }]->(origin)
        RETURN count(*) AS links_created
    """)
```

**Solution 3: Use Graphiti episode context**
```python
# When ingesting documents, add context about seed entities
from graphiti_core import Graphiti

graphiti = Graphiti(...)

# Include seed entity in episode body
await graphiti.add_episode(
    name="ACME Corp Invoice",
    episode_body=f"""
    Invoice for ACME Corporation.
    Services provided by Origin Transport (subsidiary of G).
    Fleet management services: $50,000.
    """,
    source=EpisodeType.text,
    reference_time=datetime.now()
)

# Graphiti will extract:
# - ACME Corporation (Customer)
# - Relationship: ACME Corp → CUSTOMER_OF → Origin Transport
# - Automatically links to seed "Origin Transport" entity
```

---

## 3. Multi-Database Coordination

### 3.1 Issue: UUID Mismatch Across Databases

**Symptoms:**
- Entity exists in PostgreSQL but not Neo4j
- Different UUIDs for same entity across databases
- Saga compensations failing

**Diagnosis:**
```python
# Check UUID consistency
import asyncio
from apex_memory.services import *

async def check_uuid_consistency(entity_name: str):
    """Check if entity UUID is consistent across all databases."""

    pg = PostgreSQLService()
    neo4j = Neo4jService()
    qdrant = QdrantService()

    # PostgreSQL
    pg_result = await pg.query_one("SELECT id FROM entities WHERE name = %s", (entity_name,))
    pg_uuid = pg_result['id'] if pg_result else None

    # Neo4j
    neo4j_result = neo4j.run("MATCH (e:Entity {name: $name}) RETURN e.uuid AS uuid", name=entity_name)
    neo4j_uuid = neo4j_result.single()['uuid'] if neo4j_result.single() else None

    # Qdrant
    qdrant_result = qdrant.scroll(
        collection_name="entities",
        scroll_filter={"must": [{"key": "name", "match": {"value": entity_name}}]},
        limit=1
    )
    qdrant_uuid = qdrant_result[0][0].id if qdrant_result[0] else None

    print(f"PostgreSQL UUID: {pg_uuid}")
    print(f"Neo4j UUID: {neo4j_uuid}")
    print(f"Qdrant UUID: {qdrant_uuid}")

    if pg_uuid == neo4j_uuid == qdrant_uuid:
        print("✅ UUIDs consistent")
    else:
        print("❌ UUID MISMATCH - data inconsistency detected")

# Run check
asyncio.run(check_uuid_consistency("ACME Corp"))
```

**Solutions:**

**Solution 1: Always generate UUID once at workflow level**
```python
# BAD: Generate UUID in each activity
@activity.defn
async def save_to_postgresql(entity_data: dict):
    entity_uuid = str(uuid.uuid7())  # ❌ Different UUID each time!
    pg.execute("INSERT INTO entities (id, ...) VALUES (%s, ...)", (entity_uuid, ...))

# GOOD: Generate UUID in workflow, pass to all activities
@workflow.defn
class EntityIngestionWorkflow:
    async def run(self, entity_data: dict):
        entity_uuid = str(uuid.uuid7())  # ✅ Generate once
        entity_data["uuid"] = entity_uuid

        await workflow.execute_activity(save_to_postgresql, entity_data)
        await workflow.execute_activity(save_to_neo4j, entity_data)  # Same UUID
        await workflow.execute_activity(save_to_qdrant, entity_data)  # Same UUID
```

**Solution 2: Add UUID validation to activities**
```python
@activity.defn
async def save_to_neo4j(entity_data: dict):
    if "uuid" not in entity_data:
        raise ValueError("Entity data missing UUID - must be generated in workflow")

    # Validate UUID format
    try:
        uuid.UUID(entity_data["uuid"])
    except ValueError:
        raise ValueError(f"Invalid UUID format: {entity_data['uuid']}")

    # Proceed with save
    neo4j.run("""
        CREATE (e:Entity {uuid: $uuid, ...})
    """, uuid=entity_data["uuid"], ...)
```

---

### 3.2 Issue: Saga Compensation Not Running

**Symptoms:**
- Workflow fails but entity remains in some databases
- Partial data across databases
- Temporal UI shows "Failed" but no compensation activities

**Diagnosis:**
```bash
# Check Temporal workflow event history
temporal workflow describe --workflow-id <workflow-id>

# Look for CompensationStarted events
# If missing, compensations didn't trigger
```

**Solutions:**

**Solution 1: Ensure activities have compensation activities defined**
```python
# BAD: No compensation defined
@workflow.defn
class MyWorkflow:
    async def run(self, data: dict):
        await workflow.execute_activity(save_to_postgresql, data)
        await workflow.execute_activity(save_to_neo4j, data)  # If this fails, PostgreSQL data remains!

# GOOD: Explicit compensations
@workflow.defn
class MyWorkflow:
    async def run(self, data: dict):
        try:
            result_pg = await workflow.execute_activity(save_to_postgresql, data)
        except Exception as e:
            # Nothing to compensate yet
            raise

        try:
            result_neo4j = await workflow.execute_activity(save_to_neo4j, data)
        except Exception as e:
            # Compensate PostgreSQL write
            await workflow.execute_activity(compensate_postgresql_write, result_pg['uuid'])
            raise

        try:
            result_qdrant = await workflow.execute_activity(save_to_qdrant, data)
        except Exception as e:
            # Compensate both previous writes
            await workflow.execute_activity(compensate_neo4j_write, result_neo4j['uuid'])
            await workflow.execute_activity(compensate_postgresql_write, result_pg['uuid'])
            raise
```

**Solution 2: Make compensations idempotent**
```python
@activity.defn
async def compensate_postgresql_write(entity_uuid: str):
    """Delete entity from PostgreSQL - idempotent."""

    # Check if already compensated (via Redis flag)
    redis = RedisService()
    redis_key = f"compensated:pg:{entity_uuid}"
    if redis.exists(redis_key):
        return  # Already compensated, skip

    # Delete from PostgreSQL
    pg = PostgreSQLService()
    pg.execute("DELETE FROM entities WHERE id = %s", (entity_uuid,))

    # Mark as compensated
    redis.setex(redis_key, 86400, "1")  # 24 hours
```

---

## 4. Performance Issues

### 4.1 Issue: Multi-DB Writes Taking >500ms

**Symptoms:**
- Document ingestion slow (>2s per document)
- High P90 latency for writes
- Temporal workflows backing up in queue

**Diagnosis:**
```python
# Profile individual database write times
import time

async def profile_multi_db_write(entity_data: dict):
    """Profile write times to each database."""

    times = {}

    # PostgreSQL
    start = time.time()
    await pg.execute("INSERT INTO entities (...) VALUES (...)")
    times['postgresql'] = (time.time() - start) * 1000  # ms

    # Neo4j
    start = time.time()
    neo4j.run("CREATE (e:Entity {...})")
    times['neo4j'] = (time.time() - start) * 1000

    # Qdrant
    start = time.time()
    qdrant.upsert(...)
    times['qdrant'] = (time.time() - start) * 1000

    # Redis
    start = time.time()
    redis.setex(...)
    times['redis'] = (time.time() - start) * 1000

    for db, ms in times.items():
        print(f"{db}: {ms:.2f}ms")

    return times
```

**Solutions:**

**Solution 1: Run database writes in parallel**
```python
# BAD: Sequential writes (total = sum of all)
async def save_entity_sequential(data: dict):
    await save_to_postgresql(data)  # 50ms
    await save_to_neo4j(data)       # 100ms
    await save_to_qdrant(data)      # 80ms
    await save_to_redis(data)       # 10ms
    # Total: 240ms

# GOOD: Parallel writes (total = max of all)
async def save_entity_parallel(data: dict):
    await asyncio.gather(
        save_to_postgresql(data),  # 50ms  \
        save_to_neo4j(data),       # 100ms  > Run in parallel
        save_to_qdrant(data),      # 80ms  /
        save_to_redis(data)        # 10ms /
    )
    # Total: 100ms (max)
```

**Solution 2: Batch inserts where possible**
```python
# BAD: One entity at a time
for entity in entities:
    await save_entity(entity)  # 100ms each × 100 entities = 10,000ms

# GOOD: Batch insert
await save_entities_batch(entities)  # 500ms for 100 entities
```

```python
@activity.defn
async def save_entities_batch(entities: list[dict]):
    """Save multiple entities in single batch."""

    # PostgreSQL - use executemany
    pg = PostgreSQLService()
    pg.executemany(
        "INSERT INTO entities (id, name, ...) VALUES (%s, %s, ...)",
        [(e['uuid'], e['name'], ...) for e in entities]
    )

    # Qdrant - use batch upsert
    qdrant = QdrantService()
    qdrant.upsert(
        collection_name="entities",
        points=[{
            "id": e['uuid'],
            "vector": e['embedding'],
            "payload": {...}
        } for e in entities]
    )
```

**Solution 3: Optimize indexes**
```sql
-- PostgreSQL - disable indexes during bulk insert, rebuild after
ALTER INDEX entities_name_idx SET (fillfactor = 100);
-- Insert data
REINDEX INDEX entities_name_idx;
```

---

## 5. Migration Problems

*(Complete section 5 with migration rollback, version conflicts, data loss prevention)*

---

## 6. Graphiti Integration

### 6.1 Issue: Custom Entity Labels Not Applied

**Symptoms:**
- Entity has `entity_type: 'Customer'` property
- But no `:Customer` label in Neo4j
- Can't query with `MATCH (c:Customer)`

**Diagnosis:**
```cypher
// Check entity labels
MATCH (e:Entity {name: 'ACME Corp'})
RETURN labels(e), e.entity_type;

// Expected: labels = ['Entity', 'Customer']
// Actual:   labels = ['Entity'] only
```

**Cause:**
This is a known limitation (GitHub issue #567). Graphiti does NOT automatically apply custom labels like `:Customer`, `:Invoice`, etc.

**Solutions:**

**Solution 1: Query by entity_type property (recommended)**
```cypher
// Instead of label-based query
MATCH (c:Customer)  // ❌ Won't work

// Use property-based query
MATCH (e:Entity {entity_type: 'Customer'})  // ✅ Works
RETURN e;

// With index for performance
CREATE INDEX entity_type_idx IF NOT EXISTS
FOR (e:Entity) ON (e.entity_type);
```

**Solution 2: Add custom labels post-extraction**
```python
# scripts/maintenance/apply_custom_labels.py
from apex_memory.services.neo4j_service import Neo4jService

def apply_custom_labels():
    """Apply custom labels based on entity_type property."""

    neo4j = Neo4jService()

    # Map entity_type to label
    entity_types = ['Customer', 'Invoice', 'Driver', 'Equipment', 'Load']

    for entity_type in entity_types:
        neo4j.run(f"""
            MATCH (e:Entity {{entity_type: $entity_type}})
            WHERE NOT e:{entity_type}  // Don't re-apply
            SET e:{entity_type}
            RETURN count(e) AS labeled_count
        """, entity_type=entity_type)

    print("✅ Custom labels applied")

# Run periodically (weekly)
apply_custom_labels()
```

---

## 7. Debugging Tools & Commands

### 7.1 Quick Health Checks

**All Services:**
```bash
# Check all Docker containers
docker ps | grep -E "neo4j|postgres|qdrant|redis|temporal"

# Check service health
python scripts/dev/health_check.py -v
```

**PostgreSQL:**
```sql
-- Connection count
SELECT count(*) FROM pg_stat_activity;

-- Slow queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '1 second';

-- Database size
SELECT pg_size_pretty(pg_database_size('apex_memory'));
```

**Neo4j:**
```cypher
// Connection count
CALL dbms.listConnections() YIELD connectionId, username, protocol;

// Database stats
CALL apoc.meta.stats()
YIELD nodeCount, relCount, labelCount
RETURN nodeCount, relCount, labelCount;

// Memory usage
CALL dbms.queryJmx('java.lang:type=Memory')
YIELD attributes
RETURN attributes.HeapMemoryUsage.used;
```

**Qdrant:**
```bash
# Collection info
curl -X GET "http://localhost:6333/collections/documents"

# Cluster info
curl -X GET "http://localhost:6333/cluster"
```

**Redis:**
```bash
# Server info
redis-cli INFO server

# Memory stats
redis-cli INFO memory

# Key count
redis-cli DBSIZE
```

---

### 7.2 Common Debugging Commands

**Check Entity Across All Databases:**
```bash
# Run comprehensive entity check
python scripts/debug/check_entity.py "ACME Corp"
```

```python
# scripts/debug/check_entity.py
import sys
from apex_memory.services import *

def check_entity(entity_name: str):
    """Check entity existence across all databases."""

    print(f"Checking entity: {entity_name}\n")

    # PostgreSQL
    pg = PostgreSQLService()
    pg_result = pg.query_one("SELECT * FROM entities WHERE name = %s", (entity_name,))
    print(f"PostgreSQL: {'✅ Found' if pg_result else '❌ Not found'}")
    if pg_result:
        print(f"  UUID: {pg_result['id']}")
        print(f"  Type: {pg_result['entity_type']}")

    # Neo4j
    neo4j = Neo4jService()
    neo4j_result = neo4j.run("MATCH (e:Entity {name: $name}) RETURN e", name=entity_name)
    record = neo4j_result.single()
    print(f"Neo4j: {'✅ Found' if record else '❌ Not found'}")
    if record:
        print(f"  UUID: {record['e']['uuid']}")
        print(f"  Type: {record['e'].get('entity_type')}")

    # Qdrant
    qdrant = QdrantService()
    qdrant_result = qdrant.scroll(
        collection_name="entities",
        scroll_filter={"must": [{"key": "name", "match": {"value": entity_name}}]},
        limit=1
    )
    print(f"Qdrant: {'✅ Found' if qdrant_result[0] else '❌ Not found'}")
    if qdrant_result[0]:
        print(f"  UUID: {qdrant_result[0][0].id}")

    # Redis
    # (Check all entity keys - expensive, only for debugging)
    print("Redis: Checking cache...")

if __name__ == "__main__":
    check_entity(sys.argv[1])
```

---

**Troubleshooting Checklist:**

- [ ] Check Docker containers running
- [ ] Verify database connectivity
- [ ] Run health check script
- [ ] Check Temporal workflow status
- [ ] Profile query performance
- [ ] Check logs for errors
- [ ] Validate UUIDs consistent
- [ ] Check seed entity aliases
- [ ] Run deduplication check
- [ ] Verify indexes exist and used

---

**Document Version:** 1.0
**Last Updated:** 2025-11-01
**Maintained By:** Apex Memory System Development Team
