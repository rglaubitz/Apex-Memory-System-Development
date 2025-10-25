# Task 1.3: Analyze Metadata Routing Bias

**Phase:** 1 - Investigation
**Estimated Time:** 1 hour
**Dependencies:** None
**Status:** 📝 Planned

---

## Objective

Quantify how often generic entity queries are misclassified as "metadata" instead of "graph".

**From Test Report:**
- Test #1: 75% of queries classified as "metadata" (3 out of 4)
- Returns documents (PDFs) instead of extracted entities/facts
- User expects: entity facts | System returns: PDF manuals

---

## Root Cause Hypothesis

Intent classification defaults to "metadata" unless query explicitly mentions "relationships" or "connections".

**Evidence:**
- Test #1 queries about "drivers", "cargo", "locations" → classified as "metadata"
- Test #2 query explicitly mentioning "relationships" → classified as "graph" (0.95 confidence)

**Intent Classification Rules Need:**
- Entity type detection (drivers, customers, equipment)
- Bias toward "graph" when entities mentioned
- Reduce "metadata" classification for entity queries

---

## Subtasks

### Subtask 1: Test 10 Entity Queries (30 minutes)

Run various entity queries and record intent classification.

**Test Queries:**
```bash
# Create test script: scripts/debug/test-intent-classification.py
cat > scripts/debug/test-intent-classification.py << 'EOF'
#!/usr/bin/env python3
"""Test intent classification for entity queries."""

import sys
sys.path.insert(0, 'src')

from apex_memory.query_router.analyzer import QueryAnalyzer

analyzer = QueryAnalyzer()

test_queries = [
    # Generic entity queries (should be "graph", not "metadata")
    "What shipments exist in the system?",
    "Tell me about drivers",
    "Show me cargo information",
    "What customers do we have?",
    "List all equipment",
    "Find suppliers in the database",
    "What invoices are stored?",

    # Explicit relationship queries (should be "graph")
    "How are customers connected to suppliers?",
    "Show relationships between entities",

    # Metadata queries (should be "metadata")
    "Find documents about equipment",
    "Search for PDF files",
]

print("Intent Classification Test")
print("=" * 80)

results = {
    "metadata": 0,
    "graph": 0,
    "semantic": 0,
    "temporal": 0,
}

for query in test_queries:
    intent = analyzer.analyze(query)

    # Record classification
    intent_type = intent.intent_type
    results[intent_type] += 1

    print(f"\nQuery: {query}")
    print(f"  Intent: {intent_type}")
    print(f"  Confidence: {intent.confidence}")
    print(f"  Entities: {intent.entities}")

print("\n" + "=" * 80)
print("Classification Distribution:")
for intent_type, count in results.items():
    percentage = (count / len(test_queries)) * 100
    print(f"  {intent_type}: {count}/{len(test_queries)} ({percentage:.1f}%)")

# Calculate metadata bias
metadata_pct = (results["metadata"] / len(test_queries)) * 100
print(f"\nMetadata Bias: {metadata_pct:.1f}%")
if metadata_pct > 50:
    print("  ⚠️  HIGH BIAS - Over 50% classified as metadata")
elif metadata_pct > 30:
    print("  ⚠️  MODERATE BIAS - 30-50% classified as metadata")
else:
    print("  ✅ LOW BIAS - Under 30% classified as metadata")

# Expected: entity queries should be "graph", not "metadata"
entity_queries = test_queries[:7]  # First 7 are entity queries
entity_as_metadata = 0
for query in entity_queries:
    intent = analyzer.analyze(query)
    if intent.intent_type == "metadata":
        entity_as_metadata += 1

entity_bias_pct = (entity_as_metadata / len(entity_queries)) * 100
print(f"\nEntity Query Metadata Misclassification: {entity_bias_pct:.1f}%")
print(f"  (Should be 0% - all entity queries should route to graph)")
EOF

cd apex-memory-system
python scripts/debug/test-intent-classification.py
```

**Expected Results:**
- Current: 50-75% classified as "metadata"
- Target: <30% classified as "metadata"
- Entity queries should be "graph" (not "metadata")

**Validation:**
- ✅ Quantified metadata bias percentage

---

### Subtask 2: Review Intent Classification Logic (20 minutes)

Examine how QueryAnalyzer determines intent type.

**File to Review:**
`src/apex_memory/query_router/analyzer.py`

**Commands:**
```bash
cd apex-memory-system

# Find intent classification logic
grep -n "intent_type" src/apex_memory/query_router/analyzer.py -A 5

# Find keyword lists for each intent
grep -n "metadata.*keywords\|graph.*keywords\|semantic.*keywords" src/apex_memory/query_router/analyzer.py -A 10

# Check entity detection
grep -n "entities" src/apex_memory/query_router/analyzer.py -A 5
```

**Questions to Answer:**
1. What keywords trigger "metadata" classification?
2. What keywords trigger "graph" classification?
3. Is there entity type detection (drivers, customers, equipment)?
4. What's the default classification when no keywords match?

**Validation:**
- ✅ Documented current classification rules

---

### Subtask 3: Document Recommended Changes (10 minutes)

Identify specific rule changes to reduce metadata bias.

**Create:** `FINDINGS-1.3.md`

**Template:**
```markdown
# Task 1.3 Findings: Metadata Routing Bias

## Current State
- Metadata classification: [X]%
- Entity queries as metadata: [Y]%
- Graph classification: [Z]%

## Root Cause
[Specific keywords/logic causing bias]

## Recommended Changes

### Add Entity Type Detection
Entity keywords should trigger "graph" classification:
- "drivers", "customers", "suppliers", "equipment", "invoices", "shipments"
- "people", "organizations", "companies"

### Update Classification Rules
```python
# Suggested rule:
IF query contains entity_type_keywords:
    AND NOT contains "documents" or "files":
        → intent_type = "graph"
```

### Reduce Default to Metadata
Current default may be "metadata" when no keywords match.
Should be: "graph" (since most queries are about entities, not documents)

## Expected Improvement
- Metadata classification: [X]% → <30%
- Entity queries correctly routed to graph: >90%
```

---

## Success Criteria

✅ **Task Complete When:**
1. Metadata bias quantified (current %)
2. Entity type queries identified
3. Classification rule changes documented

**Deliverables:**
- `scripts/debug/test-intent-classification.py`
- Test results showing current bias
- FINDINGS-1.3.md with recommendations

---

## Next Task

**After This Task:**
→ Phase 4: Metadata Bias Fix (requires these findings)

---

## Files to Reference

**Code:**
- `src/apex_memory/query_router/analyzer.py` (intent classification)

**Report:**
- `apex-query-router-test-report.md:159-185` (metadata bias section)

---

**Created:** 2025-10-25
**Priority:** ⚠️ High
