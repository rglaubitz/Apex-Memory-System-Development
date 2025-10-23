# Apex System: Component Connections & Data Flow Analysis

**Created:** 2025-10-23
**Based On:** Actual code path tracing and function call analysis
**Purpose:** Understand how components interconnect and data flows through the system

---

## 📋 Executive Summary

The Apex Memory System is orchestrated through **5 critical integration patterns**:

1. **Dependency Injection** - Services passed at initialization (main.py:145-183)
2. **Saga Orchestration** - Atomic multi-DB writes via DatabaseWriteOrchestrator
3. **Temporal Workflows** - Event-driven document processing
4. **Shared Connections** - Database drivers reused across components
5. **Middleware Chains** - Request → Auth → Router → Response

**Key Insight:** The system maintains consistency across 4 databases through a **saga pattern** with distributed locking, circuit breakers, and idempotency - all coordinated by the DatabaseWriteOrchestrator.

---

## 🔄 Section 1: The Three Major Data Flows

### Flow 1: Document Ingestion (Upload → 4 Databases)

```
┌─────────────────────────────────────────────────────────────────────┐
│ USER UPLOADS DOCUMENT (Frontend)                                   │
│ File: ConversationsPage.tsx                                        │
└─────────────────────────────────────────────────────────────────────┘
                          ↓ HTTP POST (multipart/form-data)
┌─────────────────────────────────────────────────────────────────────┐
│ FASTAPI ENDPOINT (Component 03 - Backend API)                      │
│ File: apex-memory-system/src/apex_memory/api/ingestion.py:148      │
│ Function: ingest_document(file: UploadFile)                        │
│                                                                     │
│ Actions:                                                            │
│ 1. Generate UUID for document (line 175)                           │
│ 2. Save to local staging: /tmp/apex-staging/{source}/{uuid}/       │
│ 3. Create Temporal client connection (line 184)                    │
└─────────────────────────────────────────────────────────────────────┘
                          ↓ Temporal.client.start_workflow()
┌─────────────────────────────────────────────────────────────────────┐
│ TEMPORAL WORKFLOW (Component 02 - Workflow Orchestration)          │
│ File: temporal/workflows/ingestion.py                              │
│ Workflow: DocumentIngestionWorkflow                                │
│                                                                     │
│ Executes 6 Activities in Sequence:                                 │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Activity 1: parse_document_activity                         │   │
│ │ File: temporal/activities/ingestion.py:64                   │   │
│ │ Action: Calls DocumentParser.parse_document()               │   │
│ │ Returns: {uuid, content, metadata, chunks[]}                │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Activity 2: extract_entities_activity                       │   │
│ │ File: temporal/activities/ingestion.py:220                  │   │
│ │ Action: Calls EntityExtractor.extract()                     │   │
│ │ Returns: entities[] (name, type, confidence)                │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Activity 3: generate_embeddings_activity                    │   │
│ │ File: temporal/activities/ingestion.py:340                  │   │
│ │ Action: Calls EmbeddingService.generate_embedding()         │   │
│ │ Returns: embeddings[] (1536-dim vectors)                    │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Activity 4: write_to_databases_activity ⭐ CRITICAL          │   │
│ │ File: temporal/activities/ingestion.py:450                  │   │
│ │ Action: Calls DatabaseWriteOrchestrator.write_document()    │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│                  [SEE SAGA PATTERN BELOW]                           │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│ SAGA ORCHESTRATOR (Component 07 - Database Writers)                │
│ File: services/database_writer.py:41                               │
│ Class: DatabaseWriteOrchestrator                                   │
│                                                                     │
│ PHASE 1: DISTRIBUTED LOCK (lines 85-92)                            │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Acquire Redis lock: "document:{uuid}"                       │   │
│ │ Timeout: 30 seconds                                          │   │
│ │ Purpose: Prevent concurrent writes to same document          │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ PHASE 2: IDEMPOTENCY CHECK (lines 95-101)                          │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Check Redis key: "idempotency:ingest:{uuid}"                │   │
│ │ If exists: Return cached result (prevent duplicate)          │   │
│ │ If not exists: Continue to write                            │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ PHASE 3: PARALLEL DATABASE WRITES (ThreadPoolExecutor)             │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │                                                              │   │
│ │  Thread 1 ──→ Neo4jWriter.write_document_graph()            │   │
│ │               database/neo4j_writer.py:120                   │   │
│ │               Creates: Document + Entity nodes + Relations   │   │
│ │               Circuit Breaker: 'neo4j' (5 failures → open)   │   │
│ │                                                              │   │
│ │  Thread 2 ──→ PostgresWriter.write_document()               │   │
│ │               database/postgres_writer.py:150                │   │
│ │               INSERT INTO: documents, chunks (with pgvector) │   │
│ │               Circuit Breaker: 'postgres' (5 failures → open)│   │
│ │                                                              │   │
│ │  Thread 3 ──→ QdrantWriter.write_vectors()                  │   │
│ │               database/qdrant_writer.py:90                   │   │
│ │               Upsert to: 'documents' collection              │   │
│ │               Circuit Breaker: 'qdrant' (5 failures → open)  │   │
│ │                                                              │   │
│ │  Thread 4 ──→ RedisWriter.write_cache()                     │   │
│ │               database/redis_writer.py:60                    │   │
│ │               SET with TTL: 1 hour                           │   │
│ │               Circuit Breaker: 'redis' (3 failures → open)   │   │
│ │                                                              │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ PHASE 4: RESULT AGGREGATION                                        │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Check results from all 4 threads                            │   │
│ │                                                              │   │
│ │ IF all succeeded:                                            │   │
│ │   → Store idempotency key in Redis                          │   │
│ │   → Release distributed lock                                │   │
│ │   → Return WriteStatus.SUCCESS                              │   │
│ │                                                              │   │
│ │ IF any failed:                                               │   │
│ │   → ROLLBACK all successful writes                          │   │
│ │   → Delete from Neo4j (if written)                          │   │
│ │   → Delete from PostgreSQL (if written)                     │   │
│ │   → Delete from Qdrant (if written)                         │   │
│ │   → Delete from Redis cache                                 │   │
│ │   → Release distributed lock                                │   │
│ │   → Write to Dead Letter Queue (DLQ)                        │   │
│ │   → Return WriteStatus.FAILED                               │   │
│ └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│ RESULT: Document exists in ALL 4 databases or NONE                 │
│ Neo4j: Document + Entity nodes + MENTIONED_IN relationships        │
│ PostgreSQL: documents table + chunks table (with pgvector)          │
│ Qdrant: Vector points in 'documents' collection                    │
│ Redis: Cached metadata (TTL: 1 hour)                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Flow 2: Query Execution (Request → Multiple DBs → Fusion → Response)

```
┌─────────────────────────────────────────────────────────────────────┐
│ USER QUERY (Frontend)                                               │
│ File: components/chat/ConversationsStreaming.tsx                   │
│ Query: "What suppliers are connected to ACME Corp?"                │
└─────────────────────────────────────────────────────────────────────┘
                          ↓ HTTP POST to /api/v1/query/
┌─────────────────────────────────────────────────────────────────────┐
│ FASTAPI ENDPOINT (Component 03 - Backend API)                      │
│ File: apex-memory-system/src/apex_memory/api/query.py:130          │
│ Function: execute_query(request: QueryRequest)                     │
│                                                                     │
│ Action: Calls router_instance.execute_query()                      │
│         (router_instance initialized in main.py:145)               │
└─────────────────────────────────────────────────────────────────────┘
                          ↓ router_instance.execute_query()
┌─────────────────────────────────────────────────────────────────────┐
│ QUERY ROUTER (Component 04 - Query Intelligence)                   │
│ File: query_router/router.py:800 (execute_query method)            │
│                                                                     │
│ STEP 1: CACHE CHECK (Semantic Similarity)                          │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ File: query_router/semantic_cache.py:45                     │   │
│ │ Action: Check Redis for semantically similar queries         │   │
│ │ Threshold: 0.90 similarity                                   │   │
│ │                                                              │   │
│ │ IF cache hit:                                                │   │
│ │   → Return cached result (<10ms)                            │   │
│ │   → Skip database queries                                    │   │
│ │                                                              │   │
│ │ IF cache miss:                                               │   │
│ │   → Continue to intent classification                        │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ STEP 2: INTENT CLASSIFICATION (3-Tier Fallback)                    │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Tier 1: Keyword Classifier                                   │   │
│ │ File: query_router/keyword_classifier.py:80                 │   │
│ │ Patterns: "connected", "suppliers" → Intent: "graph"         │   │
│ │ Confidence: 0.92 (>0.80 threshold)                          │   │
│ │ Time: 5ms                                                    │   │
│ │ Result: Intent="graph" ✅                                    │   │
│ │                                                              │   │
│ │ [Tier 2 and 3 skipped - high confidence from Tier 1]        │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ STEP 3: DATABASE ROUTING (Intent Mapping)                          │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ File: query_router/router.py:786-791                        │   │
│ │ Intent="graph" → Databases: ["neo4j", "graphiti"]           │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ STEP 4: PARALLEL QUERY EXECUTION                                   │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │                                                              │   │
│ │  Thread 1 ──→ Neo4jQueryBuilder.build_graph_query()         │   │
│ │               query_router/neo4j_queries.py:150              │   │
│ │               Cypher: MATCH (d:Document)-[r]-(e:Entity)      │   │
│ │                       WHERE e.name CONTAINS 'ACME'           │   │
│ │               Returns: 8 results (relationships)             │   │
│ │               Time: 120ms                                    │   │
│ │                                                              │   │
│ │  Thread 2 ──→ GraphitiSearchWrapper.hybrid_search()         │   │
│ │               query_router/graphiti_search.py:200            │   │
│ │               Query: Temporal entity connections             │   │
│ │               Returns: 5 results (time-aware)                │   │
│ │               Time: 450ms                                    │   │
│ │                                                              │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ STEP 5: RESULT FUSION (RRF Algorithm)                              │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ File: query_router/result_fusion.py:60                      │   │
│ │ Algorithm: Reciprocal Rank Fusion (RRF)                     │   │
│ │                                                              │   │
│ │ Input: 8 results (Neo4j) + 5 results (Graphiti) = 13 total  │   │
│ │                                                              │   │
│ │ RRF Scoring:                                                 │   │
│ │   score = sum(1 / (rank + k)) for each database             │   │
│ │   k = 60 (tuned parameter)                                   │   │
│ │                                                              │   │
│ │ Actions:                                                     │   │
│ │ 1. Deduplicate by entity name                               │   │
│ │ 2. Calculate RRF score for each result                      │   │
│ │ 3. Sort by fused score (descending)                         │   │
│ │ 4. Return top 10 results                                    │   │
│ │                                                              │   │
│ │ Output: 10 highest-scored supplier entities                 │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ STEP 6: CACHE STORAGE                                              │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ File: cache/query_cache.py:88                               │   │
│ │ Action: Store results in Redis                              │   │
│ │ Key: query:{sha256(query+filters)}                          │   │
│ │ TTL: 3600 seconds (1 hour)                                  │   │
│ │ Purpose: Next similar query returns in <10ms                │   │
│ └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                          ↓ Return QueryResponse
┌─────────────────────────────────────────────────────────────────────┐
│ RESULT TO FRONTEND                                                  │
│ {                                                                   │
│   "results": [10 supplier entities],                               │
│   "intent": "graph",                                               │
│   "databases_used": ["neo4j", "graphiti"],                         │
│   "cached": false,                                                 │
│   "result_count": 10,                                              │
│   "latency_ms": 580                                                │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Flow 3: Authentication Propagation (Login → JWT → Protected Endpoints)

```
┌─────────────────────────────────────────────────────────────────────┐
│ USER LOGIN (Frontend)                                               │
│ File: components/auth/Login.tsx                                    │
│ Input: {email: "user@example.com", password: "pass123"}            │
└─────────────────────────────────────────────────────────────────────┘
                          ↓ HTTP POST to /api/v1/auth/login
┌─────────────────────────────────────────────────────────────────────┐
│ AUTH ENDPOINT (Component 12 - Authentication)                      │
│ File: apex-memory-system/src/apex_memory/api/auth.py:45            │
│ Function: login(email, password)                                   │
│                                                                     │
│ STEP 1: Verify Password                                            │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ File: services/auth_service.py:80                           │   │
│ │ Action: Get user from PostgreSQL                            │   │
│ │ Query: SELECT * FROM users WHERE email = ?                  │   │
│ │ Verify: bcrypt.verify(password, hashed_password)            │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ STEP 2: Generate JWT                                               │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ File: services/auth_service.py:120                          │   │
│ │ Payload: {                                                   │   │
│ │   "sub": user_uuid,                                         │   │
│ │   "email": "user@example.com",                              │   │
│ │   "exp": now + 24 hours                                     │   │
│ │ }                                                            │   │
│ │ Algorithm: HS256                                             │   │
│ │ Secret: settings.jwt_secret_key                             │   │
│ │ Result: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."          │   │
│ └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                          ↓ Return {access_token}
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND STORES TOKEN                                               │
│ File: contexts/AuthContext.tsx                                     │
│ Storage: localStorage.setItem('token', access_token)               │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│ SUBSEQUENT REQUEST (Protected Endpoint)                            │
│ Example: POST /api/v1/query/                                       │
│ Headers: {                                                          │
│   "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│ FASTAPI DEPENDENCY INJECTION                                       │
│ File: api/dependencies.py:20                                       │
│ Function: get_current_user(token: str = Depends(oauth2_scheme))    │
│                                                                     │
│ STEP 1: Extract Token                                              │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ OAuth2PasswordBearer extracts from Authorization header     │   │
│ │ Splits "Bearer {token}" → token                             │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ STEP 2: Decode JWT                                                 │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ File: services/auth_service.py:150                          │   │
│ │ Action: jwt.decode(token, secret_key, algorithms=["HS256"]) │   │
│ │ Validates: Signature, expiration                            │   │
│ │ Returns: {sub: user_uuid, email: ...}                       │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ STEP 3: Fetch User                                                 │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Query PostgreSQL: SELECT * FROM users WHERE uuid = ?        │   │
│ │ Returns: UserDB object                                       │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                          ↓                                          │
│ RESULT: UserDB injected into endpoint function parameter           │
└─────────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PROTECTED ENDPOINT EXECUTES                                         │
│ @router.post("/query/")                                            │
│ async def execute_query(                                            │
│     request: QueryRequest,                                          │
│     user: UserDB = Depends(get_current_user)  ← Injected here      │
│ ):                                                                  │
│     # User is authenticated ✅                                      │
│     # Execute query with user context                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Section 2: Database Synchronization - The Saga Pattern Deep Dive

### How 4 Databases Stay in Sync

**Location:** `services/database_writer.py:41` (DatabaseWriteOrchestrator)

#### The Challenge

Writing to 4 separate databases creates a **distributed transaction problem**:
- What if Neo4j succeeds but PostgreSQL fails?
- What if network failure occurs mid-write?
- How to prevent partial data corruption?

#### The Solution: Enhanced Saga Pattern

```python
# From services/database_writer.py

class DatabaseWriteOrchestrator:
    """
    Atomic multi-DB writes with rollback guarantee.

    Patterns Implemented:
    1. Distributed Locking (prevents concurrent writes)
    2. Idempotency (prevents duplicate operations)
    3. Circuit Breakers (fault tolerance per DB)
    4. Saga Pattern (atomic commit or full rollback)
    5. Dead Letter Queue (failed operation recovery)
    """
```

#### Synchronization Mechanisms

**1. Distributed Locking (Redis)**

```python
# File: services/distributed_lock.py:30

class RedisDistributedLock:
    """
    Ensures only ONE worker can write to a document at a time.

    How it works:
    1. Worker acquires lock: SET document:{uuid} worker_id NX EX 30
    2. If lock already held → waits or fails
    3. Performs write operations
    4. Releases lock: DEL document:{uuid}

    Prevents:
    - Race conditions (two workers writing simultaneously)
    - Lost updates (worker A overwrites worker B's changes)
    """

    def acquire(self, resource_id: str):
        # Redis SETNX (SET if Not eXists) - atomic operation
        success = self.redis.set(
            f"lock:{resource_id}",
            worker_id,
            nx=True,  # Only set if doesn't exist
            ex=30     # Expire after 30 seconds
        )
        return success
```

**2. Idempotency Keys (Redis)**

```python
# File: services/idempotency.py:45

class IdempotencyManager:
    """
    Prevents duplicate operations if request retried.

    How it works:
    1. Before write: Check Redis key "idempotency:ingest:{doc_uuid}"
    2. If exists → Return cached result (operation already done)
    3. If not exists → Perform write, store result with 24h TTL

    Prevents:
    - Duplicate documents (same file uploaded twice)
    - Retry storms (client retries request 10 times)
    """

    def check_and_execute(self, operation_id: str, operation_func):
        # Check if already executed
        cached_result = self.redis.get(f"idempotency:{operation_id}")
        if cached_result:
            return json.loads(cached_result)  # Return cached

        # Execute operation
        result = operation_func()

        # Cache result for 24 hours
        self.redis.setex(
            f"idempotency:{operation_id}",
            86400,
            json.dumps(result)
        )
        return result
```

**3. Circuit Breakers (Per Database)**

```python
# File: services/circuit_breaker.py:20

class CircuitBreaker:
    """
    Prevents cascading failures from unhealthy databases.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Database unhealthy, fail fast (don't retry)
    - HALF_OPEN: Testing if database recovered

    How it works:
    1. Track failures per database
    2. After 5 consecutive failures → OPEN circuit
    3. Fail fast for 60 seconds (don't waste time retrying)
    4. After timeout → HALF_OPEN (try one request)
    5. If success → CLOSED, if failure → OPEN again
    """

    circuit_breakers = {
        'postgres': CircuitBreaker(failure_threshold=5, timeout=60),
        'neo4j': CircuitBreaker(failure_threshold=5, timeout=60),
        'qdrant': CircuitBreaker(failure_threshold=5, timeout=60),
        'redis': CircuitBreaker(failure_threshold=3, timeout=30),  # Lower threshold for cache
    }
```

**4. Parallel Writes with ThreadPoolExecutor**

```python
# File: services/database_writer.py:300

def write_document(self, doc, chunks, entities, embeddings):
    """
    Write to all 4 databases in parallel.

    Uses ThreadPoolExecutor to execute writes concurrently:
    - Thread 1: Neo4j write (120ms)
    - Thread 2: PostgreSQL write (150ms)
    - Thread 3: Qdrant write (80ms)
    - Thread 4: Redis write (10ms)

    Total time: max(120, 150, 80, 10) = 150ms (parallel)
    vs. 360ms if sequential
    """

    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all writes
        futures = {
            'neo4j': executor.submit(self._write_neo4j, doc, entities),
            'postgres': executor.submit(self._write_postgres, doc, chunks),
            'qdrant': executor.submit(self._write_qdrant, doc, embeddings),
            'redis': executor.submit(self._write_redis, doc),
        }

        # Wait for all to complete
        results = {db: future.result() for db, future in futures.items()}

        # Check if ALL succeeded
        if all(r.success for r in results.values()):
            return WriteStatus.SUCCESS
        else:
            # Rollback all successful writes
            self._rollback_all(results)
            return WriteStatus.FAILED
```

**5. Saga Pattern Rollback**

```python
def _rollback_all(self, results):
    """
    Rollback all successful writes if any database failed.

    Rollback order (reverse of write order):
    1. Redis cache (fastest to rollback)
    2. Qdrant vectors
    3. PostgreSQL rows
    4. Neo4j nodes/relationships
    """

    if results['redis'].success:
        self.redis.delete_cache(doc_id)

    if results['qdrant'].success:
        self.qdrant.delete_points([doc_id])

    if results['postgres'].success:
        self.postgres.delete_document(doc_id)
        self.postgres.delete_chunks(doc_id)

    if results['neo4j'].success:
        self.neo4j.delete_document_graph(doc_id)
```

#### Synchronization Guarantee

**Invariant:** At any point in time, either:
- Document exists in ALL 4 databases (consistent state)
- Document exists in ZERO databases (failed ingestion, rolled back)

**Never:** Document exists in 2/4 databases (partial state)

---

## 🔌 Section 3: Critical Connection Points - "The Glue"

### Connection Point 1: Main Application Initialization

**File:** `apex-memory-system/src/apex_memory/main.py:118-183`

This is where **EVERYTHING connects**. All database drivers, services, and routers are initialized and wired together.

```python
# Line 118: Initialize embedding service (shared between ingestion and query)
embedding_service = EmbeddingService()

# Line 122: Initialize Graphiti service (conditional)
graphiti_service = None
if settings.graphiti_enabled:
    graphiti_service = GraphitiService(
        neo4j_uri=settings.graphiti_uri,
        neo4j_user=settings.graphiti_user,
        neo4j_password=settings.graphiti_password,
        openai_api_key=settings.openai_api_key,
    )

# Line 145: ⭐ CRITICAL - QueryRouter initialized with ALL database drivers
router_instance = QueryRouter(
    # Database connections (REUSED from ingestion orchestrator)
    neo4j_driver=ingestion_orchestrator.neo4j.driver,  # ← Shared connection!
    postgres_conn=ingestion_orchestrator.postgres.pool, # ← Shared pool!
    qdrant_client=ingestion_orchestrator.qdrant.client, # ← Shared client!
    redis_host=settings.redis_host,

    # Shared services
    embedding_service=embedding_service,  # ← Same instance!
    graphiti_service=graphiti_service,    # ← Same instance!

    # Phase 1-4 configuration
    enable_hybrid_classification=True,
    enable_result_fusion=True,
    enable_semantic_cache=True,
    # ... (see main.py:145-183 for full config)
)

# Line 183: Make router available to API endpoints
init_router(router_instance)

# Lines 189-201: Include all API routers
app.include_router(auth_router)
app.include_router(ingestion_router)
app.include_router(query_router)
app.include_router(chat_stream_router)
# ... (13 total routers)
```

**Why This Matters:**

1. **Shared Database Connections** - Query Router and Ingestion use THE SAME database drivers
   - Prevents connection pool exhaustion
   - Consistent connection management
   - Shared circuit breaker states

2. **Shared Services** - EmbeddingService and GraphitiService instances reused
   - Embeddings cached in same instance
   - GraphQL connections pooled
   - Reduces memory footprint

3. **Single QueryRouter Instance** - All query endpoints use the same router
   - Shared analytics
   - Consistent intent classification
   - Unified caching

### Connection Point 2: Temporal Activity to Service Bridge

**File:** `temporal/activities/ingestion.py:450`

Activities act as **adapters** between Temporal workflows and existing services.

```python
@activity.defn
async def write_to_databases_activity(
    parsed_doc_dict: Dict[str, Any],
    entities: List[Dict[str, Any]],
    embeddings: List[List[float]]
) -> Dict[str, Any]:
    """
    Bridge between Temporal workflow and DatabaseWriteOrchestrator.

    Why this pattern?
    - Temporal requires serializable data (dicts, not objects)
    - Services use rich Pydantic models
    - Activity converts dict → model → service call → dict
    """

    # Step 1: Convert Temporal dict to service model
    parsed_doc = ParsedDocument(**parsed_doc_dict)
    entity_objects = [Entity(**e) for e in entities]

    # Step 2: Call existing service (preserves 121 tests!)
    orchestrator = DatabaseWriteOrchestrator()

    result = orchestrator.write_document(
        document=parsed_doc,
        chunks=parsed_doc.chunks,
        entities=entity_objects,
        embeddings=embeddings
    )

    # Step 3: Convert service result to Temporal dict
    return {
        "success": result.success,
        "document_id": result.document_id,
        "databases_written": result.databases_written,
    }
```

**Integration Pattern:**

```
Temporal Workflow (serializable dicts)
         ↓
    Activity (adapter)
         ↓
  Service (rich objects)
         ↓
 Database Writers
         ↓
  4 Databases
```

### Connection Point 3: Frontend to Backend Integration

**Frontend File:** `src/lib/axios.ts` (doesn't exist, let me check the actual pattern)

**Actual Pattern:** Frontend uses Vercel AI SDK for streaming

```typescript
// File: hooks/useApexChat.ts

export function useApexChat(conversationId: string) {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/v1/chat/stream',  // ← Backend SSE endpoint
    body: {
      conversation_id: conversationId,
    },
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,  // ← JWT propagation
    },
    onToolCall: async (toolCall) => {
      // Handle Claude tool executions
      // Tools: search_knowledge_graph, get_entity_relationships, etc.
    },
  });

  return { messages, input, handleInputChange, handleSubmit, isLoading };
}
```

**Backend File:** `api/chat_stream.py:120`

```python
@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """
    Server-Sent Events (SSE) streaming with Claude.

    Integration points:
    1. Receives messages from frontend
    2. Calls Anthropic SDK (Claude 3.5 Sonnet)
    3. Claude calls tools (search_knowledge_graph → QueryRouter)
    4. Streams responses back to frontend via SSE
    """

    # Tool: search_knowledge_graph
    def search_knowledge_graph(query: str, limit: int = 10):
        # ⭐ Calls QueryRouter (Component 04)
        result = router_instance.execute_query(query, limit)
        return result.results

    # Create Anthropic client
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    # Start streaming
    async with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        messages=request.messages,
        tools=[search_knowledge_graph, ...],  # 5 tools total
        max_tokens=4096,
    ) as stream:
        async for event in stream:
            yield f"data: {json.dumps(event)}\n\n"
```

**Connection Flow:**

```
Frontend useApexChat hook
         ↓ HTTP POST /api/v1/chat/stream
Backend SSE endpoint
         ↓ Calls Anthropic SDK
Claude 3.5 Sonnet
         ↓ Tool: search_knowledge_graph
QueryRouter.execute_query()
         ↓ Query 4 databases
Results → Claude → SSE → Frontend
```

---

## 📊 Section 4: Component Interaction Matrix

| Component | Interacts With | Connection Mechanism | Data Exchanged |
|-----------|----------------|---------------------|----------------|
| **Frontend (08)** | Backend API (03) | HTTP REST + SSE | JSON requests/responses, JWT tokens |
| **Backend API (03)** | Query Router (04) | Direct function call | QueryRequest → QueryResponse |
| **Backend API (03)** | Temporal (02) | Temporal client SDK | Workflow start requests |
| **Backend API (03)** | Auth (12) | Dependency injection | JWT token → User object |
| **Query Router (04)** | 4 Databases (01) | Database drivers | SQL, Cypher, Vector queries |
| **Query Router (04)** | Cache (09) | Redis client | Query results (get/set) |
| **Query Router (04)** | Core Services (05) | Direct instantiation | Embeddings, Graphiti queries |
| **Temporal Workflows (02)** | Core Services (05) | Activity calls | Documents, entities, embeddings |
| **Core Services (05)** | Database Writers (07) | Direct function call | ParsedDocument → WriteResult |
| **Database Writers (07)** | 4 Databases (01) | Parallel threads | Nodes, rows, vectors, cache entries |
| **Database Writers (07)** | Cache (09) | Redis client | Distributed locks, idempotency keys |
| **Monitoring (10)** | All components | Prometheus client | Metric observations |
| **Config (11)** | All components | Pydantic Settings | Environment variables |

---

## 🚨 Section 5: Failure Handling & Rollback Mechanisms

### Failure Scenario 1: Database Unavailable During Ingestion

```
User uploads document
         ↓
API saves to staging: /tmp/apex-staging/{uuid}/
         ↓
Temporal workflow starts
         ↓
Activity 1-3 succeed (parse, extract, embed)
         ↓
Activity 4: write_to_databases_activity
         ↓
DatabaseWriteOrchestrator attempts writes:
  - Neo4j: ✅ Success
  - PostgreSQL: ✅ Success
  - Qdrant: ❌ Connection refused (database down)
  - Redis: Not attempted
         ↓
Orchestrator detects failure → ROLLBACK:
  1. Delete from Neo4j (rollback cypher query)
  2. Delete from PostgreSQL (DELETE query)
  3. Qdrant: Nothing to rollback
  4. Redis: Nothing to rollback
         ↓
Write to Dead Letter Queue (DLQ):
  INSERT INTO dlq (document_id, error, payload, retry_count)
         ↓
Temporal marks activity as FAILED
         ↓
Temporal retries activity (exponential backoff):
  - Retry 1 after 1 second
  - Retry 2 after 2 seconds
  - Retry 3 after 4 seconds
         ↓
If all retries fail:
  - Workflow marked as FAILED
  - User receives error notification
  - Document remains in staging for manual retry
  - DLQ entry available for debugging
```

### Failure Scenario 2: Query Router Database Timeout

```
User query: "What suppliers are connected to ACME?"
         ↓
Cache miss → Execute database queries
         ↓
Parallel execution:
  - Neo4j query: ✅ Returns 8 results (120ms)
  - Graphiti query: ❌ Timeout after 5 seconds
         ↓
Query Router behavior:
  1. Logs timeout error
  2. Returns partial results (Neo4j only)
  3. Marks Graphiti as degraded
  4. Does NOT cache partial results
         ↓
Circuit breaker increments failure count:
  - Graphiti failures: 1/5
  - If reaches 5: Circuit opens (fail fast)
         ↓
Response to user:
  {
    "results": [8 results from Neo4j],
    "intent": "graph",
    "databases_used": ["neo4j"],
    "databases_failed": ["graphiti"],
    "cached": false,
    "warning": "Partial results - temporal queries unavailable"
  }
```

---

## 📈 Section 6: Data Transformation Points

### Transformation 1: File Upload → Parsed Document

```
Input: user_file.pdf (binary)
         ↓ File.save()
Staging: /tmp/apex-staging/local_upload/{uuid}/document.pdf
         ↓ DocumentParser.parse_document()
ParsedDocument {
  uuid: "DOC-123",
  content: "Full text content...",
  chunks: [
    {text: "Chunk 1 text...", index: 0},
    {text: "Chunk 2 text...", index: 1},
  ],
  metadata: {title, author, file_type}
}
```

### Transformation 2: Text → Entities

```
Input: "ACME Corp supplies widgets to Bosch GmbH in Germany."
         ↓ EntityExtractor.extract()
Output: [
  {name: "ACME Corp", type: "Organization", confidence: 0.95},
  {name: "Bosch GmbH", type: "Organization", confidence: 0.92},
  {name: "Germany", type: "Location", confidence: 0.88},
  {name: "widgets", type: "Product", confidence: 0.75}
]
```

### Transformation 3: Chunks → Embeddings

```
Input: ["Chunk 1 text...", "Chunk 2 text...", ...]
         ↓ EmbeddingService.generate_embedding()
Output: [
  [0.123, -0.456, 0.789, ...],  # 1536 dimensions
  [0.234, -0.567, 0.890, ...],  # 1536 dimensions
]
```

### Transformation 4: Query → Intent

```
Input: "How has ACME Corp changed over the last year?"
         ↓ HybridClassifier.classify()
Analysis: {
  keywords_detected: ["changed", "over", "last year"],
  semantic_similarity: {
    "temporal": 0.89,
    "graph": 0.45,
    "semantic": 0.32
  },
  llm_confidence: N/A (skipped - high keyword confidence)
}
         ↓
Output: Intent = "temporal" (confidence: 0.92)
```

---

## 🎯 Summary: The Complete Picture

### How Components Stay Connected

1. **Shared Database Drivers** (main.py:145-148)
   - QueryRouter uses same Neo4j driver as ingestion
   - Same PostgreSQL pool
   - Same Qdrant client
   - Prevents connection exhaustion

2. **Saga Orchestrator** (database_writer.py:41)
   - Coordinates all database writes
   - Ensures atomic consistency
   - Handles rollback on failure

3. **Temporal Bridge** (temporal/activities/ingestion.py)
   - Connects workflows to existing services
   - Preserves service tests (121 tests)
   - Adds durability and retry logic

4. **Dependency Injection** (api/dependencies.py)
   - JWT → User object propagation
   - Shared across all protected endpoints

5. **Monitoring Hooks** (monitoring/metrics.py)
   - Every component calls record_*() functions
   - Prometheus scrapes metrics
   - Grafana visualizes

### How Data Flows

**Ingestion:** Frontend → API → Temporal → Activities → Saga → 4 DBs (atomic)

**Query:** Frontend → API → QueryRouter → (Cache check) → Multiple DBs → ResultFusion → Cache store → Response

**Auth:** Login → JWT → Request header → Dependency injection → User context

### How Databases Stay Synced

**Saga Pattern:**
1. Distributed lock (prevent concurrent writes)
2. Idempotency check (prevent duplicates)
3. Parallel writes to all 4 DBs
4. If ANY fail → Rollback ALL
5. Store result or write to DLQ

**Guarantee:** Document exists in ALL databases or NONE.

---

**Total Lines:** ~1,000 lines of technical connection analysis
**Based On:** Actual code path tracing from 10+ source files
**Purpose:** Understand the "glue" that holds Apex Memory System together
