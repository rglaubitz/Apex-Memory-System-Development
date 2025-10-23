# 04 - Query Intelligence (Query Router)

## 🎯 Purpose

Routes user queries to optimal database(s) based on intent classification, then aggregates and reranks results for maximum accuracy. **90% accuracy achieved** after 5-day optimization sprint (October 2025).

**Why Query Router?**
- Different databases excel at different query types
- Intent classification prevents querying wrong database
- Result fusion combines strengths of multiple databases
- Semantic caching delivers <10ms for repeat queries

## 🛠 Technical Stack

### Intent Classification (3-Tier Fallback)
1. **Keyword Classifier** - Pattern matching (60% of queries, <10ms, 95%+ accuracy)
2. **Hybrid Classifier** - Keywords + embeddings (35% of queries, <100ms, 85-90% accuracy)
3. **LLM Classifier** - Claude Haiku fallback (5% of queries, 300-500ms, high accuracy)

### Result Processing
- **ResultFusion:** Reciprocal Rank Fusion (RRF) algorithm
- **Neo4jGraphRAG:** Unified vector+graph search (DISABLED in Phase 3)
- **Graphiti Search:** Temporal hybrid search with cross-encoder (LIMITED to 20% queries)

### Key Libraries
- **Anthropic SDK:** Claude Haiku for LLM classification
- **Sentence-Transformers:** Local embeddings for semantic classification
- **OpenAI:** Embeddings for semantic cache similarity

## 📂 Key Files

### Core Router
- `apex-memory-system/src/apex_memory/query_router/router.py` (43,683 bytes)
  - `QueryRouter` class - Main orchestration
  - Intent mapping to databases (router.py:786-791)
  - Phase 1-2 enabled, Phase 3-4 DISABLED

### Classification Strategies (3-Tier)
- `query_router/keyword_classifier.py` (13,481 bytes)
  - Pattern matching with confidence scoring
  - 60% of queries (fastest path)

- `query_router/hybrid_classifier.py` (13,076 bytes)
  - Keywords + embedding similarity
  - Balanced speed/accuracy
  - 35% of queries

- `query_router/llm_classifier.py` (10,041 bytes)
  - Claude Haiku fallback
  - Highest accuracy for ambiguous queries
  - 5% of queries

- `query_router/semantic_classifier.py` (26,485 bytes)
  - DISABLED (hurt accuracy in testing)
  - Uses embeddings only

### Result Aggregation
- `query_router/aggregator.py` (13,811 bytes)
  - Combines results from multiple databases
  - Weighted scoring based on database confidence

- `query_router/result_fusion.py` (11,457 bytes)
  - **RRF (Reciprocal Rank Fusion)** algorithm
  - +20-30% quality improvement
  - ACTIVE for all queries

### Database Query Implementations
- `query_router/neo4j_queries.py` (10,782 bytes)
  - Cypher queries for graph traversal
  - Relationship queries

- `query_router/postgres_queries.py` (13,959 bytes)
  - SQL queries with pgvector hybrid search
  - Metadata filtering

- `query_router/qdrant_queries.py` (12,494 bytes)
  - Vector similarity search
  - Payload filtering

- `query_router/graphiti_queries.py` (13,402 bytes)
  - Temporal queries (time-aware)
  - Episode search

### Advanced Features (Phase 2)
- `query_router/neo4j_graphrag.py` (13,136 bytes)
  - Unified vector+graph search
  - **DISABLED** (Phase 3) due to 500 errors

- `query_router/graphiti_search.py` (24,527 bytes)
  - Hybrid search with cross-encoder reranking
  - **LIMITED** to 20% of queries (performance)

- `query_router/semantic_cache.py` (12,516 bytes)
  - Similarity-based caching
  - Finds semantically similar queries

### Analytics & Monitoring
- `query_router/analytics.py` (16,069 bytes)
  - Query performance tracking
  - Intent distribution analysis
  - Database utilization metrics

- `query_router/cache.py` (11,146 bytes)
  - Redis-based result caching
  - TTL management

## 🔗 Dependencies

### Depends On:
1. **Database Infrastructure** (01) - All 4 databases for querying
2. **Core Services** (05) - EmbeddingService for semantic operations
3. **Cache Layer** (09) - QueryCache for result storage
4. **Data Models** (06) - Query request/response models

### Optional:
- **Graphiti Service** (if enabled) - Temporal intelligence queries

## 🔌 Interfaces

### Consumed By:
1. **Backend API** (03) - `POST /api/v1/query/` endpoint
2. **Chat Stream** (03) - `search_knowledge_graph` Claude tool

### Provides:
```python
class QueryRouter:
    def execute_query(
        self,
        query: str,
        limit: int = 10,
        filters: dict = None
    ) -> QueryResult:
        """
        Main entry point for query execution.

        Returns: QueryResult with results, metadata, confidence
        """
```

## ⚙️ Configuration

### Phase Control (main.py:154-181)

```python
# From apex-memory-system/src/apex_memory/main.py

router_instance = QueryRouter(
    # Phase 1: Foundation (ACTIVE)
    enable_semantic_classification=False,  # DISABLED - using hybrid
    enable_hybrid_classification=True,     # PRIMARY CLASSIFIER
    enable_query_rewriting=False,          # DISABLED - hurts accuracy
    enable_analytics=True,

    # Phase 2: Intelligent Routing (ACTIVE)
    enable_adaptive_routing=True,
    enable_graphrag=True,
    enable_semantic_cache=True,
    enable_result_fusion=True,             # RRF ALWAYS ON

    # Phase 3: Agentic Evolution (DISABLED)
    enable_complexity_analysis=False,
    enable_multi_router=False,
    enable_self_correction=False,
    enable_query_improvement=False,

    # Phase 4: Advanced Features (DISABLED)
    enable_feature_flags=False,
    enable_online_learning=False,
)
```

### Intent to Database Mapping (router.py:786-791)

```python
# DO NOT MODIFY - Stable after 5-day sprint
INTENT_TO_DATABASES = {
    "graph": ["neo4j", "graphiti"],
    "temporal": ["graphiti", "neo4j"],
    "semantic": ["qdrant", "postgres"],
    "metadata": ["postgres"],
    "hybrid": ["neo4j", "qdrant", "postgres", "graphiti"]
}
```

## 🚀 Query Execution Flow

```
┌─────────────────────────────────────────────────────┐
│ 1. Query Input                                      │
│    "How has ACME Corp changed over the last year?"  │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 2. Intent Classification (3-Tier Fallback)         │
│                                                     │
│    Try Tier 1: Keyword Classifier                  │
│    → Confidence > 0.80? → Intent="temporal"        │
│                                                     │
│    If confidence < 0.80:                           │
│    Try Tier 2: Hybrid Classifier                   │
│    → Confidence > 0.70? → Intent="temporal"        │
│                                                     │
│    If confidence < 0.70:                           │
│    Tier 3: LLM Classifier (Claude Haiku)           │
│    → Final Intent="temporal"                       │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 3. Cache Check (Semantic Similarity)               │
│    → Is this query similar to a cached query?      │
│    → Similarity > 0.90? → Return cached results    │
│    → Cache Miss → Continue to database routing     │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 4. Database Routing                                │
│    Intent="temporal" → Databases: [Graphiti, Neo4j]│
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 5. Parallel Execution                              │
│                                                     │
│    Thread 1: Graphiti.hybrid_search()              │
│    → Returns: 12 temporal results (with dates)     │
│                                                     │
│    Thread 2: Neo4j.temporal_query()                │
│    → Returns: 8 graph results (relationships)      │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 6. Result Fusion (RRF Algorithm)                   │
│    → Combine 12 + 8 = 20 results                   │
│    → Reciprocal Rank Fusion scoring                │
│    → Remove duplicates                             │
│    → Sort by fused score                           │
│    → Top 10 results                                │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 7. Cache & Return                                  │
│    → Store in semantic cache (TTL: 1 hour)         │
│    → Return QueryResult to API                     │
│    {                                                │
│      results: [10 items],                          │
│      metadata: {                                    │
│        intent: "temporal",                         │
│        databases_used: ["graphiti", "neo4j"],      │
│        cache_hit: false,                           │
│        latency_ms: 850                             │
│      }                                              │
│    }                                                │
└─────────────────────────────────────────────────────┘
```

## 📊 Performance Metrics

### Accuracy (October 2025 Testing)

- **Overall Accuracy:** 94-95% (90% target exceeded)
- **Keyword Classifier:** 95%+ accuracy (60% of queries)
- **Hybrid Classifier:** 85-90% accuracy (35% of queries)
- **LLM Classifier:** High accuracy (5% of queries)

### Latency (P50/P90/P99)

| Scenario | P50 | P90 | P99 |
|----------|-----|-----|-----|
| **Cache Hit** | 8ms | 15ms | 30ms |
| **Keyword Path** (no cache) | 350ms | 600ms | 1200ms |
| **Hybrid Path** (no cache) | 600ms | 1000ms | 2000ms |
| **LLM Path** (no cache) | 800ms | 1500ms | 3000ms |

### Cache Performance

- **Hit Rate:** 95% in steady state
- **Semantic Similarity:** 0.90+ threshold
- **TTL:** 1 hour (configurable)

## 🔧 Three Reranking Systems

### 1. ResultFusion (RRF) - ACTIVE (100% queries)

**Location:** `query_router/result_fusion.py`

**Algorithm:**
```python
# Reciprocal Rank Fusion
rrf_score = sum(1 / (rank + k) for each database)
# k = 60 (tuned parameter)
```

**Impact:** +20-30% quality improvement

**Status:** ✅ **ALWAYS ON** - Stable, do not disable

### 2. GraphitiSearch (Cross-Encoder) - LIMITED (20% queries)

**Location:** `query_router/graphiti_search.py`

**Algorithm:** Hybrid search with cross-encoder reranking

**Impact:** High quality but slow (500ms+)

**Status:** ⚠️ **LIMITED** - Only for temporal queries, max 20%

### 3. Neo4jGraphRAG - DISABLED (Phase 3)

**Location:** `query_router/neo4j_graphrag.py`

**Algorithm:** Unified vector+graph search

**Impact:** Caused 500 errors

**Status:** ❌ **DISABLED** - See QUERY-ROUTER-STATE.md

## 🚨 Critical Warnings

### DO NOT Enable Phase 3 Without Investigation

From `main.py:174-177`:
```python
# Phase 3: Agentic Evolution (TEMPORARILY DISABLED - causing 500 errors)
enable_complexity_analysis=False,
enable_multi_router=False,
enable_self_correction=False,
enable_query_improvement=False,
```

**Reason:** Query rewriting regression (-0.7 points accuracy)

**Before Re-enabling:**
1. Read QUERY-ROUTER-STATE.md
2. Investigate root cause of 500 errors
3. Test with query_router test suite (90 tests)
4. Compare accuracy before/after

### DO NOT Modify Intent Mapping

From `router.py:786-791` - **Stable after 5-day sprint**

Changing this mapping will affect 90% accuracy achievement.

## 🔬 Testing

### Query Router Test Suite

```bash
cd apex-memory-system

# Run all query router tests (90 tests)
pytest tests/unit/test_query_router*.py -v

# Test specific classifier
pytest tests/unit/test_keyword_classifier.py -v
pytest tests/unit/test_hybrid_classifier.py -v

# Integration tests (requires running databases)
pytest tests/integration/test_query_execution.py -v

# Performance tests
pytest tests/performance/test_query_latency.py -v
```

### Manual Testing

```bash
# Explain query routing
curl -X GET "http://localhost:8000/api/v1/query/explain?query=How%20has%20ACME%20changed" | jq

# Execute query
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query":"What is connected to ACME?","limit":10}' | jq

# Check cache stats
curl http://localhost:8000/api/v1/query/cache/stats | jq
```

## 📚 Documentation References

**MUST READ:**
- `QUERY-ROUTER-STATE.md` - Phase 3-4 disabled state, three reranking systems
- `research/architecture-decisions/ADR-002-query-router-architecture.md` - Design decisions
- `monitoring/query-router/PERFORMANCE.md` - 90% accuracy achievement

---

**Previous Component:** [03-Backend-API](../03-Backend-API/README.md)
**Next Component:** [05-Core-Services](../05-Core-Services/README.md)
