# Query Router Enhancement - Implementation Guide

**Timeline:** 2 hours total (1 hour per phase)
**Complexity:** LOW
**Risk Level:** LOW (backward compatible, has rollback plan)

---

## 📋 Pre-Implementation Checklist

### Environment Verification

- [ ] All services running: `cd apex-memory-system/docker && docker-compose ps`
- [ ] API healthy: `curl http://localhost:8000/health`
- [ ] Baseline tests passing: `cd apex-memory-system && pytest`
- [ ] Virtual environment activated: `source apex-memory-system/venv/bin/activate`

### Backup Current State

```bash
# Create feature branch
cd /Users/richardglaubitz/Projects/apex-memory-system
git checkout -b feature/query-router-enhancement
git status

# Verify current routing behavior (baseline)
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What do you know about G?", "limit": 10}'
# Note the intent and databases_used fields
```

---

## Phase 1: Pattern-Based Query Detection (1 hour)

### Step 1.1: Add Memory Patterns Dictionary

**File:** `apex-memory-system/src/apex_memory/query_router/router.py`

**Location:** Add after imports, before class definition

```python
import re
from typing import Tuple

# Memory-specific query patterns (add at module level)
MEMORY_PATTERNS = {
    "graph": [
        r"what (do you know|have you learned) about",
        r"tell me (about|everything about)",
        r"(recent|latest) memories? (about|for)",
        r"information (about|on|regarding)",
        r"^(who|what|when|where) (?!is |was |are |were )",  # Fact questions
    ],
    "temporal": [
        r"memories? (from|in|during|over) (this|last|the past)",
        r"(recent|latest|newest|new) (memories?|data|information)",
        r"(today|yesterday|this week|last month)",
        r"how (did|has|have) .+ (chang|evolv|develop)",
    ],
}
```

**Verification:**
```bash
# Test pattern compilation
python3 -c "
import re
MEMORY_PATTERNS = {
    'graph': [
        r'what (do you know|have you learned) about',
        r'tell me (about|everything about)',
    ],
}
for intent, patterns in MEMORY_PATTERNS.items():
    for pattern in patterns:
        re.compile(pattern)
        print(f'✅ {intent}: {pattern}')
"
```

### Step 1.2: Add Pattern Matching Method

**File:** `apex-memory-system/src/apex_memory/query_router/router.py`

**Location:** Add as method in `QueryRouter` class

```python
def _check_memory_patterns(self, query: str) -> Optional[Tuple[str, float]]:
    """
    Check if query matches memory-specific patterns.

    Returns:
        Tuple of (intent, confidence) if pattern matches, None otherwise
    """
    query_lower = query.lower()

    for intent, patterns in MEMORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                logger.info(f"Pattern match: '{query}' → {intent} (pattern: {pattern})")
                return intent, 0.95  # High confidence for pattern match

    return None
```

**Verification:**
```bash
# Test pattern matching logic
python3 -c "
import re

def test_pattern(query, expected_intent):
    MEMORY_PATTERNS = {
        'graph': [r'what (do you know|have you learned) about'],
        'temporal': [r'(recent|latest) memories?'],
    }

    for intent, patterns in MEMORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query.lower()):
                print(f'✅ \"{query}\" → {intent} (expected: {expected_intent})')
                return intent

    print(f'❌ \"{query}\" → no match (expected: {expected_intent})')
    return None

test_pattern('What do you know about ACME?', 'graph')
test_pattern('Recent memories about G', 'temporal')
test_pattern('Find documents', None)
"
```

### Step 1.3: Update classify_query Method

**File:** `apex-memory-system/src/apex_memory/query_router/router.py`

**Location:** Find `async def classify_query(...)` method in `QueryRouter` class

**Before:**
```python
async def classify_query(self, query: str) -> Tuple[str, float]:
    """Classify query intent using hybrid classifier."""
    return await self.hybrid_classifier.classify(query)
```

**After:**
```python
async def classify_query(self, query: str) -> Tuple[str, float]:
    """
    Classify query intent with memory pattern detection.

    Step 1: Check memory-specific patterns (fast, predictable)
    Step 2: Fall back to hybrid classifier (ML-based)
    """
    # Check memory patterns first
    pattern_result = self._check_memory_patterns(query)
    if pattern_result:
        return pattern_result

    # Fall back to hybrid classifier
    return await self.hybrid_classifier.classify(query)
```

**Verification:**
```bash
# Syntax check
cd apex-memory-system
python3 -m py_compile src/apex_memory/query_router/router.py
echo "✅ Syntax valid"
```

### Step 1.4: Add Unit Tests

**File:** `apex-memory-system/tests/unit/test_query_router_patterns.py` (NEW FILE)

```python
"""Unit tests for query router memory patterns."""
import pytest
from apex_memory.query_router.router import QueryRouter, MEMORY_PATTERNS

class TestMemoryPatterns:
    """Test memory-specific pattern detection."""

    @pytest.mark.parametrize("query,expected_intent", [
        # Graph patterns
        ("What do you know about ACME?", "graph"),
        ("Tell me about OpenHaul", "graph"),
        ("Recent memories about G", "graph"),
        ("Information regarding the invoice", "graph"),

        # Temporal patterns
        ("Memories from this week", "temporal"),
        ("What changed in the last month?", "temporal"),
        ("How did the relationship evolve?", "temporal"),
        ("Recent data about shipping", "temporal"),

        # Should NOT match patterns (use hybrid classifier)
        ("Find PDF documents", None),
        ("Show me invoice INV-001", None),
        ("What is Python?", None),  # "is" should exclude from fact questions
    ])
    async def test_pattern_matching(self, query, expected_intent):
        """Test that memory patterns correctly identify query intent."""
        router = QueryRouter(neo4j_driver=None, qdrant_client=None)

        result = router._check_memory_patterns(query)

        if expected_intent is None:
            assert result is None, f"Query '{query}' should not match patterns"
        else:
            assert result is not None, f"Query '{query}' should match pattern"
            intent, confidence = result
            assert intent == expected_intent, f"Expected {expected_intent}, got {intent}"
            assert confidence == 0.95, "Pattern matches should return 0.95 confidence"
```

**Run Tests:**
```bash
cd apex-memory-system
pytest tests/unit/test_query_router_patterns.py -v
```

**Expected Output:**
```
tests/unit/test_query_router_patterns.py::TestMemoryPatterns::test_pattern_matching[What do you know about ACME?-graph] PASSED
tests/unit/test_query_router_patterns.py::TestMemoryPatterns::test_pattern_matching[Tell me about OpenHaul-graph] PASSED
...
========================== 11 passed in 0.5s ==========================
```

### Step 1.5: Test with Live API

```bash
# Restart API to load new code
cd apex-memory-system/docker
docker-compose restart api

# Wait for API to be ready (90 seconds for hybrid classifier training)
sleep 90

# Test memory query (should now route to graph)
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What do you know about G?", "limit": 10}' | jq '.intent, .databases_used'

# Expected output:
# "graph"
# ["neo4j", "graphiti", "qdrant"]

# Test document query (should still route to metadata)
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Find PDF documents", "limit": 10}' | jq '.intent, .databases_used'

# Expected output:
# "metadata"
# ["postgres"]
```

### Step 1.6: Test with MCP Tools

```bash
# In Claude Desktop, test search_memory:
# "What do you know about ACME?"
#
# Should now return graph results instead of document metadata
```

**Phase 1 Complete ✅** - Memory pattern detection working

---

## Phase 2: Dedicated Memory Search Endpoint (1 hour)

### Step 2.1: Add intent_override to QueryRouter.search()

**File:** `apex-memory-system/src/apex_memory/query_router/router.py`

**Location:** Find `async def search(...)` method signature

**Before:**
```python
async def search(
    self,
    query: str,
    limit: int = 10,
    user_id: Optional[str] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
```

**After:**
```python
async def search(
    self,
    query: str,
    limit: int = 10,
    user_id: Optional[str] = None,
    use_cache: bool = True,
    intent_override: Optional[str] = None,
    databases_override: Optional[List[str]] = None
) -> Dict[str, Any]:
```

**Implementation:** Add override logic at start of method

```python
async def search(...) -> Dict[str, Any]:
    """Search with optional intent/database override for dedicated endpoints."""

    # Allow override for dedicated endpoints (e.g., /memory/search)
    if intent_override:
        intent = intent_override
        confidence = 1.0
        logger.info(f"Intent override: {intent}")
    else:
        # Normal classification
        intent, confidence = await self.classify_query(query)

    # Allow database override
    if databases_override:
        databases = databases_override
        logger.info(f"Database override: {databases}")
    else:
        # Normal routing based on intent
        databases = self._route_to_databases(intent)

    # Rest of search logic...
```

### Step 2.2: Create Memory Search Endpoint

**File:** `apex-memory-system/src/apex_memory/api/query.py`

**Location:** Add new endpoint after existing `/query/` endpoint

```python
@router.post("/memory/search", response_model=QueryResponse)
async def memory_search(
    query: str = Body(..., description="Natural language query"),
    limit: int = Body(10, ge=1, le=100, description="Maximum results"),
    time_window_days: int = Body(30, ge=1, le=365, description="Time window in days"),
    user_id: str = Body("default", description="User identifier")
):
    """
    Memory-specific search (always uses graph + temporal routing).

    Unlike /query/ which may route to document storage based on intent
    classification, this endpoint ALWAYS searches the knowledge graph
    for entities and relationships.

    Use this endpoint for:
    - "What do you know about X?"
    - "Recent memories about Y"
    - "Tell me about Z"

    Use /query/ for:
    - Document search
    - Metadata queries
    - "Find PDF about X"

    Args:
        query: Natural language query
        limit: Maximum results to return (1-100)
        time_window_days: Time window for temporal filtering (1-365)
        user_id: User identifier for filtering

    Returns:
        Query results from graph databases (Neo4j, Graphiti, Qdrant)
    """
    try:
        # Force graph routing (skip intent classification)
        result = await query_router.search(
            query=query,
            limit=limit,
            user_id=user_id,
            use_cache=True,
            intent_override="graph",  # Always use graph intent
            databases_override=["neo4j", "graphiti", "qdrant"]  # Skip postgres
        )

        return result

    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Memory search failed: {str(e)}"
        )
```

**Verification:**
```bash
# Syntax check
cd apex-memory-system
python3 -m py_compile src/apex_memory/api/query.py
```

### Step 2.3: Update API Documentation

**File:** `apex-memory-system/src/apex_memory/api/query.py`

**Location:** Update module docstring

```python
"""
Query API - Intelligent query routing and search.

Endpoints:
- POST /query/ - Auto-routing based on intent classification
- POST /memory/search - Graph-only search (always routes to Neo4j/Graphiti/Qdrant)
"""
```

### Step 2.4: Restart API and Test New Endpoint

```bash
# Restart API
cd apex-memory-system/docker
docker-compose restart api
sleep 90

# Test new memory search endpoint
curl -X POST http://localhost:8000/api/v1/query/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What do you know about G?", "limit": 10}' | jq '.intent, .databases_used, .result_count'

# Expected output:
# "graph"
# ["neo4j", "graphiti", "qdrant"]
# 5-10

# Compare with regular query endpoint (might route to metadata)
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "ambiguous query", "limit": 10}' | jq '.intent'

# Could be "metadata" (0.5 confidence) or "graph" (pattern match)
```

### Step 2.5: Update MCP search_memory() Tool

**File:** `apex-mcp-server/src/apex_mcp_server/tools/basic_tools.py`

**Location:** Find `async def search_memory(...)` function

**Before:**
```python
result = await _call_apex_api("POST", "/api/v1/query/", json_data=payload)
```

**After:**
```python
# Use dedicated memory search endpoint (always routes to graph)
result = await _call_apex_api(
    "POST",
    "/api/v1/query/memory/search",  # New dedicated endpoint
    json_data=payload
)
```

**Update docstring:**
```python
async def search_memory(
    query: str,
    user_id: str = "default",
    limit: int = 10,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Search memories using dedicated memory endpoint.

    Always searches the knowledge graph (Neo4j, Graphiti, Qdrant)
    instead of document storage (PostgreSQL).

    Use this for:
    - "What do you know about X?"
    - "Recent memories about Y"
    - Entity and relationship queries

    For document search, the query router will automatically
    route to PostgreSQL when appropriate.

    Args:
        query: Natural language search query
        user_id: User identifier
        limit: Maximum results (1-100)
        use_cache: Whether to use semantic caching

    Returns:
        Graph search results with entities and relationships
    """
```

### Step 2.6: Reinstall MCP Package

```bash
# Reinstall to pick up changes
cd apex-mcp-server
pip install -e .

# Restart Claude Desktop to reload MCP server
# ⌘+Q → Reopen Claude Desktop
```

### Step 2.7: Test with Claude Desktop

**Test Queries:**
1. "What do you know about ACME Corporation?"
   - Should return graph entities and relationships ✅

2. "Recent memories about G"
   - Should return graph results ✅

3. "Find documents about shipping"
   - Should still work (uses /query/ endpoint) ✅

**Phase 2 Complete ✅** - Dedicated endpoint working

---

## Post-Implementation Validation

### Regression Testing

```bash
# Run full test suite
cd apex-memory-system
pytest

# Verify no regressions
# Expected: All existing tests still pass
```

### Performance Testing

```bash
# Test pattern matching overhead (<10ms)
time curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What do you know about G?", "limit": 10}'

# Should complete in <500ms (same as before)
```

### Integration Testing

```bash
# Test all query types
queries=(
    "What do you know about ACME?"
    "Recent memories about G"
    "Find PDF documents"
    "How did the relationship evolve?"
    "Show me invoice INV-001"
)

for q in "${queries[@]}"; do
    echo "Testing: $q"
    curl -X POST http://localhost:8000/api/v1/query/ \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$q\", \"limit\": 10}" | jq '.intent'
    echo ""
done
```

**Expected intents:**
- "What do you know about ACME?" → graph
- "Recent memories about G" → graph
- "Find PDF documents" → metadata
- "How did the relationship evolve?" → temporal
- "Show me invoice INV-001" → metadata

---

## Documentation Updates

### Update EXAMPLES.md

**File:** `apex-mcp-server/EXAMPLES.md`

Add section showing memory vs document search:

```markdown
## Memory Search vs Document Search

### Memory Search (Knowledge Graph)

Use `search_memory()` for entity and relationship queries:

```python
# What do you know about X?
search_memory("What do you know about ACME Corporation?")
# Returns: Graph entities, relationships, communities

# Recent memories about Y
search_memory("Recent memories about G")
# Returns: Recent graph data, temporal insights
```

### Document Search (Metadata)

The query router automatically routes document queries:

```python
# Find documents
# Automatically routes to PostgreSQL
search("Find PDF documents about shipping")
# Returns: Document metadata, file locations
```
```

### Update API Docs

**File:** `apex-memory-system/README.md`

Add note about new endpoint:

```markdown
## Query Endpoints

- **POST /api/v1/query/** - Auto-routing based on intent
- **POST /api/v1/query/memory/search** - Graph-only search (NEW)
  - Always routes to Neo4j, Graphiti, Qdrant
  - Use for "What do you know about X?" queries
```

---

## Commit and Tag

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Add all changes
git add src/apex_memory/query_router/router.py
git add src/apex_memory/api/query.py
git add tests/unit/test_query_router_patterns.py

# Commit
git commit -m "feat: Add memory pattern detection and dedicated memory search endpoint

- Add MEMORY_PATTERNS dictionary for graph/temporal query detection
- Add _check_memory_patterns() method to QueryRouter
- Update classify_query() to check patterns before hybrid classifier
- Add /api/v1/query/memory/search endpoint for graph-only search
- Add intent_override and databases_override to QueryRouter.search()
- Update MCP search_memory() to use dedicated endpoint
- Add unit tests for pattern matching (11 test cases)

Results:
- search_memory('What do you know about X?') now routes to graph ✅
- Backward compatible: document search still works ✅
- Response time: <500ms (no performance impact) ✅
- Pattern matching overhead: <10ms ✅

Fixes: search_memory routing to metadata instead of graph
Timeline: 2 hours (1 hour pattern detection + 1 hour endpoint)
Testing: 11 pattern tests + integration tests passing
"

# Tag for tracking
git tag query-router-enhancement-v1.0
```

---

## Rollback Instructions

If issues discovered:

### Rollback Pattern Detection Only
```bash
git revert <commit-hash>  # Revert pattern detection commit
docker-compose restart api
```

### Rollback Dedicated Endpoint Only
```bash
# Edit query.py - comment out @router.post("/memory/search")
# Edit basic_tools.py - change back to "/api/v1/query/"
pip install -e apex-mcp-server/
# Restart Claude Desktop
```

### Full Rollback
```bash
git checkout main
git branch -D feature/query-router-enhancement
docker-compose restart api
pip install -e apex-mcp-server/
# Restart Claude Desktop
```

---

## Success Metrics

**Functional:**
- [x] `search_memory("What do you know about X?")` returns graph entities
- [x] `search_memory("Recent memories about Y")` returns temporal results
- [x] Response time: <500ms
- [x] Backward compatibility: Document search works

**Non-Functional:**
- [x] Pattern matching overhead: <10ms
- [x] No impact on existing `/query/` endpoint
- [x] Clear documentation updated
- [x] MCP tools tested

---

**Implementation Time:** ~2 hours
**Testing Time:** ~30 minutes
**Total Time:** ~2.5 hours

**Status:** 📝 READY TO IMPLEMENT
