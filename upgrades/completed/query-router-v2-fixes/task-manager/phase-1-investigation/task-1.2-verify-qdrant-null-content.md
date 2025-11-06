# Task 1.2: Verify Qdrant Null Content

**Phase:** 1 - Investigation
**Estimated Time:** 1 hour
**Dependencies:** None
**Status:** 📝 Planned

---

## Objective

Determine if Qdrant content is stored but not retrieved, or never stored at all.

**From Test Report:**
- 15 Qdrant results returned with `content: null`
- UUIDs exist but content field is null
- Suggests indexing issue or incomplete data sync

---

## Root Cause Hypothesis

**Option A:** Content IS stored in Qdrant payload, but query router doesn't extract it
**Option B:** Content is NOT stored in Qdrant (writer bug)
**Option C:** Content stored but in different field name

**Evidence from code:**
- `qdrant_writer.py:254` - DOES store content: `payload['content'] = chunk`
- `qdrant_queries.py:245-284` - execute_query returns payload
- Likely retrieval/extraction issue (Option A)

---

## Subtasks

### Subtask 1: Direct Qdrant Query (20 minutes)

Query Qdrant directly to check if content is stored.

**Commands:**
```bash
cd apex-memory-system

# Test script: scripts/debug/verify-qdrant-content.py
cat > scripts/debug/verify-qdrant-content.py << 'EOF'
#!/usr/bin/env python3
"""Verify Qdrant content storage."""

from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)

# Get a sample of points from apex_documents collection
results = client.scroll(
    collection_name="apex_documents",
    limit=15,
    with_payload=True,
    with_vectors=False
)

points, _ = results

print(f"Found {len(points)} points in apex_documents collection\n")

for idx, point in enumerate(points[:15], 1):
    print(f"Point {idx}:")
    print(f"  ID: {point.id}")
    print(f"  Payload keys: {list(point.payload.keys())}")

    # Check for content field
    if 'content' in point.payload:
        content = point.payload['content']
        if content:
            print(f"  Content: {content[:100]}...")  # First 100 chars
        else:
            print(f"  Content: NULL or EMPTY")
    else:
        print(f"  Content field: MISSING")

    print()

# Also check chunks collection
print("\n" + "="*80)
print("Checking 'chunks' collection:")
print("="*80 + "\n")

try:
    results = client.scroll(
        collection_name="chunks",
        limit=5,
        with_payload=True,
        with_vectors=False
    )

    points, _ = results
    print(f"Found {len(points)} chunks\n")

    for idx, point in enumerate(points[:5], 1):
        print(f"Chunk {idx}:")
        print(f"  Payload keys: {list(point.payload.keys())}")
        if 'content' in point.payload:
            content = point.payload['content']
            print(f"  Content: {content[:100] if content else 'NULL'}...")
        print()

except Exception as e:
    print(f"Chunks collection not found or error: {e}")
EOF

python scripts/debug/verify-qdrant-content.py
```

**Expected Results:**
- If content IS stored: Payload has 'content' key with text
- If content NOT stored: Payload missing 'content' or content is null
- Identify correct collection (apex_documents vs chunks)

**Validation:**
- ✅ Confirmed whether content exists in Qdrant

---

### Subtask 2: Trace Query Router Path (20 minutes)

Follow the code path from query router to Qdrant result extraction.

**Files to Review:**
1. `src/apex_memory/query_router/qdrant_queries.py:245-284` - execute_query
2. `src/apex_memory/query_router/orchestrator.py` (if exists) - result extraction
3. `apex-mcp-server/src/apex_mcp_server/tools/search.py` - MCP search tool

**Commands:**
```bash
# Find where Qdrant results are processed
cd apex-memory-system
grep -rn "execute_query" src/apex_memory/query_router/ --include="*.py"

# Check how payload is extracted
grep -rn "\.payload" src/apex_memory/query_router/ --include="*.py" -A 3

# Check MCP server search tool
grep -rn "content" apex-mcp-server/src/apex_mcp_server/tools/ -A 2
```

**Questions to Answer:**
1. Does execute_query return payload['content']?
2. Is content field mapped to result['content']?
3. Is there a field name mismatch (e.g., 'text' vs 'content')?

**Validation:**
- ✅ Identified exact code location where content should be extracted

---

### Subtask 3: Test Query Router Search (15 minutes)

Test semantic search through the query router.

**Commands:**
```bash
# Use MCP search tool or direct API
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cargo shipment items",
    "limit": 5
  }' | jq '.results[] | {uuid, title, content: (.content // "NULL")}'
```

**Expected:**
- If content retrieved: JSON shows content field with text
- If content null: Confirms retrieval bug

**Validation:**
- ✅ Tested end-to-end query path

---

### Subtask 4: Document Findings (5 minutes)

**Create:** `FINDINGS-1.2.md`

**Template:**
```markdown
# Task 1.2 Findings: Qdrant Null Content

## Root Cause
[Storage issue vs Retrieval issue]

## Evidence
- Direct Qdrant query: [Content exists/missing]
- Query router path: [Where content is lost]
- End-to-end test: [Result]

## Recommended Fix
[Specific file and function to fix]
```

---

## Success Criteria

✅ **Task Complete When:**
1. Confirmed whether content is stored in Qdrant
2. Identified where content is lost (if storage is OK)
3. Documented exact fix location

**Deliverables:**
- `scripts/debug/verify-qdrant-content.py`
- Direct query results
- FINDINGS-1.2.md

---

## Next Task

**After This Task:**
→ Phase 3: Qdrant Fix (if root cause is clear)

---

## Files to Reference

**Code:**
- `src/apex_memory/database/qdrant_writer.py:200-288` (write_chunks)
- `src/apex_memory/query_router/qdrant_queries.py:245-284` (execute_query)

**Report:**
- `apex-query-router-test-report.md:188-217`

---

**Created:** 2025-10-25
**Priority:** 🚨 Critical
