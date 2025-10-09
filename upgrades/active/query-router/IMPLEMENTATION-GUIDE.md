# Query Router Implementation Guide

**Status:** Ready for Implementation
**Priority:** High
**Timeline:** 8 weeks (phased rollout)
**Last Updated:** October 7, 2025

---

## Executive Summary

This guide provides step-by-step implementation instructions for upgrading the Apex Memory System query router to 2025 standards. Based on comprehensive research (Exa + GitHub), this plan uses **best-in-class solutions verified as of October 2025**.

**Key Decisions:**
- ✅ **Semantic Router 0.1.11** (latest, 2.8k GitHub stars - industry standard)
- ✅ **Claude API** for query rewriting (superior to OpenAI: better quality, 67% lower cost)
- ✅ **Full async conversion** (2025 Python best practice, FastAPI-native)
- ✅ **Prometheus + Jaeger** for production-grade observability
- ✅ **Time-series partitioned PostgreSQL** for analytics at scale

---

## Table of Contents

1. [Pre-Flight Verification](#pre-flight-verification)
2. [Dependency Installation](#dependency-installation)
3. [Phase 1: Foundation](#phase-1-foundation-week-1-2)
4. [Phase 2: Intelligent Routing](#phase-2-intelligent-routing-week-3-4)
5. [Phase 3: Async Conversion](#phase-3-async-conversion-week-5)
6. [Phase 4: Shadow Mode & Rollout](#phase-4-shadow-mode--rollout-week-6-7)
7. [Testing Strategy](#testing-strategy)
8. [Rollback Procedures](#rollback-procedures)

---

## Pre-Flight Verification

### 1. Check Neo4j Version (GraphRAG Requirement)

```bash
# Check Neo4j version in docker-compose
grep -A 5 "neo4j:" apex-memory-system/docker/docker-compose.yml

# If running, check version directly
docker exec apex-neo4j neo4j --version

# Requirement: Neo4j 5.11+ for vector index support
# If < 5.11, update docker-compose.yml:
#   image: neo4j:5.11  # or later
```

**Why:** GraphRAG Phase (2.2) requires `CREATE VECTOR INDEX` (Neo4j 5.11+)

### 2. Check Redis Memory Limits

```bash
# Check Redis config
grep -A 10 "redis:" apex-memory-system/docker/docker-compose.yml

# If running, check memory
docker exec apex-redis redis-cli INFO memory | grep maxmemory

# Requirement: ~100MB for semantic cache
# Calculation: 1536 floats × 4 bytes × 10,000 queries ≈ 60MB
```

**Recommended Config:**
```yaml
redis:
  image: redis:7-alpine
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### 3. Add Prometheus & Jaeger Services

```yaml
# Add to docker-compose.yml

prometheus:
  image: prom/prometheus:v2.53.0
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'

jaeger:
  image: jaegertracing/all-in-one:1.58
  ports:
    - "16686:16686"  # Jaeger UI
    - "6831:6831/udp"  # Jaeger agent (traces)
  environment:
    - COLLECTOR_ZIPKIN_HTTP_PORT=9411

grafana:
  image: grafana/grafana:10.4.0
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=apexmemory2024
  volumes:
    - grafana-storage:/var/lib/grafana
```

**Create prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'apex-api'
    static_configs:
      - targets: ['host.docker.internal:8000']  # FastAPI metrics endpoint
```

### 4. Verify FastAPI is Async

```bash
# Check main.py for async def
grep -n "async def" apex-memory-system/src/apex_memory/main.py

# All routes should be async def (FastAPI best practice)
```

---

## Dependency Installation

### Update requirements.txt

```bash
cd apex-memory-system

# Add to requirements.txt:
cat >> requirements.txt << 'EOF'

# Query Router Upgrades (Phase 1-4)
semantic-router==0.1.11  # Latest (verified Oct 2025)
anthropic==0.39.0  # For Claude query rewriting
prometheus-client==0.21.0  # Metrics
opentelemetry-api==1.27.0  # Jaeger tracing
opentelemetry-sdk==1.27.0
opentelemetry-exporter-jaeger==1.27.0
scipy==1.14.1  # Contextual bandits (matrix operations)
litellm==1.61.3  # Multi-LLM support (included with semantic-router)
EOF

# Install
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "import semantic_router; print(semantic_router.__version__)"
# Expected: 0.1.11

python -c "import anthropic; print(anthropic.__version__)"
# Expected: 0.39.0
```

---

## Phase 1: Foundation (Week 1-2)

### Day 1-2: Quick Wins

#### 1.1 Add Confidence Scores

**File:** `src/apex_memory/query_router/analyzer.py`

```python
@dataclass
class QueryIntent:
    query_text: str
    query_type: QueryType
    databases: Set[str] = field(default_factory=set)
    confidence: float = 1.0  # ADD THIS

    # ... existing fields ...

class QueryAnalyzer:
    def _detect_query_type(self, query_lower: str) -> QueryType:
        scores = {
            QueryType.GRAPH: 0,
            QueryType.TEMPORAL: 0,
            QueryType.SEMANTIC: 0,
            QueryType.METADATA: 0,
        }

        # ... existing scoring logic ...

        # Calculate confidence
        max_score = max(scores.values())
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0

        # Store for use in QueryIntent creation
        self.last_confidence = confidence

        return max(scores, key=scores.get)
```

#### 1.2 Replace print() with Structured Logging

**File:** `src/apex_memory/query_router/router.py`

```python
import logging
logger = logging.getLogger(__name__)

# BEFORE:
# print(f"Neo4j query error: {e}")

# AFTER:
logger.error("Neo4j query failed", extra={
    "error": str(e),
    "query_text": query_text,
    "intent": intent.query_type.value,
    "database": "neo4j"
})
```

#### 1.3 Add Query Normalization

**File:** `src/apex_memory/query_router/router.py`

```python
def _normalize_query(self, query: str) -> str:
    """Normalize query for consistent processing."""
    # Strip whitespace
    normalized = query.strip()

    # Remove multiple spaces
    normalized = " ".join(normalized.split())

    # Remove common punctuation at end
    normalized = normalized.rstrip('?!.')

    return normalized

async def query(self, query_text: str, **kwargs):
    # Normalize query first
    normalized = self._normalize_query(query_text)

    # Use normalized for analysis
    intent = self.analyzer.analyze(normalized)
    ...
```

#### 1.4 Add Database Timing Tracking

**File:** `src/apex_memory/query_router/router.py`

```python
import time

def _route_query(self, intent, query_embedding):
    results = {}
    timings = {}  # Track per-database latency

    for db_name in intent.databases:
        start_time = time.time()

        try:
            # Execute query
            results[db_name] = self._query_database(db_name, intent, query_embedding)
        except Exception as e:
            logger.error(f"{db_name} query failed", extra={
                "error": str(e),
                "intent": intent.query_type.value
            })
            results[db_name] = []
        finally:
            # Always track timing
            timings[db_name] = (time.time() - start_time) * 1000

    # Log timings
    logger.info("Database query timings", extra={
        "timings_ms": timings,
        "total_ms": sum(timings.values())
    })

    return results, timings
```

### Day 3-5: Semantic Classification

**File:** `src/apex_memory/query_router/semantic_classifier.py` (NEW)

```python
"""Semantic Intent Classification using semantic-router library."""

import logging
from typing import Optional
from semantic_router import Route, SemanticRouter
from semantic_router.encoders import OpenAIEncoder

logger = logging.getLogger(__name__)


class SemanticIntentClassifier:
    """Semantic intent classification using embeddings."""

    def __init__(self, openai_api_key: str):
        """Initialize semantic router with training routes."""

        # Define routes with example utterances
        self.routes = [
            Route(
                name="graph",
                utterances=[
                    "what equipment is connected to ACME Corp",
                    "show me all relationships between customer and invoices",
                    "which drivers are associated with truck T-1234",
                    "find all customers linked to overdue invoices",
                    "what entities are related to load L-5678",
                    "show network of connections for invoice INV-001",
                    "display the relationship graph for customer ACME",
                    "how is equipment E-999 tied to its assignments",
                    "what loads are connected to driver John Smith",
                    "trace all associations from truck T-5000",
                    "map the connections between customers and equipment",
                    "show me entities linked through MENTIONS relationship"
                ],
                score_threshold=0.75
            ),
            Route(
                name="temporal",
                utterances=[
                    "how has payment behavior changed over the last 6 months",
                    "what was the status of invoice X last month",
                    "show me the history of customer ACME's transactions",
                    "when did the invoice status change from pending to paid",
                    "what trends emerged in equipment usage this quarter",
                    "has customer engagement evolved over time",
                    "compare driver performance from January to March",
                    "what patterns appeared in late payments this year",
                    "show me how load volumes changed week by week",
                    "track the evolution of customer creditworthiness",
                    "what was different about operations 3 months ago",
                    "identify shifts in equipment maintenance patterns"
                ],
                score_threshold=0.70
            ),
            Route(
                name="semantic",
                utterances=[
                    "find documents similar to quarterly financial report",
                    "search for content about equipment maintenance procedures",
                    "documents related to payment terms and conditions",
                    "find similar customer profiles to ACME Corp",
                    "search for contracts semantically similar to Contract-X",
                    "retrieve documents about late payment penalties",
                    "find content regarding driver safety protocols",
                    "documents about fuel cost optimization",
                    "search for information on customer onboarding",
                    "find similar invoices to INV-12345",
                    "content related to equipment depreciation",
                    "documents about dispute resolution processes"
                ],
                score_threshold=0.75
            ),
            Route(
                name="metadata",
                utterances=[
                    "show me all overdue invoices",
                    "list documents created after January 1 2025",
                    "find invoices authored by John Smith",
                    "filter documents by type PDF",
                    "show all active customer accounts",
                    "retrieve pending loads from last week",
                    "list equipment with status maintenance required",
                    "find documents modified in the last 7 days",
                    "show invoices with amount greater than 10000",
                    "filter by customer status VIP",
                    "list all completed deliveries this month",
                    "show documents tagged as urgent"
                ],
                score_threshold=0.70
            )
        ]

        # Initialize encoder and router
        self.encoder = OpenAIEncoder(api_key=openai_api_key)
        self.router = SemanticRouter(
            encoder=self.encoder,
            routes=self.routes,
            auto_sync="local"  # Sync embeddings locally
        )

        logger.info(f"Semantic router initialized with {len(self.routes)} routes")

    def classify(self, query_text: str) -> Optional[str]:
        """
        Classify query intent using semantic similarity.

        Args:
            query_text: Natural language query

        Returns:
            Route name (graph/temporal/semantic/metadata) or None for out-of-scope
        """
        try:
            route = self.router(query_text)

            if route is None:
                # Out-of-scope query
                logger.warning(f"Out-of-scope query detected: {query_text}")
                return None

            logger.info(f"Classified query as '{route.name}'", extra={
                "query": query_text,
                "intent": route.name,
                "score": route.similarity_score if hasattr(route, 'similarity_score') else None
            })

            return route.name

        except Exception as e:
            logger.error(f"Semantic classification failed: {e}")
            return None  # Fallback to keyword-based
```

**Integration:**

```python
# File: src/apex_memory/query_router/analyzer.py

from .semantic_classifier import SemanticIntentClassifier

class QueryAnalyzer:
    def __init__(self, use_semantic: bool = True):
        self.use_semantic = use_semantic

        if self.use_semantic:
            import os
            self.semantic_classifier = SemanticIntentClassifier(
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )

    def _detect_query_type(self, query_lower: str) -> Optional[QueryType]:
        """Detect query type with semantic classification."""

        if self.use_semantic:
            # Try semantic classification first
            route_name = self.semantic_classifier.classify(query_lower)

            if route_name is None:
                # Out-of-scope query
                logger.warning(f"Out-of-scope query: {query_lower}")
                return None

            # Map route name to QueryType
            return QueryType(route_name)

        # Fallback to keyword-based classification
        return self._keyword_based_classification(query_lower)
```

### Day 5-7: Query Rewriting with Claude

**File:** `src/apex_memory/query_router/query_rewriter.py` (NEW)

```python
"""Query rewriting using Claude API for optimal retrieval."""

import logging
import os
from typing import List, Optional
from enum import Enum
import anthropic
from apex_memory.utils.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class RewriteStrategy(Enum):
    """Query rewriting strategies."""
    NORMALIZATION = "normalization"
    HYDE = "hyde"  # Hypothetical Document Embeddings
    DECOMPOSITION = "decomposition"
    EXPANSION = "expansion"


class ClaudeQueryRewriter:
    """
    Query rewriting using Claude 3.5 Sonnet.

    Claude was chosen over OpenAI for:
    - Better instruction following
    - Lower cost (~$3/M tokens vs GPT-4 ~$10/M)
    - Faster response times
    - Superior reasoning for decomposition
    """

    def __init__(self, redis_client=None, cache_ttl: int = 3600):
        """
        Initialize Claude rewriter.

        Args:
            redis_client: Optional Redis for caching rewrites
            cache_ttl: Cache TTL in seconds (default 1 hour)
        """
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.redis = redis_client
        self.cache_ttl = cache_ttl

        # Circuit breaker for API failures
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60
        )

        logger.info("Claude query rewriter initialized")

    async def rewrite(
        self,
        query: str,
        strategy: RewriteStrategy
    ) -> List[str]:
        """
        Rewrite query using specified strategy.

        Args:
            query: Original query
            strategy: Rewriting strategy

        Returns:
            List of rewritten queries (includes original)
        """
        # Check cache first
        if self.redis:
            cache_key = f"rewrite:{hash(query)}:{strategy.value}"
            cached = await self.redis.get(cache_key)
            if cached:
                logger.info(f"Cache hit for rewrite: {query}")
                return json.loads(cached)

        # Rewrite with circuit breaker
        try:
            with self.circuit_breaker:
                rewrites = await self._rewrite_with_claude(query, strategy)

                # Cache result
                if self.redis:
                    await self.redis.setex(
                        cache_key,
                        self.cache_ttl,
                        json.dumps(rewrites)
                    )

                return rewrites

        except Exception as e:
            logger.error(f"Rewrite failed: {e}, falling back to original")
            return [query]  # Fallback to original

    async def _rewrite_with_claude(
        self,
        query: str,
        strategy: RewriteStrategy
    ) -> List[str]:
        """Execute rewriting with Claude API."""

        # Strategy-specific prompts
        prompts = {
            RewriteStrategy.NORMALIZATION: f"""Fix grammar and spelling, standardize formatting:

Query: {query}

Return only the corrected query.""",

            RewriteStrategy.HYDE: f"""Generate a hypothetical document passage that would answer this query:

Query: {query}

Write a concise passage (2-3 sentences) that directly answers this question. Return only the passage.""",

            RewriteStrategy.DECOMPOSITION: f"""Break this complex query into 2-3 simpler sub-queries:

Query: {query}

Return numbered sub-queries (1., 2., 3.) that together answer the original query.""",

            RewriteStrategy.EXPANSION: f"""Expand this query with synonyms and related terms:

Query: {query}

Add relevant synonyms and related search terms. Return only the expanded query."""
        }

        prompt = prompts.get(strategy, "")

        # Call Claude API
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Latest model
            max_tokens=512,
            temperature=0.3,  # Low temperature for consistency
            messages=[{"role": "user", "content": prompt}]
        )

        rewritten_text = response.content[0].text.strip()

        # Parse based on strategy
        if strategy == RewriteStrategy.DECOMPOSITION:
            # Extract numbered list
            rewrites = []
            for line in rewritten_text.split('\n'):
                if line.strip() and any(line.startswith(f"{i}.") for i in range(1, 10)):
                    rewrites.append(line.split('.', 1)[1].strip())
            return [query] + rewrites  # Include original
        else:
            return [query, rewritten_text]  # Original + rewrite
```

### Day 8-10: Analytics Infrastructure

**File:** `init-scripts/postgres/analytics.sql` (NEW)

```sql
-- Query Router Analytics Schema
-- Time-series partitioned for scale

CREATE TABLE IF NOT EXISTS routing_decisions (
    id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    query TEXT,
    intent VARCHAR(50),
    databases_used TEXT[],
    database_scores JSONB,
    database_latencies JSONB,
    num_results INTEGER,
    avg_relevance FLOAT,
    latency_ms FLOAT,
    cached BOOLEAN,
    trace_id VARCHAR(64),
    user_id VARCHAR(255),

    -- Partitioning key
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions
CREATE TABLE routing_decisions_2025_10 PARTITION OF routing_decisions
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE routing_decisions_2025_11 PARTITION OF routing_decisions
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE routing_decisions_2025_12 PARTITION OF routing_decisions
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Indices for fast queries
CREATE INDEX idx_routing_timestamp ON routing_decisions(timestamp DESC);
CREATE INDEX idx_routing_intent ON routing_decisions(intent);
CREATE INDEX idx_routing_trace_id ON routing_decisions(trace_id);
CREATE INDEX idx_routing_user_id ON routing_decisions(user_id);

-- GIN index for JSONB queries
CREATE INDEX idx_routing_database_scores ON routing_decisions USING gin(database_scores);
CREATE INDEX idx_routing_database_latencies ON routing_decisions USING gin(database_latencies);

-- Views for common queries
CREATE OR REPLACE VIEW routing_metrics_hourly AS
SELECT
    date_trunc('hour', timestamp) as hour,
    intent,
    COUNT(*) as total_queries,
    AVG(latency_ms) as avg_latency_ms,
    AVG(avg_relevance) as avg_relevance,
    SUM(CASE WHEN cached THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as cache_hit_rate
FROM routing_decisions
GROUP BY date_trunc('hour', timestamp), intent
ORDER BY hour DESC;
```

**File:** `src/apex_memory/query_router/analytics.py` (NEW)

```python
"""Routing analytics with Prometheus + Jaeger."""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

from prometheus_client import Counter, Histogram, Gauge
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)


# Prometheus Metrics
routing_requests_total = Counter(
    'apex_routing_requests_total',
    'Total routing requests',
    ['intent', 'cached']
)

routing_latency = Histogram(
    'apex_routing_latency_seconds',
    'Routing decision latency',
    ['intent', 'databases'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

routing_accuracy = Gauge(
    'apex_routing_accuracy',
    'Routing accuracy score',
    ['intent']
)

database_query_latency = Histogram(
    'apex_database_query_latency_seconds',
    'Per-database query latency',
    ['database', 'query_type'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)


# Jaeger Tracing Setup
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
    """Record of a routing decision."""
    timestamp: datetime
    query: str
    intent: str
    databases_used: List[str]
    database_scores: Dict[str, float]
    database_latencies: Dict[str, float]
    num_results: int
    avg_relevance: float
    latency_ms: float
    cached: bool
    trace_id: Optional[str] = None
    user_id: Optional[str] = None


class RoutingAnalytics:
    """Track routing decisions with Prometheus + Jaeger + PostgreSQL."""

    def __init__(self, postgres_conn):
        """Initialize analytics."""
        self.db = postgres_conn
        self.tracer = tracer
        logger.info("Routing analytics initialized")

    async def log_decision(
        self,
        query: str,
        intent,
        databases_used: List[str],
        database_scores: Dict[str, float],
        database_latencies: Dict[str, float],
        results: List,
        latency_ms: float,
        cached: bool,
        trace_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Log routing decision to all sinks."""

        avg_relevance = (
            sum(r.get('relevance', 0) for r in results) / len(results)
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

        # Store in PostgreSQL (async)
        await self.db.execute("""
            INSERT INTO routing_decisions (
                timestamp, query, intent, databases_used,
                database_scores, database_latencies, num_results,
                avg_relevance, latency_ms, cached, trace_id, user_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        """,
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
            trace_id,
            user_id
        )
```

---

## Testing Strategy

### Unit Tests

**File:** `tests/unit/test_semantic_classifier.py` (NEW)

```python
import pytest
from src.apex_memory.query_router.semantic_classifier import SemanticIntentClassifier

@pytest.fixture
def classifier():
    return SemanticIntentClassifier(api_key="test-key")

def test_graph_queries(classifier):
    """Test graph query classification."""
    assert classifier.classify("what is connected to ACME Corp") == "graph"
    assert classifier.classify("show relationships between X and Y") == "graph"

def test_temporal_queries(classifier):
    """Test temporal query classification."""
    assert classifier.classify("how did this change over time") == "temporal"
    assert classifier.classify("payment trends last 6 months") == "temporal"

def test_out_of_scope(classifier):
    """Test out-of-scope detection."""
    assert classifier.classify("what is the weather today") is None
    assert classifier.classify("how to cook pasta") is None
```

### Integration Tests

**File:** `tests/integration/test_query_router_upgrade.py` (NEW)

```python
import pytest
from src.apex_memory.query_router.router import QueryRouter

@pytest.mark.asyncio
async def test_semantic_classification_accuracy(router):
    """Test semantic classifier outperforms keyword."""
    test_queries = [
        ("what equipment is connected to ACME", "graph"),
        ("how has behavior changed", "temporal"),
        ("find similar documents", "semantic"),
    ]

    correct = 0
    for query, expected_intent in test_queries:
        result = await router.query(query)
        if result["intent"] == expected_intent:
            correct += 1

    accuracy = correct / len(test_queries)
    assert accuracy >= 0.90  # 90% minimum

@pytest.mark.asyncio
async def test_analytics_integration(router, postgres_pool):
    """Test analytics logging works end-to-end."""
    await router.query("test query")

    # Check PostgreSQL has record
    result = await postgres_pool.fetch_one(
        "SELECT COUNT(*) FROM routing_decisions WHERE query = 'test query'"
    )
    assert result[0] == 1
```

---

## Rollback Procedures

### Emergency Rollback

If critical issues arise during deployment:

```bash
# 1. Disable semantic classification via feature flag
redis-cli SET flag:semantic_router:rollout_pct 0

# 2. Revert to previous Docker image
docker-compose down
git checkout <previous-commit>
docker-compose up -d

# 3. Monitor logs
docker logs -f apex-api
```

### Gradual Rollback

```bash
# Reduce canary percentage
redis-cli SET flag:semantic_router:rollout_pct 5  # From 25% to 5%

# Monitor for 1 hour
# If stable, continue reduction

redis-cli SET flag:semantic_router:rollout_pct 0  # Full rollback
```

---

## Next Steps

1. Complete Phase 0 verification
2. Install dependencies
3. Begin Phase 1 implementation
4. Create Grafana dashboards for monitoring
5. Train semantic router with production queries

---

**Questions or issues?** Refer to [IMPROVEMENT-PLAN.md](./IMPROVEMENT-PLAN.md) for detailed specifications.
