# Task 4.1: Retune Intent Classification

**Phase:** 4 - Metadata Bias Fix
**Time:** 3-4 hours
**Dependencies:** Task 1.3 (analysis complete)
**Status:** 📝 Planned

---

## Objective

Update query analyzer to classify entity queries as "graph" instead of "metadata".

---

## Implementation

**File:** `src/apex_memory/query_router/analyzer.py`

**Changes:**

1. **Add Entity Type Keywords:**
```python
ENTITY_KEYWORDS = [
    "drivers", "customers", "suppliers", "equipment",
    "invoices", "shipments", "cargo", "people",
    "organizations", "companies", "employees"
]
```

2. **Update Classification Logic:**
```python
# NEW RULE: Entity queries → graph
if any(keyword in query_lower for keyword in ENTITY_KEYWORDS):
    if not any(doc_kw in query_lower for doc_kw in ["documents", "files", "PDFs"]):
        intent_type = "graph"
        confidence = 0.85
        return intent_type, confidence
```

3. **Change Default:**
```python
# OLD: Default to "metadata"
# NEW: Default to "graph" (most queries are about entities)
default_intent = "graph"
```

---

## Testing

Use script from Task 1.3:
```bash
python scripts/debug/test-intent-classification.py
```

**Expected:**
- Entity queries: "graph" (not "metadata")
- Metadata bias: <40% (down from 75%)

---

## Success Criteria

✅ Intent classification updated
✅ Entity queries route to graph
✅ Tests pass

---

**Created:** 2025-10-25
**Priority:** ⚠️ High
