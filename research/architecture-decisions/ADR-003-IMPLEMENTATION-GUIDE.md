# ADR-003 Implementation Guide: Query Routing System

**Document Type:** Implementation Quick Reference
**ADR Reference:** ADR-003-intent-based-query-routing.md
**Target Audience:** Development Team
**Implementation Timeline:** Week 1-6 (6 weeks)

---

## Quick Start

**What we're building:** Hybrid query routing system that routes queries to optimal database(s) using rule-based patterns (fast) with LLM fallback (accurate).

**Success criteria:**
- 70-80% rule hit rate
- P90 routing latency <500ms
- Routing accuracy >95%
- Cost <$0.0002/query

---

## Phase 1: Rule-Based Foundation (Week 1-2)

### Objective
Implement fast, deterministic routing for common query patterns.

### Deliverables

**1. Rule Router Class (`src/apex_memory/query_router/rule_router.py`)**

```python
from dataclasses import dataclass
from typing import List
import re

@dataclass
class RouteDecision:
    """Routing decision output"""
    intent: str  # "graph_traversal" | "vector_similarity" | "hybrid_search" | "temporal_reasoning" | "multi_database"
    databases: List[str]  # ["neo4j", "qdrant", "postgresql", "redis"]
    confidence: float  # 0.0 to 1.0
    reasoning: str
    routing_method: str  # "rule_based" | "llm_fallback" | "degraded_mode"

class RuleRouter:
    """Rule-based query router for high-confidence patterns"""

    # High-confidence patterns (95%+ accuracy)
    GRAPH_PATTERNS = [
        r"\b(how|what).*(related|connection|path|link)",
        r"\bshortest path\b",
        r"\bhops?\b.*\b(away|from)",
        r"\bconnect(s|ed|ing)?\b.*\bto\b",
    ]

    VECTOR_PATTERNS = [
        r"\b(similar|like|resembles)\b",
        r"\bsemantically\b.*\b(related|close)",
        r"\brecommend\b",
        r"\bfind.*\b(similar|like)\b",
    ]

    HYBRID_PATTERNS = [
        r"\b(author|date|tag|category|metadata)\b",
        r"\bfilter.*\b(by|with)\b",
        r"\bsince\b.*\b\d{4}\b",  # Date filtering
        r"\bwith\b.*\b(tag|category|label)\b",
    ]

    TEMPORAL_PATTERNS = [
        r"\b(changed|evolved|trend|pattern).*\bover time\b",
        r"\btemporal\b",
        r"\bduring\b.*\b\d{4}\b",
        r"\bhistory\b.*\b(of|for)\b",
    ]

    def route(self, query: str) -> RouteDecision:
        """Route query using rule-based patterns"""

        query_lower = query.lower()

        # Check patterns in priority order
        if self._match_patterns(query_lower, self.TEMPORAL_PATTERNS):
            return RouteDecision(
                intent="temporal_reasoning",
                databases=["neo4j", "graphiti"],
                confidence=0.95,
                reasoning="Temporal keywords detected (changed/evolved/trend over time)",
                routing_method="rule_based"
            )

        if self._match_patterns(query_lower, self.GRAPH_PATTERNS):
            return RouteDecision(
                intent="graph_traversal",
                databases=["neo4j"],
                confidence=0.95,
                reasoning="Graph relationship keywords detected (related/connection/path)",
                routing_method="rule_based"
            )

        if self._match_patterns(query_lower, self.VECTOR_PATTERNS):
            return RouteDecision(
                intent="vector_similarity",
                databases=["qdrant"],
                confidence=0.95,
                reasoning="Similarity keywords detected (similar/like/resembles)",
                routing_method="rule_based"
            )

        if self._match_patterns(query_lower, self.HYBRID_PATTERNS):
            return RouteDecision(
                intent="hybrid_search",
                databases=["postgresql"],
                confidence=0.90,
                reasoning="Metadata filtering keywords detected (author/date/tag)",
                routing_method="rule_based"
            )

        # Low confidence - no clear pattern
        return RouteDecision(
            intent="unknown",
            databases=[],
            confidence=0.0,
            reasoning="No high-confidence pattern matched",
            routing_method="rule_based"
        )

    def _match_patterns(self, query: str, patterns: List[str]) -> bool:
        """Check if query matches any pattern in list"""
        return any(re.search(pattern, query) for pattern in patterns)
```

**2. Unit Tests (`tests/unit/query_router/test_rule_router.py`)**

```python
import pytest
from apex_memory.query_router.rule_router import RuleRouter, RouteDecision

@pytest.fixture
def router():
    return RuleRouter()

class TestGraphTraversal:
    """Test graph traversal pattern matching"""

    def test_related_pattern(self, router):
        query = "How are entities X and Y related?"
        decision = router.route(query)

        assert decision.intent == "graph_traversal"
        assert "neo4j" in decision.databases
        assert decision.confidence >= 0.95
        assert decision.routing_method == "rule_based"

    def test_connection_pattern(self, router):
        query = "What connects X to Y?"
        decision = router.route(query)

        assert decision.intent == "graph_traversal"
        assert decision.confidence >= 0.95

    def test_shortest_path_pattern(self, router):
        query = "What is the shortest path between X and Y?"
        decision = router.route(query)

        assert decision.intent == "graph_traversal"
        assert decision.confidence >= 0.95

class TestVectorSimilarity:
    """Test vector similarity pattern matching"""

    def test_similar_pattern(self, router):
        query = "Find documents similar to this concept"
        decision = router.route(query)

        assert decision.intent == "vector_similarity"
        assert "qdrant" in decision.databases
        assert decision.confidence >= 0.95

    def test_like_pattern(self, router):
        query = "Show me papers like this example"
        decision = router.route(query)

        assert decision.intent == "vector_similarity"
        assert decision.confidence >= 0.95

class TestHybridSearch:
    """Test hybrid search pattern matching"""

    def test_author_filter(self, router):
        query = "Papers by author X on topic Y"
        decision = router.route(query)

        assert decision.intent == "hybrid_search"
        assert "postgresql" in decision.databases
        assert decision.confidence >= 0.90

    def test_date_filter(self, router):
        query = "Documents since 2023 about AI"
        decision = router.route(query)

        assert decision.intent == "hybrid_search"
        assert decision.confidence >= 0.90

class TestTemporalReasoning:
    """Test temporal reasoning pattern matching"""

    def test_changed_over_time(self, router):
        query = "How has X's relationship with Y changed over time?"
        decision = router.route(query)

        assert decision.intent == "temporal_reasoning"
        assert "neo4j" in decision.databases
        assert "graphiti" in decision.databases
        assert decision.confidence >= 0.95

class TestEdgeCases:
    """Test edge cases and low-confidence scenarios"""

    def test_ambiguous_query(self, router):
        query = "Tell me about X"
        decision = router.route(query)

        assert decision.intent == "unknown"
        assert decision.confidence == 0.0
        assert decision.databases == []

    def test_empty_query(self, router):
        query = ""
        decision = router.route(query)

        assert decision.intent == "unknown"
        assert decision.confidence == 0.0
```

**3. Performance Target: <50ms P90 latency**

Validate with benchmark:

```python
import time
import numpy as np

def benchmark_rule_router():
    router = RuleRouter()
    queries = [
        "How are X and Y related?",
        "Find documents similar to X",
        "Papers by author X since 2023",
        # ... 100+ test queries
    ]

    latencies = []
    for query in queries:
        start = time.perf_counter()
        router.route(query)
        latencies.append((time.perf_counter() - start) * 1000)  # ms

    print(f"P50: {np.percentile(latencies, 50):.2f}ms")
    print(f"P90: {np.percentile(latencies, 90):.2f}ms")
    print(f"P99: {np.percentile(latencies, 99):.2f}ms")

    assert np.percentile(latencies, 90) < 50, "P90 latency exceeds 50ms"
```

---

## Phase 2: LLM Fallback (Week 3-4)

### Objective
Add LLM-based intent classification for ambiguous queries.

### Deliverables

**1. LLM Router Class (`src/apex_memory/query_router/llm_router.py`)**

```python
from openai import OpenAI
import json
from typing import Optional
from .rule_router import RouteDecision

class LLMRouter:
    """LLM-based query router for ambiguous patterns"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)

    def classify(self, query: str) -> RouteDecision:
        """Classify query intent using GPT-4o function calling"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",  # 100% structured output reliability
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a query router for a multi-database system with:\n"
                            "- Neo4j: Graph relationships and multi-hop traversal\n"
                            "- Qdrant: Vector similarity search\n"
                            "- PostgreSQL: Hybrid search (metadata + semantic)\n"
                            "- Redis: Cache layer\n\n"
                            "Classify the user's query intent and select optimal database(s)."
                        )
                    },
                    {"role": "user", "content": query}
                ],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "route_query",
                        "description": "Route query to optimal database(s) based on intent",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "intent": {
                                    "type": "string",
                                    "enum": [
                                        "graph_traversal",
                                        "vector_similarity",
                                        "hybrid_search",
                                        "temporal_reasoning",
                                        "multi_database"
                                    ],
                                    "description": "Primary query intent"
                                },
                                "databases": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": ["neo4j", "qdrant", "postgresql", "redis", "graphiti"]
                                    },
                                    "description": "Optimal database(s) to query"
                                },
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                    "description": "Confidence in routing decision (0.0-1.0)"
                                },
                                "reasoning": {
                                    "type": "string",
                                    "description": "Explain why this routing was chosen"
                                }
                            },
                            "required": ["intent", "databases", "confidence", "reasoning"]
                        }
                    }
                }],
                tool_choice={"type": "function", "function": {"name": "route_query"}}
            )

            # Parse function call response
            tool_call = response.choices[0].message.tool_calls[0]
            result = json.loads(tool_call.function.arguments)

            return RouteDecision(
                intent=result["intent"],
                databases=result["databases"],
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                routing_method="llm_fallback"
            )

        except Exception as e:
            # Fallback to degraded mode on API error
            return RouteDecision(
                intent="vector_similarity",
                databases=["qdrant"],
                confidence=0.5,
                reasoning=f"LLM API error, fallback to default vector search: {str(e)}",
                routing_method="degraded_mode"
            )
```

**2. Hybrid Coordinator (`src/apex_memory/query_router/hybrid_router.py`)**

```python
from .rule_router import RuleRouter, RouteDecision
from .llm_router import LLMRouter

class HybridRouter:
    """Hybrid query router combining rules + LLM fallback"""

    def __init__(self, confidence_threshold: float = 0.9, llm_api_key: str = None):
        self.rule_router = RuleRouter()
        self.llm_router = LLMRouter(api_key=llm_api_key)
        self.confidence_threshold = confidence_threshold

    def route(self, query: str) -> RouteDecision:
        """Route query using rules with LLM fallback for ambiguous queries"""

        # Step 1: Try rule-based routing
        rule_decision = self.rule_router.route(query)

        # Step 2: If high confidence, use rules
        if rule_decision.confidence >= self.confidence_threshold:
            return rule_decision

        # Step 3: Fallback to LLM for ambiguous queries
        llm_decision = self.llm_router.classify(query)

        # Log rule confidence for monitoring
        llm_decision.reasoning += f" (rule_confidence: {rule_decision.confidence:.2f})"

        return llm_decision
```

**3. Integration Tests (`tests/integration/query_router/test_hybrid_router.py`)**

```python
import pytest
from apex_memory.query_router.hybrid_router import HybridRouter

@pytest.fixture
def router():
    return HybridRouter(confidence_threshold=0.9)

class TestRuleHitRate:
    """Test that common queries hit rules (not LLM)"""

    def test_common_graph_query_uses_rules(self, router):
        query = "How are X and Y related?"
        decision = router.route(query)

        assert decision.routing_method == "rule_based"
        assert decision.confidence >= 0.9

    def test_common_vector_query_uses_rules(self, router):
        query = "Find documents similar to X"
        decision = router.route(query)

        assert decision.routing_method == "rule_based"
        assert decision.confidence >= 0.9

class TestLLMFallback:
    """Test that ambiguous queries use LLM fallback"""

    def test_ambiguous_query_uses_llm(self, router):
        query = "Find similar relationships to X's network"
        decision = router.route(query)

        assert decision.routing_method == "llm_fallback"
        assert decision.intent in ["graph_traversal", "vector_similarity", "multi_database"]

    def test_complex_multi_database_query(self, router):
        query = "Papers by X that relate to Y's connections"
        decision = router.route(query)

        assert decision.routing_method == "llm_fallback"
        assert len(decision.databases) >= 2  # Multi-database query
```

---

## Phase 3: Monitoring & Tuning (Week 5-6)

### Objective
Implement monitoring, A/B test confidence thresholds, validate production readiness.

### Deliverables

**1. Prometheus Metrics (`src/apex_memory/query_router/metrics.py`)**

```python
from prometheus_client import Counter, Histogram, Gauge

# Routing decision metrics
routing_decisions = Counter(
    'query_routing_decisions_total',
    'Total routing decisions',
    ['routing_method', 'intent', 'databases']
)

routing_latency = Histogram(
    'query_routing_latency_seconds',
    'Routing decision latency',
    ['routing_method'],
    buckets=[0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

routing_confidence = Histogram(
    'query_routing_confidence',
    'Routing decision confidence scores',
    ['routing_method'],
    buckets=[0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0]
)

llm_api_errors = Counter(
    'query_routing_llm_errors_total',
    'LLM API errors',
    ['error_type']
)

rule_hit_rate = Gauge(
    'query_routing_rule_hit_rate',
    'Percentage of queries routed by rules'
)
```

**2. Grafana Dashboard**

Create dashboard with 6 key metrics:

- **Rule Hit Rate** (target: 70-80%)
- **LLM Fallback Rate** (target: 20-30%)
- **P50/P90/P99 Latency** (target: P90 <500ms)
- **Routing Accuracy** (manual validation, target: >95%)
- **Cost per Query** (target: <$0.0002)
- **Cache Hit Rate** (Redis, target: >70%)

**3. A/B Testing Script**

```python
def ab_test_confidence_thresholds():
    """Test different confidence thresholds: 0.85, 0.9, 0.95"""

    thresholds = [0.85, 0.9, 0.95]
    test_queries = load_real_usage_queries(n=1000)  # From logs

    results = {}
    for threshold in thresholds:
        router = HybridRouter(confidence_threshold=threshold)

        rule_hits = 0
        llm_fallbacks = 0
        total_latency = []

        for query in test_queries:
            start = time.perf_counter()
            decision = router.route(query)
            latency = time.perf_counter() - start

            total_latency.append(latency)

            if decision.routing_method == "rule_based":
                rule_hits += 1
            elif decision.routing_method == "llm_fallback":
                llm_fallbacks += 1

        results[threshold] = {
            "rule_hit_rate": rule_hits / len(test_queries),
            "llm_fallback_rate": llm_fallbacks / len(test_queries),
            "p90_latency_ms": np.percentile(total_latency, 90) * 1000
        }

    print(results)
    # Select threshold with best balance: 70-80% rule hit rate, P90 <500ms
```

---

## Production Checklist

### Week 6: Pre-Launch Validation

- [ ] **Unit Tests:** 95% code coverage (50+ test cases)
- [ ] **Integration Tests:** 100+ queries from real usage logs
- [ ] **Performance:**
  - [ ] P90 routing latency <500ms
  - [ ] Rule hit rate 70-80%
  - [ ] LLM fallback rate 20-30%
- [ ] **Accuracy:** Manual validation of 100 queries (>95% correct routing)
- [ ] **Cost:** Average cost <$0.0002/query
- [ ] **Monitoring:**
  - [ ] Prometheus metrics instrumented
  - [ ] Grafana dashboard deployed
  - [ ] Alerts configured (LLM error rate >5%, routing accuracy <90%)
- [ ] **Fallback Mechanisms:**
  - [ ] Degraded mode tested (LLM API offline)
  - [ ] Default to Qdrant vector search validated
- [ ] **Documentation:**
  - [ ] Code comments for all routing patterns
  - [ ] Decision matrix (query pattern → database mapping)
  - [ ] Runbook for monitoring and troubleshooting

### Gradual Rollout Plan

1. **10% traffic** (Day 1-2): Monitor for errors, validate metrics
2. **50% traffic** (Day 3-5): A/B test vs old routing (if exists)
3. **100% traffic** (Day 6+): Full production, continue monitoring

**Rollback Criteria:**
- Routing accuracy <90%
- P90 latency >1s
- LLM API error rate >10%
- Cost >2x target ($0.0004/query)

---

## Key Research References

**For implementation questions, refer to:**

1. **LangChain Routing Guide** (Tier 1)
   - URL: https://python.langchain.com/docs/how_to/routing/
   - Use case: Rule-based routing patterns

2. **OpenAI Structured Outputs** (Tier 1)
   - URL: https://openai.com/index/introducing-structured-outputs-in-the-api/
   - Use case: GPT-4o function calling implementation

3. **LangChain Multi-Index Router** (Tier 2)
   - URL: https://github.com/langchain-ai/langchain/tree/v0.2/templates/rag-multi-index-router/
   - Use case: Production routing example

4. **Haystack Fallback Tutorial** (Tier 2)
   - URL: https://haystack.deepset.ai/tutorials/36_building_fallbacks_with_conditional_routing
   - Use case: Fallback mechanisms

**All research saved at:**
- `research/documentation/` (official docs)
- `research/examples/` (code samples)
- `research/architecture-decisions/ADR-003-RESEARCH-SUMMARY.md` (full research summary)

---

## Support Contacts

- **ADR Author:** Deep Researcher Agent
- **Technical Review:** CTO
- **Research Validation:** CIO
- **Operational Review:** COO
- **Implementation Lead:** [Your Name]

---

**Document Version:** 1.0
**Last Updated:** 2025-10-06
**Next Review:** Post-implementation (Week 6)
