# Known Issues - Pre-Deployment

**Purpose:** Track verified bugs and issues discovered during deployment verification that require resolution before production deployment.

**Status Definitions:**
- 🔴 **CRITICAL** - Blocks deployment, must be fixed
- 🟡 **HIGH** - Should be fixed before deployment, has workarounds
- 🟢 **LOW** - Can be deferred to post-deployment, minimal user impact

---

## Table of Contents

1. [Critical Issues](#critical-issues)
2. [High Priority Issues](#high-priority-issues)
3. [Low Priority Issues](#low-priority-issues)
4. [Resolved Issues](#resolved-issues)

---

## Critical Issues

### 🔴 ISSUE-001: AI Conversation Hub - Citation Retrieval Returns Zero Results

**Status:** CRITICAL - Blocks AI Conversation Hub production use
**Discovered:** 2025-10-22
**Component:** Query Router + Conversation Service Integration
**Severity:** Complete feature failure - conversations work but no context/citations from knowledge graph

#### Description

The AI Conversation Hub successfully generates responses using Claude 3.5 Sonnet, but **zero documents are retrieved from the knowledge graph** despite 944 documents existing in the database with valid embeddings. This means all responses are purely from Claude's general knowledge without any memory-grounded context.

#### User Impact

- ❌ Citations section always shows `[]` (empty)
- ❌ Claude responses include disclaimer: "I don't have specific context from your knowledge graph"
- ❌ No document sources provided to users
- ❌ Defeats primary value proposition: memory-grounded conversations

#### Evidence Gathered

**Database Health: ✅ Working**
```bash
# PostgreSQL
$ docker exec apex-postgres psql -U apex -d apex_memory -c "SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL;"
 count
-------
   944

# Documents with agricultural content exist
$ SELECT title FROM documents WHERE title ILIKE '%agricultural%';
- "Agricultural Exemption Guidelines"
- "Agricultural_Exempt_CFR_395.1"
- "Ag_Exempt_DOT_Permit_Binder"
```

**Embedding Service: ✅ Working**
```python
# Embeddings generate correctly
service = EmbeddingService()
embedding = service.generate_embedding('agricultural exemptions')
# Returns: 1536-dimensional vector with valid values
```

**Query Router Execution: ⚠️ Returns Empty Results**
```python
# Query router executes but returns 0 results
router = QueryRouter(redis_host='redis')
results = await router.query('agricultural exemptions')
# Results count: 0 (expected: 3-5 relevant documents)
```

**Logs Show Suspicious Behavior:**
```
2025-10-22 10:15:21 - INFO - query() - Complexity: medium (databases: ['neo4j', 'graphiti', 'postgres'])
2025-10-22 10:15:21 - INFO - Neo4j query: 0ms
2025-10-22 10:15:21 - INFO - Graphiti query: 0ms
2025-10-22 10:15:21 - INFO - TOTAL _route_query time: 1ms
2025-10-22 10:15:21 - INFO - Result aggregation: 0ms (results: 0)
```

**Suspicious Indicators:**
- ❌ All database queries complete in 0ms (suspiciously fast)
- ❌ No exceptions or error logs
- ❌ Query router reports success but returns empty results
- ❌ All 3 databases (Neo4j, Graphiti, PostgreSQL) return 0 results

#### Fixes Already Applied

**Fix 1: Method Name Correction** ✅
- **File:** `src/apex_memory/services/conversation_service.py:282`
- **Issue:** Called wrong method name
- **Before:** `await self.query_router.route_query(query)`
- **After:** `await self.query_router.query(query)`

**Fix 2: Redis Connection** ✅
- **File:** `src/apex_memory/services/conversation_service.py:58`
- **Issue:** QueryRouter defaulted to `localhost` instead of Docker service name
- **Before:** `self.query_router = QueryRouter()`
- **After:** `self.query_router = QueryRouter(redis_host=self.settings.redis_host)`

**Fix 3: Missing Content Field** ✅
- **File:** `src/apex_memory/query_router/postgres_queries.py`
- **Issue:** PostgreSQL queries didn't select `content` column (required for LLM context)
- **Fixed:** Added `content` to all 3 query types (vector, metadata, fulltext)

**Result:** All 3 fixes correct but issue persists - deeper problem exists.

#### Root Cause Hypothesis

The query router's `_route_query()` method appears to execute database queries but returns no results. Likely causes:

1. **Async Query Execution Not Awaited**
   - Database queries may be fire-and-forget without proper await
   - Results collection happens before queries complete

2. **Silent Exception Handling**
   - Exceptions caught and suppressed without logging
   - Query execution fails but returns empty list gracefully

3. **Database Connection Pool Issues**
   - Connections established but queries don't execute
   - Connection pool exhaustion or misconfiguration

4. **Query Building Logic Error**
   - SQL/Cypher queries malformed
   - Vector similarity search parameters incorrect (distance metric, threshold)

#### Investigation Steps Required

**Phase 1: Query Execution Path Tracing (30-60min)**
1. Add debug logging to `_route_query()` method:
   - Log SQL/Cypher queries being executed
   - Log parameters being passed
   - Log raw database responses

2. Test direct database queries:
   - Execute postgres_queries.py SQL directly against PostgreSQL
   - Execute Neo4j Cypher queries directly
   - Verify embeddings match expected format

3. Check async execution:
   - Verify all database queries properly awaited
   - Check if concurrent queries complete before aggregation

**Phase 2: Database Query Validation (30min)**
1. Test vector similarity search directly:
   ```sql
   SELECT uuid, title, embedding <=> '[embedding_vector]'::vector AS distance
   FROM documents
   ORDER BY distance
   LIMIT 5;
   ```

2. Verify Neo4j vector index:
   ```cypher
   SHOW INDEXES
   CALL db.index.vector.queryNodes('document_embeddings', 5, [embedding_vector])
   ```

3. Check Graphiti search implementation

**Phase 3: Result Aggregation (15min)**
1. Log results from each database before fusion
2. Verify result_fusion.py not filtering out all results
3. Check if result deduplication removes all results

#### Workaround

None available. Feature is completely non-functional without context retrieval.

#### Priority Justification

**CRITICAL** because:
- Blocks entire AI Conversation Hub value proposition
- Users receive generic Claude responses instead of memory-grounded answers
- No citations provided, defeating knowledge graph integration
- Makes the feature misleading (appears to work but doesn't use user's data)

#### Resolution Target

**Before production deployment** - This is a core feature blocker.

---

## High Priority Issues

_None currently identified_

---

## Low Priority Issues

_None currently identified_

---

## Resolved Issues

### ✅ RESOLVED-001: API Container Redis Connection Failure

**Discovered:** 2025-10-22
**Resolved:** 2025-10-22
**Component:** Query Router - Redis Cache Connection

**Issue:**
API container couldn't connect to Redis cache, causing "Connection refused" errors.

**Root Cause:**
QueryRouter defaulted to `redis_host="localhost"` but Redis runs as Docker service named `redis`.

**Fix:**
```python
# conversation_service.py:58
self.query_router = QueryRouter(redis_host=self.settings.redis_host)
```

**Verification:**
No more Redis connection errors in logs. Cache layer operational.

---

### ✅ RESOLVED-002: Missing Content Field in PostgreSQL Queries

**Discovered:** 2025-10-22
**Resolved:** 2025-10-22
**Component:** Query Router - PostgreSQL Query Builder

**Issue:**
Vector/metadata/fulltext queries returned document metadata but not content, preventing LLM from generating context-aware responses.

**Root Cause:**
`postgres_queries.py` SELECT statements omitted `content` column.

**Fix:**
Added `content` field to all 3 query types in `postgres_queries.py`:
- `_build_vector_query()` - lines 88-117
- `_build_metadata_query()` - lines 160-191
- `_build_fulltext_query()` - lines 209-223

**Verification:**
PostgreSQL queries now return content field (though still returning 0 results due to ISSUE-001).

---

## Issue Tracking Workflow

**When a new issue is discovered:**

1. Add to appropriate severity section (Critical/High/Low)
2. Include all evidence gathered during investigation
3. Document reproduction steps
4. Estimate investigation time
5. Set resolution target (before/after deployment)

**When an issue is resolved:**

1. Move from severity section to "Resolved Issues"
2. Document resolution method
3. Include verification steps
4. Link to related commits/PRs

**Before deployment:**

1. All CRITICAL issues must be resolved
2. HIGH issues should be resolved or have workarounds
3. LOW issues documented for post-deployment

---

## Related Documentation

- [Deployment Verification Workflow](WORKFLOW-CHECKLIST.md)
- [Verified Features](verified/implemented/)
- [Missing Features](verified/missing/)
- [Testing Suite](../testing/TESTING-KIT.md)
