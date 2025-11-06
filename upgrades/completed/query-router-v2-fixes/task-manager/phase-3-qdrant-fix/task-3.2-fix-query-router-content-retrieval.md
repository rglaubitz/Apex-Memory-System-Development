# Task 3.2: Fix Query Router Content Retrieval

**Phase:** 3 - Qdrant Fix
**Time:** 2-3 hours
**Dependencies:** Task 3.1
**Status:** 📝 Planned

---

## Objective

Update query router to extract and return content field from Qdrant results.

---

## Files to Modify

1. `src/apex_memory/query_router/qdrant_queries.py:245-284` - execute_query
2. Query orchestrator (ensure payload.content extracted)
3. MCP search tool (return content field)

---

## Implementation

**Update execute_query:**
```python
formatted_results.append({
    "id": result.id,
    "score": result.score,
    "payload": result.payload,
    # Ensure content is accessible
    "content": result.payload.get("content", None),
    "title": result.payload.get("title", "Untitled"),
})
```

---

## Testing

```bash
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "cargo items", "limit": 5}' \
  | jq '.results[] | {content: .content}'
```

Expected: content field with text (not null)

---

## Success Criteria

✅ Query returns content field
✅ 15+ results have valid content
✅ Integration test passes

---

**Created:** 2025-10-25
**Priority:** 🚨 Critical
