# Fluid Mind Patterns to Adopt

**Purpose:** Practical guide for incorporating Fluid Mind patterns into Conversational Memory Integration
**Source:** Teammate's "Fluid Mind Architecture" proposal
**Status:** Recommended for Phase 1 (low-complexity additions)

---

## Overview

The Fluid Mind Architecture proposes a "one brain with specialized regions" approach where multiple agents (CFO, COO, Sales) share the same knowledge infrastructure with logical separation.

**Key Insight:** We can adopt the **namespacing patterns** from Fluid Mind (PostgreSQL schemas, Neo4j labels, Qdrant collections, Redis namespaces) without the complexity of the full "UnifiedMind" orchestrator.

**When to Use:** Immediately in Conversational Memory Phase 1 (minimal complexity, future-proofs architecture)

---

## Pattern 1: Redis Namespace Strategy

### What It Is
Prefix all Redis keys with `agent_id:` to enable agent-specific caching.

### Why Adopt
- **Prevents cache collisions** when adding multiple agents later
- **Easier debugging** (know which agent created which cache entry)
- **Cleaner eviction policies** (can expire agent caches independently)
- **Zero performance impact** (Redis handles namespaces natively)

### Implementation

**Before (Current Plan):**
```python
# Generic cache key
cache_key = f"conversation:{conv_id}:context"
await redis.setex(cache_key, 1800, json.dumps(context))
```

**After (With Fluid Mind Pattern):**
```python
# Agent-namespaced cache key
cache_key = f"{agent_id}:conversation:{conv_id}:context"
await redis.setex(cache_key, 1800, json.dumps(context))

# Example keys:
# - "oscar:conversation:123:context"
# - "sarah:conversation:456:context"
# - "maya:conversation:789:context"

# Shared knowledge (no agent prefix)
shared_key = f"shared:entity:{entity_id}"
await redis.setex(shared_key, 3600, json.dumps(entity))
```

### Code Changes Required

**File:** `apex-memory-system/src/apex_memory/services/cache_service.py`

```python
class CacheService:
    def __init__(self, redis_client, agent_id: str = "system"):
        self.redis = redis_client
        self.agent_id = agent_id  # ← Add agent_id parameter

    async def cache_conversation_context(
        self,
        conversation_id: UUID,
        context: dict,
        ttl: int = 1800
    ):
        # Use agent-namespaced key
        key = f"{self.agent_id}:conversation:{conversation_id}:context"
        await self.redis.setex(key, ttl, json.dumps(context))

    async def cache_entity(self, entity_id: UUID, entity: dict, ttl: int = 3600):
        # Shared knowledge (no agent prefix)
        key = f"shared:entity:{entity_id}"
        await self.redis.setex(key, ttl, json.dumps(entity))
```

**Estimated Effort:** 1-2 hours
**Risk:** NEGLIGIBLE

---

## Pattern 2: Qdrant Agent-Specific Collections

### What It Is
Create separate Qdrant collections for each agent instead of one monolithic collection.

### Why Adopt
- **Faster queries** (smaller collections = faster vector search)
- **Cleaner data organization** (Oscar's fleet knowledge ≠ Sarah's financial knowledge)
- **Better monitoring** (per-agent metrics on vector search performance)
- **Easier to scale** (can optimize collection configurations per agent)

### Implementation

**Before (Current Plan):**
```python
# One collection for all documents
await qdrant.create_collection(
    collection_name="documents",
    vectors_config={"size": 1536, "distance": "Cosine"}
)

# Query searches all documents
results = await qdrant.search(
    collection_name="documents",
    query_vector=embedding,
    limit=10
)
```

**After (With Fluid Mind Pattern):**
```python
# Agent-specific collections
AGENT_COLLECTIONS = {
    "oscar": "oscar_fleet_knowledge",
    "sarah": "sarah_financial_knowledge",
    "maya": "maya_sales_knowledge",
    "shared": "shared_documents"  # Cross-agent knowledge
}

# Create collections per agent
for agent_id, collection_name in AGENT_COLLECTIONS.items():
    await qdrant.create_collection(
        collection_name=collection_name,
        vectors_config={"size": 1536, "distance": "Cosine"}
    )

# Query agent-specific collection
results = await qdrant.search(
    collection_name=f"{agent_id}_knowledge",
    query_vector=embedding,
    limit=10
)

# Cross-agent query (if needed)
results_all = []
for collection in ["oscar_fleet_knowledge", "sarah_financial_knowledge"]:
    results = await qdrant.search(
        collection_name=collection,
        query_vector=embedding,
        limit=5
    )
    results_all.extend(results)
```

### Code Changes Required

**File:** `apex-memory-system/src/apex_memory/services/vector_service.py`

```python
class VectorService:
    AGENT_COLLECTIONS = {
        "oscar": "oscar_fleet_knowledge",
        "sarah": "sarah_financial_knowledge",
        "maya": "maya_sales_knowledge",
        "shared": "shared_documents"
    }

    def __init__(self, qdrant_client, agent_id: str = "shared"):
        self.qdrant = qdrant_client
        self.agent_id = agent_id
        self.collection_name = self.AGENT_COLLECTIONS.get(agent_id, "shared_documents")

    async def search(self, query_vector: list[float], limit: int = 10):
        """Search in agent-specific collection"""
        return await self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )

    async def search_cross_agent(
        self,
        query_vector: list[float],
        agents: list[str],
        limit_per_agent: int = 5
    ):
        """Search across multiple agent collections"""
        results = []
        for agent_id in agents:
            collection = self.AGENT_COLLECTIONS.get(agent_id)
            if collection:
                agent_results = await self.qdrant.search(
                    collection_name=collection,
                    query_vector=query_vector,
                    limit=limit_per_agent
                )
                results.extend(agent_results)
        return results
```

**Estimated Effort:** 4-6 hours
**Risk:** LOW (straightforward)

---

## Pattern 3: Neo4j Label-Based Agent Separation

### What It Is
Add agent-specific labels to Neo4j nodes for efficient filtering.

### Why Adopt
- **Efficient agent-specific queries** (single-label filter vs property filter)
- **Cross-domain queries possible** (can query multiple labels when needed)
- **Better query performance** (Neo4j optimizes label filters)
- **Cleaner graph visualization** (can color-code by agent domain)

### Implementation

**Before (Current Plan):**
```cypher
// Generic entity node
CREATE (e:Entity {
  uuid: '123',
  name: 'Truck 247',
  type: 'equipment'
})

// Query all entities (slow for agent-specific views)
MATCH (e:Entity)
WHERE e.type = 'equipment'
RETURN e
```

**After (With Fluid Mind Pattern):**
```cypher
// Entity with agent-specific label
CREATE (e:Entity:Oscar_Domain {
  uuid: '123',
  name: 'Truck 247',
  type: 'equipment',
  agent_id: 'oscar'
})

// Efficient agent-specific query
MATCH (e:Entity:Oscar_Domain)
RETURN e

// Cross-domain query (e.g., "How do maintenance costs affect sales?")
MATCH (e:Entity)
WHERE e:Oscar_Domain OR e:Sarah_Domain
RETURN e
```

### Code Changes Required

**File:** `apex-memory-system/src/apex_memory/services/graph_service.py`

```python
class GraphService:
    AGENT_LABELS = {
        "oscar": "Oscar_Domain",
        "sarah": "Sarah_Domain",
        "maya": "Maya_Domain",
        "shared": "Shared"
    }

    def __init__(self, neo4j_driver, agent_id: str = "shared"):
        self.neo4j = neo4j_driver
        self.agent_id = agent_id
        self.agent_label = self.AGENT_LABELS.get(agent_id, "Shared")

    async def create_entity(self, entity: dict):
        """Create entity with agent-specific label"""
        query = f"""
        CREATE (e:Entity:{self.agent_label} {{
          uuid: $uuid,
          name: $name,
          type: $type,
          agent_id: $agent_id,
          created_at: datetime()
        }})
        RETURN e
        """
        return await self.neo4j.run(query, **entity, agent_id=self.agent_id)

    async def query_agent_entities(self, entity_type: str = None):
        """Query only this agent's entities"""
        where_clause = f"AND e.type = '{entity_type}'" if entity_type else ""
        query = f"""
        MATCH (e:Entity:{self.agent_label})
        WHERE 1=1 {where_clause}
        RETURN e
        """
        return await self.neo4j.run(query)

    async def query_cross_domain(self, agents: list[str], entity_type: str = None):
        """Query across multiple agent domains"""
        labels = [self.AGENT_LABELS[agent] for agent in agents]
        label_filter = " OR ".join([f"e:{label}" for label in labels])
        where_clause = f"AND e.type = '{entity_type}'" if entity_type else ""

        query = f"""
        MATCH (e:Entity)
        WHERE ({label_filter}) {where_clause}
        RETURN e
        """
        return await self.neo4j.run(query)
```

**Estimated Effort:** 4-6 hours
**Risk:** LOW

---

## Pattern 4: PostgreSQL Schema Separation (Future-Ready)

### What It Is
Create agent-specific schemas in PostgreSQL (e.g., `cfo`, `coo`, `oscar`) alongside `core` schema.

### Why Adopt
- **Clean data isolation** (Oscar's fleet data ≠ Sarah's financial data)
- **Easier RBAC** (grant schema-level permissions)
- **Better performance** (smaller tables = faster queries)
- **Compliance-friendly** (agent data can be isolated for audits)

### Implementation

**Before (Current Plan):**
```sql
-- All tables in public schema
CREATE TABLE messages (...);
CREATE TABLE entities (...);
```

**After (With Fluid Mind Pattern):**
```sql
-- Core schema (shared tables)
CREATE SCHEMA IF NOT EXISTS core;
SET search_path TO core;
CREATE TABLE messages (...);  -- All conversations
CREATE TABLE entities (...);  -- All entities

-- Agent-specific schemas
CREATE SCHEMA IF NOT EXISTS oscar;
SET search_path TO oscar;
CREATE TABLE fleet_metrics (...);  -- Oscar's fleet data
CREATE TABLE maintenance_schedules (...);

CREATE SCHEMA IF NOT EXISTS sarah;
SET search_path TO sarah;
CREATE TABLE financial_patterns (...);  -- Sarah's finance data
CREATE TABLE vendor_overcharges (...);

CREATE SCHEMA IF NOT EXISTS maya;
SET search_path TO maya;
CREATE TABLE sales_quotes (...);  -- Maya's sales data
CREATE TABLE customer_lanes (...);
```

### Code Changes Required

**File:** `apex-memory-system/src/apex_memory/services/database_service.py`

```python
class DatabaseService:
    AGENT_SCHEMAS = {
        "oscar": "oscar",
        "sarah": "sarah",
        "maya": "maya",
        "shared": "core"
    }

    def __init__(self, db_connection, agent_id: str = "shared"):
        self.db = db_connection
        self.agent_id = agent_id
        self.schema = self.AGENT_SCHEMAS.get(agent_id, "core")

    async def write_message(self, message: dict):
        """Write to core schema (all messages visible)"""
        query = """
        INSERT INTO core.messages (uuid, content, agent_id, created_at)
        VALUES ($1, $2, $3, NOW())
        """
        return await self.db.execute(query, message['uuid'], message['content'], self.agent_id)

    async def write_agent_specific_data(self, table: str, data: dict):
        """Write to agent-specific schema"""
        query = f"""
        INSERT INTO {self.schema}.{table} (...)
        VALUES (...)
        """
        return await self.db.execute(query, **data)

    async def query_agent_data(self, table: str, filters: dict):
        """Query from agent-specific schema"""
        query = f"SELECT * FROM {self.schema}.{table} WHERE ..."
        return await self.db.fetch_all(query, **filters)
```

**Estimated Effort:** 6-8 hours (schema creation + migration scripts)
**Risk:** MEDIUM (requires database migrations)

**Recommendation:** Prepare schemas in Phase 1, but only use `core` schema until Phase 2 (Fluid Mind patterns)

---

## Implementation Priority

### Phase 1 (Conversational Memory - Weeks 1-8)

**Adopt Immediately (Low Complexity):**
1. ✅ **Redis Namespace Pattern** (1-2 hours)
   - Zero risk, immediate benefit
   - Future-proofs caching layer

2. ✅ **Qdrant Agent Collections** (4-6 hours)
   - Small effort, significant performance benefit
   - Easier than migrating later

**Prepare for Phase 2:**
3. ⚠️ **PostgreSQL Schema Prep** (2-4 hours)
   - Create `core`, `agents` schemas
   - Don't use agent-specific schemas yet (Phase 2)

**Defer to Phase 2:**
4. ❌ **Neo4j Labels** (4-6 hours)
   - Requires schema migration
   - Wait until Phase 2 (Fluid Mind patterns)

---

### Phase 2 (Fluid Mind Patterns - Weeks 9-14)

**Activate All Patterns:**
1. ✅ Complete PostgreSQL schema separation
2. ✅ Add Neo4j agent-specific labels
3. ✅ Implement cross-agent query capabilities
4. ✅ Add query router agent-identity routing

---

## Timeline Impact

**Without Fluid Mind Patterns:** 6-8 weeks (Conversational Memory only)

**With Low-Complexity Patterns (Recommended):**
- Redis namespaces: +1-2 hours
- Qdrant collections: +4-6 hours
- PostgreSQL schema prep: +2-4 hours
- **Total: +1 week → 7-9 weeks**

**Benefit:** Smooth transition to Phase 2 (Fluid Mind patterns already in place)

---

## Testing Strategy

### Unit Tests (Add 5 tests)

1. `test_redis_namespace_isolation()` - Verify agent caches don't collide
2. `test_qdrant_agent_collection_search()` - Verify agent-specific searches
3. `test_qdrant_cross_agent_search()` - Verify cross-agent queries work
4. `test_postgresql_schema_access()` - Verify schema isolation
5. `test_neo4j_label_filtering()` - Verify label-based filtering

### Integration Tests (Add 2 tests)

1. `test_multi_agent_concurrent_writes()` - Verify no contention
2. `test_cross_domain_query()` - Verify Oscar + Sarah query works

---

## Monitoring & Metrics

**Add Per-Agent Metrics:**
```python
# Cache hit rates per agent
cache_hit_rate_oscar = redis.get("metrics:oscar:cache_hit_rate")
cache_hit_rate_sarah = redis.get("metrics:sarah:cache_hit_rate")

# Query latency per agent
query_latency_oscar = prometheus.histogram("query_latency", labels={"agent": "oscar"})
query_latency_sarah = prometheus.histogram("query_latency", labels={"agent": "sarah"})

# Vector search performance per collection
vector_search_oscar = qdrant.get_collection_metrics("oscar_fleet_knowledge")
vector_search_sarah = qdrant.get_collection_metrics("sarah_financial_knowledge")
```

**Grafana Dashboard Additions:**
- Per-agent cache hit rates
- Per-agent query latency (P50/P95)
- Per-collection vector search performance
- Cross-agent query frequency

---

## References

**Full Analysis:** `research/architectural-analysis/fluid-mind-vs-conversational-memory.md`

**Related Documentation:**
- Conversational Memory Integration: `upgrades/active/conversational-memory-integration/`
- Future Enhancements: `research/future-enhancements/`

**Original Proposal:** Teammate's "Fluid Mind Architecture" concept (November 2025)

---

**Last Updated:** 2025-11-14
**Status:** Recommended for Phase 1 (Redis, Qdrant) + Phase 2 (PostgreSQL, Neo4j)
**Estimated Impact:** +1 week timeline, significant future-proofing benefit
