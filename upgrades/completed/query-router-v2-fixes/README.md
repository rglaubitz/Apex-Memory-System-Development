# Query Router Enhancement - search_memory Routing Improvement

**Priority:** MEDIUM
**Timeline:** 1-2 hours
**Status:** 📝 **PLANNED** (Not blocking PyPI deployment)
**Created:** 2025-10-24

---

## 📊 Quick Summary

**Problem:** `search_memory()` MCP tool routes to PostgreSQL (document metadata) instead of Neo4j/Graphiti (memory graph), returning old documents instead of recent memories.

**Impact:** Users expect "What do you know about X?" to search the knowledge graph, but it currently searches document storage.

**Solution:** Two-phase hybrid approach:
1. **Phase 1 (1 hour):** Add pattern-based query detection to identify memory queries
2. **Phase 2 (1 hour):** Create dedicated `/api/v1/memory/search` endpoint

**Workaround (Immediate):** Use `temporal_search()` for recent memory queries instead of `search_memory()`

---

## 📂 Documentation Structure

This upgrade folder contains:

- **[README.md](README.md)** (this file) - Quick overview and navigation
- **[PLANNING.md](PLANNING.md)** - Complete enhancement plan (374 lines)
  - Problem statement and root cause analysis
  - 3 implementation options with pros/cons
  - Recommended hybrid approach
  - Testing plan and success criteria
  - Implementation checklist
  - Rollback plan

- **IMPLEMENTATION.md** (to be created) - Step-by-step implementation guide
- **TESTING.md** (to be created) - Test specifications and validation

---

## 🎯 Problem Statement

### Current Behavior (Incorrect)
```python
search_memory("recent memories about G")
├─ Intent Classifier → "metadata" (confidence: 0.5)
├─ Router → PostgreSQL only
└─ Results → OLD invoice documents (not recent memories)
```

### Expected Behavior (Correct)
```python
search_memory("recent memories about G")
├─ Intent Classifier → "graph" or "hybrid" (high confidence)
├─ Router → Neo4j + Graphiti + Qdrant
└─ Results → RECENT graph entities and relationships
```

**Root Cause:** Query router's hybrid classifier defaults to "metadata" intent at 0.5 confidence for ambiguous queries. This is correct for DOCUMENT search but wrong for MEMORY search.

---

## 🛠️ Solution Overview

### Recommended Hybrid Approach (2 hours total)

**Phase 1: Pattern Detection (1 hour)**
- Add memory-specific regex patterns BEFORE hybrid classification
- Patterns identify common memory query structures:
  - "What do you know about X?"
  - "Recent memories about Y"
  - "Tell me about Z"
  - "Memories from this week"
- Returns high confidence (0.95) when pattern matches
- Falls back to hybrid classifier if no pattern match

**Phase 2: Dedicated Endpoint (1 hour)**
- Create `/api/v1/memory/search` endpoint
- Always routes to graph databases (Neo4j, Graphiti, Qdrant)
- Update MCP `search_memory()` tool to use new endpoint
- Keep `/query/` for document search (backward compatibility)

**Benefits:**
- ✅ Immediate fix via pattern detection
- ✅ Long-term clean architecture via dedicated endpoint
- ✅ Backward compatibility (existing `/query/` unchanged)
- ✅ Clear API semantics (documents vs memories)

---

## 📋 Implementation Checklist

### Phase 1: Pattern Detection (1 hour)

- [ ] Add `MEMORY_PATTERNS` dictionary to `router.py`
- [ ] Create `_check_memory_patterns()` method
- [ ] Update `classify_query()` to check patterns first
- [ ] Add unit tests for pattern matching
- [ ] Test with MCP tools (search_memory)
- [ ] Document pattern matching in router.py

### Phase 2: Dedicated Endpoint (1 hour)

- [ ] Create `/api/v1/memory/search` endpoint
- [ ] Add `intent_override` parameter to `QueryRouter.search()`
- [ ] Update MCP `search_memory()` to use new endpoint
- [ ] Add endpoint to API documentation
- [ ] Test with curl + Claude Desktop
- [ ] Update EXAMPLES.md with memory search examples

---

## 🧪 Testing Plan

### Test Queries (Should Route to Graph)

**Memory-specific queries:**
- "What do you know about ACME?" → graph ✅
- "Recent memories about G" → graph ✅
- "Tell me about OpenHaul" → graph ✅

**Temporal queries:**
- "Memories from this week" → temporal ✅
- "What changed in the last month?" → temporal ✅
- "How did the relationship evolve?" → temporal ✅

**Should still route to metadata:**
- "Find PDF documents" → metadata ✅
- "Show me invoice INV-001" → metadata ✅
- "Documents about shipping" → metadata ✅

### Performance Benchmarks

**Before enhancement:**
```
search_memory("What do you know about G?")
# Intent: metadata | Databases: [postgres] | Results: 0 (or wrong docs)
```

**After enhancement:**
```
search_memory("What do you know about G?")
# Intent: graph | Databases: [neo4j, graphiti, qdrant] | Results: 5-10 ✅
```

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

## 📚 Related Files

**Query Router (Core Logic):**
- `apex-memory-system/src/apex_memory/query_router/hybrid_classifier.py`
- `apex-memory-system/src/apex_memory/query_router/router.py`

**API Endpoints:**
- `apex-memory-system/src/apex_memory/api/query.py`

**MCP Tools:**
- `apex-mcp-server/src/apex_mcp_server/tools/basic_tools.py`

**Testing Results:**
- `apex-mcp-server/PHASE-2-FIX-SUMMARY.md`
- `apex-mcp-server/PHASE-2-TESTING-RESULTS.md`

---

## 🚀 Next Steps

**After PyPI deployment (Phase 3-5 complete):**

1. Create GitHub issue with enhancement plan
2. Schedule 2-hour implementation session
3. Implement Phase 1 (pattern detection)
4. Test with MCP tools
5. Implement Phase 2 (dedicated endpoint)
6. Update documentation

**Estimated Completion:** 1 day after starting (2 hours implementation + testing)

---

## 📝 Status

- **Current Status:** 📝 PLANNED
- **Blocking PyPI Deployment:** ❌ NO (workaround exists - use temporal_search)
- **Priority:** MEDIUM (can be done post-launch)
- **Complexity:** LOW (clear implementation path)
- **Timeline:** 1-2 hours total

---

**Last Updated:** 2025-10-24
**Created By:** Claude Code
**Related Deployment:** MCP Server Phase 2 Complete (8/10 tools passing)
