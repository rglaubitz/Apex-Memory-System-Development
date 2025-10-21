# Phase 4: Query Router Implementation

**Status:** UNVERIFIED
**Created:** 2025-10-20
**Researcher:** TBD
**Priority:** CRITICAL

---

## Hypothesis

The Query Router exists but may be incomplete or non-functional. While code exists for intent classification and database routing, the end-to-end query flow (intent → route → retrieve → aggregate) may have gaps.

**Specific Gaps Suspected:**
1. LLM intent classifier may not be fully integrated
2. Database-specific query executors may be missing
3. Result aggregation logic may be incomplete
4. Cache layer may not be functional
5. No end-to-end query tests
6. Performance may not meet <1s latency target

**What This Means:**
Users cannot efficiently query the multi-database system. Even if data is stored correctly, retrieval may be slow, incorrect, or incomplete.

---

## Expected Behavior

### Complete Query Flow:

```
User Query: "Who supplies brake parts?"
    ↓
POST /api/v1/query
{"query": "Who supplies brake parts?"}
    ↓
LLM Intent Classifier (Claude 3.5 Sonnet)
→ Intent: "graph" (relationship-based query)
→ Confidence: 0.92
    ↓
Database Router
→ Selected: Neo4j (graph database)
    ↓
Query Executor (Neo4j)
→ Cypher: MATCH (supplier)-[:SUPPLIES]->(part {name: "brake parts"}) RETURN supplier
→ Results: [{"name": "ACME Corp", "type": "supplier"}]
    ↓
Result Aggregator
→ Format results
→ Add metadata (source, confidence, timestamp)
    ↓
Cache Layer (Redis)
→ Store query + results (TTL: 1 hour)
    ↓
Response to User:
{
  "intent": "graph",
  "database": "neo4j",
  "results": [
    {
      "name": "ACME Corp",
      "type": "supplier",
      "relationship": "SUPPLIES",
      "target": "brake parts"
    }
  ],
  "confidence": 0.92,
  "cached": false,
  "latency_ms": 847
}
```

### Where it should exist:

**1. API Endpoint:**
- Location: `apex-memory-system/src/apex_memory/api/routes/query.py`
- Endpoint: `POST /api/v1/query`
- Accepts: `{query: str, filters?: object}`

**2. Intent Classifier:**
- Location: `apex-memory-system/src/apex_memory/query_router/llm_classifier.py`
- Class: `LLMIntentClassifier`
- Method: `classify(query: str) -> (intent: str, confidence: float)`
- Intents: `graph`, `semantic`, `temporal`, `metadata`

**3. Database Router:**
- Location: `apex-memory-system/src/apex_memory/query_router/router.py`
- Class: `QueryRouter`
- Method: `route(intent: str) -> database: str`
- Routing logic:
  - `graph` → Neo4j
  - `semantic` → Qdrant
  - `temporal` → Graphiti (Neo4j)
  - `metadata` → PostgreSQL

**4. Query Executors:**
- Location: `apex-memory-system/src/apex_memory/query_router/executors/`
- Executors:
  - `neo4j_executor.py` - Execute Cypher queries
  - `qdrant_executor.py` - Execute vector similarity search
  - `postgres_executor.py` - Execute SQL queries
  - `graphiti_executor.py` - Execute temporal queries

**5. Result Aggregator:**
- Location: `apex-memory-system/src/apex_memory/query_router/aggregator.py`
- Class: `ResultAggregator`
- Method: `aggregate(results: List[dict]) -> dict`
- Functionality:
  - Combine results from multiple databases (if needed)
  - Deduplicate
  - Rank by relevance
  - Format for response

**6. Cache Layer:**
- Location: `apex-memory-system/src/apex_memory/query_router/cache.py`
- Class: `QueryCache`
- Methods:
  - `get(query: str) -> Optional[dict]`
  - `set(query: str, results: dict, ttl: int)`
- Backend: Redis
- TTL: 1 hour default

---

## Why Important

**Deployment Impact:** CRITICAL

**This is CRITICAL because:**

1. **Core User Experience:** Querying is the primary user interaction. If users can't retrieve data, the system is unusable.

2. **Performance:** Query latency must be <1s (P90). Without proper routing and caching, queries may be too slow.

3. **Accuracy:** Intent classification must be >80% accurate. Wrong database → wrong results → user frustration.

4. **Multi-Database Value:** The whole point of 4 databases is intelligent routing. Without it, multi-DB architecture adds complexity with no benefit.

5. **Testing Validity:** Testing-kit validates query router, but if it's incomplete, tests are invalid.

**Without a functional query router, deployment would result in poor UX and system underutilization.**

---

## Research Plan

### Files to Check:

**API Endpoint:**
```bash
# Search for query endpoint
grep -r "def query" apex-memory-system/src/apex_memory/api/routes/query.py

# Check POST /api/v1/query
grep -r "@router.post" apex-memory-system/src/apex_memory/api/routes/query.py
```

**Intent Classifier:**
```bash
# Search for LLMIntentClassifier
grep -r "class LLMIntentClassifier" apex-memory-system/src/apex_memory/query_router/

# Check Claude API integration
grep -r "anthropic" apex-memory-system/src/apex_memory/query_router/llm_classifier.py

# Check intent types
grep -r "graph\|semantic\|temporal\|metadata" apex-memory-system/src/apex_memory/query_router/llm_classifier.py
```

**Database Router:**
```bash
# Search for QueryRouter
grep -r "class QueryRouter" apex-memory-system/src/apex_memory/query_router/

# Check routing logic
grep -r "def route" apex-memory-system/src/apex_memory/query_router/router.py
```

**Query Executors:**
```bash
# Check executors exist
ls apex-memory-system/src/apex_memory/query_router/executors/

# Verify all 4 executors
ls apex-memory-system/src/apex_memory/query_router/executors/ | grep -E "neo4j|qdrant|postgres|graphiti"
```

**Result Aggregator:**
```bash
# Search for ResultAggregator
grep -r "class ResultAggregator" apex-memory-system/src/apex_memory/query_router/

# Check aggregation logic
grep -r "def aggregate" apex-memory-system/src/apex_memory/query_router/aggregator.py
```

**Cache Layer:**
```bash
# Search for QueryCache
grep -r "class QueryCache" apex-memory-system/src/apex_memory/query_router/

# Check Redis integration
grep -r "redis" apex-memory-system/src/apex_memory/query_router/cache.py
```

### Tests to Run:

**Unit Tests:**
```bash
# Search for query router tests
find apex-memory-system/tests/unit/ -name "*query_router*"
find apex-memory-system/tests/unit/ -name "*intent*"

# Run intent classifier tests
pytest apex-memory-system/tests/unit/test_intent_classifier.py -v

# Run router tests
pytest apex-memory-system/tests/unit/test_query_router.py -v

# Run cache tests
pytest apex-memory-system/tests/unit/test_cache.py -v
```

**Integration Tests:**
```bash
# Search for query integration tests
find apex-memory-system/tests/integration/ -name "*query*"

# Run E2E query tests
pytest apex-memory-system/tests/integration/ -v -k "query"
```

**Manual API Tests:**
```bash
# Test graph query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who supplies brake parts?"}'

# Expected:
# {"intent": "graph", "database": "neo4j", "results": [...]}

# Test semantic query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find documents about safety procedures"}'

# Expected:
# {"intent": "semantic", "database": "qdrant", "results": [...]}

# Test cache
curl http://localhost:8000/api/v1/query/cache/stats

# Expected:
# {"cache_hits": X, "cache_misses": Y, "hit_rate": Z}
```

**Performance Tests:**
```bash
# Test query latency
time curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who supplies brake parts?"}'

# Should complete in <1s for P90
```

### Evidence Needed:

**To prove IMPLEMENTED:**
- [ ] API endpoint `/api/v1/query` exists and responds 200
- [ ] LLM classifier achieves >80% accuracy
- [ ] All 4 database executors exist
- [ ] Results aggregated correctly
- [ ] Cache hit rate >60% (with traffic)
- [ ] Query latency <1s (P90)
- [ ] Tests passing (unit + integration)

**To prove MISSING:**
- [ ] No API endpoint, OR
- [ ] Intent classifier <80% accurate, OR
- [ ] Missing executors, OR
- [ ] No aggregation logic, OR
- [ ] Cache not functional, OR
- [ ] Latency >1s, OR
- [ ] Tests missing/failing

### Success Criteria:

**Feature is IMPLEMENTED if:**
1. API endpoint functional
2. Intent classification >80% accurate
3. All 4 databases routable
4. Results aggregated correctly
5. Cache functional (>60% hit rate with traffic)
6. Latency <1s (P90)
7. Tests passing

**Feature is MISSING if:**
1. API not functional, OR
2. Intent classification inaccurate, OR
3. Missing database executors, OR
4. No aggregation, OR
5. Cache not working, OR
6. Latency >1s, OR
7. Tests failing

---

## Research Log

**Link:** `research-logs/phase-4-query-router-implementation-research.md`

---

## Verification Decision

**Status:** PENDING

**Decision Date:** TBD
**Verified By:** TBD

**Evidence:**
[To be filled after research]

**Next Steps:**
- If IMPLEMENTED: Move to `verified/implemented/` and document architecture
- If MISSING: Move to `verified/missing/` and create completion plan

---

**Expected Outcome:** PARTIAL (code exists, but may have gaps or performance issues)

**Reason:** Testing-kit shows query router unit tests blocked by Prometheus metrics duplication, suggesting implementation exists but may have issues. Performance metrics (latency, cache hit rate) not validated.

**If MISSING, Auto-Trigger:**
- Create `upgrades/active/query-router-completion/`
- Priority: CRITICAL
- Timeline: 1-2 weeks to complete missing pieces and validate performance
