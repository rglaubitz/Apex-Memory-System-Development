# Query Router Enhancement - search_memory Routing Improvement

**Priority:** MEDIUM
**Timeline:** 1-2 hours
**Status:** 📝 **PLANNED** (Not blocking PyPI deployment)
**Created:** 2025-10-24

---

## 🎯 Problem Statement

**Current Behavior:**
```python
search_memory("recent memories about G")
├─ Intent Classifier → "metadata" (confidence: 0.5)
├─ Router → PostgreSQL only
└─ Results → OLD invoice documents (not recent memories)
```

**Expected Behavior:**
```python
search_memory("recent memories about G")
├─ Intent Classifier → "graph" or "hybrid" (high confidence)
├─ Router → Neo4j + Graphiti + Qdrant
└─ Results → RECENT graph entities and relationships
```

**Impact:**
- Users expect `search_memory()` to find recent memories
- Current default routing returns document metadata instead
- Workaround exists (`temporal_search()`) but not intuitive

---

## 🔍 Root Cause Analysis

### Intent Classification Defaults

**Hybrid Classifier Behavior:**
```python
# File: apex-memory-system/src/apex_memory/query_router/hybrid_classifier.py

# Tier 1: Keyword matching (returns None if no keywords match)
# Tier 2: Semantic embedding similarity (returns route with highest score)
# Tier 3: LLM classification (Claude 3.5 Sonnet fallback)

# Problem: Ambiguous queries default to "metadata" at 0.5 confidence
# This is correct for DOCUMENT search but wrong for MEMORY search
```

**Query Patterns That Fail:**
- "What do you know about X?" → metadata (should be graph)
- "Recent memories about Y" → metadata (should be temporal)
- "Tell me about Z" → metadata (should be graph)
- "Memories from this week" → metadata (should be temporal)

**Query Patterns That Work:**
- "Relationships between A and B" → graph ✅ (keyword: "relationships")
- "How did X change?" → temporal ✅ (keyword: "change")
- "Find documents about Y" → metadata ✅ (keyword: "documents")

---

## 🛠️ Enhancement Strategy

### Option 1: Pattern-Based Query Type Detection (RECOMMENDED)

**Approach:** Add memory-specific pattern matching BEFORE hybrid classification

**Implementation:**
```python
# File: apex-memory-system/src/apex_memory/query_router/router.py

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

async def classify_query(self, query: str) -> Tuple[str, float]:
    """Enhanced query classification with memory patterns."""

    # Step 1: Check memory-specific patterns FIRST
    for intent, patterns in MEMORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query.lower()):
                return intent, 0.95  # High confidence for pattern match

    # Step 2: Fall back to hybrid classifier
    return await self.hybrid_classifier.classify(query)
```

**Pros:**
- Fast (regex matching)
- Predictable (clear patterns)
- No ML training needed
- Easy to extend

**Cons:**
- Requires pattern maintenance
- May miss edge cases

**Timeline:** 1 hour

---

### Option 2: Adjust Confidence Thresholds

**Approach:** Lower threshold for "graph" intent, raise for "metadata"

**Implementation:**
```python
# File: apex-memory-system/src/apex_memory/query_router/hybrid_classifier.py

async def classify(self, query: str) -> Tuple[str, float]:
    """Classify with memory-biased thresholds."""

    intent, confidence = await self._classify_internal(query)

    # If ambiguous (< 0.7), prefer graph over metadata for MCP queries
    if confidence < 0.7:
        if intent == "metadata":
            # Recheck if query could be graph/temporal
            if self._has_entity_references(query):
                return "graph", 0.75
            if self._has_temporal_keywords(query):
                return "temporal", 0.75
        # For very low confidence, use hybrid routing
        if confidence < 0.5:
            return "hybrid", 0.6  # Search all databases

    return intent, confidence
```

**Pros:**
- Minimal code changes
- Leverages existing ML models
- Graceful degradation

**Cons:**
- Less predictable
- May affect document search accuracy
- Harder to debug

**Timeline:** 30 minutes

---

### Option 3: Add Dedicated Memory Search Endpoint

**Approach:** Create `/api/v1/memory/search` that always uses graph routing

**Implementation:**
```python
# File: apex-memory-system/src/apex_memory/api/query.py

@router.post("/memory/search", response_model=QueryResponse)
async def memory_search(
    query: str,
    limit: int = QueryParam(10, ge=1, le=100),
    time_window_days: int = QueryParam(30, ge=1, le=365)
):
    """
    Memory-specific search (always uses graph + temporal routing).

    Unlike /query/ which may route to document storage, this endpoint
    always searches the knowledge graph for entities and relationships.
    """
    # Force graph + temporal routing
    result = await query_router.search(
        query=query,
        limit=limit,
        intent_override="graph",  # Force graph routing
        databases_override=["neo4j", "graphiti", "qdrant"],  # Skip postgres
        time_filter_days=time_window_days
    )

    return result
```

**MCP Tool Update:**
```python
# File: apex-mcp-server/src/apex_mcp_server/tools/basic_tools.py

async def search_memory(query: str, ...) -> Dict[str, Any]:
    """Search memories using dedicated memory endpoint."""

    # Use new memory-specific endpoint
    result = await _call_apex_api(
        "POST",
        "/api/v1/memory/search",  # New endpoint
        json_data={"query": query, "limit": limit}
    )
```

**Pros:**
- Clean separation (documents vs memories)
- No risk to existing document search
- Easy to test and validate
- Clear API semantics

**Cons:**
- Requires new endpoint
- More code to maintain
- Doesn't fix underlying routing

**Timeline:** 2 hours

---

## 📊 Recommended Approach

### Hybrid Solution (Option 1 + Option 3)

**Phase 1 (Quick Fix - 1 hour):**
1. Add memory pattern detection (Option 1)
2. Update existing `/query/` endpoint
3. Test with MCP tools

**Phase 2 (Clean Architecture - 1 hour):**
1. Create `/memory/search` endpoint (Option 3)
2. Update MCP `search_memory()` tool
3. Keep `/query/` for document search

**Total Timeline:** 2 hours

**Benefits:**
- Immediate fix (pattern detection)
- Long-term clean architecture (dedicated endpoint)
- Backward compatibility (existing `/query/` unchanged)

---

## 🧪 Testing Plan

### Test Queries (Should Route to Graph)

```python
test_cases = [
    # Memory-specific queries
    ("What do you know about ACME?", "graph"),
    ("Recent memories about G", "graph"),
    ("Tell me about OpenHaul", "graph"),

    # Temporal queries
    ("Memories from this week", "temporal"),
    ("What changed in the last month?", "temporal"),
    ("How did the relationship evolve?", "temporal"),

    # Should still route to metadata
    ("Find PDF documents", "metadata"),
    ("Show me invoice INV-001", "metadata"),
    ("Documents about shipping", "metadata"),
]

for query, expected_intent in test_cases:
    intent, confidence = await router.classify_query(query)
    assert intent == expected_intent, f"Failed: {query} → {intent} (expected {expected_intent})"
```

### Performance Benchmarks

```bash
# Before enhancement:
search_memory("What do you know about G?")
# Intent: metadata | Databases: [postgres] | Results: 0 (or wrong docs)

# After enhancement:
search_memory("What do you know about G?")
# Intent: graph | Databases: [neo4j, graphiti, qdrant] | Results: 5-10 ✅
```

---

## 📝 Implementation Checklist

### Phase 1: Pattern Detection (1 hour)

- [ ] Add `MEMORY_PATTERNS` dictionary to router.py
- [ ] Create `_check_memory_patterns()` method
- [ ] Update `classify_query()` to check patterns first
- [ ] Add unit tests for pattern matching
- [ ] Test with MCP tools (search_memory)
- [ ] Document pattern matching in router.py

### Phase 2: Dedicated Endpoint (1 hour)

- [ ] Create `/api/v1/memory/search` endpoint
- [ ] Add `intent_override` parameter to QueryRouter.search()
- [ ] Update MCP `search_memory()` to use new endpoint
- [ ] Add endpoint to API documentation
- [ ] Test with curl + Claude Desktop
- [ ] Update EXAMPLES.md with memory search examples

---

## 🎯 Success Criteria

### Functional Requirements

✅ `search_memory("What do you know about X?")` returns graph entities
✅ `search_memory("Recent memories about Y")` returns temporal results
✅ Response time: <500ms (same as current)
✅ Backward compatibility: Document search still works

### Non-Functional Requirements

✅ Pattern matching: <10ms overhead
✅ No impact on existing `/query/` endpoint
✅ Clear documentation for memory vs document search
✅ MCP tools updated and tested

---

## 🔄 Rollback Plan

If enhancement causes issues:

1. **Revert pattern detection:**
   ```bash
   git revert <commit-hash>
   docker-compose restart api
   ```

2. **Disable new endpoint:**
   ```python
   # Comment out @router.post("/memory/search") in query.py
   ```

3. **Restore MCP tool:**
   ```python
   # Change endpoint back to "/api/v1/query/" in basic_tools.py
   ```

---

## 📚 Related Documentation

- **Current Implementation:** `apex-memory-system/src/apex_memory/query_router/hybrid_classifier.py`
- **API Endpoints:** `apex-memory-system/src/apex_memory/api/query.py`
- **MCP Tools:** `apex-mcp-server/src/apex_mcp_server/tools/basic_tools.py`
- **Testing Results:** `PHASE-2-FIX-SUMMARY.md`

---

## 🚀 Next Steps

**After Phase 2 MCP Testing Complete:**

1. Create GitHub issue with this plan
2. Schedule 2-hour implementation session
3. Implement Phase 1 (pattern detection)
4. Test with MCP tools
5. Implement Phase 2 (dedicated endpoint)
6. Update documentation

**Estimated Completion:** 1 day after starting

---

**Status:** 📝 PLANNED - Not blocking PyPI deployment
**Priority:** MEDIUM - Can be done post-launch
**Complexity:** LOW - Clear implementation path
