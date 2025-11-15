# Conversational Memory Integration - Technical Architecture

**Status:** Finalized Architecture
**Decision Date:** 2025-11-14
**Target Deployment:** Mid-January 2026

---

## Executive Summary

### The Problem

Apex Memory System currently has a critical architectural gap:
- ✅ **Documents (PDFs, DOCX)** → Successfully ingested and stored in knowledge graph
- ❌ **Conversations (User↔Agent, Agent↔Agent)** → Stored in PostgreSQL but NOT enriched into knowledge graph
- **Result:** System doesn't learn from conversations, agents can't access conversational context

### The Solution

Implement automatic conversation→knowledge graph ingestion with:
- **Human↔Agent path** (70% traffic): Slack → PostgreSQL → Background extraction → Neo4j/Graphiti
- **Agent↔Agent path** (30% traffic): NATS → PostgreSQL → Background extraction → Neo4j/Graphiti
- **Redis caching** (critical): 60% latency reduction, 5x cost savings
- **5-tier degradation**: Prevent unbounded growth (filter, score, decay, archive, consolidate)

---

## Architecture Principles

### 1. Clean Separation of Concerns
- **Slack** = Human interface (commands, notifications, conversations)
- **NATS** = Agent backbone (fast, reliable agent↔agent messaging)
- **PostgreSQL** = Source of truth (all messages stored here first)
- **Neo4j/Graphiti** = Knowledge layer (extracted entities, relationships, patterns)
- **Redis** = Performance layer (caching, deduplication)

### 2. Realistic Performance Targets
- **Human response:** 2-3s typical (P50: 2s, P95: 3s, Max: 5s)
- **Agent messaging:** <20ms typical (P50: 10ms, P95: 20ms, Max: 50ms)
- **Background ingestion:** 10-20s typical (P50: 10s, P95: 20s, Max: 60s)

### 3. Scalability by Design
- **Horizontal scaling:** All components scale independently
- **Caching strategy:** Redis reduces load by 60-95% across the stack
- **Degradation strategy:** 5 tiers prevent unbounded growth
- **Storage architecture:** PostgreSQL primary storage (no migration planned)

---

## Final Tool Decisions

| Component | Tool | Rationale |
|-----------|------|-----------|
| **Human Interface** | Slack Bolt (Python) | Native to team workflow, rich UI, proven at scale |
| **Agent Communication** | NATS (agent↔agent only) | <10ms latency, pub/sub + request-reply, already in stack |
| **Primary Storage** | PostgreSQL | ACID guarantees, queryable, 90% implemented |
| **Knowledge Graph** | Neo4j + Graphiti | Temporal reasoning, entity relationships, patterns |
| **Caching** | Redis | 60% latency reduction, 5x cost savings, critical |
| **Background Jobs** | Temporal.io | Durable workflows, retry logic, observability |
| **Observability** | LangSmith + Grafana + Streamlit | Traces + infrastructure + custom dashboards |
| **Agent Orchestration** | LangGraph | Stateful workflows, already chosen for agents |

---

## Complete Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: INTERFACES                          │
├─────────────────────────────────────────────────────────────────┤
│  • Slack Bolt SDK (Human ↔ Agent conversations)                 │
│  • Apex REST API (Programmatic access, mobile apps)             │
└─────────────────────────────────────────────────────────────────┘
         ↓ (70% traffic)                       ↓ (30% traffic)
┌──────────────────────────┐         ┌────────────────────────────┐
│   HUMAN PATH             │         │   AGENT PATH               │
│                          │         │                            │
│  Slack Event             │         │  Oscar                     │
│         ↓                │         │    ↓                       │
│  ConversationService     │         │  NATS Pub (<10ms)          │
│         ↓                │         │    ↓                       │
│  Redis Check             │         │  Maya Subscriber           │
│  (conversation context)  │         │    ↓                       │
│         ↓                │         │  NATS Reply (<10ms)        │
│  PostgreSQL Write        │         │    ↓                       │
│  (messages table)        │         │  AgentInteractionService   │
│    Latency: 50-100ms     │         │    ↓                       │
│         ↓                │         │  PostgreSQL Write          │
│  QueryRouter             │         │  (agent_interactions)      │
│  (retrieve context)      │         │    Latency: 50-100ms       │
│    Latency: 200-800ms    │         │    ↓                       │
│         ↓                │         │  Temporal Queue            │
│  Claude API              │         │                            │
│  (generate response)     │         │                            │
│    Latency: 500-2000ms   │         │                            │
│         ↓                │         │                            │
│  PostgreSQL Write        │         │                            │
│  (assistant message)     │         │                            │
│         ↓                │         │                            │
│  Temporal Queue          │         │                            │
│  (background job)        │         │                            │
│                          │         │                            │
└──────────────────────────┘         └────────────────────────────┘
         ↓                                       ↓
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 2: BACKGROUND PROCESSING                      │
├─────────────────────────────────────────────────────────────────┤
│  Temporal Workflow: ConversationIngestionWorkflow                │
│                                                                  │
│  Activity 1: Fetch messages from PostgreSQL (50-100ms)          │
│         ↓                                                        │
│  Redis Check: Entities already extracted?                        │
│         ↓ (miss)                        ↓ (hit - skip)          │
│  Activity 2: Extract entities (LLM) ────┘                        │
│    • Claude API: 1-3s per message                                │
│    • Cost: $0.01-0.05 per message                                │
│    • Cache in Redis (1 hour TTL)                                 │
│         ↓                                                        │
│  Redis Check: User profile cached?                               │
│         ↓ (miss)                        ↓ (hit)                  │
│  Activity 3: Fetch user profile (100-500ms) ───┘                 │
│         ↓                                                        │
│  Activity 4: Calculate importance score                          │
│    • Recency (30% weight)                                        │
│    • Frequency (20% weight)                                      │
│    • Relevance (40% weight)                                      │
│    • Actionability (10% weight)                                  │
│         ↓                                                        │
│  Quality Filter: Should ingest?                                  │
│    • Too generic? (filter)                                       │
│    • Too short? (filter)                                         │
│    • Low actionability? (filter)                                 │
│    • Duplicate? (filter)                                         │
│         ↓ (50-70% pass)                                          │
│  Activity 5: Create Graphiti Episode                             │
│    • Write to Neo4j (entities, relationships)                    │
│    • Latency: 200-800ms                                          │
│         ↓                                                        │
│  Activity 6: Update message metadata                             │
│    • importance_score, retention_tier, archive_after_date        │
│    • PostgreSQL update: 50-200ms                                 │
│                                                                  │
│  Total: 2-13s per message (no backlog)                           │
│  Target: 10-20s P95 (with moderate backlog)                      │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│         LAYER 3: MEMORY LAYER (Knowledge Graph)                  │
├─────────────────────────────────────────────────────────────────┤
│  • Neo4j: Entities, relationships, graph traversal               │
│  • Graphiti: Temporal episodes, pattern detection                │
│  • PostgreSQL: Raw messages, metadata, importance scores         │
│  • Qdrant: Vector similarity search                              │
│  • Redis: Hot cache (conversation context, user profiles)        │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│       LAYER 4: OBSERVABILITY (Monitoring & Debugging)            │
├─────────────────────────────────────────────────────────────────┤
│  • LangSmith: Agent traces, LLM metrics, cost tracking           │
│  • Grafana: Infrastructure metrics (NATS, Redis, databases)      │
│  • Streamlit: Custom dashboards (conversation analytics)         │
│  • Slack: Alerts, notifications, human-in-the-loop               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Redis Caching Strategy (3 Layers)

### Layer 1: Conversation Context Caching ⭐ HIGHEST IMPACT

**Purpose:** Avoid fetching last N messages on every user request

**Cache Key:** `conversation:{conversation_uuid}:context`
**TTL:** 30 minutes (1800s)
**Hit Rate:** 95% (ongoing conversations)
**Performance Impact:** Saves 150-200ms per message

**Implementation:**
```python
# Check Redis first
context = await redis.get(f"conversation:{conv_id}:context")

if not context:
    # Cache miss - fetch from PostgreSQL
    context = await db.fetch_messages(conv_id, limit=20)  # 50-200ms
    await redis.setex(f"conversation:{conv_id}:context", 1800, json.dumps(context))

# Use cached context
return context  # <5ms if cached
```

**Metrics:**
- Latency reduction: 150-200ms → <5ms (97% faster)
- PostgreSQL load reduction: 95% fewer queries
- Cost: Minimal (20KB per conversation × 1000 active = 20MB)

### Layer 2: Entity Extraction Deduplication ⭐ HIGH IMPACT (COST)

**Purpose:** Prevent duplicate LLM API calls on retries or re-ingestion

**Cache Key:** `entities:{message_hash}`
**TTL:** 1 hour (3600s)
**Hit Rate:** 20-30% (retries, duplicates)
**Cost Impact:** Saves $300-1500/month

**Implementation:**
```python
message_hash = hashlib.sha256(message.encode()).hexdigest()
cache_key = f"entities:{message_hash}"

entities = await redis.get(cache_key)

if not entities:
    # Cache miss - call LLM (expensive)
    entities = await llm.extract_entities(message)  # $0.01-0.05, 1-3s
    await redis.setex(cache_key, 3600, json.dumps(entities))

return entities  # Free if cached
```

**Metrics:**
- Cost reduction: $0.01-0.05 per duplicate → $0 (100% savings on dupes)
- Estimated savings: $300-1500/month (based on 20-30% duplication rate)
- Latency reduction: 1-3s → <5ms on cache hits

### Layer 3: User Profile Caching ⭐ MEDIUM-HIGH IMPACT

**Purpose:** Avoid complex aggregation query on every importance calculation

**Cache Key:** `user:{user_id}:profile`
**TTL:** 1 hour (3600s)
**Hit Rate:** 90% (users have multiple conversations per hour)
**Performance Impact:** Saves 100-500ms per message

**Implementation:**
```python
cache_key = f"user:{user_id}:profile"
profile = await redis.get(cache_key)

if not profile:
    # Cache miss - expensive aggregation query
    profile = await db.fetch_user_profile(user_id)  # 100-500ms
    await redis.setex(cache_key, 3600, json.dumps(profile))

# Use for importance scoring
importance = calculate_importance(message, profile)  # <5ms if cached
```

**Metrics:**
- Latency reduction: 100-500ms → <5ms (95-99% faster)
- PostgreSQL load reduction: 90% fewer complex queries
- Enables real-time importance scoring without bottleneck

---

## 5-Tier Degradation Strategy

### Overview

**Goal:** Prevent unbounded knowledge graph growth while maintaining quality

**Without degradation:**
- 1000 conversations/day × 365 days = 365,000 episodes/year
- Neo4j instance cost: $200/month → $2000/month
- Query latency: <500ms → 2-5s

**With 5-tier degradation:**
- Hot storage (Neo4j): ~50,000 episodes (only recent + important)
- Query latency: <500ms maintained
- Neo4j cost: $200/month (10x savings)

---

### Tier 1: Pre-Ingestion Filtering (Block 30-50%)

**Filters low-quality messages BEFORE knowledge graph write**

```python
class MemoryQualityFilter:

    async def should_ingest(self, message: Message) -> tuple[bool, str]:
        # Filter 1: Too generic
        if message.content.lower().strip() in ["ok", "thanks", "got it", "sure"]:
            return False, "too_generic"

        # Filter 2: Too short
        if len(message.content.strip()) < 10:
            return False, "too_short"

        # Filter 3: Low actionability
        actionability = await self._calculate_actionability(message)
        if actionability < 0.3:
            return False, "low_actionability"

        # Filter 4: Duplicate (semantic similarity)
        if await self._is_semantic_duplicate(message):
            return False, "duplicate"

        return True, "passed_filters"
```

**Database tracking:**
```sql
ALTER TABLE messages ADD COLUMN ingestion_skipped BOOLEAN DEFAULT FALSE;
ALTER TABLE messages ADD COLUMN skip_reason VARCHAR(50);
```

**Metrics:**
- Messages blocked: 30-50%
- Storage saved: 150-200 GB/year (PostgreSQL + Neo4j)
- Processing cost saved: $1000-2000/year (LLM entity extraction)

---

### Tier 2: Importance Scoring (All Stored Messages)

**Multi-factor scoring for retrieval prioritization**

```python
importance = (
    recency_score * 0.3 +        # Exponential decay (half-life: 30 days)
    frequency_score * 0.2 +      # Access count (how often retrieved)
    relevance_score * 0.4 +      # Semantic similarity to user profile
    actionability_score * 0.1    # Preference > fact > chit-chat
)
```

**Recency decay formula:**
```python
def calculate_recency(created_at: datetime) -> float:
    days_ago = (datetime.utcnow() - created_at).days
    half_life_days = 30
    decay_factor = 0.5 ** (days_ago / half_life_days)
    return decay_factor

# Example:
# Day 0:   importance = 0.8
# Day 30:  importance = 0.4 (decayed to 50%)
# Day 90:  importance = 0.1 (candidate for archival)
```

**Database schema:**
```sql
ALTER TABLE messages ADD COLUMN importance_score FLOAT DEFAULT 0.5;
ALTER TABLE messages ADD COLUMN last_accessed_at TIMESTAMP;
ALTER TABLE messages ADD COLUMN access_count INTEGER DEFAULT 0;
```

---

### Tier 3: Memory Decay (Daily Cron Job)

**Automatic importance score updates**

```python
@workflow.defn
class MemoryDecayWorkflow:
    """Runs daily at 2 AM UTC"""

    @workflow.run
    async def run(self, batch_size: int = 1000) -> dict:
        scorer = MemoryImportanceScorer()
        updated_count = 0

        # Process messages in batches
        offset = 0
        while True:
            messages = await workflow.execute_activity(
                fetch_messages_batch,
                args=[offset, batch_size],
                start_to_close_timeout=timedelta(seconds=60)
            )

            if not messages:
                break

            # Recalculate importance for batch
            await workflow.execute_activity(
                recalculate_importance_batch,
                args=[messages],
                start_to_close_timeout=timedelta(minutes=5)
            )

            updated_count += len(messages)
            offset += batch_size

        return {"updated_count": updated_count}
```

**Schedule:** Daily cron via Temporal
**Duration:** 5-10 minutes for 10,000 messages
**Result:** Old conversations naturally fade away

---

### Tier 4: Retention Policy (Full Implementation - Phase 3)

**Status:** ✅ Included in Phase 3 full implementation
**Timeline:** Phase 3, Days 8-10 (Week 2)
**Storage Solution:** ✅ Google Cloud Storage (GCS) - See ADR-001

**Goal:** Tiered retention based on message importance (ephemeral, normal, important, critical)

**Key Features:**
- Automatic archival to **Google Cloud Storage (GCS)** after retention period
- 4 retention tiers: 7 days (ephemeral) → 1 year (important) → forever (critical)
- Storage tier optimization: Hot (Neo4j) → Warm (PostgreSQL) → Cold (GCS)

**GCS Configuration:**
- Storage class: **Nearline** ($0.012/GB/month)
- Lifecycle policies: Auto-transition to Coldline (90 days) → Archive (365 days)
- Bucket: `apex-memory-archive`
- Python SDK: `google-cloud-storage`

**Estimated Cost Savings:**
- Neo4j: $200/month (vs $2000/month without archival)
- GCS cost: <$1/year (even at scale)
- Total savings: $2,250/month ($27,000/year)

**Architecture Decision:** See `research/architecture-decisions/ADR-001-cold-storage-gcs.md`

---

### Tier 5: Duplicate Fact Consolidation (Full Implementation - Phase 3)

**Status:** ✅ Included in Phase 3 full implementation
**Timeline:** Phase 3, Days 11-13 (Week 3)

**Goal:** Detect and merge redundant information using semantic similarity

**Problem Example:**
- User mentions "ACME Corp prefers aisle seats" in 10 conversations
- Without consolidation: 10 separate facts in knowledge graph
- With consolidation: 1 fact with confidence=10, last_mentioned=recent

**Key Features:**
- Semantic similarity detection (vector.similarity > 0.9)
- Automatic fact merging with confidence scoring
- Weekly consolidation workflow (Temporal.io)

**Estimated Benefits:**
- Redundancy reduction: 20-40% of facts are duplicates
- Storage saved: 50-100 GB/year (Neo4j)
- Query performance: 20-30% faster (fewer facts to traverse)

**Implementation Details:** See `research/future-enhancements/duplicate-consolidation.md`

---

## Multi-Agent Namespacing Strategy

### Overview

The Conversational Memory Integration supports **multiple specialized agents** sharing the same knowledge infrastructure with logical separation. This "one knowledge base, multiple specialized access patterns" design enables clean agent-specific organization while maintaining cross-agent insights.

**Design Philosophy:** Each agent (Oscar, Sarah, Maya) has its own namespace across all databases, allowing:
- **Agent-specific queries** - Fast filtering without cross-contamination
- **Cross-agent insights** - Query multiple namespaces when needed
- **Dynamic agent addition** - Add new agents without code changes (15-30 minutes)
- **Clean monitoring** - Per-agent metrics and performance tracking

**Key Benefits:**
- **Performance:** Smaller collections = faster queries (agent-specific collections)
- **Scalability:** Each agent's data scales independently
- **Monitoring:** Per-agent cache hit rates, query latency, cost tracking
- **Future-ready:** Smooth transition to Phase 2 (multi-agent specialization)

**Reference:** See `agent-registry.md` for complete agent documentation and `research/future-enhancements/fluid-mind-patterns-to-adopt.md` for implementation patterns.

---

### Known Agents

**Active Agents (Phase 1):**
- **Oscar** (`oscar`) - Fleet Manager - Trucks, maintenance, routes, drivers
- **System** (`system`) - Default agent for shared operations and cross-agent knowledge

**Planned Agents (Phase 2 - Weeks 9-14):**
- **Sarah** (`sarah`) - CFO / Finance Agent - Invoices, costs, vendor analysis
- **Maya** (`maya`) - Sales / CRM Agent - Customers, quotes, pricing, deals

**Agent Selection Logic:**
```python
# Conversation determines agent_id
agent_id = conversation.agent_id or "system"  # Default to "system"

# All services use agent_id
cache = CacheService(redis, agent_id=agent_id)
vector = VectorService(qdrant, agent_id=agent_id)
graph = GraphService(neo4j, agent_id=agent_id)
```

---

### Redis Namespace Pattern

**Purpose:** Prevent cache collisions when adding multiple agents

**Pattern:** `{agent_id}:resource:id:detail`

**Implementation:**
```python
class CacheService:
    def __init__(self, redis_client, agent_id: str = "system"):
        self.redis = redis_client
        self.agent_id = agent_id  # ← Agent namespace

    async def cache_conversation_context(
        self,
        conversation_id: UUID,
        context: dict,
        ttl: int = 1800
    ):
        # Agent-namespaced key
        key = f"{self.agent_id}:conversation:{conversation_id}:context"
        await self.redis.setex(key, ttl, json.dumps(context))

    async def cache_entity(self, entity_id: UUID, entity: dict, ttl: int = 3600):
        # Shared knowledge (no agent prefix)
        key = f"shared:entity:{entity_id}"
        await self.redis.setex(key, ttl, json.dumps(entity))
```

**Example Keys:**
- `oscar:conversation:123:context` - Oscar's conversation cache
- `sarah:invoice:456:analysis` - Sarah's invoice analysis
- `maya:quote:789:pricing` - Maya's quote pricing
- `shared:entity:999:metadata` - Cross-agent shared entity

**Benefits:**
- **Zero performance impact** - Redis handles namespaces natively
- **Easier debugging** - Know which agent created which cache entry
- **Cleaner eviction** - Expire agent caches independently
- **Prevents collisions** - Oscar's context ≠ Sarah's context

**Effort:** 1-2 hours (minimal code change, maximum future-proofing)

---

### Qdrant Agent Collections

**Purpose:** Separate vector collections per agent for faster queries

**Collection Mapping:**
```python
AGENT_COLLECTIONS = {
    "oscar": "oscar_fleet_knowledge",
    "sarah": "sarah_financial_knowledge",
    "maya": "maya_sales_knowledge",
    "system": "shared_documents"
}
```

**Implementation:**
```python
class VectorService:
    def __init__(self, qdrant_client, agent_id: str = "system"):
        self.qdrant = qdrant_client
        self.agent_id = agent_id
        self.collection_name = AGENT_COLLECTIONS.get(agent_id, "shared_documents")

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
            collection = AGENT_COLLECTIONS.get(agent_id)
            if collection:
                agent_results = await self.qdrant.search(
                    collection_name=collection,
                    query_vector=query_vector,
                    limit=limit_per_agent
                )
                results.extend(agent_results)
        return results
```

**Benefits:**
- **Faster queries** - Smaller collections = faster vector search
- **Better organization** - Oscar's fleet knowledge ≠ Sarah's financial knowledge
- **Better monitoring** - Per-collection metrics on search performance
- **Easier to scale** - Optimize collection configurations per agent

**Collection Creation:**
```python
# One-time setup (no code changes for new agents)
await qdrant.create_collection(
    collection_name="oscar_fleet_knowledge",
    vectors_config={"size": 1536, "distance": "Cosine"}
)
```

**Effort:** 4-6 hours (straightforward implementation, significant benefits)

---

### PostgreSQL Schema Preparation (Phase 2)

**Purpose:** Prepare agent-specific schemas for Phase 2 (don't use until multi-agent activation)

**Schema Strategy:**
```sql
-- Core schema (shared tables) - USE NOW
CREATE SCHEMA IF NOT EXISTS core;
SET search_path TO core;
CREATE TABLE messages (...);  -- All conversations
CREATE TABLE entities (...);  -- All entities
CREATE TABLE conversations (...);  -- All conversations

-- Agent-specific schemas - PREPARE BUT DON'T USE YET
CREATE SCHEMA IF NOT EXISTS oscar;
CREATE SCHEMA IF NOT EXISTS sarah;
CREATE SCHEMA IF NOT EXISTS maya;

-- Phase 2: Agent-specific tables (when needed)
-- CREATE TABLE oscar.fleet_metrics (...);
-- CREATE TABLE sarah.financial_patterns (...);
-- CREATE TABLE maya.sales_quotes (...);
```

**Implementation (Phase 1):**
```python
class DatabaseService:
    AGENT_SCHEMAS = {
        "oscar": "oscar",
        "sarah": "sarah",
        "maya": "maya",
        "system": "core"
    }

    def __init__(self, db_connection, agent_id: str = "system"):
        self.db = db_connection
        self.agent_id = agent_id
        self.schema = self.AGENT_SCHEMAS.get(agent_id, "core")

    async def write_message(self, message: dict):
        """Write to core schema (all messages visible)"""
        query = """
        INSERT INTO core.messages (uuid, content, agent_id, created_at)
        VALUES ($1, $2, $3, NOW())
        """
        return await self.db.execute(
            query,
            message['uuid'],
            message['content'],
            self.agent_id
        )
```

**Phase 1 Status:**
- ✅ Create schemas (preparation only)
- ✅ All tables in `core` schema
- ❌ Don't use agent-specific schemas yet (Phase 2)

**Phase 2 Activation:**
- Add agent-specific tables (fleet_metrics, financial_patterns, sales_quotes)
- Update services to write to agent schemas
- Maintain core schema for shared tables

**Benefits:**
- **Clean isolation** - Oscar's fleet data ≠ Sarah's financial data
- **Easier RBAC** - Grant schema-level permissions
- **Better performance** - Smaller tables = faster queries
- **Compliance-friendly** - Agent data isolated for audits

**Effort:** 2-4 hours (schema creation only, no table migrations needed)

---

### Neo4j Label-Based Separation (Phase 2)

**Purpose:** Add agent-specific labels to Neo4j nodes for efficient filtering

**Label Strategy:**
```cypher
-- Entity with agent-specific label
CREATE (e:Entity:Oscar_Domain {
  uuid: '123',
  name: 'Truck 247',
  type: 'equipment',
  agent_id: 'oscar',
  created_at: datetime()
})

-- Efficient agent-specific query
MATCH (e:Entity:Oscar_Domain)
RETURN e

-- Cross-domain query (when needed)
MATCH (e:Entity)
WHERE e:Oscar_Domain OR e:Sarah_Domain
RETURN e
```

**Implementation (Phase 2):**
```python
class GraphService:
    AGENT_LABELS = {
        "oscar": "Oscar_Domain",
        "sarah": "Sarah_Domain",
        "maya": "Maya_Domain",
        "system": "Shared"
    }

    def __init__(self, neo4j_driver, agent_id: str = "system"):
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
```

**Benefits:**
- **Efficient queries** - Single-label filter vs property filter
- **Cross-domain possible** - Query multiple labels when needed
- **Better performance** - Neo4j optimizes label filters
- **Cleaner visualization** - Color-code by agent domain

**Phase 1 Status:** Defer to Phase 2 (requires schema migration)

**Effort:** 4-6 hours (Phase 2 implementation)

---

### Adding New Agents (Dynamic Pattern)

**Process:** 15-30 minutes per new agent (no code changes required)

**Step 1: Update Agent Registry**
- Add agent definition to `agent-registry.md`
- Document domain, responsibilities, data scope

**Step 2: Create Database Namespaces**

**Redis:** No action needed (dynamic namespacing)
```python
# Just pass new agent_id - works instantly
cache = CacheService(redis, agent_id="alex")
```

**Qdrant:** Create collection
```python
await qdrant.create_collection(
    collection_name="alex_domain_knowledge",
    vectors_config={"size": 1536, "distance": "Cosine"}
)
```

**PostgreSQL:** Create schema (Phase 2 only)
```sql
CREATE SCHEMA IF NOT EXISTS alex;
```

**Neo4j:** Use label (Phase 2 only)
```cypher
CREATE (e:Entity:Alex_Domain {name: "Example"})
```

**Step 3: Update Configuration**
```python
# File: apex-memory-system/config/agent_registry.py
AGENT_COLLECTIONS = {
    "oscar": "oscar_fleet_knowledge",
    "sarah": "sarah_financial_knowledge",
    "maya": "maya_sales_knowledge",
    "alex": "alex_domain_knowledge",  # ← Add here
    "system": "shared_documents"
}
```

**Total Time:** 15-30 minutes (no application restarts needed)

---

### Cross-Agent Interaction Patterns

**Single-Agent Operation (Most Common):**
```python
# Oscar receives message about truck maintenance
agent_id = "oscar"

# Redis cache (Oscar namespace)
cache = CacheService(redis, agent_id=agent_id)
await cache.cache_conversation_context(conv_id, context)
# Key: oscar:conversation:123:context

# Qdrant search (Oscar collection)
vector = VectorService(qdrant, agent_id=agent_id)
results = await vector.search(query_vector)
# Searches: oscar_fleet_knowledge
```

**Cross-Agent Operation (Advanced - Phase 2):**
```python
# Query: "How do maintenance costs (Oscar) affect our margins (Sarah)?"

# Query Oscar's fleet data
oscar_service = VectorService(qdrant, agent_id="oscar")
fleet_data = await oscar_service.search(query_vector)

# Query Sarah's financial data
sarah_service = VectorService(qdrant, agent_id="sarah")
cost_data = await sarah_service.search(query_vector)

# Synthesize cross-domain insight
insight = synthesize_cross_domain(fleet_data, cost_data)
```

---

### Monitoring & Metrics (Per-Agent)

**Grafana Dashboard Additions:**
```python
# Cache hit rates per agent
cache_hit_rate_oscar = redis.get("metrics:oscar:cache_hit_rate")
cache_hit_rate_sarah = redis.get("metrics:sarah:cache_hit_rate")

# Query latency per agent
query_latency_oscar = prometheus.histogram(
    "query_latency",
    labels={"agent": "oscar"}
)
query_latency_sarah = prometheus.histogram(
    "query_latency",
    labels={"agent": "sarah"}
)

# Vector search performance per collection
vector_search_oscar = qdrant.get_collection_metrics("oscar_fleet_knowledge")
vector_search_sarah = qdrant.get_collection_metrics("sarah_financial_knowledge")
```

**Dashboard Panels:**
- Per-agent cache hit rates (Oscar: 95%, Sarah: 92%, Maya: 88%)
- Per-agent query latency (P50/P95)
- Per-collection vector search performance
- Cross-agent query frequency
- Cost per agent (LLM API usage)

---

### Timeline Impact

**Phase 1 (Weeks 1-8): Low-Complexity Patterns**
- ✅ Redis namespaces: +1-2 hours
- ✅ Qdrant collections: +4-6 hours
- ⚠️ PostgreSQL schema prep: +2-4 hours

**Total Phase 1 Impact:** +1 week → 7-9 weeks (vs original 6-8 weeks)

**Phase 2 (Weeks 9-14): Multi-Agent Specialization**
- ✅ Activate PostgreSQL schemas
- ✅ Add Neo4j agent labels
- ✅ Implement cross-agent query capabilities
- ✅ Add agent identity routing to query router

**Benefit:** Smooth transition to multi-agent architecture with zero rework.

---

## Storage Architecture: PostgreSQL Primary

### Finalized Decision ✅

**Architecture:**
```
Message → PostgreSQL → Temporal → Graphiti
```

**Why PostgreSQL primary works:**
- **90% implemented** - conversations table exists, API functional
- **ACID guarantees** - Reliable, transactional integrity
- **Fast to ship** - 2-3 weeks to production (no migration needed)
- **Query capable** - Full SQL for analytics and debugging
- **Proven at scale** - Handles 1,000+ messages/hour easily

**NATS role:**
- Agent↔agent messaging ONLY (30% of traffic)
- High-speed communication (<20ms latency)
- Pub/sub pattern for agent coordination
- NOT used for primary storage

### Future Considerations (Optional)

**If traffic exceeds 10,000 messages/hour sustained:**
- Consider event sourcing migration (PostgreSQL → NATS JetStream)
- See `research/future-enhancements/event-sourcing-migration.md` for details
- Not planned for MVP or Phase 1 implementation

**Current capacity:**
- PostgreSQL handles 10,000+ messages/hour with proper indexing
- Redis caching reduces load by 60-95%
- Horizontal scaling available if needed (read replicas)

---

## Latency Targets (Realistic SLAs)

Based on industry benchmarks and our architecture:

| Metric | Target (P50) | Target (P95) | Max Acceptable | Industry Benchmark |
|--------|--------------|--------------|----------------|--------------------|
| **Slack response** | 2s | 3s | 5s | ChatGPT: 1-5s, Copilot: 1-3s |
| **Agent↔Agent (NATS)** | 10ms | 20ms | 50ms | Uber: <10ms, Netflix: <5ms |
| **Background ingestion** | 10s | 20s | 60s | Zep: 5-15s, Mem0: 3-10s |
| **Cache hit (Redis)** | <5ms | 10ms | 50ms | Industry: <10ms |
| **Vector search (Qdrant)** | 200ms | 500ms | 1s | Typical: 100-500ms |
| **Graph query (Neo4j)** | 300ms | 800ms | 2s | Typical: 200-1000ms |

**P50 = 50th percentile (median), P95 = 95th percentile**

### Breakdown: Slack Response Time (2-3s typical)

```
Component                        Latency        Notes
────────────────────────────────────────────────────────────
Slack event received             +0ms
Redis check (conversation)       +5ms           95% cache hit
PostgreSQL write (user msg)      +50-100ms
QueryRouter context retrieval    +200-800ms     Varies by cache
  - Redis (cache hit):           <10ms          90% of time
  - Qdrant (vector search):      100-300ms      Fresh queries
  - Neo4j (graph query):         100-500ms      Complex queries
Claude API call                  +500-2000ms    Depends on length
PostgreSQL write (assistant)     +50-100ms
Slack message send               +50-200ms
────────────────────────────────────────────────────────────
TOTAL (P50 - cache hit):         ~1500ms (1.5s) ✅ Good UX
TOTAL (P95 - cache miss):        ~3000ms (3s)   ✅ Acceptable
TOTAL (Max - complex query):     ~5000ms (5s)   ⚠️ Slow but rare
```

**Optimization opportunities:**
1. **Streaming responses:** Show Claude output as it generates (perceived latency 10x faster)
2. **Aggressive caching:** Pre-warm caches for frequent users/entities
3. **Async ingestion:** Don't wait for Temporal queue (shave 50-100ms)

---

## Scalability Analysis

### Conversation Volume (Target: 1000/hour sustained)

**Without Redis:**
- PostgreSQL: 1000 queries/hour × 100ms = 100s query time/hour
- QueryRouter: 1000 × 500ms = 500s retrieval/hour
- Bottleneck: QueryRouter (Neo4j/Qdrant under load)

**With Redis (95% cache hit):**
- PostgreSQL: 50 queries/hour × 100ms = 5s query time/hour (20x reduction)
- QueryRouter: 50 × 500ms = 25s retrieval/hour (20x reduction)
- Bottleneck: Claude API rate limits (not system architecture)

**Scaling strategy:**
- **Horizontal:** Add more API servers (stateless, easy to scale)
- **Redis:** Single instance handles 100K ops/sec (plenty of headroom)
- **PostgreSQL:** Read replicas for QueryRouter (if needed)

---

### Agent↔Agent Messages (Target: 10,000/min = 166/sec)

**NATS Performance:**
- Single instance: 1M+ messages/sec
- Latency: <1ms pub/sub
- Your target: 166/sec (0.016% of capacity)

**Bottleneck:** Not NATS, but background ingestion keeping up

**Scaling strategy:**
- **Temporal workers:** Add more worker instances (horizontal scaling)
- **Batch processing:** Extract entities for 10 messages in one LLM call
- **Priority queue:** Prioritize user↔agent over agent↔agent

---

### Background Ingestion (Target: 1000 msgs/hour = 16.7/min)

**Single worker capacity:**
- Entity extraction: 1-3s/message
- Max throughput: 20-60 messages/minute (single worker)
- Your target: 16.7/min (easily handled)

**During spikes (10x = 10,000 msgs/hour = 166/min):**
- Single worker: Would fall behind (~3 hour backlog)
- 5 workers: 100-300 messages/minute (comfortable)
- 10 workers: 200-600 messages/minute (plenty of headroom)

**Scaling strategy:**
- **Horizontal:** Temporal workers auto-scale based on queue depth
- **Batching:** Process 5-10 messages per LLM call (5x throughput)
- **Priority:** User-facing messages processed first

---

## Security & Privacy Considerations

### Data Retention Compliance

**Support for GDPR/CCPA:**
- User data deletion: Cascade delete from all databases
- Right to access: Export all user conversations + episodes
- Retention limits: Automatic archival enforces data minimization

**Implementation:**
```python
async def delete_user_data(user_id: UUID):
    """GDPR-compliant user data deletion"""

    # 1. Delete from PostgreSQL
    await db.execute("DELETE FROM messages WHERE user_id = ?", user_id)
    await db.execute("DELETE FROM conversations WHERE user_id = ?", user_id)

    # 2. Delete from Neo4j
    await neo4j.query(
        "MATCH (e:Episode)-[:BELONGS_TO]->(:User {id: $user_id}) DETACH DELETE e",
        user_id=user_id
    )

    # 3. Delete from Qdrant
    await qdrant.delete(filter={"user_id": user_id})

    # 4. Clear from Redis
    await redis.delete(f"user:{user_id}:*")

    # 5. Delete from GCS archives
    await gcs.delete_user_archives(user_id)
```

### Sensitive Information Handling

**Filter before storage:**
- Credit card numbers (regex: `\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b`)
- Social Security Numbers (regex: `\b\d{3}-\d{2}-\d{4}\b`)
- API keys/tokens (regex: `(api[_-]?key|token)[\"']?\\s*[:=]\\s*[\"']?([a-zA-Z0-9_-]+)`)

**Redaction policy:**
```python
def redact_sensitive_info(message: str) -> str:
    """Redact PII before storage"""

    # Credit cards
    message = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[REDACTED_CC]', message)

    # SSNs
    message = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', message)

    # API keys
    message = re.sub(
        r'(api[_-]?key|token)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)',
        r'\1=[REDACTED]',
        message,
        flags=re.IGNORECASE
    )

    return message
```

---

## Monitoring & Observability

### Key Metrics to Track

**Performance Metrics:**
- Slack response latency (P50, P95, P99)
- NATS pub/sub latency (P50, P95, Max)
- Background ingestion throughput (messages/min)
- Redis cache hit rate (%)
- PostgreSQL query latency
- Neo4j query latency
- Qdrant query latency

**Quality Metrics:**
- Entity extraction accuracy (% correct entities)
- Importance scoring distribution (avg, P50, P95)
- Quality filter effectiveness (% blocked)
- Duplicate detection rate (% duplicates found)
- Consolidation effectiveness (% facts merged)

**Cost Metrics:**
- LLM API costs ($/1000 messages)
- Redis memory usage (GB)
- PostgreSQL storage growth (GB/day)
- Neo4j storage growth (GB/day)
- GCS archival costs ($/month)

**Business Metrics:**
- Knowledge graph growth (entities/day, relationships/day)
- User engagement (conversations/user/day)
- Agent utilization (agent interactions/day)
- Human escalation rate (% agent requests requiring human)

### Alerting Strategy

**Critical Alerts (Page on-call):**
- Slack response latency P95 > 5s (sustained 5 min)
- Background ingestion backlog > 10,000 messages
- Redis cache hit rate < 70%
- PostgreSQL/Neo4j down
- NATS cluster unhealthy

**Warning Alerts (Slack notification):**
- LLM API costs > $500/day
- Entity extraction accuracy < 80%
- Quality filter blocking > 60% (too aggressive)
- Duplicate detection rate > 50% (something wrong upstream)

---

## Success Metrics (Phase-by-Phase)

### Phase 2: Core Feedback Loop
- ✅ 100% of conversations auto-queued for ingestion
- ✅ 85%+ entity extraction accuracy
- ✅ <100ms latency increase for Slack responses
- ✅ Background ingestion completes within 20s (P95)
- ✅ All 20 tests passing

### Phase 3: Memory Quality & Importance
- ✅ 30-50% of low-value messages filtered
- ✅ Importance scores calculated for 100% of messages
- ✅ Daily decay workflow runs successfully
- ✅ All 15 tests passing

### Phase 4: Agent↔Agent Communication
- ✅ 100% of agent interactions logged
- ✅ <20ms agent messaging latency (P95)
- ✅ Knowledge graph enriched from agent collaborations
- ✅ All 15 tests passing

### Phase 5: Proactive Features
- ✅ Proactive suggestions relevant >80% of the time
- ✅ Memory consolidation reduces redundancy by 20-30%
- ✅ Pattern detection identifies 5+ recurring patterns/user
- ✅ All 15 tests passing

### Phase 6: Production Validation
- ✅ 156 Enhanced Saga tests pass (100% pass rate)
- ✅ Load tests: 10+ concurrent users, 1000+ messages/hour
- ✅ Cost: <$0.05 per conversation (including LLM)
- ✅ Neo4j storage: <100 GB (with archival)
- ✅ Redis: <2 GB memory usage
- ✅ User feedback: Positive on suggestion relevance

---

## Risk Mitigation

### Technical Risks

**Risk: Performance degradation under load**
- **Mitigation:** Redis caching (95% load reduction), horizontal scaling
- **Rollback:** Disable background ingestion (feature flag)

**Risk: Entity extraction inaccuracy**
- **Mitigation:** Manual validation dataset, quality filters, consolidation
- **Fallback:** Lower importance threshold, add manual review

**Risk: LLM API cost overruns**
- **Mitigation:** Redis deduplication (5x savings), quality filters (30-50% reduction)
- **Monitoring:** Daily cost alerts, per-message budget tracking

**Risk: Database performance**
- **Mitigation:** Proper indexing, Redis caching, read replicas
- **Monitoring:** Query latency dashboards, slow query alerts

### Operational Risks

**Risk: Breaking changes (regression)**
- **Mitigation:** Enhanced Saga baseline (156 tests), feature flags
- **Rollback:** Alembic migration rollback, disable flags

**Risk: Data quality issues**
- **Mitigation:** Quality filters, consolidation, manual review tools
- **Monitoring:** Quality metric dashboards, anomaly detection

**Risk: Team knowledge gap (NATS, event sourcing)**
- **Mitigation:** Start simple (PostgreSQL), migrate later when ready
- **Training:** Documentation, runbooks, team workshops

---

## Conclusion

This architecture provides:
- ✅ **Clean separation of concerns** (Slack, NATS, PostgreSQL, Neo4j, Redis each have clear roles)
- ✅ **Realistic performance targets** (based on industry benchmarks)
- ✅ **Horizontal scalability** (all components scale independently)
- ✅ **Cost optimization** (Redis + degradation = 10x savings)
- ✅ **Migration path** (PostgreSQL → Event Sourcing when ready)
- ✅ **Production readiness** (monitoring, alerting, security, rollback plans)

**Next step:** Begin Phase 1 (Research & Documentation) followed by Phase 2 (Core Feedback Loop with Redis).

---

**Architecture Finalized:** 2025-11-14
**Status:** Ready for Implementation
**Timeline:** 6-8 weeks to completion
