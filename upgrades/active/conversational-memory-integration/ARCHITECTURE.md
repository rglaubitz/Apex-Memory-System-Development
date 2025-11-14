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
- **Migration path:** PostgreSQL → Event Sourcing (NATS JetStream) when ready

---

## Final Tool Decisions

| Component | Tool | Rationale |
|-----------|------|-----------|
| **Human Interface** | Slack Bolt (Python) | Native to team workflow, rich UI, proven at scale |
| **Agent Communication** | NATS (agent↔agent only) | <10ms latency, pub/sub + request-reply, already in stack |
| **Primary Storage** | PostgreSQL | ACID guarantees, queryable, 90% implemented |
| **Event Streaming** | NATS JetStream (Phase 2) | Migration path for event sourcing when needed |
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

### Tier 4: Retention Policy (Automatic Archival) ⭐ NEW

**Tiered retention based on message importance**

```python
RETENTION_TIERS = {
    "critical": None,          # Keep forever (user preferences, key facts)
    "important": 365,          # 1 year (valuable conversations)
    "normal": 90,              # 3 months (typical interactions)
    "ephemeral": 7             # 1 week (chit-chat, status checks)
}

def classify_message(message: Message) -> str:
    # Critical: User preferences, important entities
    if contains_preference(message) or mentions_key_entity(message):
        return "critical"

    # Important: Task assignments, decisions, approvals
    if is_task(message) or is_decision(message):
        return "important"

    # Ephemeral: Status checks, greetings
    if is_status_check(message) or is_greeting(message):
        return "ephemeral"

    # Normal: Everything else
    return "normal"
```

**Database schema:**
```sql
ALTER TABLE messages ADD COLUMN retention_tier VARCHAR(20) DEFAULT 'normal';
ALTER TABLE messages ADD COLUMN archive_after_date TIMESTAMP;

-- Index for archival job
CREATE INDEX idx_messages_archive ON messages(archive_after_date)
WHERE archive_after_date IS NOT NULL AND archived = FALSE;
```

**Archival workflow (weekly cron):**
```python
@workflow.defn
class ArchivalWorkflow:
    """Runs weekly, moves old messages to cold storage"""

    @workflow.run
    async def run(self) -> dict:
        # Find messages past archive_after_date
        messages = await workflow.execute_activity(
            fetch_archival_candidates,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Move to S3 or archive table
        await workflow.execute_activity(
            archive_messages_to_s3,
            args=[messages],
            start_to_close_timeout=timedelta(minutes=30)
        )

        # Mark as archived in PostgreSQL
        await workflow.execute_activity(
            mark_messages_archived,
            args=[message_ids],
            start_to_close_timeout=timedelta(minutes=5)
        )

        return {
            "archived_count": len(messages),
            "cold_storage_bytes": calculate_size(messages)
        }
```

**Storage tiers:**
- **Hot (Neo4j):** Last 90 days + all critical (50,000 episodes)
- **Warm (PostgreSQL):** Last 365 days (200,000 episodes)
- **Cold (S3):** Everything older (unlimited, $0.023/GB/month)

**Cost impact:**
- Neo4j: $200/month (vs $2000/month without archival)
- S3: $50/month (vs $500/month PostgreSQL)
- Total savings: $2250/month ($27,000/year)

---

### Tier 5: Duplicate Fact Consolidation ⭐ NEW

**Detect and merge redundant information**

**Problem:**
- User says "ACME Corp prefers aisle seats" in 10 different conversations
- Without consolidation: 10 separate facts in knowledge graph
- With consolidation: 1 fact with confidence=10, last_mentioned=recent

**Implementation:**
```python
class DuplicateFactDetector:

    async def detect_duplicates(self, new_episode: Episode) -> list[Episode]:
        """Find existing episodes with same semantic meaning"""

        # Extract facts from new episode
        new_facts = await self.extract_facts(new_episode)

        # Query knowledge graph for similar facts (semantic similarity > 0.9)
        for fact in new_facts:
            existing = await self.neo4j.query(
                """
                MATCH (e:Episode)-[:CONTAINS]->(f:Fact)
                WHERE vector.similarity(f.embedding, $embedding) > 0.9
                AND f.entity = $entity
                RETURN e, f
                ORDER BY f.confidence DESC
                LIMIT 1
                """,
                embedding=fact.embedding,
                entity=fact.entity
            )

            if existing:
                yield (fact, existing)

    async def consolidate_or_skip(self, new_episode, duplicates):
        """Decide: skip new episode or update existing fact"""

        if duplicates:
            # Update existing fact's confidence and recency
            for new_fact, existing_fact in duplicates:
                await self.neo4j.query(
                    """
                    MATCH (f:Fact {uuid: $uuid})
                    SET f.confidence = f.confidence + 1,
                        f.last_mentioned = $now,
                        f.mention_count = f.mention_count + 1
                    """,
                    uuid=existing_fact.uuid,
                    now=datetime.utcnow()
                )

            # Skip creating new episode (redundant)
            await self.db.update_message(
                message_uuid=new_episode.message_uuid,
                ingestion_skipped=True,
                skip_reason="duplicate_fact_consolidated"
            )

            return "consolidated"
        else:
            # Create new episode (novel information)
            await self.graphiti.create_episode(new_episode)
            return "created"
```

**Consolidation workflow (weekly cron):**
```python
@workflow.defn
class FactConsolidationWorkflow:
    """Runs weekly, identifies and merges duplicate facts"""

    @workflow.run
    async def run(self) -> dict:
        # Find fact clusters (semantic similarity > 0.9)
        clusters = await workflow.execute_activity(
            identify_fact_clusters,
            start_to_close_timeout=timedelta(minutes=30)
        )

        consolidated_count = 0
        for cluster in clusters:
            # Merge cluster into single canonical fact
            await workflow.execute_activity(
                consolidate_fact_cluster,
                args=[cluster],
                start_to_close_timeout=timedelta(minutes=5)
            )
            consolidated_count += len(cluster) - 1

        return {
            "clusters_found": len(clusters),
            "facts_consolidated": consolidated_count
        }
```

**Metrics:**
- Redundancy reduction: 20-40% of facts are duplicates
- Storage saved: 50-100 GB/year (Neo4j)
- Query performance: 20-30% faster (fewer facts to traverse)

---

## Migration Path: PostgreSQL → Event Sourcing

### Phase 1 (Weeks 1-8): PostgreSQL Primary ✅

**Current architecture - ship this first:**
```
Message → PostgreSQL → Temporal → Graphiti
```

**Pros:**
- 90% implemented (conversations table exists)
- ACID guarantees (reliable)
- Fast to ship (2-3 weeks)

**Cons:**
- Two-stage storage (write twice)
- Limited replay capability

---

### Phase 2 (Months 3-6): Hybrid (Add NATS Publisher)

**Add event streaming without breaking existing system:**
```
Message → PostgreSQL → (NEW) NATS Publisher Job
                ↓              ↓
            Temporal     NATS JetStream
                                ↓
                        (Optional Analytics Consumers)
```

**Benefits:**
- Event streaming for analytics
- Replay capability
- No breaking changes

**Implementation:**
```python
@workflow.defn
class NATSPublisherWorkflow:
    """Publishes PostgreSQL changes to NATS JetStream"""

    @workflow.run
    async def run(self, message_uuid: UUID) -> dict:
        # Fetch message from PostgreSQL
        message = await workflow.execute_activity(
            fetch_message,
            args=[message_uuid],
            start_to_close_timeout=timedelta(seconds=30)
        )

        # Publish to NATS JetStream (persistent)
        await workflow.execute_activity(
            publish_to_nats_jetstream,
            args=[message],
            start_to_close_timeout=timedelta(seconds=30)
        )

        return {"published": True}
```

---

### Phase 3 (Months 6-12): Event Sourcing Primary (Optional)

**Migrate to NATS JetStream as primary source:**
```
Message → NATS JetStream (primary)
               ↓              ↓              ↓
       PostgreSQL      Graphiti          Analytics
       (Consumer)      (Consumer)        (Consumer)
```

**Benefits:**
- Complete event sourcing
- Horizontal scaling
- Full replay capability
- Decoupled consumers

**Cons:**
- Complex setup (clustering, retention)
- Operational overhead (monitoring, rebalancing)
- Learning curve

**Decision point:** Only migrate if you need:
- >10,000 messages/hour sustained
- Multiple consumer teams (analytics, ML, etc.)
- Event replay for debugging/reprocessing

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

    # 5. Delete from S3 archives
    await s3.delete_user_archives(user_id)
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
- S3 archival costs ($/month)

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
