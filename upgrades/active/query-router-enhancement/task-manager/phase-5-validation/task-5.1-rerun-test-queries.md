# Task 5.1: Re-run Test Queries

**Phase:** 5 - Validation
**Time:** 1-2 hours
**Dependencies:** Phases 2, 3, 4 complete
**Status:** 📝 Planned

---

## Objective

Re-run the original failing queries from the test report and verify fixes.

---

## Test Queries

### Test Query 1 (Generic Logistics)
```
"What shipments and logistics data exist in the system?
Tell me about drivers, cargo, and locations."
```

**Before Fix:**
- 75% classified as "metadata"
- Returned PDF documents
- Grade: C

**After Fix Expected:**
- Classified as "graph"
- Returns entities (drivers, cargo, locations)
- Grade: B+ or A

---

### Test Query 2 (Explicit Graph)
```
"What are the relationships between Equipment entities
and Customer entities? Show me the connection graph."
```

**Before Fix:**
- Worked perfectly (Grade: A)

**After Fix Expected:**
- Still works (no regression)
- Grade: A

---

### Test Query 3 (New - Semantic Search)
```
"What cargo data exists in the system?"
```

**Purpose:** Test Qdrant content fix

**Expected:**
- Returns entities with full content
- No null content fields
- Grade: A

---

## Testing Script

```bash
# Create validation script
cat > scripts/validation/test-query-router-fixes.sh << 'EOF'
#!/bin/bash
set -e

echo "Query Router Fix Validation"
echo "============================"

# Test 1: Generic logistics query
echo -e "\nTest 1: Generic Logistics Query"
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What shipments and logistics data exist? Tell me about drivers, cargo, and locations.",
    "limit": 10
  }' | jq '.intent_type, .results[] | {type: .type, title: .title, content: (.content[:50])}'

# Test 2: Explicit graph query
echo -e "\n\nTest 2: Explicit Graph Query"
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the relationships between Equipment and Customer entities?",
    "limit": 10
  }' | jq '.intent_type, .results[0:5]'

# Test 3: Semantic search
echo -e "\n\nTest 3: Semantic Search (Qdrant)"
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cargo shipment items",
    "limit": 10
  }' | jq '.results[] | {uuid, content: (.content != null)}'

echo -e "\n\n✅ Validation complete"
EOF

chmod +x scripts/validation/test-query-router-fixes.sh
./scripts/validation/test-query-router-fixes.sh
```

---

## Success Criteria

✅ Test 1: Returns entities (not PDFs)
✅ Test 2: Still works (no regression)
✅ Test 3: Content field not null

---

**Created:** 2025-10-25
**Priority:** 🚨 Critical
