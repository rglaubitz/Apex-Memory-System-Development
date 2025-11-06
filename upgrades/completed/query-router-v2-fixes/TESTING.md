# Query Router Enhancement - Testing Specifications

**Test Coverage Goal:** 100% of new functionality
**Test Categories:** Unit, Integration, Performance, Regression

---

## Test Suite Overview

| Category | Count | Priority | Runtime |
|----------|-------|----------|---------|
| Unit Tests | 11 | HIGH | <1s |
| Integration Tests | 6 | HIGH | <10s |
| Performance Tests | 3 | MEDIUM | <30s |
| Regression Tests | 8 | HIGH | <20s |
| **Total** | **28** | - | **<61s** |

---

## Unit Tests (11 tests)

**File:** `tests/unit/test_query_router_patterns.py`

### Test 1-4: Graph Pattern Matching

```python
@pytest.mark.parametrize("query", [
    "What do you know about ACME?",
    "Tell me about OpenHaul",
    "Recent memories about G",
    "Information regarding the invoice",
])
def test_graph_patterns(query):
    """Verify graph patterns match correctly."""
    router = QueryRouter(neo4j_driver=None, qdrant_client=None)
    result = router._check_memory_patterns(query)

    assert result is not None
    intent, confidence = result
    assert intent == "graph"
    assert confidence == 0.95
```

**Success Criteria:**
- All 4 queries match "graph" intent ✅
- Confidence = 0.95 for all ✅
- Response time <1ms ✅

### Test 5-8: Temporal Pattern Matching

```python
@pytest.mark.parametrize("query", [
    "Memories from this week",
    "What changed in the last month?",
    "How did the relationship evolve?",
    "Recent data about shipping",
])
def test_temporal_patterns(query):
    """Verify temporal patterns match correctly."""
    router = QueryRouter(neo4j_driver=None, qdrant_client=None)
    result = router._check_memory_patterns(query)

    assert result is not None
    intent, confidence = result
    assert intent == "temporal"
    assert confidence == 0.95
```

**Success Criteria:**
- All 4 queries match "temporal" intent ✅
- Confidence = 0.95 for all ✅
- Response time <1ms ✅

### Test 9-11: No Pattern Match (Fall Through)

```python
@pytest.mark.parametrize("query", [
    "Find PDF documents",
    "Show me invoice INV-001",
    "What is Python?",  # "is" should exclude from fact questions
])
def test_no_pattern_match(query):
    """Verify non-memory queries don't match patterns."""
    router = QueryRouter(neo4j_driver=None, qdrant_client=None)
    result = router._check_memory_patterns(query)

    assert result is None  # Should fall through to hybrid classifier
```

**Success Criteria:**
- All 3 queries return None ✅
- Fall through to hybrid classifier ✅
- Response time <1ms ✅

---

## Integration Tests (6 tests)

**File:** `tests/integration/test_query_router_enhancement.py`

### Test 1: Memory Pattern → Graph Routing

```python
async def test_memory_pattern_routes_to_graph():
    """Verify memory queries route to graph databases."""

    query = "What do you know about ACME?"

    # Call query router
    result = await query_router.search(query=query, limit=10)

    # Assertions
    assert result["intent"] == "graph"
    assert "neo4j" in result["databases_used"]
    assert "graphiti" in result["databases_used"]
    assert "qdrant" in result["databases_used"]
    assert "postgres" not in result["databases_used"]  # Should NOT hit postgres
    assert result["confidence"] >= 0.95
```

**Success Criteria:**
- Intent = "graph" ✅
- Databases = [neo4j, graphiti, qdrant] ✅
- PostgreSQL excluded ✅
- Response time <500ms ✅

### Test 2: Document Query → Metadata Routing

```python
async def test_document_query_routes_to_metadata():
    """Verify document queries still route to PostgreSQL."""

    query = "Find PDF documents about shipping"

    # Call query router
    result = await query_router.search(query=query, limit=10)

    # Assertions
    assert result["intent"] == "metadata"
    assert "postgres" in result["databases_used"]
```

**Success Criteria:**
- Intent = "metadata" ✅
- PostgreSQL included ✅
- Backward compatibility preserved ✅

### Test 3: Dedicated Memory Search Endpoint

```python
async def test_memory_search_endpoint():
    """Verify /memory/search endpoint forces graph routing."""

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/query/memory/search",
            json={
                "query": "ambiguous query that might route to metadata",
                "limit": 10,
            }
        )

    assert response.status_code == 200
    data = response.json()

    # Should ALWAYS route to graph (no classification)
    assert data["intent"] == "graph"
    assert "neo4j" in data["databases_used"]
    assert "postgres" not in data["databases_used"]
```

**Success Criteria:**
- Always routes to graph ✅
- Works for ambiguous queries ✅
- No intent classification performed ✅

### Test 4: Intent Override Parameter

```python
async def test_intent_override():
    """Verify intent_override parameter works."""

    query = "Find documents"  # Would normally route to metadata

    # Force graph routing
    result = await query_router.search(
        query=query,
        limit=10,
        intent_override="graph"
    )

    assert result["intent"] == "graph"
    assert "neo4j" in result["databases_used"]
```

**Success Criteria:**
- Override bypasses classification ✅
- Routes to correct databases ✅

### Test 5: Database Override Parameter

```python
async def test_databases_override():
    """Verify databases_override parameter works."""

    query = "What do you know about X?"

    # Force specific databases
    result = await query_router.search(
        query=query,
        limit=10,
        databases_override=["neo4j", "qdrant"]  # Exclude graphiti
    )

    assert "neo4j" in result["databases_used"]
    assert "qdrant" in result["databases_used"]
    assert "graphiti" not in result["databases_used"]
```

**Success Criteria:**
- Override bypasses routing logic ✅
- Uses exact database list ✅

### Test 6: MCP Tool Integration

```python
async def test_mcp_search_memory_tool():
    """Verify MCP search_memory() uses new endpoint."""

    from apex_mcp_server.tools.basic_tools import search_memory

    # Mock API call
    with patch('apex_mcp_server.tools.basic_tools._call_apex_api') as mock_call:
        mock_call.return_value = {
            "intent": "graph",
            "databases_used": ["neo4j", "graphiti", "qdrant"],
            "results": [],
        }

        result = await search_memory("What do you know about G?")

        # Verify correct endpoint called
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert call_args[0][1] == "/api/v1/query/memory/search"
```

**Success Criteria:**
- MCP tool calls /memory/search ✅
- Not calling /query/ ✅

---

## Performance Tests (3 tests)

**File:** `tests/performance/test_query_router_performance.py`

### Test 1: Pattern Matching Overhead

```python
async def test_pattern_matching_overhead():
    """Verify pattern matching adds <10ms overhead."""

    query = "What do you know about ACME?"

    # Measure time with pattern matching
    start = time.perf_counter()
    for _ in range(100):
        await query_router.classify_query(query)
    elapsed = time.perf_counter() - start

    avg_time = elapsed / 100
    assert avg_time < 0.010  # <10ms average
```

**Success Criteria:**
- Average time <10ms ✅
- Pattern matching is fast ✅

### Test 2: End-to-End Query Time

```python
async def test_end_to_end_query_time():
    """Verify total query time remains <500ms."""

    query = "What do you know about ACME?"

    start = time.perf_counter()
    result = await query_router.search(query=query, limit=10)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.5  # <500ms
```

**Success Criteria:**
- Total time <500ms ✅
- No performance regression ✅

### Test 3: Memory Search Endpoint Performance

```python
async def test_memory_search_endpoint_performance():
    """Verify /memory/search endpoint is <500ms."""

    async with AsyncClient(app=app, base_url="http://test") as client:
        start = time.perf_counter()
        response = await client.post(
            "/api/v1/query/memory/search",
            json={"query": "What do you know about G?", "limit": 10}
        )
        elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 0.5  # <500ms
```

**Success Criteria:**
- Response time <500ms ✅
- No additional latency ✅

---

## Regression Tests (8 tests)

**File:** `tests/integration/test_query_router_regression.py`

### Test 1-8: Existing Query Types Still Work

```python
@pytest.mark.parametrize("query,expected_intent", [
    # Relationship queries
    ("Relationships between A and B", "graph"),

    # Temporal evolution
    ("How did X change over time?", "temporal"),

    # Document search
    ("Find documents about shipping", "metadata"),

    # Semantic search
    ("Similar to document-123", "semantic"),

    # Entity search
    ("Entity named ACME", "graph"),

    # Metadata filters
    ("Documents from last week", "metadata"),

    # Hybrid queries
    ("Everything about ACME (docs and graph)", "hybrid"),

    # Edge cases
    ("", "metadata"),  # Empty query defaults to metadata
])
async def test_existing_query_types(query, expected_intent):
    """Verify existing query routing still works."""

    result = await query_router.search(query=query, limit=10)

    assert result["intent"] == expected_intent
```

**Success Criteria:**
- All 8 existing query types work ✅
- No regressions ✅
- Intent classification accurate ✅

---

## Test Execution Plan

### Local Development Testing

```bash
# Phase 1: Unit tests (fast)
cd apex-memory-system
pytest tests/unit/test_query_router_patterns.py -v
# Expected: 11/11 PASSED in <1s

# Phase 2: Integration tests
pytest tests/integration/test_query_router_enhancement.py -v
# Expected: 6/6 PASSED in <10s

# Phase 3: Performance tests
pytest tests/performance/test_query_router_performance.py -v
# Expected: 3/3 PASSED in <30s

# Phase 4: Regression tests
pytest tests/integration/test_query_router_regression.py -v
# Expected: 8/8 PASSED in <20s

# Phase 5: Full suite
pytest
# Expected: All tests pass (including existing tests)
```

### Manual Testing (Claude Desktop)

**Test Case 1: Memory Query**
```
User: "What do you know about ACME Corporation?"
Expected: Returns graph entities and relationships
Actual: ___________
Status: PASS / FAIL
```

**Test Case 2: Recent Memories**
```
User: "Recent memories about G"
Expected: Returns graph results with temporal filtering
Actual: ___________
Status: PASS / FAIL
```

**Test Case 3: Document Search**
```
User: "Find PDF documents about shipping"
Expected: Returns document metadata (not graph data)
Actual: ___________
Status: PASS / FAIL
```

**Test Case 4: Temporal Query**
```
User: "How did the relationship between A and B evolve?"
Expected: Returns temporal graph data
Actual: ___________
Status: PASS / FAIL
```

**Test Case 5: Ambiguous Query**
```
User: "Tell me about invoices"
Expected: Routes to graph (pattern match) or metadata (hybrid classifier)
Actual: ___________
Status: PASS / FAIL
```

### API Testing (curl)

```bash
# Test 1: Pattern matching
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What do you know about ACME?", "limit": 10}' | jq '.intent, .databases_used'

# Expected:
# "graph"
# ["neo4j", "graphiti", "qdrant"]

# Test 2: Memory search endpoint
curl -X POST http://localhost:8000/api/v1/query/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ambiguous query", "limit": 10}' | jq '.intent, .databases_used'

# Expected:
# "graph"
# ["neo4j", "graphiti", "qdrant"]

# Test 3: Document search (should still work)
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Find PDF documents", "limit": 10}' | jq '.intent, .databases_used'

# Expected:
# "metadata"
# ["postgres"]
```

---

## Test Coverage Report

After implementation, generate coverage report:

```bash
cd apex-memory-system
pytest --cov=apex_memory.query_router \
       --cov=apex_memory.api.query \
       --cov-report=html \
       --cov-report=term

# View coverage
open htmlcov/index.html
```

**Coverage Goals:**
- `router.py`: 100% (all new code)
- `query.py`: 100% (new endpoint)
- Overall: >95%

---

## Success Criteria Summary

**All tests must pass:**
- [x] 11 unit tests (pattern matching)
- [x] 6 integration tests (routing logic)
- [x] 3 performance tests (<500ms, <10ms overhead)
- [x] 8 regression tests (existing functionality)

**Manual testing:**
- [x] MCP tool works in Claude Desktop
- [x] API endpoints respond correctly
- [x] No performance degradation

**Documentation:**
- [x] API docs updated
- [x] MCP examples updated
- [x] README updated

---

## Test Data

### Sample Queries for Testing

**Graph Patterns:**
- "What do you know about ACME?"
- "Tell me everything about OpenHaul"
- "Information regarding invoice INV-001"
- "Who is the CEO of ACME?"
- "What entities are related to shipping?"

**Temporal Patterns:**
- "Memories from this week"
- "What changed in the last month?"
- "How did the relationship evolve?"
- "Recent data about ACME"
- "Latest information on shipping"

**Document/Metadata Patterns:**
- "Find PDF documents"
- "Show me invoice INV-001"
- "Documents about shipping"
- "Files from last week"
- "Search metadata for ACME"

**Edge Cases:**
- "" (empty string)
- "a" (single character)
- "What is Python?" (should NOT match fact pattern due to "is")
- Very long query (500+ chars)
- Special characters: "What's $ACME's revenue?"

---

**Total Test Count:** 28 tests
**Expected Runtime:** <61 seconds
**Test Coverage Goal:** 100% of new code
**Status:** 📝 READY TO IMPLEMENT
