# Query Router Advanced Features - Testing Guide

**Document:** Comprehensive Testing Specifications
**Test Count:** 40+ tests across 4 weeks
**Coverage Goal:** 100% of new features + zero regression

---

## Test Overview

**Total Tests:** 263 (223 existing + 40 new)

**New Tests Breakdown:**
- Week 1: Community Detection (10 tests)
- Week 2: Query Explanation + Temporal Analytics (15 tests)
- Week 3: Graph Analytics (5 tests)
- Week 4: Integration + Re-enabled Tests (10 new + 45 re-enabled)

---

## Week 1 Tests: Community Detection (10 tests)

### Unit Tests: `test_community_detection.py`

**Test 1: `test_detect_communities_filters_by_min_size`**
```python
# Verify communities filtered by minimum member count
assert len(communities) == 1  # Only comm with 12 members, not 2
assert communities[0].member_count == 12
```

**Test 2: `test_generate_community_summary_calls_gpt5`**
```python
# Verify GPT-5 called for summary generation
assert call_kwargs['model'] == "gpt-5"
assert summary == "Test community summary"
```

**Test 3: `test_get_community_insights_returns_insights`**
```python
# Verify insights calculated correctly
assert insights.common_attributes['entity_types'] == ['Equipment']
assert insights.avg_entity_age_days == 120.5
```

**Test 4: `test_detect_communities_handles_errors_gracefully`**
```python
# Verify graceful error handling
communities = await manager.detect_communities()  # Neo4j error injected
assert communities == []  # Returns empty list on error
```

**Test 5: `test_generate_summary_truncates_members_to_20`**
```python
# Verify prompt truncates large member lists
member_mentions = prompt.count("Entity ")
assert member_mentions == 20  # Truncated from 30 to 20
```

**Test 6: `test_generate_all_summaries_batch_processing`**
```python
# Verify batch summary generation
result = await manager.generate_all_summaries(communities)
assert len(result) == 2
assert all(c.summary for c in result)
```

**Test 7: `test_build_community_hierarchy_when_disabled`**
```python
# Verify hierarchy returns empty when disabled
hierarchy = await manager.build_community_hierarchy(communities)
assert hierarchy == {}
```

**Test 8: `test_build_community_hierarchy_groups_by_type`**
```python
# Verify hierarchy grouping
assert "Equipment" in hierarchy
assert "Vehicle" in hierarchy
assert "c-001" in hierarchy["Equipment"]
```

**Test 9: `test_get_community_members_returns_entity_list`**
```python
# Verify member list retrieval
members = await manager._get_community_members(community_id="c-001")
assert len(members) == 2
assert members[0]['name'] == 'Entity 1'
```

**Test 10: `test_extract_primary_type_identifies_equipment`**
```python
# Verify entity type extraction from summary
primary_type = manager._extract_primary_type("equipment community with loaders")
assert primary_type == "Equipment"
```

---

### Integration Tests: `test_community_router_integration.py`

**Test 11: `test_query_with_community_detection_enabled`**
```python
# E2E test with community detection ON
result = await router.query("Find all equipment")
assert "communities" in result
assert len(result["communities"]) > 0
assert result["communities"][0]["summary"] is not None
```

**Test 12: `test_query_with_community_detection_disabled`**
```python
# E2E test with community detection OFF
result = await router.query("Find all equipment")
assert result["communities"] == []
```

**Expected Results:** 12/12 tests passing

---

## Week 2 Tests: Query Explanation + Temporal Analytics (15 tests)

### Unit Tests: `test_query_explanation.py` (8 tests)

**Test 1: `test_explain_results_generates_explanation`**
```python
# Verify explanation generated
explanation = await explainer.explain_results(...)
assert len(explanation.why_these_results) > 50  # Meaningful explanation
assert explanation.confidence > 0
```

**Test 2: `test_explain_results_calls_claude`**
```python
# Verify Claude 3.5 Sonnet called
assert call_kwargs['model'] == "claude-3-5-sonnet-20241022"
```

**Test 3: `test_explain_results_includes_reasoning_steps`**
```python
# Verify reasoning steps present
assert len(explanation.reasoning_steps) >= 3
assert "Intent Classification" in explanation.reasoning_steps[0]
```

**Test 4: `test_suggest_alternative_queries_returns_3_queries`**
```python
# Verify alternative queries suggested
alternatives = await explainer.suggest_alternative_queries(...)
assert len(alternatives) == 3
assert all(isinstance(q, str) for q in alternatives)
```

**Test 5: `test_calculate_confidence_intervals_for_results`**
```python
# Verify confidence intervals calculated
intervals = await explainer.calculate_confidence_intervals(results)
assert len(intervals) == len(results)
assert all(0 <= i.lower <= i.upper <= 1 for i in intervals)
```

**Test 6: `test_build_context_includes_all_info`**
```python
# Verify context string complete
context = explainer._build_context(...)
assert "Intent Classification" in context
assert "Databases Queried" in context
assert "Results Returned" in context
```

**Test 7: `test_explain_results_handles_errors_gracefully`**
```python
# Verify graceful error handling
explanation = await explainer.explain_results(...)  # Claude error injected
assert explanation.why_these_results == "Unable to generate explanation (error occurred)"
```

**Test 8: `test_explanation_generation_under_500ms`**
```python
# Verify performance requirement
explanation = await explainer.explain_results(...)
assert explanation.generation_time_ms < 500
```

---

### Unit Tests: `test_temporal_analytics.py` (7 tests)

**Test 1: `test_predict_patterns_returns_patterns`**
```python
# Verify pattern prediction
patterns = await analytics.predict_patterns(entity_type="Equipment", property_name="maintenance_cost")
assert len(patterns) > 0
assert patterns[0].confidence > 0.8
```

**Test 2: `test_detect_anomalies_identifies_outliers`**
```python
# Verify anomaly detection
anomalies = await analytics.detect_anomalies(entity_uuid="e-001", property_name="frequency")
assert len(anomalies) > 0
assert anomalies[0].severity in ["low", "medium", "high"]
```

**Test 3: `test_forecast_trend_predicts_future_values`**
```python
# Verify time-series forecasting
forecast = await analytics.forecast_trend(entity_type="Equipment", forecast_days=30)
assert len(forecast.predicted_values) == 30
assert all(v.confidence_lower <= v.value <= v.confidence_upper for v in forecast.predicted_values)
```

**Test 4: `test_pattern_prediction_accuracy_above_85_percent`**
```python
# Verify pattern prediction accuracy
patterns = await analytics.predict_patterns(...)
true_positives = sum(1 for p in patterns if p.verified)
accuracy = true_positives / len(patterns)
assert accuracy >= 0.85
```

**Test 5: `test_anomaly_detection_precision_above_90_percent`**
```python
# Verify anomaly detection precision
anomalies = await analytics.detect_anomalies(...)
true_anomalies = sum(1 for a in anomalies if a.verified)
precision = true_anomalies / len(anomalies)
assert precision >= 0.90
```

**Test 6: `test_temporal_analytics_latency_under_1s`**
```python
# Verify performance
start = time.time()
patterns = await analytics.predict_patterns(...)
elapsed_ms = (time.time() - start) * 1000
assert elapsed_ms < 1000
```

**Test 7: `test_temporal_analytics_handles_missing_data`**
```python
# Verify robustness with missing data
patterns = await analytics.predict_patterns(entity_type="NonExistent")
assert patterns == []  # Graceful handling
```

**Expected Results:** 15/15 tests passing

---

## Week 3 Tests: Graph Analytics (5 tests)

### Unit Tests: `test_graph_analytics.py`

**Test 1: `test_calculate_centrality_returns_pagerank`**
```python
# Verify PageRank centrality
centrality = await analytics.calculate_centrality(entity_type="Equipment")
assert "pagerank" in centrality
assert 0 <= centrality["pagerank"]["CAT 950"] <= 1
```

**Test 2: `test_find_shortest_path_returns_path`**
```python
# Verify shortest path calculation
path = await analytics.find_shortest_path(from_uuid="e-001", to_uuid="e-002")
assert len(path.nodes) >= 2
assert path.nodes[0] == "e-001"
assert path.nodes[-1] == "e-002"
```

**Test 3: `test_extract_subgraph_returns_nodes_and_edges`**
```python
# Verify subgraph extraction
subgraph = await analytics.extract_subgraph(center_uuid="e-001", max_depth=2)
assert len(subgraph.nodes) > 1
assert len(subgraph.edges) > 0
```

**Test 4: `test_centrality_identifies_most_central_entity`**
```python
# Verify centrality ranking
centrality = await analytics.calculate_centrality()
most_central = max(centrality["pagerank"].items(), key=lambda x: x[1])
assert most_central[1] > 0.1  # Meaningful centrality score
```

**Test 5: `test_graph_analytics_latency_under_1s`**
```python
# Verify performance
start = time.time()
centrality = await analytics.calculate_centrality()
elapsed_ms = (time.time() - start) * 1000
assert elapsed_ms < 1000
```

**Expected Results:** 5/5 tests passing

---

## Week 4 Tests: Integration + Re-enabled Tests (55 tests)

### Integration Tests: `test_graphrag_integration.py` (10 tests)

**Test 1: `test_graphrag_multi_hop_with_communities`**
```python
# Verify GraphRAG with community context
result = await router.query("Find all equipment maintenance patterns")
assert "communities" in result
assert "patterns" in result
assert len(result["patterns"]) > 0
```

**Test 2: `test_community_based_routing`**
```python
# Verify routing uses community information
result = await router.query("Equipment issues in Heavy Equipment community")
assert "Heavy Equipment" in [c["name"] for c in result["communities"]]
```

**Test 3: `test_end_to_end_enhanced_query_flow`**
```python
# Complete E2E test
result = await router.query("Find equipment-related issues")

# Verify all enhancements present
assert "communities" in result
assert len(result["communities"]) > 0
assert "explanation" in result
assert result["explanation"]["why_these_results"]
assert "patterns" in result
assert "anomalies" in result
assert "graph_analytics" in result
```

**Test 4-10:** Additional GraphRAG scenarios (community summaries, hierarchical clustering, cross-community patterns, etc.)

---

### Re-enabled Tests from `phase3_disabled/` (45 tests)

**File:** `test_router_async.py` (15 tests)
- All async routing tests
- Parallel database execution
- Error handling in async flow

**File:** `test_multi_router.py` (12 tests)
- Complex query decomposition
- Sub-query routing
- Result aggregation

**File:** `test_query_improver.py` (8 tests)
- Query normalization
- HyDE query expansion
- Query clarification

**File:** `test_query_rewriter.py` (10 tests)
- Claude-powered query rewriting
- Intent-based rewriting
- Query optimization

---

## Performance Benchmarks

### Community Queries

**Requirement:** <2s for community detection + summary generation

**Test:**
```bash
pytest tests/performance/test_community_performance.py -v

# Expected:
# Community detection: <500ms
# Summary generation (batch 10): <1500ms
# Total: <2000ms ✅
```

---

### Query Explanations

**Requirement:** <500ms for explanation generation

**Test:**
```bash
pytest tests/performance/test_explanation_performance.py -v

# Expected:
# Claude API call: <400ms
# JSON parsing: <50ms
# Total: <450ms ✅
```

---

### Temporal Analytics

**Requirement:** <1s for pattern prediction

**Test:**
```bash
pytest tests/performance/test_temporal_performance.py -v

# Expected:
# Historical data fetch: <300ms
# Pattern analysis (scikit-learn): <500ms
# Anomaly detection: <200ms
# Total: <1000ms ✅
```

---

### Graph Analytics

**Requirement:** <1s for centrality calculation

**Test:**
```bash
pytest tests/performance/test_graph_analytics_performance.py -v

# Expected:
# PageRank calculation (NetworkX): <600ms
# Betweenness centrality: <400ms
# Total: <1000ms ✅
```

---

## Regression Testing

**Requirement:** All 223 existing tests must still pass

**Test:**
```bash
cd apex-memory-system
pytest tests/ --ignore=tests/load/ -v

# Expected: 223/223 tests passing (no regression)
```

---

## Complete Test Suite Validation

**Final Validation:** Run all 263 tests

```bash
# Run all tests
pytest tests/ --ignore=tests/load/ -v

# Expected Results:
# - Week 1: 12 tests passing (community detection)
# - Week 2: 15 tests passing (explanation + temporal)
# - Week 3: 5 tests passing (graph analytics)
# - Week 4: 10 tests passing (GraphRAG integration)
# - Re-enabled: 45 tests passing (phase3_disabled)
# - Existing: 223 tests passing (no regression)
# Total: 263 tests passing ✅
```

---

## Manual Validation Queries

### Test 1: Community Detection

**Query Neo4j to verify communities exist:**

```cypher
// Check community count
MATCH (c:Community {group_id: "default"})
RETURN count(c) as community_count

// Expected: community_count >= 3
```

---

### Test 2: Community Summaries

**Verify summaries auto-generated:**

```cypher
// Get community with summary
MATCH (c:Community {group_id: "default"})
WHERE c.summary IS NOT NULL
RETURN c.name, c.summary
LIMIT 5

// Expected: All communities have summaries
```

---

### Test 3: Query Explanation Quality

**Test explanation via API:**

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find all equipment",
    "limit": 10
  }'

# Verify response includes:
# - "explanation": { "why_these_results": "...", ... }
# - explanation.confidence > 0.8
# - explanation.alternative_queries.length == 3
```

---

### Test 4: Temporal Analytics

**Verify patterns detected:**

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me equipment maintenance patterns",
    "limit": 10
  }'

# Verify response includes:
# - "patterns": [ ... ]
# - "anomalies": [ ... ]
```

---

## Success Criteria

**All criteria must be met:**

1. ✅ **263 total tests passing** (223 existing + 40 new)
2. ✅ **Community detection functional** (10+ communities detected)
3. ✅ **Query explanations working** (90%+ user satisfaction)
4. ✅ **Temporal analytics accurate** (85%+ pattern prediction accuracy, 90%+ anomaly precision)
5. ✅ **Graph analytics functional** (centrality, shortest paths working)
6. ✅ **Performance requirements met** (community <2s, explanation <500ms, analytics <1s)
7. ✅ **Zero regression** (all existing tests passing)

**When all criteria met:** Deployment ready ✅

---

## Automated Test Execution

**Run all tests in sequence:**

```bash
#!/bin/bash
# run_all_tests.sh

echo "=== Week 1: Community Detection ==="
pytest tests/unit/test_community_detection.py -v
pytest tests/integration/test_community_router_integration.py -v

echo "=== Week 2: Explanation + Temporal ==="
pytest tests/unit/test_query_explanation.py -v
pytest tests/unit/test_temporal_analytics.py -v

echo "=== Week 3: Graph Analytics ==="
pytest tests/unit/test_graph_analytics.py -v

echo "=== Week 4: Integration + Re-enabled ==="
pytest tests/integration/test_graphrag_integration.py -v
pytest tests/unit/phase3_disabled/ -v

echo "=== Regression Test ==="
pytest tests/ --ignore=tests/load/ --ignore=upgrades/ -v

echo "=== Performance Benchmarks ==="
pytest tests/performance/ -v
```

**Expected Output:**
```
Total: 263 tests passed ✅
Performance: All benchmarks met ✅
Regression: Zero failures ✅
```

---

**End of Testing Guide**

**Next Step:** Review TROUBLESHOOTING.md for common issues and solutions.
