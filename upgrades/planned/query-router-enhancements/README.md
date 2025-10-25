# Query Router Advanced Features

**Status:** 📝 Planning Complete | Ready for Implementation
**Priority:** Non-Critical (Nice to Have)
**Timeline:** 3-4 weeks
**Goal:** Advanced Graphiti features (GraphRAG community detection, query explanation, temporal analytics, graph analytics)

---

## Quick Start

**For implementers:**
1. Read [IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md) - Understand the problem and approach (5 min)
2. Follow [IMPLEMENTATION.md](IMPLEMENTATION.md) - Step-by-step implementation guide (3-4 weeks)
3. Run tests per [TESTING.md](TESTING.md) - Validate all features working (1 hour)
4. If issues arise, check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common problems and solutions

**For reviewers:**
1. Review [IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md) - Goals and success metrics
2. Check [TESTING.md](TESTING.md) - Validation criteria and expected outputs

---

## Problem Statement

**Current State:** Query Router is production-ready (98-99% accuracy) but underutilizes 30% of Graphiti capabilities

**Example (Current - Missing Community Detection):**

```
Query: "Find all equipment-related issues"

Current Routing:
→ Neo4j: Equipment entities
→ Graphiti: Equipment mentions
→ Qdrant: Equipment-related documents

Missing:
❌ Community detection (clusters of related equipment)
❌ Community summaries (auto-generated overviews)
❌ Cross-community patterns
```

**Problem:** Without community detection, the query router cannot:
- Group related equipment into logical clusters
- Provide high-level summaries of equipment communities
- Detect patterns across communities (e.g., "all heavy equipment has similar failure modes")

---

**Desired State:** Full Graphiti capability utilization with community detection, query explanations, and advanced analytics

**Example (Desired - With All Features):**

```
Query: "Find all equipment-related issues"

Enhanced Routing:
→ Neo4j: Equipment entities
→ Graphiti: Hybrid search + community detection
→ Qdrant: Equipment-related documents
→ Community Analysis: Clusters equipment into logical communities

Results:
{
  "entities": [
    {"name": "CAT 950 Loader", "type": "Equipment", "community": "Heavy Equipment"},
    {"name": "Komatsu D65", "type": "Equipment", "community": "Heavy Equipment"},
    {"name": "Volvo VNL 780", "type": "Equipment", "community": "Transportation"}
  ],
  "communities": [
    {
      "name": "Heavy Equipment",
      "summary": "Construction equipment community with 12 machines, primarily used for earth-moving operations",
      "members": 12,
      "common_issues": ["hydraulic failures", "track wear"]
    },
    {
      "name": "Transportation",
      "summary": "Fleet vehicles for long-haul transportation, 28 trucks total",
      "members": 28,
      "common_issues": ["brake wear", "engine diagnostics"]
    }
  ],
  "patterns": [
    {
      "pattern": "Heavy equipment shows 3× higher maintenance costs in winter months",
      "confidence": 0.89
    }
  ],
  "explanation": {
    "why_these_results": "Query classified as 'graph' intent, routed to Neo4j + Graphiti for relationship discovery. Community detection identified 2 primary equipment clusters based on usage patterns and shared maintenance history.",
    "confidence": 0.94,
    "alternative_queries": [
      "Show me heavy equipment maintenance trends",
      "What are the common issues for transportation fleet?"
    ]
  }
}
```

**Benefit:** Comprehensive insights with community clustering, pattern detection, and LLM-generated explanations.

---

## Solution Overview

### What We're Building

**1. Community Detection & GraphRAG** (`apex_memory.query_router.community_manager`)

- Enable Graphiti community detection (fix graphiti-core 0.22.0 bug)
- Auto-generate community summaries (GraphRAG approach)
- Integrate community-based routing into query router
- Support hierarchical community clustering

**2. Query Explanation** (`apex_memory.query_router.query_explainer`)

- LLM-generated result explanations ("Why these results?")
- Confidence intervals for each result
- Alternative query suggestions
- Claude-powered natural language explanations

**3. Temporal Analytics** (`apex_memory.query_router.temporal_analytics`)

- Pattern prediction (predict future trends from historical data)
- Anomaly detection (identify outliers in temporal data)
- Time-series forecasting (predict equipment failures, utilization trends)

**4. Graph Analytics** (`apex_memory.query_router.graph_analytics`)

- Centrality metrics (PageRank, betweenness centrality)
- Shortest path queries (find relationship paths between entities)
- Subgraph extraction (extract relevant entity clusters)
- Entity canonicalization (deduplicate entities across sources)

---

## Architecture

### Before (Current - 70% Graphiti Utilization)

```
Query → Router → [Neo4j, Graphiti (basic), PostgreSQL, Qdrant]
Missing: Community detection, explanations, advanced analytics
```

### After (Enhanced - 100% Graphiti Utilization)

```
Query → Router → Intent Classification
                       ↓
         Complexity Analysis → Simple/Medium/Complex
                       ↓
         Database Selection → [Neo4j, Graphiti (full), PostgreSQL, Qdrant]
                       ↓
         Execute Queries → Parallel execution
                       ↓
         Community Detection → GraphRAG summaries
                       ↓
         Temporal Analytics → Pattern prediction, anomaly detection
                       ↓
         Graph Analytics → Centrality, shortest paths
                       ↓
         Result Aggregation → Intelligent fusion
                       ↓
         Query Explanation → LLM-powered explanations
                       ↓
         Return Enhanced Results
```

---

## Implementation Timeline

### Week 1: Community Detection & GraphRAG (6-8 hours)

**Deliverables:**
- ✅ Fix graphiti-core 0.22.0 bug OR upgrade to 0.23.0+
- ✅ Enable community detection in GraphitiService
- ✅ Create CommunityManager wrapper class
- ✅ Integrate community summaries into query router
- ✅ GraphRAG multi-hop reasoning with communities
- ✅ 10 community detection tests

**Outcome:** Community detection enabled, GraphRAG fully functional

---

### Week 2: Query Explanation & Temporal Analytics (6-8 hours)

**Deliverables:**
- ✅ QueryExplainer class (Claude-powered explanations)
- ✅ Confidence intervals for results
- ✅ Alternative query suggestions
- ✅ Temporal pattern prediction
- ✅ Anomaly detection on temporal data
- ✅ Time-series forecasting
- ✅ 15 tests (8 explanation + 7 temporal)

**Outcome:** Query explanations + temporal analytics fully functional

---

### Week 3: Graph Analytics & Performance (6-8 hours)

**Deliverables:**
- ✅ GraphAnalytics wrapper class
- ✅ Centrality metrics (PageRank, betweenness)
- ✅ Shortest path queries
- ✅ Subgraph extraction
- ✅ Entity canonicalization (deduplication)
- ✅ Performance optimization (batch queries)
- ✅ 5 graph analytics tests

**Outcome:** Graph analytics functional, performance optimized

---

### Week 4: Testing & Documentation (6-8 hours)

**Deliverables:**
- ✅ Fix all disabled tests in `phase3_disabled/`
- ✅ 40+ new tests passing
- ✅ All 223 existing tests still passing (no regression)
- ✅ Complete documentation suite (5 docs)
- ✅ Performance benchmarks (community queries <2s)
- ✅ Deployment guide

**Outcome:** All tests passing, comprehensive documentation

---

## Success Metrics

**Minimum Requirements (Completing Upgrade):**

1. ✅ **Community Detection Enabled** (no bug, working in production)
2. ✅ **GraphRAG Integrated** (community summaries in multi-hop queries)
3. ✅ **Query Explanation** (90%+ user satisfaction with explanations)
4. ✅ **Temporal Analytics** (pattern prediction, anomaly detection working)
5. ✅ **Graph Analytics** (centrality, shortest paths functional)
6. ✅ **All Tests Passing** (223 existing + 40 new = 263 total)
7. ✅ **Zero Regression** (98-99% accuracy maintained)
8. ✅ **Performance** (community queries <2s, explanations <500ms)

**When all criteria met:** Query Router utilizes 100% of Graphiti capabilities

---

## Directory Structure

```
query-router-enhancements/
├── README.md                      # This file - project overview
├── IMPROVEMENT-PLAN.md            # Problem statement, goals, approach (800+ lines)
├── IMPLEMENTATION.md              # Step-by-step implementation guide (2,000+ lines)
├── TESTING.md                     # Test specifications and validation (700+ lines)
├── TROUBLESHOOTING.md             # Common issues and solutions (600+ lines)
│
├── research/                      # Research documentation
│   ├── GRAPHITI-COMMUNITY-DETECTION.md    # Community detection capabilities
│   ├── GRAPHRAG-IMPLEMENTATION.md         # GraphRAG patterns from Microsoft
│   ├── TEMPORAL-ANALYTICS.md              # Time-series analysis best practices
│   └── GRAPH-ALGORITHMS.md                # PageRank, centrality, shortest paths
│
├── tests/                         # Test artifacts
│   ├── sample-queries/            # 10 realistic test queries
│   ├── expected-outputs/          # Expected results with communities
│   ├── validation-queries/        # Cypher validation queries
│   ├── test_community_detection.py
│   ├── test_graphrag_integration.py
│   ├── test_query_explanation.py
│   ├── test_temporal_analytics.py
│   └── test_graph_analytics.py
│
└── examples/                      # Configuration examples
    ├── community-config.yaml      # Community detection settings
    ├── graphrag-config.yaml       # GraphRAG parameters
    └── query-explanation-template.txt  # LLM prompt template
```

---

## Documentation Suite

### For Implementers

**1. [IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md)** (800+ lines)
- Executive summary and problem statement
- Example: current vs desired state
- Goals and success metrics
- Technical approach with architecture diagrams
- 4-week implementation timeline
- Deliverables checklist

**2. [IMPLEMENTATION.md](IMPLEMENTATION.md)** (2,000+ lines)
- Step-by-step implementation guide
- **Week 1:** Community Detection & GraphRAG
- **Week 2:** Query Explanation & Temporal Analytics
- **Week 3:** Graph Analytics & Performance
- **Week 4:** Testing & Documentation
- Code examples and validation steps
- Rollback plan if issues arise

**3. [TESTING.md](TESTING.md)** (700+ lines)
- 40+ test specifications across 4 weeks
- Automated test requirements
- Manual validation queries
- Performance benchmarks
- Success criteria and acceptance tests

**4. [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** (600+ lines)
- Common issues and solutions
- Community detection bugs (graphiti-core 0.22.0 fix)
- GraphRAG performance issues
- Query explanation accuracy problems
- Temporal analytics edge cases
- Graph analytics optimization
- Debugging tools

### For Reviewers

**1. Review IMPROVEMENT-PLAN.md:**
- Validate problem statement is accurate
- Confirm goals align with Query Router enhancement needs
- Check success metrics are measurable

**2. Review TESTING.md:**
- Verify test coverage is comprehensive (40+ tests)
- Check performance benchmarks are realistic
- Confirm validation criteria match enhancement needs

---

## Key Files

### Production Code (To Be Created)

**`apex-memory-system/src/apex_memory/query_router/community_manager.py`** (500+ lines)
- Community detection wrapper for Graphiti
- Community summary generation
- Community-based routing logic
- Hierarchical clustering

**`apex-memory-system/src/apex_memory/query_router/query_explainer.py`** (400+ lines)
- QueryExplainer class
- Claude-powered explanations
- Confidence interval calculation
- Alternative query generation

**`apex-memory-system/src/apex_memory/query_router/temporal_analytics.py`** (600+ lines)
- Pattern prediction
- Anomaly detection
- Time-series forecasting
- Temporal query optimization

**`apex-memory-system/src/apex_memory/query_router/graph_analytics.py`** (500+ lines)
- Centrality metrics (PageRank, betweenness)
- Shortest path algorithms
- Subgraph extraction
- Entity canonicalization

**`apex-memory-system/src/apex_memory/services/graphiti_service.py`** (UPDATED)
- Enable `update_communities=True`
- Fix graphiti-core 0.22.0 bug workaround

**`apex-memory-system/src/apex_memory/query_router/router.py`** (UPDATED)
- Integrate CommunityManager
- Add QueryExplainer
- Add TemporalAnalytics
- Add GraphAnalytics
- Update response format (include explanations, communities)

### Test Artifacts (To Be Created)

**`tests/unit/test_community_detection.py`** (10 tests)
- Community detection accuracy
- Community summary generation
- Hierarchical clustering

**`tests/unit/test_query_explanation.py`** (8 tests)
- Explanation accuracy
- Confidence intervals
- Alternative query suggestions

**`tests/unit/test_temporal_analytics.py`** (7 tests)
- Pattern prediction
- Anomaly detection
- Time-series forecasting

**`tests/unit/test_graph_analytics.py`** (5 tests)
- Centrality metrics
- Shortest paths
- Subgraph extraction

**`tests/integration/test_graphrag_integration.py`** (10 tests)
- End-to-end GraphRAG queries
- Community-based routing
- Multi-hop reasoning with communities

---

## Feature Flag Strategy

### Safe Defaults

**Default:** All new features disabled (safe rollout)

```python
# router.py
enable_community_detection=False  # Feature flag
enable_query_explanation=False    # Feature flag
enable_temporal_analytics=False   # Feature flag
enable_graph_analytics=False      # Feature flag
```

**Opt-In:** Enable features individually

```python
# Enable community detection only
enable_community_detection=True

# Enable all features
enable_community_detection=True
enable_query_explanation=True
enable_temporal_analytics=True
enable_graph_analytics=True
```

### Testing Strategy

**Phase 1: Feature Flags Off (Baseline Preservation)**

```bash
# All features disabled
cd apex-memory-system
pytest tests/ --ignore=tests/load/ -v

# Expected: All 223 existing tests pass (no regression)
```

**Phase 2: Feature Flags On (New Feature Validation)**

```bash
# Enable all features
# Update test configuration to enable features

pytest upgrades/active/query-router-enhancements/tests/ -v

# Expected: 40+ new tests pass
```

**Phase 3: Deployment**

```bash
# After validation passes, enable in production
# Update router initialization to enable features

# Monitor performance
# Community queries: <2s
# Query explanations: <500ms
```

---

## Dependencies

### Required Services

- **Neo4j:** Running on `localhost:7687` (for Graphiti community detection)
- **OpenAI API:** Valid API key for GPT-5 (for community summaries)
- **Anthropic API:** Valid API key for Claude 3.5 Sonnet (for query explanations)

### Python Dependencies

- `graphiti-core` (0.23.0+) - Temporal knowledge graph (fix community detection bug)
- `pydantic` - Data validation (already installed)
- `openai` - OpenAI API client (already installed)
- `anthropic` - Anthropic API client (already installed)
- `networkx` - Graph analytics (NEW - for centrality metrics)
- `scikit-learn` - Time-series analysis (NEW - for pattern prediction)

**New dependencies to add:**

```bash
pip install networkx scikit-learn
```

---

## Deployment Checklist

**Before Deployment:**

- [ ] All 4 weeks of implementation complete
- [ ] CommunityManager class created and tested
- [ ] QueryExplainer class created and tested
- [ ] TemporalAnalytics class created and tested
- [ ] GraphAnalytics class created and tested
- [ ] Feature flags tested (on/off)
- [ ] 40+ new tests passing
- [ ] Existing 223 tests still passing
- [ ] Performance benchmarks met (community queries <2s, explanations <500ms)
- [ ] Rollback plan tested

**After Deployment:**

- [ ] Enable community detection in production (feature flag)
- [ ] Monitor Grafana metrics for community queries
- [ ] Query Neo4j to verify communities exist
- [ ] Review first 100 queries for explanation quality
- [ ] Track user satisfaction with explanations
- [ ] Document any issues in GitHub

---

## Expected Outcomes

### Immediate (Post-Implementation)

1. **100% Graphiti Utilization** (vs. 70% current)
2. **Community Detection** (auto-clustering of related entities)
3. **Query Explanations** (90%+ user satisfaction)
4. **Temporal Analytics** (pattern prediction, anomaly detection)
5. **Graph Analytics** (centrality, shortest paths)

### Medium-Term (1-2 weeks post-deployment)

1. **Better Search Results** (community-based routing improves relevance)
2. **Improved User Experience** (explanations build trust)
3. **Advanced Analytics** (patterns and anomalies detected automatically)

### Long-Term (1+ months post-deployment)

1. **Competitive Advantage** (100% Graphiti utilization vs competitors)
2. **Community Insights** (auto-generated summaries of entity clusters)
3. **Predictive Analytics** (forecast trends, equipment failures)

---

## Risks and Mitigations

### Risk 1: Community Detection Bug Persists

**Mitigation:**
- Test graphiti-core 0.23.0+ first
- If bug persists, implement custom community detection using NetworkX
- Document workaround in TROUBLESHOOTING.md

### Risk 2: Query Explanation Accuracy Low

**Mitigation:**
- Start with simple template-based explanations
- Iterate on Claude prompt based on user feedback
- Add confidence intervals to flag low-quality explanations

### Risk 3: Performance Impact

**Mitigation:**
- Feature flags allow gradual rollout
- Cache community summaries (1 hour TTL)
- Async execution for all new features
- Monitor P90/P99 latency closely

### Risk 4: Implementation Takes Longer Than 4 Weeks

**Mitigation:**
- Detailed week-by-week implementation guide
- Clear success criteria for each week
- Can deploy partial (Week 1+2 complete, Week 3+4 post-deployment)

---

## Next Steps

### For Implementers

1. **Read IMPROVEMENT-PLAN.md** (5 min) - Understand the why
2. **Follow IMPLEMENTATION.md Week 1** (6-8 hours) - Community Detection & GraphRAG
3. **Follow IMPLEMENTATION.md Week 2** (6-8 hours) - Query Explanation & Temporal Analytics
4. **Follow IMPLEMENTATION.md Week 3** (6-8 hours) - Graph Analytics & Performance
5. **Follow IMPLEMENTATION.md Week 4** (6-8 hours) - Testing & Documentation
6. **Deploy to production** - Enable features via feature flags

### For Reviewers

1. **Review IMPROVEMENT-PLAN.md** - Validate approach
2. **Review TESTING.md** - Confirm test coverage adequate
3. **Approve for implementation** - If satisfied with plan

---

## Support and Questions

**Documentation:**
- See [IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md) for problem statement and approach
- See [IMPLEMENTATION.md](IMPLEMENTATION.md) for step-by-step guide
- See [TESTING.md](TESTING.md) for validation criteria
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

**Research:**
- See `research/GRAPHITI-COMMUNITY-DETECTION.md` for community detection capabilities
- See `research/GRAPHRAG-IMPLEMENTATION.md` for GraphRAG patterns
- See `research/TEMPORAL-ANALYTICS.md` for time-series analysis
- See `research/GRAPH-ALGORITHMS.md` for graph algorithm documentation

**Examples:**
- See `examples/community-config.yaml` for community detection configuration
- See `examples/graphrag-config.yaml` for GraphRAG parameters
- See `examples/query-explanation-template.txt` for explanation prompt template

---

**Status:** Ready for Implementation
**Timeline:** 3-4 weeks
**Success Criteria:** 100% Graphiti utilization + 40+ new tests passing + zero regression
**Blocking:** None (non-critical enhancement)

Let's unlock the full power of Graphiti! 🚀
