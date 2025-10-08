# Query Router Improvement Plan

**Status:** Planning
**Priority:** High
**Timeline:** 8 weeks (Phased Implementation)
**Last Updated:** October 7, 2025

---

## Executive Summary

After comprehensive research into state-of-the-art query routing systems (October 2025), we've identified **10 critical flaws** in Apex's current query router and designed a **4-phase improvement roadmap** to bring it to 2025 standards.

**Expected Gains:**
- **+21-28 points** relevance improvement (query rewriting)
- **90ms faster** routing decisions (semantic classification)
- **15-30%** accuracy improvement (adaptive weights)
- **99% precision** on relationship queries (GraphRAG)
- **90%+ cache hit** rate (semantic caching)

**Research Foundation:**
- 📚 [Semantic Router](../../research/documentation/query-routing/semantic-router.md) - 10ms intent classification
- 📚 [Query Rewriting](../../research/documentation/query-routing/query-rewriting-rag.md) - Microsoft +21 point improvement
- 📚 [Agentic RAG](../../research/documentation/query-routing/agentic-rag-2025.md) - 2025 paradigm shift
- 📚 [Adaptive Routing](../../research/documentation/query-routing/adaptive-routing-learning.md) - Learned weights
- 📚 [GraphRAG](../../research/documentation/query-routing/graphrag-hybrid-search.md) - 99% precision hybrid search

---

## Table of Contents

1. [Critical Flaws Identified](#critical-flaws-identified)
2. [Phase 1: Foundation Upgrades](#phase-1-foundation-upgrades-week-1-2)
3. [Phase 2: Intelligent Routing](#phase-2-intelligent-routing-week-3-4)
4. [Phase 3: Agentic Evolution](#phase-3-agentic-evolution-week-5-6)
5. [Phase 4: Advanced Features](#phase-4-advanced-features-week-7-8)
6. [Quick Wins](#quick-wins-immediate-implementation)
7. [Competitive Analysis](#competitive-analysis)
8. [Implementation Guidelines](#implementation-guidelines)
9. [Success Metrics](#success-metrics)
10. [References](#references)

---

## Critical Flaws Identified

### 🔴 Flaw #1: Brittle Keyword-Based Classification

**Current Implementation:** [`analyzer.py:62-86`](../../../apex-memory-system/src/apex_memory/query_router/analyzer.py)

```python
# Hardcoded keyword sets
GRAPH_KEYWORDS = {"related", "relationship", "connected", ...}
TEMPORAL_KEYWORDS = {"changed", "evolved", "history", ...}
```

**Problems:**
- 63.64% potential misclassification rate ([Research](../../research/documentation/query-routing/semantic-router.md#advantages-over-keyword-matching))
- Can't handle synonyms or paraphrasing
- No semantic understanding
- Brittle to wording changes

**Solution:** Semantic intent classification using embeddings
- **Research:** [Semantic Router](../../research/documentation/query-routing/semantic-router.md)
- **Technology:** aurelio-labs/semantic-router (10ms decisions)
- **Implementation:** Phase 1.1

---

### 🔴 Flaw #2: No Query Rewriting

**Current Implementation:** Raw queries passed directly to databases

**Problems:**
- Missing +21-28 point relevance improvement ([Microsoft Research](../../research/documentation/query-routing/query-rewriting-rag.md#state-of-the-art-microsoft-azure-ai-2024))
- No handling of imprecise language
- No query expansion or decomposition
- Suboptimal retrieval

**Solution:** Multi-strategy query rewriting
- **Research:** [Query Rewriting for RAG](../../research/documentation/query-routing/query-rewriting-rag.md)
- **Techniques:** HyDE, decomposition, normalization, expansion
- **Implementation:** Phase 1.2

---

### 🔴 Flaw #3: Static Score Weights (No Learning)

**Current Implementation:** [`aggregator.py:54-59`](../../../apex-memory-system/src/apex_memory/query_router/aggregator.py)

```python
self.score_weights = {
    "qdrant": 0.4,    # Why 40%?
    "postgres": 0.3,  # Why 30%?
    "neo4j": 0.2,     # Why 20%?
    "graphiti": 0.1,  # Why 10%?
}
```

**Problems:**
- No data-driven justification
- Same weights for all query types
- No adaptation to performance
- Suboptimal for many queries

**Solution:** Adaptive learned weights
- **Research:** [Adaptive Routing with Learned Weights](../../research/documentation/query-routing/adaptive-routing-learning.md)
- **Technology:** Contextual bandits (PILOT system), Matrix factorization
- **Performance:** +15-30% accuracy improvement
- **Implementation:** Phase 2.1

---

### 🔴 Flaw #4: No Agentic Decision-Making

**Current Implementation:** Static rule-based routing

**Problems:**
- Can't adapt to query complexity
- No self-correction
- No planning or reflection
- One-shot retrieval only

**Solution:** Agentic RAG with autonomous agents
- **Research:** [Agentic RAG 2025](../../research/documentation/query-routing/agentic-rag-2025.md)
- **Capabilities:** Reflection, planning, tool use, multi-agent collaboration
- **Performance:** 85-95% accuracy (vs 70-75% static)
- **Implementation:** Phase 3

---

### 🔴 Flaw #5: Hybrid Query Overkill

**Current Implementation:** [`analyzer.py:218-251`](../../../apex-memory-system/src/apex_memory/query_router/analyzer.py)

When multiple query types score similarly → route to ALL databases

**Problems:**
- Inefficient: Why query Qdrant for pure graph traversal?
- Wastes resources and adds latency
- No cost-benefit analysis
- Poor database selection

**Solution:** Query complexity analysis + confidence-based routing
- **Research:** [Agentic RAG - Adaptive Routing](../../research/documentation/query-routing/agentic-rag-2025.md#adaptive-rag-2025)
- **Implementation:** Phase 3.1

---

### 🔴 Flaw #6: No Out-of-Scope Detection

**Current Implementation:** [`analyzer.py:174-216`](../../../apex-memory-system/src/apex_memory/query_router/analyzer.py)

Unknown queries → default to `SEMANTIC`

**Problems:**
- Can't detect irrelevant queries
- Wastes resources on bad queries
- No filtering of nonsense
- Poor user experience

**Solution:** Out-of-scope detection
- **Research:** [Semantic Router - OOS Detection](../../research/documentation/query-routing/semantic-router.md#out-of-scope-detection)
- **Behavior:** Return `None` for irrelevant queries
- **Implementation:** Quick Win #3

---

### 🔴 Flaw #7: No GraphRAG Integration

**Current Implementation:** Graph (Neo4j) and Vector (Qdrant) are completely separate

**Problems:**
- Two separate queries = 2x latency
- Complex merging logic
- Relationship context lost in vector results
- Misses 99% precision opportunity

**Solution:** Unified GraphRAG hybrid search
- **Research:** [GraphRAG Hybrid Search](../../research/documentation/query-routing/graphrag-hybrid-search.md)
- **Performance:** 99% precision on relationship queries
- **Technology:** Neo4j vector index OR unified GraphRAG DB
- **Implementation:** Phase 2.2

---

### 🔴 Flaw #8: Simple Cache Strategy

**Current Implementation:** [`cache.py:51-74`](../../../apex-memory-system/src/apex_memory/query_router/cache.py)

Exact query text match only

**Problems:**
- Misses semantically similar queries
- "What trucks are at ACME?" ≠ "Which trucks at ACME Corp?"
- Low cache hit rate potential
- Inefficient cache utilization

**Solution:** Semantic caching with similarity thresholds
- **Research:** [Adaptive Routing - Semantic Caching](../../research/documentation/query-routing/adaptive-routing-learning.md#implementation-roadmap-for-apex)
- **Target:** 75% → 90%+ cache hit rate
- **Implementation:** Phase 2.3

---

### 🔴 Flaw #9: No Routing Analytics

**Current Implementation:** No tracking of routing decisions

**Problems:**
- Can't optimize without data
- No performance insights
- No A/B testing capability
- No feedback loop

**Solution:** Comprehensive routing analytics
- **Research:** [Adaptive Routing - Data Collection](../../research/documentation/query-routing/adaptive-routing-learning.md#phase-1-data-collection-week-1)
- **Metrics:** Accuracy, latency, relevance, cost, user satisfaction
- **Implementation:** Quick Win #2 + Phase 1.3

---

### 🔴 Flaw #10: Manual Weight Tuning

**Current Implementation:** [`analyzer.py:188-190`](../../../apex-memory-system/src/apex_memory/query_router/analyzer.py)

Temporal keywords get 2x weight (hardcoded)

**Problems:**
- Why 2x? No justification
- No data-driven approach
- Can't optimize
- Suboptimal for many queries

**Solution:** Threshold optimization with training data
- **Research:** [Semantic Router - Route Optimization](../../research/documentation/query-routing/semantic-router.md#performance-benchmarks)
- **Approach:** Learn optimal thresholds from production data
- **Implementation:** Phase 2.1

---

## Phase 1: Foundation Upgrades (Week 1-2)

### 1.1 Semantic Intent Classification

**Goal:** Replace keyword matching with embedding-based routing

**Research:** [Semantic Router Documentation](../../research/documentation/query-routing/semantic-router.md)

**Implementation:**

```python
# File: src/apex_memory/query_router/semantic_classifier.py

from semantic_router import Route, SemanticRouter
from semantic_router.encoders import OpenAIEncoder

class SemanticIntentClassifier:
    """Semantic intent classification using embeddings."""

    def __init__(self, openai_api_key: str):
        # Define routes with example utterances
        self.routes = [
            Route(
                name="graph",
                utterances=[
                    "what equipment is connected to ACME Corp",
                    "show me relationships between customer and invoices",
                    "how are drivers linked to trucks",
                    "find all entities related to Invoice 123",
                    "what is connected to this customer"
                ],
                score_threshold=0.75
            ),
            Route(
                name="temporal",
                utterances=[
                    "how has payment behavior changed over time",
                    "show me the history of customer interactions",
                    "what trends emerged in Q1 vs Q2",
                    "when did the invoice status change",
                    "track the evolution of this entity"
                ],
                score_threshold=0.70
            ),
            Route(
                name="semantic",
                utterances=[
                    "find documents similar to this invoice",
                    "search for content about equipment maintenance",
                    "documents related to payment issues",
                    "find similar customer profiles",
                    "search for relevant reports"
                ],
                score_threshold=0.75
            ),
            Route(
                name="metadata",
                utterances=[
                    "show me all overdue invoices",
                    "filter documents by type PDF",
                    "invoices created after January 1",
                    "documents authored by John Smith",
                    "find all pending status records"
                ],
                score_threshold=0.70
            )
        ]

        # Initialize router with OpenAI encoder (already in Apex)
        self.encoder = OpenAIEncoder(api_key=openai_api_key)
        self.router = SemanticRouter(
            encoder=self.encoder,
            routes=self.routes,
            auto_sync="local"
        )

    def classify(self, query_text: str) -> Optional[str]:
        """
        Classify query intent using semantic similarity.

        Returns:
            Route name or None for out-of-scope queries
        """
        route = self.router(query_text)

        if route is None:
            # Out-of-scope query
            return None

        return route.name
```

**Integration with Existing Analyzer:**

```python
# File: src/apex_memory/query_router/analyzer.py

class QueryAnalyzer:
    def __init__(self, use_semantic_classification: bool = True):
        self.use_semantic = use_semantic_classification

        if self.use_semantic:
            self.semantic_classifier = SemanticIntentClassifier(
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )

    def _detect_query_type(self, query_lower: str) -> QueryType:
        """Detect query type with semantic classification."""

        if self.use_semantic:
            # Try semantic classification first
            route_name = self.semantic_classifier.classify(query_lower)

            if route_name is None:
                # Out-of-scope - return None or raise
                logger.warning(f"Out-of-scope query: {query_lower}")
                return None  # Handle in caller

            # Map route name to QueryType
            return QueryType(route_name)

        # Fallback to keyword-based (current implementation)
        return self._keyword_based_classification(query_lower)
```

**Testing:**

```python
# File: tests/unit/test_semantic_classifier.py

def test_semantic_classification():
    classifier = SemanticIntentClassifier(api_key=TEST_API_KEY)

    # Test graph queries
    assert classifier.classify("what is connected to ACME Corp") == "graph"
    assert classifier.classify("show relationships") == "graph"

    # Test temporal queries
    assert classifier.classify("how did this change over time") == "temporal"
    assert classifier.classify("payment trends last 6 months") == "temporal"

    # Test out-of-scope
    assert classifier.classify("what is the weather today") is None
    assert classifier.classify("llama 2 training data") is None
```

**Performance Target:** <10ms routing decision

**Rollout Strategy:**
1. Deploy alongside keyword classifier (A/B test 10% traffic)
2. Compare accuracy metrics
3. Gradually increase to 100% if accuracy > keyword + 5%

---

### 1.2 Query Rewriting Pipeline

**Goal:** Implement multi-strategy query rewriting for better retrieval

**Research:** [Query Rewriting Documentation](../../research/documentation/query-routing/query-rewriting-rag.md)

**Implementation:**

```python
# File: src/apex_memory/query_router/query_rewriter.py

from typing import List, Optional
from enum import Enum

class RewriteStrategy(Enum):
    NORMALIZATION = "normalization"
    HYDE = "hyde"
    DECOMPOSITION = "decomposition"
    EXPANSION = "expansion"

class QueryRewriter:
    """Multi-strategy query rewriting for RAG optimization."""

    def __init__(self, llm_service, embedding_service):
        self.llm = llm_service
        self.embeddings = embedding_service

    def rewrite(
        self,
        query: str,
        query_type: QueryType,
        strategies: Optional[List[RewriteStrategy]] = None
    ) -> List[str]:
        """
        Rewrite query using multiple strategies.

        Args:
            query: Original query
            query_type: Intent-based query type
            strategies: List of strategies to apply (auto-select if None)

        Returns:
            List of rewritten queries (original + variations)
        """
        if strategies is None:
            strategies = self._auto_select_strategies(query_type)

        rewrites = [query]  # Always include original

        for strategy in strategies:
            if strategy == RewriteStrategy.NORMALIZATION:
                rewrites.append(self._normalize(query))

            elif strategy == RewriteStrategy.HYDE:
                rewrites.append(self._hyde(query))

            elif strategy == RewriteStrategy.DECOMPOSITION:
                rewrites.extend(self._decompose(query))

            elif strategy == RewriteStrategy.EXPANSION:
                rewrites.append(self._expand(query))

        # Deduplicate
        return list(set(rewrites))

    def _normalize(self, query: str) -> str:
        """Fix grammar, spelling, standardize."""
        # Simple normalization
        normalized = query.strip().lower()
        # TODO: Add spell checker, grammar fixer
        return normalized

    def _hyde(self, query: str) -> str:
        """Generate hypothetical answer, use for search."""
        prompt = f"""Write a concise passage that answers this question:
Question: {query}
Answer:"""

        hypothetical_answer = self.llm.generate(prompt, max_tokens=200)
        return hypothetical_answer

    def _decompose(self, query: str) -> List[str]:
        """Break complex query into sub-queries."""
        if len(query.split()) < 10:
            # Too short to decompose
            return []

        prompt = f"""Break this complex question into 2-3 simpler sub-questions:
Question: {query}
Sub-questions:
1."""

        decomposed = self.llm.generate(prompt, max_tokens=300)
        sub_queries = self._parse_numbered_list(decomposed)
        return sub_queries

    def _expand(self, query: str) -> str:
        """Expand with synonyms and related terms."""
        # Extract key terms
        terms = self._extract_key_terms(query)

        # Get synonyms (simple approach)
        expanded_terms = []
        for term in terms:
            synonyms = self._get_synonyms(term)
            expanded_terms.extend(synonyms)

        # Reconstruct query with expansions
        return f"{query} {' '.join(expanded_terms)}"

    def _auto_select_strategies(self, query_type: QueryType) -> List[RewriteStrategy]:
        """Auto-select rewrite strategies based on query type."""
        # Always normalize
        strategies = [RewriteStrategy.NORMALIZATION]

        if query_type == QueryType.SEMANTIC:
            # HyDE works best for semantic search
            strategies.append(RewriteStrategy.HYDE)

        elif query_type == QueryType.HYBRID:
            # Decompose complex queries
            strategies.append(RewriteStrategy.DECOMPOSITION)

        elif query_type == QueryType.METADATA:
            # Expand with metadata terms
            strategies.append(RewriteStrategy.EXPANSION)

        return strategies
```

**Integration:**

```python
# File: src/apex_memory/query_router/router.py

class QueryRouter:
    def __init__(self, ...):
        self.query_rewriter = QueryRewriter(llm_service, embedding_service)

    def query(self, query_text: str, ...):
        # Step 1: Analyze intent
        intent = self.analyzer.analyze(query_text)

        # Step 1.5: Rewrite query
        rewrites = self.query_rewriter.rewrite(
            query_text,
            intent.query_type
        )

        # Use best rewrite (or multiple for diversity)
        best_rewrite = rewrites[0]  # Start with original
        if len(rewrites) > 1:
            best_rewrite = self._select_best_rewrite(rewrites, intent)

        # Continue with rewritten query
        intent.query_text = best_rewrite
        ...
```

**Performance Target:** +21-28 point relevance improvement

---

### 1.3 Routing Analytics & Telemetry

**Goal:** Track all routing decisions for optimization with production-grade observability

**Research:** [Adaptive Routing - Data Collection](../../research/documentation/query-routing/adaptive-routing-learning.md#phase-1-data-collection-week-1)

**Implementation:**

```python
# File: src/apex_memory/query_router/analytics.py

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import json
from prometheus_client import Counter, Histogram, Gauge
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Prometheus Metrics
routing_requests_total = Counter(
    'apex_routing_requests_total',
    'Total number of routing requests',
    ['intent', 'cached']
)

routing_latency = Histogram(
    'apex_routing_latency_seconds',
    'Routing decision latency in seconds',
    ['intent', 'databases']
)

routing_accuracy = Gauge(
    'apex_routing_accuracy',
    'Routing accuracy score',
    ['intent']
)

database_query_latency = Histogram(
    'apex_database_query_latency_seconds',
    'Database query latency in seconds',
    ['database', 'query_type']
)

# Jaeger Distributed Tracing
tracer_provider = TracerProvider()
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

@dataclass
class RoutingDecision:
    """Record of a single routing decision."""
    timestamp: datetime
    query: str
    intent: str
    databases_used: List[str]
    databases_scores: Dict[str, float]
    database_latencies: Dict[str, float]  # NEW: Per-database timing
    num_results: int
    avg_relevance: float
    latency_ms: float
    cached: bool
    trace_id: Optional[str] = None  # NEW: Jaeger trace ID
    user_clicked: Optional[bool] = None
    user_satisfaction: Optional[float] = None

class RoutingAnalytics:
    """Track and analyze routing decisions with Prometheus + Jaeger."""

    def __init__(self, postgres_conn):
        self.db = postgres_conn
        self.tracer = tracer
        self._create_tables()

    def _create_tables(self):
        """Create analytics tables."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS routing_decisions (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                query TEXT NOT NULL,
                intent VARCHAR(50) NOT NULL,
                databases_used TEXT[] NOT NULL,
                database_scores JSONB NOT NULL,
                database_latencies JSONB NOT NULL,
                num_results INTEGER NOT NULL,
                avg_relevance FLOAT,
                latency_ms FLOAT NOT NULL,
                cached BOOLEAN NOT NULL,
                trace_id VARCHAR(64),
                user_clicked BOOLEAN,
                user_satisfaction FLOAT
            );

            CREATE INDEX idx_routing_timestamp ON routing_decisions(timestamp);
            CREATE INDEX idx_routing_intent ON routing_decisions(intent);
            CREATE INDEX idx_routing_trace_id ON routing_decisions(trace_id);
        """)

    def log_decision(
        self,
        query: str,
        intent: QueryIntent,
        databases_used: List[str],
        database_scores: Dict[str, float],
        database_latencies: Dict[str, float],
        results: List[AggregatedResult],
        latency_ms: float,
        cached: bool,
        trace_id: Optional[str] = None
    ):
        """Log a routing decision with Prometheus metrics and Jaeger tracing."""
        avg_relevance = (
            sum(r.relevance for r in results) / len(results)
            if results else 0.0
        )

        # Update Prometheus metrics
        routing_requests_total.labels(
            intent=intent.query_type.value,
            cached=cached
        ).inc()

        routing_latency.labels(
            intent=intent.query_type.value,
            databases=",".join(sorted(databases_used))
        ).observe(latency_ms / 1000.0)

        routing_accuracy.labels(
            intent=intent.query_type.value
        ).set(avg_relevance)

        # Track per-database latency
        for db, db_latency in database_latencies.items():
            database_query_latency.labels(
                database=db,
                query_type=intent.query_type.value
            ).observe(db_latency / 1000.0)

        # Store in PostgreSQL
        self.db.execute("""
            INSERT INTO routing_decisions (
                timestamp, query, intent, databases_used,
                database_scores, database_latencies, num_results,
                avg_relevance, latency_ms, cached, trace_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datetime.now(),
            query,
            intent.query_type.value,
            databases_used,
            json.dumps(database_scores),
            json.dumps(database_latencies),
            len(results),
            avg_relevance,
            latency_ms,
            cached,
            trace_id
        ))

    def get_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get routing metrics for date range."""
        result = self.db.fetch_one("""
            SELECT
                COUNT(*) as total_queries,
                AVG(latency_ms) as avg_latency,
                AVG(avg_relevance) as avg_relevance,
                SUM(CASE WHEN cached THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as cache_hit_rate,
                AVG(num_results) as avg_results
            FROM routing_decisions
            WHERE timestamp BETWEEN %s AND %s
        """, (start_date, end_date))

        return dict(result)

    def get_intent_breakdown(self) -> Dict[str, int]:
        """Get query count by intent type."""
        results = self.db.fetch_all("""
            SELECT intent, COUNT(*) as count
            FROM routing_decisions
            GROUP BY intent
            ORDER BY count DESC
        """)

        return {row['intent']: row['count'] for row in results}
```

**Router Integration with Jaeger Tracing:**

```python
# File: src/apex_memory/query_router/router.py

class QueryRouter:
    def __init__(self, ...):
        self.analytics = RoutingAnalytics(postgres_conn)
        self.tracer = tracer

    async def query(self, query_text: str, ...):
        # Start Jaeger trace
        with self.tracer.start_as_current_span("query_routing") as span:
            span.set_attribute("query", query_text)
            trace_id = format(span.get_span_context().trace_id, '032x')

            start_time = time.time()
            database_latencies = {}

            # Analyze intent
            with self.tracer.start_as_current_span("intent_analysis"):
                intent = self.analyzer.analyze(query_text)
                span.set_attribute("intent", intent.query_type.value)

            # Rewrite query
            with self.tracer.start_as_current_span("query_rewriting"):
                rewrites = self.query_rewriter.rewrite(query_text, intent.query_type)

            # Route to databases
            with self.tracer.start_as_current_span("database_routing") as routing_span:
                for db in intent.databases:
                    db_start = time.time()
                    with self.tracer.start_as_current_span(f"query_{db}"):
                        results[db] = await self._query_database(db, embedding)
                    database_latencies[db] = (time.time() - db_start) * 1000

            latency_ms = (time.time() - start_time) * 1000

            # Log with trace ID
            self.analytics.log_decision(
                query=query_text,
                intent=intent,
                databases_used=list(intent.databases),
                database_scores=database_scores,
                database_latencies=database_latencies,
                results=aggregated_results,
                latency_ms=latency_ms,
                cached=use_cache,
                trace_id=trace_id
            )

            span.set_attribute("latency_ms", latency_ms)
            span.set_attribute("num_results", len(aggregated_results))

            return aggregated_results
```

**Dashboard API:**

```python
# File: src/apex_memory/api/analytics.py

@router.get("/analytics/routing/metrics")
async def get_routing_metrics(
    start_date: datetime,
    end_date: datetime,
    analytics: RoutingAnalytics = Depends(get_analytics)
):
    """Get routing performance metrics."""
    return analytics.get_metrics(start_date, end_date)

@router.get("/analytics/routing/intent-breakdown")
async def get_intent_breakdown(
    analytics: RoutingAnalytics = Depends(get_analytics)
):
    """Get query distribution by intent."""
    return analytics.get_intent_breakdown()

@router.get("/analytics/routing/trace/{trace_id}")
async def get_trace_details(
    trace_id: str,
    analytics: RoutingAnalytics = Depends(get_analytics)
):
    """Get detailed trace for debugging (links to Jaeger UI)."""
    return {
        "trace_id": trace_id,
        "jaeger_url": f"http://localhost:16686/trace/{trace_id}",
        "decision": analytics.get_decision_by_trace(trace_id)
    }
```

**Grafana Dashboard Configuration:**

Create dashboard with panels for:
- Query throughput (requests/sec by intent)
- P50/P95/P99 latency by database
- Cache hit rate over time
- Routing accuracy by intent
- Database latency heatmap
- Error rate and anomaly detection

---

## Phase 2: Intelligent Routing (Week 3-4)

### 2.1 Adaptive Score Weighting

**Goal:** Learn optimal database weights from production data

**Research:** [Adaptive Routing with Learned Weights](../../research/documentation/query-routing/adaptive-routing-learning.md#1-contextual-bandits-for-llm-routing)

**Implementation:** Contextual Bandit (LinUCB) approach

```python
# File: src/apex_memory/query_router/adaptive_weights.py

import numpy as np
from typing import Dict, List

class ContextualBandit:
    """LinUCB algorithm for adaptive database routing."""

    def __init__(self, n_databases: int, embedding_dim: int, alpha: float = 1.0):
        """
        Args:
            n_databases: Number of databases
            embedding_dim: Query embedding dimension
            alpha: Exploration parameter (higher = more exploration)
        """
        self.n_databases = n_databases
        self.alpha = alpha

        # Initialize parameters for each database
        self.A = [np.identity(embedding_dim) for _ in range(n_databases)]
        self.b = [np.zeros(embedding_dim) for _ in range(n_databases)]
        self.theta = [np.zeros(embedding_dim) for _ in range(n_databases)]

    def select_databases(
        self,
        query_embedding: np.ndarray,
        k: int = 1
    ) -> List[int]:
        """
        Select top-k databases for query.

        Args:
            query_embedding: Query vector
            k: Number of databases to select

        Returns:
            List of database indices
        """
        scores = []

        for db_idx in range(self.n_databases):
            # Compute UCB score
            A_inv = np.linalg.inv(self.A[db_idx])
            theta = A_inv @ self.b[db_idx]

            # Expected reward
            expected_reward = theta @ query_embedding

            # Uncertainty bonus
            uncertainty = self.alpha * np.sqrt(
                query_embedding @ A_inv @ query_embedding
            )

            # UCB score = expected + uncertainty
            ucb_score = expected_reward + uncertainty

            scores.append((db_idx, ucb_score))

        # Sort by score, return top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return [db_idx for db_idx, _ in scores[:k]]

    def update(
        self,
        query_embedding: np.ndarray,
        db_idx: int,
        reward: float
    ):
        """
        Update model based on feedback.

        Args:
            query_embedding: Query vector
            db_idx: Database index
            reward: Reward signal (0-1, higher is better)
        """
        self.A[db_idx] += np.outer(query_embedding, query_embedding)
        self.b[db_idx] += reward * query_embedding

        # Recompute theta
        A_inv = np.linalg.inv(self.A[db_idx])
        self.theta[db_idx] = A_inv @ self.b[db_idx]
```

**Integration:**

```python
# File: src/apex_memory/query_router/router.py

class QueryRouter:
    def __init__(self, ...):
        self.use_adaptive_weights = True

        if self.use_adaptive_weights:
            self.bandit = ContextualBandit(
                n_databases=4,  # neo4j, postgres, qdrant, graphiti
                embedding_dim=1536,  # OpenAI embedding size
                alpha=0.5  # Exploration parameter
            )

    def query(self, query_text: str, ...):
        # ... existing code ...

        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query_text)

        # Select databases using bandit
        if self.use_adaptive_weights:
            db_indices = self.bandit.select_databases(query_embedding, k=2)
            databases = [DB_NAMES[idx] for idx in db_indices]
        else:
            databases = intent.databases

        # Execute queries
        results = self._route_query(databases, query_embedding)

        # Compute reward from results
        reward = self._compute_reward(results)

        # Update bandit model
        if self.use_adaptive_weights:
            for db_idx in db_indices:
                self.bandit.update(query_embedding, db_idx, reward)

        return results

    def _compute_reward(self, results: List[AggregatedResult]) -> float:
        """Compute reward from retrieval results."""
        if not results:
            return 0.0

        # Factors:
        # - Average relevance (0-1)
        # - Coverage (found docs / expected docs)
        # - Diversity (unique sources)

        avg_relevance = sum(r.relevance for r in results) / len(results)
        coverage = min(len(results) / 10, 1.0)  # Expect 10 results
        diversity = len(set(r.sources for r in results)) / 4  # 4 databases

        reward = (avg_relevance * 0.6) + (coverage * 0.3) + (diversity * 0.1)

        return reward
```

**Performance Target:** +15-30% accuracy improvement over static weights

---

### 2.2 GraphRAG Hybrid Search

**Goal:** Unified graph + vector search for 99% precision

**Research:** [GraphRAG Hybrid Search](../../research/documentation/query-routing/graphrag-hybrid-search.md)

**Option A: Neo4j Vector Index (Recommended)**

```python
# File: src/apex_memory/database/neo4j_graphrag.py

from neo4j import GraphDatabase
from typing import List, Dict, Optional
import numpy as np

class Neo4jGraphRAG:
    """Unified graph + vector search in Neo4j."""

    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._create_vector_index()

    def _create_vector_index(self):
        """Create vector index on Document nodes."""
        with self.driver.session() as session:
            # Create vector index if not exists
            session.run("""
                CREATE VECTOR INDEX document_embeddings IF NOT EXISTS
                FOR (d:Document)
                ON d.embedding
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: 1536,
                        `vector.similarity_function`: 'cosine'
                    }
                }
            """)

    def hybrid_search(
        self,
        query_embedding: List[float],
        query_entities: Optional[List[str]] = None,
        limit: int = 10,
        semantic_weight: float = 0.6,
        graph_weight: float = 0.4
    ) -> List[Dict]:
        """
        Hybrid vector + graph search.

        Args:
            query_embedding: Query vector
            query_entities: Optional entities to traverse from
            limit: Max results
            semantic_weight: Weight for semantic similarity (0-1)
            graph_weight: Weight for graph centrality (0-1)

        Returns:
            List of results with combined scores
        """
        with self.driver.session() as session:
            if query_entities:
                # Graph-enhanced vector search
                query = """
                    // Vector search
                    CALL db.index.vector.queryNodes(
                        'document_embeddings',
                        $limit * 3,  // Get more candidates
                        $embedding
                    ) YIELD node, score

                    // Graph traversal from entities
                    OPTIONAL MATCH (node)-[r]-(entity)
                    WHERE entity.name IN $entities

                    // Compute graph score (centrality)
                    WITH node, score,
                         COUNT(DISTINCT r) as relationships,
                         COUNT(DISTINCT entity) as matched_entities

                    // Combined scoring
                    WITH node, score,
                         relationships,
                         matched_entities,
                         (score * $semantic_weight +
                          (relationships / 10.0) * $graph_weight * 0.5 +
                          (matched_entities / SIZE($entities)) * $graph_weight * 0.5
                         ) as final_score

                    RETURN
                        node.uuid as uuid,
                        node.title as title,
                        node.content as content,
                        score as semantic_score,
                        relationships,
                        matched_entities,
                        final_score
                    ORDER BY final_score DESC
                    LIMIT $limit
                """

                result = session.run(
                    query,
                    embedding=query_embedding,
                    entities=query_entities,
                    limit=limit,
                    semantic_weight=semantic_weight,
                    graph_weight=graph_weight
                )
            else:
                # Pure vector search with graph enrichment
                query = """
                    CALL db.index.vector.queryNodes(
                        'document_embeddings',
                        $limit,
                        $embedding
                    ) YIELD node, score

                    // Enrich with relationships
                    OPTIONAL MATCH (node)-[r]-(connected)
                    WITH node, score, COLLECT(DISTINCT connected) as connections

                    RETURN
                        node.uuid as uuid,
                        node.title as title,
                        node.content as content,
                        score as semantic_score,
                        SIZE(connections) as num_connections,
                        connections[0..5] as sample_connections
                    ORDER BY score DESC
                """

                result = session.run(
                    query,
                    embedding=query_embedding,
                    limit=limit
                )

            return [dict(record) for record in result]
```

**Integration:**

```python
# File: src/apex_memory/query_router/router.py

class QueryRouter:
    def __init__(self, ...):
        # Add GraphRAG searcher
        self.graphrag = Neo4jGraphRAG(
            uri=NEO4J_URI,
            user=NEO4J_USER,
            password=NEO4J_PASSWORD
        )

    def _route_query(self, intent, query_embedding):
        results = {}

        # Use GraphRAG for graph + semantic queries
        if "neo4j" in intent.databases and "qdrant" in intent.databases:
            # Hybrid graph + vector
            graphrag_results = self.graphrag.hybrid_search(
                query_embedding=query_embedding,
                query_entities=intent.entities,
                limit=intent.limit
            )
            results["graphrag"] = graphrag_results

        elif "neo4j" in intent.databases:
            # Graph-only (but can still use vector for ranking)
            results["neo4j"] = self.neo4j_builder.execute_query(...)

        # ... rest of routing ...

        return results
```

**Performance Target:** 99% precision on relationship queries

---

### 2.3 Semantic Caching

**Goal:** Cache similar queries, not just exact matches

**Implementation:**

```python
# File: src/apex_memory/query_router/semantic_cache.py

import numpy as np
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta

class SemanticCache:
    """Semantic caching with similarity thresholds."""

    def __init__(
        self,
        redis_client,
        embedding_service,
        similarity_threshold: float = 0.95
    ):
        self.redis = redis_client
        self.embeddings = embedding_service
        self.threshold = similarity_threshold

    def get(self, query: str, query_embedding: Optional[np.ndarray] = None) -> Optional[Dict]:
        """
        Get cached result for query or similar query.

        Args:
            query: Query text
            query_embedding: Optional pre-computed embedding

        Returns:
            Cached result or None
        """
        # Try exact match first
        exact_key = f"cache:exact:{query.lower()}"
        exact_cached = self.redis.get(exact_key)

        if exact_cached:
            return json.loads(exact_cached)

        # Semantic similarity search
        if query_embedding is None:
            query_embedding = self.embeddings.generate_embedding(query)

        # Get all cached query embeddings
        cached_queries = self._get_cached_query_embeddings()

        # Find most similar
        best_match, best_similarity = self._find_most_similar(
            query_embedding,
            cached_queries
        )

        if best_similarity >= self.threshold:
            # Similar enough - return cached result
            cache_key = f"cache:semantic:{best_match['query_hash']}"
            cached = self.redis.get(cache_key)

            if cached:
                return json.loads(cached)

        return None

    def set(
        self,
        query: str,
        result: Dict,
        query_embedding: Optional[np.ndarray] = None,
        ttl: int = 600
    ):
        """Cache query result with both exact and semantic indexing."""
        # Exact match cache
        exact_key = f"cache:exact:{query.lower()}"
        self.redis.setex(exact_key, ttl, json.dumps(result))

        # Semantic cache
        if query_embedding is None:
            query_embedding = self.embeddings.generate_embedding(query)

        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]

        # Store embedding for similarity search
        self._store_query_embedding(query, query_hash, query_embedding, ttl)

        # Store result
        semantic_key = f"cache:semantic:{query_hash}"
        self.redis.setex(semantic_key, ttl, json.dumps(result))

    def _find_most_similar(
        self,
        query_embedding: np.ndarray,
        cached_queries: List[Dict]
    ) -> Tuple[Optional[Dict], float]:
        """Find most similar cached query."""
        if not cached_queries:
            return None, 0.0

        best_match = None
        best_similarity = 0.0

        for cached in cached_queries:
            similarity = np.dot(query_embedding, cached['embedding']) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(cached['embedding'])
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = cached

        return best_match, best_similarity
```

**Performance Target:** 75% → 90%+ cache hit rate

---

## Phase 3: Agentic Evolution (Week 5-6)

### 3.1 Query Complexity Analyzer

**Goal:** Route based on query complexity, not just type

**Research:** [Agentic RAG - Adaptive Routing](../../research/documentation/query-routing/agentic-rag-2025.md#adaptive-rag-2025)

**Implementation:**

```python
# File: src/apex_memory/query_router/complexity_analyzer.py

from enum import Enum
from dataclasses import dataclass

class QueryComplexity(Enum):
    SIMPLE = "simple"      # Single database, straightforward
    MEDIUM = "medium"      # Multi-database, standard
    COMPLEX = "complex"    # Multi-step, requires planning

@dataclass
class ComplexityAnalysis:
    complexity: QueryComplexity
    reasoning: str
    recommended_strategy: str
    estimated_steps: int

class QueryComplexityAnalyzer:
    """Analyze query complexity to determine routing strategy."""

    def analyze(self, query: str, intent: QueryIntent) -> ComplexityAnalysis:
        """Analyze query complexity."""
        complexity_score = 0
        reasoning = []

        # Factor 1: Query length
        word_count = len(query.split())
        if word_count < 5:
            complexity_score += 0
            reasoning.append("short query")
        elif word_count < 15:
            complexity_score += 1
            reasoning.append("medium-length query")
        else:
            complexity_score += 2
            reasoning.append("long query")

        # Factor 2: Number of entities
        num_entities = len(intent.entities)
        complexity_score += min(num_entities, 3)
        if num_entities > 0:
            reasoning.append(f"{num_entities} entities detected")

        # Factor 3: Temporal analysis
        if intent.time_range:
            complexity_score += 1
            reasoning.append("temporal component")

        # Factor 4: Multi-database requirement
        num_databases = len(intent.databases)
        if num_databases > 2:
            complexity_score += 2
            reasoning.append(f"requires {num_databases} databases")

        # Factor 5: Comparison/aggregation keywords
        comparison_keywords = ["compare", "vs", "versus", "difference", "trend"]
        if any(kw in query.lower() for kw in comparison_keywords):
            complexity_score += 2
            reasoning.append("comparison/aggregation required")

        # Determine complexity level
        if complexity_score <= 2:
            complexity = QueryComplexity.SIMPLE
            strategy = "single_database_fast"
            steps = 1
        elif complexity_score <= 5:
            complexity = QueryComplexity.MEDIUM
            strategy = "multi_database_parallel"
            steps = 2
        else:
            complexity = QueryComplexity.COMPLEX
            strategy = "agentic_multi_step"
            steps = 3+

        return ComplexityAnalysis(
            complexity=complexity,
            reasoning=" + ".join(reasoning),
            recommended_strategy=strategy,
            estimated_steps=steps
        )
```

**Routing Strategy:**

```python
# File: src/apex_memory/query_router/router.py

class QueryRouter:
    def query(self, query_text: str, ...):
        # Analyze intent
        intent = self.analyzer.analyze(query_text)

        # Analyze complexity
        complexity = self.complexity_analyzer.analyze(query_text, intent)

        # Route based on complexity
        if complexity.complexity == QueryComplexity.SIMPLE:
            # Fast path: single database
            results = self._simple_route(intent, query_embedding)

        elif complexity.complexity == QueryComplexity.MEDIUM:
            # Standard path: parallel multi-database
            results = self._parallel_route(intent, query_embedding)

        else:  # COMPLEX
            # Agentic path: multi-step reasoning
            results = self._agentic_route(intent, query_text, query_embedding)

        return results

    def _simple_route(self, intent, embedding):
        """Fast single-database routing."""
        best_db = self._select_best_database(intent)
        return self._query_single_database(best_db, embedding)

    def _parallel_route(self, intent, embedding):
        """Parallel multi-database routing."""
        return asyncio.gather(*[
            self._query_database(db, embedding)
            for db in intent.databases
        ])

    def _agentic_route(self, intent, query, embedding):
        """Multi-step agentic routing with planning."""
        # Decompose query
        sub_queries = self.rewriter.decompose(query)

        # Execute sub-queries sequentially
        all_results = []
        for sub_query in sub_queries:
            sub_results = self._parallel_route(intent, sub_query_embedding)
            all_results.extend(sub_results)

        # Aggregate and synthesize
        return self.aggregator.aggregate_complex(all_results, query)
```

**Performance Target:** 40% reduction in unnecessary DB calls

---

### 3.2 Multi-Router Architecture

**Goal:** Specialized routers for different domains

**Research:** [Agentic RAG - Multi-Router](../../research/documentation/query-routing/agentic-rag-2025.md#multi-router-architecture-2025)

**Implementation:**

```python
# File: src/apex_memory/query_router/multi_router.py

from abc import ABC, abstractmethod

class SpecializedRouter(ABC):
    """Base class for specialized routers."""

    @abstractmethod
    def can_handle(self, intent: QueryIntent) -> float:
        """Return confidence (0-1) that this router can handle the query."""
        pass

    @abstractmethod
    def route(self, query: str, intent: QueryIntent, embedding: np.ndarray) -> List[Dict]:
        """Execute routing and return results."""
        pass

class TemporalRouter(SpecializedRouter):
    """Specialized router for temporal queries."""

    def can_handle(self, intent: QueryIntent) -> float:
        if intent.query_type == QueryType.TEMPORAL:
            return 1.0
        elif intent.time_range is not None:
            return 0.8
        return 0.0

    def route(self, query, intent, embedding):
        # Prioritize Graphiti for temporal queries
        return self.graphiti_service.temporal_search(
            query=query,
            time_range=intent.time_range,
            limit=intent.limit
        )

class SemanticRouter(SpecializedRouter):
    """Specialized router for semantic search."""

    def can_handle(self, intent: QueryIntent) -> float:
        if intent.query_type == QueryType.SEMANTIC:
            return 1.0
        return 0.3

    def route(self, query, intent, embedding):
        # Use Qdrant for high-performance semantic search
        return self.qdrant_client.search(
            collection_name="documents",
            query_vector=embedding,
            limit=intent.limit
        )

class GraphRouter(SpecializedRouter):
    """Specialized router for graph traversal."""

    def can_handle(self, intent: QueryIntent) -> float:
        if intent.query_type == QueryType.GRAPH:
            return 1.0
        elif len(intent.entities) > 0:
            return 0.7
        return 0.2

    def route(self, query, intent, embedding):
        # Use Neo4j GraphRAG for relationship queries
        return self.neo4j_graphrag.hybrid_search(
            query_embedding=embedding,
            query_entities=intent.entities,
            limit=intent.limit
        )

class MetaRouter:
    """Router-of-routers meta-controller."""

    def __init__(self):
        self.routers = [
            TemporalRouter(),
            SemanticRouter(),
            GraphRouter(),
            MetadataRouter()
        ]

    def route(self, query: str, intent: QueryIntent, embedding: np.ndarray) -> Dict:
        """Route to best specialized router(s)."""
        # Get confidence from each router
        confidences = [
            (router, router.can_handle(intent))
            for router in self.routers
        ]

        # Sort by confidence
        confidences.sort(key=lambda x: x[1], reverse=True)

        # Use top router(s)
        if confidences[0][1] >= 0.9:
            # Single high-confidence router
            return confidences[0][0].route(query, intent, embedding)

        elif confidences[0][1] >= 0.6 and confidences[1][1] >= 0.6:
            # Multiple moderate-confidence routers - use both
            results_1 = confidences[0][0].route(query, intent, embedding)
            results_2 = confidences[1][0].route(query, intent, embedding)

            # Weighted merge
            return self._merge_results(
                results_1,
                results_2,
                weight_1=confidences[0][1],
                weight_2=confidences[1][1]
            )

        else:
            # Fallback to default routing
            return self._default_route(query, intent, embedding)
```

---

### 3.3 Self-Correction Loop

**Goal:** Validate and auto-correct routing decisions

**Research:** [Agentic RAG - Self-Correction](../../research/documentation/query-routing/agentic-rag-2025.md#self-correction-mechanisms)

**Implementation:**

```python
# File: src/apex_memory/query_router/self_correction.py

class SelfCorrectingRouter:
    """Router with self-correction and validation."""

    def __init__(self, base_router, rewriter):
        self.router = base_router
        self.rewriter = rewriter

    async def route_with_validation(
        self,
        query: str,
        intent: QueryIntent,
        embedding: np.ndarray,
        max_retries: int = 2
    ) -> List[Dict]:
        """Route with validation and self-correction."""
        attempt = 0

        while attempt < max_retries:
            # Execute routing
            results = await self.router.route(query, intent, embedding)

            # Validate results
            validation = self._validate_results(results, intent)

            if validation.is_valid:
                # Results look good
                return results

            # Low confidence - try correction
            logger.warning(
                f"Low confidence routing (score: {validation.confidence}), "
                f"reason: {validation.reason}. Attempting correction..."
            )

            if validation.suggested_correction == "rewrite_query":
                # Rewrite and retry
                query = self.rewriter.rewrite(query, intent.query_type)[0]
                embedding = self.embeddings.generate_embedding(query)

            elif validation.suggested_correction == "try_different_databases":
                # Try alternative databases
                intent.databases = self._get_alternative_databases(intent)

            elif validation.suggested_correction == "decompose_query":
                # Query too complex, decompose
                sub_queries = self.rewriter.decompose(query)
                results = []
                for sub_q in sub_queries:
                    sub_results = await self.router.route(sub_q, intent, embedding)
                    results.extend(sub_results)
                return results

            attempt += 1

        # Max retries reached, return best attempt
        return results

    def _validate_results(self, results: List[Dict], intent: QueryIntent) -> ValidationResult:
        """Validate retrieval results."""
        if not results:
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                reason="No results found",
                suggested_correction="rewrite_query"
            )

        # Check relevance scores
        avg_relevance = sum(r.get('relevance', 0) for r in results) / len(results)

        if avg_relevance < 0.5:
            return ValidationResult(
                is_valid=False,
                confidence=avg_relevance,
                reason=f"Low average relevance: {avg_relevance:.2f}",
                suggested_correction="try_different_databases"
            )

        # Check result diversity
        unique_sources = len(set(r.get('source') for r in results))

        if unique_sources < 2 and len(intent.databases) > 2:
            return ValidationResult(
                is_valid=False,
                confidence=0.6,
                reason="Low source diversity",
                suggested_correction="try_different_databases"
            )

        # Results look good
        return ValidationResult(
            is_valid=True,
            confidence=avg_relevance,
            reason="Valid results",
            suggested_correction=None
        )
```

**Performance Target:** 95%+ routing accuracy with self-correction

---

## Phase 4: Advanced Features (Week 7-8)

### 4.1 Multimodal Support

**Goal:** Handle image/document embeddings alongside text

**Implementation:**

```python
# File: src/apex_memory/query_router/multimodal_router.py

from typing import Union, List
import numpy as np

class MultimodalRouter:
    """Router for multimodal queries (text + images + documents)."""

    def __init__(self, text_embedder, image_embedder, document_embedder):
        self.text_embedder = text_embedder
        self.image_embedder = image_embedder
        self.document_embedder = document_embedder

    async def route(
        self,
        query_text: Optional[str] = None,
        query_image: Optional[bytes] = None,
        query_document: Optional[bytes] = None
    ) -> List[Dict]:
        """Route multimodal query."""
        embeddings = []

        # Generate embeddings for each modality
        if query_text:
            text_emb = self.text_embedder.embed(query_text)
            embeddings.append(("text", text_emb))

        if query_image:
            image_emb = self.image_embedder.embed(query_image)
            embeddings.append(("image", image_emb))

        if query_document:
            doc_emb = self.document_embedder.embed(query_document)
            embeddings.append(("document", doc_emb))

        # Fuse embeddings (weighted average)
        fused_embedding = self._fuse_embeddings(embeddings)

        # Route with fused embedding
        return await self.unified_search(fused_embedding)
```

---

### 4.2 Real-Time Adaptation

**Goal:** Continuously learn and adapt from live traffic

**Implementation:**

```python
# File: src/apex_memory/query_router/online_learning.py

class OnlineLearningRouter:
    """Router with continuous online learning."""

    def __init__(self, base_router, bandit_model):
        self.router = base_router
        self.bandit = bandit_model
        self.feedback_queue = asyncio.Queue()

        # Start background learning task
        asyncio.create_task(self._continuous_learning())

    async def route(self, query, intent, embedding):
        """Route and track for learning."""
        # Get routing decision
        results = await self.router.route(query, intent, embedding)

        # Queue for feedback collection
        await self.feedback_queue.put({
            "query": query,
            "embedding": embedding,
            "intent": intent,
            "results": results,
            "timestamp": datetime.now()
        })

        return results

    async def _continuous_learning(self):
        """Background task for continuous model updates."""
        while True:
            # Batch feedback
            batch = []
            for _ in range(100):  # Batch size
                item = await self.feedback_queue.get()
                batch.append(item)

            # Update models
            await self._update_models(batch)

    async def _update_models(self, batch):
        """Update routing models from feedback batch."""
        for item in batch:
            # Get user feedback (click, satisfaction)
            feedback = await self._collect_user_feedback(item)

            if feedback:
                # Update bandit model
                reward = feedback['satisfaction']
                self.bandit.update(
                    item['embedding'],
                    item['database_index'],
                    reward
                )
```

---

## Phase 4.3: Gradual Rollout Strategy

**Goal:** Safe, incremental deployment with feature flags and A/B testing

**Implementation:**

### 4.3.1 Feature Flag System

```python
# File: src/apex_memory/feature_flags.py

from enum import Enum
from typing import Dict, Optional
import redis

class FeatureFlag(Enum):
    SEMANTIC_CLASSIFICATION = "semantic_classification"
    QUERY_REWRITING = "query_rewriting"
    ADAPTIVE_WEIGHTS = "adaptive_weights"
    GRAPHRAG_HYBRID = "graphrag_hybrid"
    SEMANTIC_CACHING = "semantic_caching"
    MULTI_ROUTER = "multi_router"
    SELF_CORRECTION = "self_correction"

class FeatureFlagManager:
    """Manage feature flags for gradual rollout."""

    def __init__(self, redis_client):
        self.redis = redis_client

    def is_enabled(self, flag: FeatureFlag, user_id: Optional[str] = None) -> bool:
        """Check if feature is enabled for user."""
        # Global flag
        global_key = f"flag:{flag.value}:enabled"
        global_enabled = self.redis.get(global_key)

        if global_enabled == "false":
            return False

        # Rollout percentage
        rollout_key = f"flag:{flag.value}:rollout_pct"
        rollout_pct = float(self.redis.get(rollout_key) or 0)

        if user_id:
            # Consistent hash for user
            user_hash = hash(user_id) % 100
            return user_hash < rollout_pct

        # Random sampling for anonymous
        import random
        return random.random() * 100 < rollout_pct

    def set_rollout(self, flag: FeatureFlag, percentage: float):
        """Set rollout percentage (0-100)."""
        self.redis.set(f"flag:{flag.value}:rollout_pct", str(percentage))
```

### 4.3.2 Shadow Mode Testing

```python
# File: src/apex_memory/query_router/shadow_router.py

class ShadowRouter:
    """Run new router alongside old router without affecting users."""

    def __init__(self, old_router, new_router, analytics):
        self.old_router = old_router
        self.new_router = new_router
        self.analytics = analytics

    async def query(self, query_text: str, user_id: Optional[str] = None):
        """Execute both routers, return old results, compare in background."""
        # Always use old router for user-facing results
        old_results = await self.old_router.query(query_text)

        # Execute new router in background (no user impact)
        asyncio.create_task(self._shadow_query(query_text, old_results, user_id))

        return old_results

    async def _shadow_query(self, query: str, old_results, user_id):
        """Execute new router and compare results."""
        try:
            new_results = await self.new_router.query(query)

            # Compare results
            comparison = self._compare_results(old_results, new_results)

            # Log comparison
            await self.analytics.log_shadow_comparison(
                query=query,
                user_id=user_id,
                old_results=old_results,
                new_results=new_results,
                comparison=comparison
            )
        except Exception as e:
            logger.error(f"Shadow query failed: {e}")
```

### 4.3.3 Canary Deployment

```python
# File: src/apex_memory/query_router/canary_router.py

class CanaryRouter:
    """Route percentage of traffic to new router."""

    def __init__(self, old_router, new_router, feature_flags):
        self.old_router = old_router
        self.new_router = new_router
        self.flags = feature_flags

    async def query(self, query_text: str, user_id: Optional[str] = None):
        """Route to old or new router based on canary percentage."""
        if self.flags.is_enabled(FeatureFlag.SEMANTIC_CLASSIFICATION, user_id):
            # Canary: use new router
            return await self.new_router.query(query_text)
        else:
            # Control: use old router
            return await self.old_router.query(query_text)
```

**Rollout Schedule:**

1. **Week 1:** Shadow mode (0% users affected, 100% comparison data)
2. **Week 2:** 5% canary (monitor metrics closely)
3. **Week 3:** 25% canary (if metrics improve ≥5%)
4. **Week 4:** 50% canary (if no regressions)
5. **Week 5:** 100% rollout (if all metrics pass)

---

## Integration with Other Upgrades

### Integration: Saga Pattern Enhancement

**Cross-Reference:** [Saga Pattern Enhancement](../saga-pattern-enhancement/README.md)

The query router integrates with the saga pattern enhancement for distributed transaction consistency:

**Key Integration Points:**

1. **Distributed Locking for Write Operations**
   - Query router coordinates with saga pattern's Redis Redlock
   - Prevents concurrent writes during query routing
   - Ensures consistency across database writes

2. **Idempotency Key Integration**
   ```python
   # File: src/apex_memory/query_router/router.py

   class QueryRouter:
       async def query_with_write(self, query_text: str, write_data: Dict):
           """Query with potential write operation (uses saga pattern)."""
           # Generate idempotency key
           idempotency_key = self.saga_coordinator.generate_idempotency_key(
               query_text,
               write_data
           )

           # Check if already processed
           if await self.saga_coordinator.is_processed(idempotency_key):
               return await self.saga_coordinator.get_result(idempotency_key)

           # Acquire distributed lock
           lock = await self.saga_coordinator.acquire_lock(idempotency_key)

           try:
               # Execute routing with saga pattern
               results = await self._execute_with_saga(query_text, write_data)
               return results
           finally:
               await lock.release()
   ```

3. **Circuit Breaker Integration**
   - Query router respects circuit breaker states from saga pattern
   - Fails fast if database circuit breaker is open
   - Routes around failing databases

**Expected Benefits:**
- 99.9% consistency for queries with writes
- Zero duplicate query executions
- Graceful degradation when databases fail

---

### Integration: Security Layer (Planned)

**Cross-Reference:** [Security Layer](../planned/security-layer/README.md)

The query router will integrate with the planned security layer for:

**Key Integration Points:**

1. **Authentication Middleware**
   ```python
   # File: src/apex_memory/query_router/router.py

   from fastapi import Depends
   from apex_memory.security import get_current_user

   @router.post("/api/query")
   async def query_endpoint(
       query_request: QueryRequest,
       current_user: User = Depends(get_current_user)  # Security layer
   ):
       """Protected query endpoint."""
       # Log user context
       logger.info(f"Query from user {current_user.id}: {query_request.query}")

       # Execute routing
       results = await query_router.query(
           query_text=query_request.query,
           user_id=current_user.id  # For personalization
       )

       # Audit logging
       await audit_log.log_query(current_user.id, query_request.query, results)

       return results
   ```

2. **Rate Limiting Integration**
   - Per-user query limits (e.g., 1000 queries/day)
   - Redis-based distributed rate limiter
   - Graceful 429 responses

3. **Row-Level Security (Future)**
   - Filter query results by user permissions
   - Integrate with PostgreSQL RLS
   - RBAC enforcement at routing layer

**Migration Plan:**
- Phase 1: Add authentication (Week 1 of security upgrade)
- Phase 2: Add rate limiting (Week 2 of security upgrade)
- Phase 3: Add RBAC filtering (Week 3+ of security upgrade)

---

## Quick Wins (Immediate Implementation)

### Quick Win #1: Add Confidence Scores

**File:** `src/apex_memory/query_router/analyzer.py`

```python
@dataclass
class QueryIntent:
    query_text: str
    query_type: QueryType
    databases: Set[str] = field(default_factory=set)
    confidence: float = 1.0  # ← ADD THIS

    # ... rest of class ...

class QueryAnalyzer:
    def _detect_query_type(self, query_lower: str) -> QueryType:
        scores = {...}

        # ... existing scoring logic ...

        max_score = max(scores.values())

        # Calculate confidence ← ADD THIS
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0

        # Store confidence
        self.last_confidence = confidence

        # ... rest of method ...
```

**Effort:** 30 minutes
**Impact:** Enables future confidence-based routing

---

### Quick Win #2: Routing Decision Logging

**File:** `src/apex_memory/query_router/router.py`

```python
class QueryRouter:
    def query(self, query_text: str, ...):
        start_time = time.time()

        # ... existing code ...

        # Log decision ← ADD THIS
        self._log_routing_decision(
            query=query_text,
            intent=intent,
            databases_used=list(intent.databases),
            num_results=len(aggregated_results),
            latency_ms=(time.time() - start_time) * 1000,
            cached=use_cache
        )

        return results

    def _log_routing_decision(self, **kwargs):
        """Log routing decision to analytics."""
        logger.info(f"Routing decision: {json.dumps(kwargs)}")
        # TODO: Store in analytics DB
```

**Effort:** 1 hour
**Impact:** Data for optimization, debugging, analytics

---

### Quick Win #3: Out-of-Scope Detection

**File:** `src/apex_memory/query_router/analyzer.py`

```python
def _detect_query_type(self, query_lower: str) -> Optional[QueryType]:
    scores = {...}

    # ... existing scoring logic ...

    max_score = max(scores.values())

    # Out-of-scope detection ← ADD THIS
    if max_score == 0:
        logger.warning(f"Out-of-scope query: {query_lower}")
        return None  # Indicate OOS

    # ... rest of method ...
```

**File:** `src/apex_memory/query_router/router.py`

```python
def query(self, query_text: str, ...):
    intent = self.analyzer.analyze(query_text)

    # Handle OOS ← ADD THIS
    if intent.query_type is None:
        return {
            "query": query_text,
            "error": "out_of_scope",
            "message": "Query does not match any supported intent",
            "results": [],
            "result_count": 0
        }

    # ... rest of method ...
```

**Effort:** 1 hour
**Impact:** Better UX, resource savings

---

### Quick Win #4: Query Normalization

**File:** `src/apex_memory/query_router/router.py`

```python
def query(self, query_text: str, ...):
    # Normalize query ← ADD THIS
    normalized = self._normalize_query(query_text)

    # Use normalized query
    intent = self.analyzer.analyze(normalized)

    # ... rest of method ...

def _normalize_query(self, query: str) -> str:
    """Basic query normalization."""
    # Strip whitespace
    normalized = query.strip()

    # Lowercase (for matching, keep original for display)
    # Remove multiple spaces
    normalized = " ".join(normalized.split())

    return normalized
```

**Effort:** 30 minutes
**Impact:** Better cache hits, more consistent routing

---

### Quick Win #5: Database Response Time Tracking

**File:** `src/apex_memory/query_router/router.py`

```python
def _route_query(self, intent, query_embedding):
    results = {}
    timings = {}  # ← ADD THIS

    for db_name in intent.databases:
        start_time = time.time()  # ← ADD THIS

        try:
            # ... existing query execution ...
            results[db_name] = db_results

        except Exception as e:
            # ... existing error handling ...

        finally:
            # Track timing ← ADD THIS
            timings[db_name] = (time.time() - start_time) * 1000

    # Log performance ← ADD THIS
    logger.info(f"Database timings: {json.dumps(timings)}")

    return results
```

**Effort:** 1 hour
**Impact:** Performance insights, optimization data

---

## Competitive Analysis

| Feature | Apex (Current) | Apex (After) | Mem0 | Zep | 2025 SOTA |
|---------|---------------|--------------|------|-----|-----------|
| **Intent Classification** | Keywords ❌ | Semantic ✅ | Basic ⚠️ | Temporal KG ✅ | LLM/Semantic ✅ |
| **Query Rewriting** | None ❌ | Multi-strategy ✅ | None ❌ | Limited ⚠️ | Advanced ✅ |
| **Adaptive Routing** | Static ❌ | Bandit ✅ | None ❌ | Hybrid ⚠️ | Agentic ✅ |
| **GraphRAG** | Separate ⚠️ | Unified ✅ | Add-on ⚠️ | Built-in ✅ | Unified ✅ |
| **Learning Weights** | Fixed ❌ | Online learning ✅ | Static ❌ | Limited ⚠️ | Contextual bandit ✅ |
| **Cache Strategy** | Exact match ⚠️ | Semantic ✅ | Basic ⚠️ | Basic ⚠️ | Semantic + ML ✅ |
| **Multi-Router** | Single ❌ | Specialized ✅ | Single ❌ | Single ❌ | Multi-agent ✅ |
| **Self-Correction** | None ❌ | Validation loop ✅ | None ❌ | None ❌ | Agentic ✅ |
| **Out-of-Scope Detection** | None ❌ | Semantic ✅ | None ❌ | None ❌ | Yes ✅ |
| **Analytics** | None ❌ | Comprehensive ✅ | Basic ⚠️ | Basic ⚠️ | Advanced ✅ |

**Post-Implementation:** Apex will be competitive with 2025 state-of-the-art systems

---

## Implementation Guidelines

### Development Principles

1. **Incremental Rollout**
   - Deploy alongside existing system
   - A/B test with 10% traffic initially
   - Gradually increase based on metrics

2. **Backward Compatibility**
   - Keep existing endpoints working
   - Feature flags for new capabilities
   - Gradual migration path

3. **Comprehensive Testing**
   - Unit tests for all new components
   - Integration tests for routing decisions
   - Performance benchmarks
   - A/B testing in production

4. **Monitoring & Observability**
   - Log all routing decisions
   - Track latency per component
   - Monitor accuracy metrics
   - Alert on degradations

### Code Organization

```
src/apex_memory/query_router/
├── analyzer.py               # Existing intent analyzer
├── semantic_classifier.py    # NEW: Semantic classification
├── query_rewriter.py         # NEW: Query rewriting
├── adaptive_weights.py       # NEW: Learned weights
├── complexity_analyzer.py    # NEW: Complexity analysis
├── multi_router.py           # NEW: Multi-router architecture
├── self_correction.py        # NEW: Self-correction loop
├── analytics.py              # NEW: Routing analytics
├── router.py                 # UPDATED: Main router
├── aggregator.py             # Existing aggregator
└── cache.py                  # UPDATED: Semantic caching
```

### Testing Strategy

```python
# tests/integration/test_query_router_upgrade.py

class TestQueryRouterUpgrade:
    """Integration tests for router upgrades."""

    def test_semantic_classification_accuracy(self):
        """Test semantic classifier outperforms keyword."""
        # ... test implementation ...

    def test_query_rewriting_improves_relevance(self):
        """Test query rewriting improves results."""
        # ... test implementation ...

    def test_adaptive_weights_learn(self):
        """Test bandit model learns from feedback."""
        # ... test implementation ...

    def test_graphrag_hybrid_search(self):
        """Test unified graph + vector search."""
        # ... test implementation ...

    def test_complexity_based_routing(self):
        """Test routing adapts to query complexity."""
        # ... test implementation ...

    def test_out_of_scope_detection(self):
        """Test OOS queries are correctly identified."""
        # ... test implementation ...

    def test_semantic_caching(self):
        """Test similar queries hit cache."""
        # ... test implementation ...
```

---

## Success Metrics

### Performance Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Routing Accuracy | 70-75% | 90%+ | % queries routed to optimal DB |
| Intent Classification | 70% | 95%+ | % correctly classified intents |
| Query Latency (P95) | 800ms | 600ms | 95th percentile response time |
| Cache Hit Rate | 75% | 90%+ | % queries served from cache |
| Result Relevance | 0.70 | 0.85+ | Avg relevance score (0-1) |
| GraphRAG Precision | 75% | 99% | % relevant results for graph queries |
| Cost Efficiency | Baseline | -30% | Compute cost per query |

### Business Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| User Satisfaction | Unknown | 4.5/5 | User ratings |
| Time to Answer | Unknown | <2s | End-to-end query time |
| Query Success Rate | Unknown | 95%+ | % queries returning useful results |
| System Throughput | Unknown | 2x | Queries per second |

### Learning Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Model Convergence | <1000 queries | Queries until stable weights |
| Exploration Rate | 10-20% | % exploratory routing decisions |
| Feedback Loop Latency | <1 hour | Time from feedback to model update |
| A/B Test Power | 95% confidence | Statistical significance threshold |

---

## References

### Research Documentation

1. **[Semantic Router](../../research/documentation/query-routing/semantic-router.md)**
   - 10ms intent classification
   - Out-of-scope detection
   - Embedding-based routing

2. **[Query Rewriting for RAG](../../research/documentation/query-routing/query-rewriting-rag.md)**
   - Microsoft +21-28 point improvement
   - HyDE, decomposition, expansion
   - RaFe and LLM-QE frameworks

3. **[Agentic RAG 2025](../../research/documentation/query-routing/agentic-rag-2025.md)**
   - Paradigm shift to autonomous agents
   - Reflection, planning, tool use
   - Multi-router architectures

4. **[Adaptive Routing with Learned Weights](../../research/documentation/query-routing/adaptive-routing-learning.md)**
   - Contextual bandits (PILOT)
   - Matrix factorization
   - Online learning

5. **[GraphRAG Hybrid Search](../../research/documentation/query-routing/graphrag-hybrid-search.md)**
   - 99% precision benchmarks
   - Neo4j vector index
   - Unified graph + vector

### External Resources

- **Semantic Router:** https://github.com/aurelio-labs/semantic-router
- **Microsoft Query Rewriting:** https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/raising-the-bar-for-rag-excellence-query-rewriting-and-new-semantic-ranker/4302729
- **Agentic RAG Survey:** https://arxiv.org/abs/2501.09136
- **PILOT System:** https://arxiv.org/html/2508.21141
- **Neo4j GraphRAG:** https://neo4j.com/blog/developer/vectors-graphs-better-together/

---

## Related Upgrades

This improvement plan integrates with and depends on:

1. **[Saga Pattern Enhancement](../saga-pattern-enhancement/README.md)** (Active)
   - Distributed locking for query-with-write operations
   - Idempotency keys for safe retries
   - Circuit breakers for graceful degradation
   - Status: Active implementation (5-day timeline)

2. **[Security Layer](../planned/security-layer/README.md)** (Planned)
   - Authentication middleware for protected endpoints
   - Per-user rate limiting
   - Row-level security for result filtering
   - Status: Planned (before production launch)

3. **[External Engineer Proposal Analysis](../../research/review/external-engineer-proposal-analysis.md)**
   - Comprehensive comparison of external proposals to our research-backed plan
   - Validated our approach superior to BERT-based routing
   - Integrated enhanced analytics (Prometheus + Jaeger)
   - Status: Completed analysis

---

## Next Steps

1. **Review and Approve Plan** ✅
2. **Set up Development Environment**
   - Install Prometheus, Jaeger, Grafana
   - Configure feature flag Redis
3. **Implement Quick Wins (Week 1)**
   - Confidence scores
   - Routing decision logging
   - Out-of-scope detection
   - Query normalization
   - Database response time tracking
4. **Begin Phase 1 Implementation (Week 1-2)**
   - Semantic intent classification
   - Query rewriting pipeline
   - Enhanced analytics with Prometheus + Jaeger
5. **Deploy in Shadow Mode (Week 3)**
   - Run new router alongside old
   - Collect comparison data
   - Validate improvements
6. **Gradual Canary Rollout (Week 4-5)**
   - 5% → 25% → 50% → 100%
   - Monitor metrics at each step
7. **Continuous evaluation and iteration**

---

**Last Updated:** October 7, 2025
**Status:** Planning → Ready for Implementation (Enhanced with External Analysis)
**Owner:** Apex Engineering Team
