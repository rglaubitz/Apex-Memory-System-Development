# Task 1.2 Findings: Qdrant Null Content

## Root Cause: Mixed Document Types in Qdrant

**Discovery Date:** 2025-10-25

### Problem Summary

Qdrant collection `apex_documents` contains TWO types of points:
1. **Document metadata points** - No `content` field (document headers)
2. **Chunk points** - Has `content` field (actual text chunks)

**When query router searches Qdrant, it returns BOTH types, causing null content results.**

---

## Evidence from Direct Qdrant Query

**Test:** `scripts/debug/verify-qdrant-content.py`

### Document Metadata Points (NO content field)
```python
{
  "ID": "00361feb-e644-46c4-b482-f891566ddb79",
  "Payload keys": ['uuid', 'title', 'file_type', 'source_path', 'created_at', 'chunk_count'],
  "Content field": "MISSING"
}
```

**Characteristics:**
- Has `uuid` (document ID)
- Has `chunk_count` (number of chunks)
- **NO** `content` field
- **NO** `document_uuid` field
- **NO** `is_chunk` field

### Chunk Points (HAS content field)
```python
{
  "ID": "004608a1-28a0-5eef-be8d-e1be073aabdb",
  "Payload keys": ['document_uuid', 'chunk_index', 'content', 'is_chunk', 'title', 'file_type', 'doc_type', 'created_at', 'source_path'],
  "Content": "Load Test Document 36\n\nThis is test document number 36 for load testing the Apex Memory System.\nIt c..."
}
```

**Characteristics:**
- Has `document_uuid` (references parent document)
- Has `chunk_index` (position in document)
- Has `content` field ✅ **THIS IS WHAT WE WANT**
- Has `is_chunk` field (True)

---

## Data Distribution

**Out of 15 sampled points:**
- 9 points = Document metadata (no content)
- 6 points = Chunks (with content)

**Ratio:** ~40% chunks, ~60% metadata

**Implication:** When query router searches, **60% of results will have null content** unless filtered correctly.

---

## Root Cause Analysis

### Why This Happens

**Qdrant Writer (`qdrant_writer.py`) stores two types of points:**

1. **Document metadata point:**
```python
# Line ~254: Store document header
client.upsert(
    collection_name="apex_documents",
    points=[
        PointStruct(
            id=doc_uuid,
            vector=doc_embedding,
            payload={
                "uuid": doc_uuid,
                "title": title,
                "file_type": file_type,
                # NO content field
            }
        )
    ]
)
```

2. **Chunk points:**
```python
# Line ~254: Store chunks
for chunk in chunks:
    client.upsert(
        collection_name="apex_documents",
        points=[
            PointStruct(
                id=chunk_uuid,
                vector=chunk_embedding,
                payload={
                    "document_uuid": doc_uuid,
                    "chunk_index": idx,
                    "content": chunk,  # ✅ HAS CONTENT
                    "is_chunk": True
                }
            )
        ]
    )
```

**Query Router Problem:**

When `qdrant_queries.py` searches, it returns **both document metadata AND chunks** without filtering. The test report showed "15 Qdrant results with `content: null`" - these were likely document metadata points.

---

## Recommended Fix

### Option A: Filter Query to Chunks Only (RECOMMENDED)

Modify `qdrant_queries.py` to filter results:

```python
# qdrant_queries.py:execute_query

# Add filter to return only chunks
results = client.search(
    collection_name="apex_documents",
    query_vector=query_vector,
    limit=limit,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="is_chunk",
                match=models.MatchValue(value=True)
            )
        ]
    )
)
```

**Pros:**
- Simple, one-line fix
- Returns only results with content
- No breaking changes

**Cons:**
- Can't search document metadata (titles, file types)

---

### Option B: Return Both, Extract Content When Available

```python
# Extract content from results
for hit in results:
    if "content" in hit.payload:
        result["content"] = hit.payload["content"]
    elif "title" in hit.payload:
        # Document metadata - fetch chunks from PostgreSQL
        result["content"] = fetch_from_postgres(hit.payload["uuid"])
    else:
        result["content"] = None
```

**Pros:**
- Can search both metadata and content
- More flexible

**Cons:**
- More complex
- Requires fallback to PostgreSQL

---

### Option C: Separate Collections

Store documents and chunks in separate collections:
- `apex_documents` - Document metadata only
- `apex_chunks` - Content chunks only

**Pros:**
- Clean separation
- Explicit search targets

**Cons:**
- Breaking change
- Requires data migration
- Need to update writer

---

## Recommended Fix: Option A + PostgreSQL Fallback

1. **Immediate:** Add `is_chunk=True` filter to Qdrant queries (Phase 3, Task 3.2)
2. **Backup:** Add PostgreSQL fallback for metadata-only results (Phase 3, Task 3.3)

**Expected Result:**
- 100% of semantic search results will have content
- Document metadata searches still work via PostgreSQL
- Zero null content in query router responses

---

## Files to Modify

**Phase 3, Task 3.2:**
- `src/apex_memory/query_router/qdrant_queries.py:245-284` (add filter)

**Phase 3, Task 3.3:**
- `src/apex_memory/query_router/orchestrator.py` (add PostgreSQL fallback)

---

## Test Validation

**After Fix, Rerun:**
```bash
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cargo shipment items",
    "limit": 15
  }' | jq '.results[] | {uuid, title, content: (.content // "NULL")}'
```

**Expected:**
- 0 results with `content: null`
- All 15 results have valid content
- Content extracted from chunk payload

---

## Impact Assessment

**Before Fix:**
- 60% of Qdrant results: `content: null` (document metadata)
- 40% of Qdrant results: Valid content (chunks)
- User experience: F (semantic search broken)

**After Fix:**
- 100% of Qdrant results: Valid content (filtered to chunks)
- 0% null content
- User experience: A (semantic search works)

---

**Investigation Complete:** ✅
**Next Step:** Phase 3, Task 3.2 - Implement filter fix
**Priority:** 🚨 Critical
**Estimated Fix Time:** 30 minutes (one-line change + tests)
