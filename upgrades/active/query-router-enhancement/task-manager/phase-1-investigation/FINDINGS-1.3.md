# Task 1.3 Findings: Metadata Routing Bias

## Test Results Summary

**Test Date:** 2025-10-25
**Test Script:** `scripts/debug/test-intent-classification.py`

### Classification Distribution (11 test queries)

| Query Type | Count | Percentage | Expected |
|------------|-------|------------|----------|
| semantic | 5 | 45.5% | Low (0-20%) |
| metadata | 3 | 27.3% | Low (18-27%) |
| graph | 2 | 18.2% | **High (60-70%)** ❌ |
| hybrid | 1 | 9.1% | Low (0-10%) |
| temporal | 0 | 0.0% | Low (0%) |

**Overall Metadata Bias: 27.3%** ✅ (Target: <30%)
**Entity Query Misclassification: 42.9%** ❌ (Target: 0%)

---

## Critical Finding: Entity Queries Not Recognized as Graph

**Problem:** Generic entity queries are classified as "semantic" or "metadata" instead of "graph".

### Entity Query Test Results (7 queries - all should be "graph")

| # | Query | Classified As | Correct? |
|---|-------|---------------|----------|
| 1 | "What shipments exist in the system?" | **metadata** | ❌ |
| 2 | "Tell me about drivers" | **semantic** | ❌ |
| 3 | "Show me cargo information" | **metadata** | ❌ |
| 4 | "What customers do we have?" | **semantic** | ❌ |
| 5 | "List all equipment" | **semantic** | ❌ |
| 6 | "Find suppliers in the database" | **hybrid** | ❌ |
| 7 | "What invoices are stored?" | **metadata** | ❌ |

**Success Rate: 0/7 (0%)** - All entity queries misclassified!

---

## What Works: Explicit Relationship Queries

| Query | Classified As | Correct? |
|-------|---------------|----------|
| "How are customers connected to suppliers?" | **graph** | ✅ |
| "Show relationships between entities" | **graph** | ✅ |

**Success Rate: 2/2 (100%)** - Perfect when using relationship keywords

---

## Root Cause Analysis

### Current Keyword Lists (from `analyzer.py:62-86`)

**GRAPH_KEYWORDS (Line 63-67):**
```python
GRAPH_KEYWORDS = {
    "related", "relationship", "connected", "links", "associated",
    "between", "linked to", "network", "graph", "connections",
    "connected to", "ties to", "relates to"
}
```

❌ **Missing:** Entity type keywords (customers, drivers, equipment, etc.)

**SEMANTIC_KEYWORDS (Line 76-80):**
```python
SEMANTIC_KEYWORDS = {
    "similar", "like", "about", "regarding", "concerning", "related to",
    "relevant", "pertaining", "find", "search", "semantically",
    "meaning", "context", "topic", "theme", "subject"
}
```

❌ **Problem:** Includes "about", "find", "search" → Matches entity queries like "Tell me **about** drivers"

**METADATA_KEYWORDS (Line 82-86):**
```python
METADATA_KEYWORDS = {
    "type", "status", "created", "author", "source", "date", "filter",
    "where", "with", "by", "from", "in", "on", "dated", "authored by",
    "written by", "published", "uploaded", "modified"
}
```

❌ **Problem:** Includes "with", "by", "from", "in", "on" → Matches entity queries like "Find suppliers **in** the database"

---

## Why Entity Queries Fail

### Query: "Tell me about drivers"

**Matches:**
- SEMANTIC_KEYWORDS: "about" ✅
- GRAPH_KEYWORDS: ❌ (no match)

**Result:** Classified as "semantic" (wrong)

**Expected:** Should recognize "drivers" as entity type → classify as "graph"

### Query: "What shipments exist in the system?"

**Matches:**
- METADATA_KEYWORDS: "in" ✅
- GRAPH_KEYWORDS: ❌ (no match)

**Result:** Classified as "metadata" (wrong)

**Expected:** Should recognize "shipments" as entity type → classify as "graph"

---

## Recommended Changes

### 1. Add Entity Type Keywords to GRAPH_KEYWORDS

```python
GRAPH_KEYWORDS = {
    # Existing relationship keywords
    "related", "relationship", "connected", "links", "associated",
    "between", "linked to", "network", "graph", "connections",
    "connected to", "ties to", "relates to",

    # NEW: Entity type keywords
    "customers", "customer", "clients", "client", "accounts", "account",
    "drivers", "driver", "operators", "operator",
    "equipment", "vehicles", "vehicle", "trucks", "truck", "trailers", "trailer",
    "suppliers", "supplier", "vendors", "vendor",
    "invoices", "invoice", "bills", "bill",
    "shipments", "shipment", "loads", "load", "freight",
    "cargo", "goods",
    "people", "person", "employees", "employee",
    "companies", "company", "organizations", "organization",
    "entities", "entity"
}
```

---

### 2. Remove Generic Words from SEMANTIC_KEYWORDS

**Remove:** "about", "find", "search" (too generic)

```python
SEMANTIC_KEYWORDS = {
    "similar", "like", "regarding", "concerning", "related to",
    "relevant", "pertaining", "semantically",
    "meaning", "context", "topic", "theme", "subject"
    # Removed: "about", "find", "search"
}
```

---

### 3. Remove Generic Prepositions from METADATA_KEYWORDS

**Remove:** "with", "by", "from", "in", "on" (too generic)

```python
METADATA_KEYWORDS = {
    "type", "status", "created", "author", "source", "date", "filter",
    "where", "dated", "authored by",
    "written by", "published", "uploaded", "modified"
    # Removed: "with", "by", "from", "in", "on"
}
```

---

### 4. Add Entity Type Detection Rule

**New Logic:**
```python
# In analyzer.py analyze() method
def analyze(self, query: str) -> QueryIntent:
    # ... existing code ...

    # NEW: Check for entity type keywords
    entity_types_mentioned = []
    for entity_type in ENTITY_TYPE_KEYWORDS:
        if entity_type in query_lower:
            entity_types_mentioned.append(entity_type)

    # If entity types mentioned AND no document keywords, classify as graph
    document_keywords = {"document", "documents", "file", "files", "pdf", "doc"}
    has_document_keywords = any(kw in query_lower for kw in document_keywords)

    if entity_types_mentioned and not has_document_keywords:
        query_type = QueryType.GRAPH
        confidence = 0.9
        return QueryIntent(
            query_text=query,
            query_type=query_type,
            confidence=confidence,
            entities=entity_types_mentioned
        )
```

---

## Expected Impact of Changes

### Before Changes
- Entity queries as graph: 0/7 (0%)
- Entity queries as metadata: 3/7 (42.9%)
- Entity queries as semantic: 3/7 (42.9%)

### After Changes
- Entity queries as graph: 7/7 (100%) ✅
- Entity queries as metadata: 0/7 (0%) ✅
- Entity queries as semantic: 0/7 (0%) ✅

---

## Test Report Correlation

**From `apex-query-router-test-report.md:159-185`:**

> Test #1: 75% of queries classified as "metadata" (3 out of 4)
>
> Router defaults to "metadata" intent unless query explicitly mentions relationships/connections

**Our Findings Confirm:**
- Generic entity queries misclassified
- Only explicit relationship keywords trigger "graph" classification
- Matches test report observations exactly

---

## Next Steps (Phase 4)

1. **Task 4.1:** Implement keyword changes in `analyzer.py`
2. **Task 4.2:** Add entity type detection rule
3. **Retest:** Run `test-intent-classification.py` to verify 100% entity query accuracy
4. **Integration test:** Verify ask_apex returns entities (not PDFs) for generic queries

---

## Files to Modify

**analyzer.py:src/apex_memory/query_router/analyzer.py**
- Line 63-67: Add entity type keywords to GRAPH_KEYWORDS
- Line 76-80: Remove generic words from SEMANTIC_KEYWORDS
- Line 82-86: Remove generic prepositions from METADATA_KEYWORDS
- Line ~150-200: Add entity type detection rule in analyze() method

---

**Investigation Complete:** ✅
**Next Phase:** Phase 4 - Metadata Bias Fix
**Priority:** ⚠️ High (affects user experience significantly)
**Estimated Fix Time:** 2-3 hours (keyword updates + entity detection logic + tests)
