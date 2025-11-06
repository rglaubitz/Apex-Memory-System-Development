# Task 1.1: Verify Temporal Endpoint Error

**Phase:** 1 - Investigation
**Estimated Time:** 1-2 hours
**Dependencies:** None
**Status:** 📝 Planned

---

## Objective

Reproduce the 422 error from the temporal pattern endpoint and identify the root cause.

**From Test Report:**
- Endpoint: `/api/v1/patterns/aggregation/change-frequency`
- Error: `422 Unprocessable Entity`
- Occurs in: ask_apex orchestration (Steps 5 in both Test #1 and Test #2)

---

## Root Cause Hypothesis

The ask_apex tool uses an LLM to plan API calls. When planning calls to the pattern endpoint, the LLM may:

1. **Not provide required fields** (`entity_uuids`, `property_name`)
2. **Provide invalid window_days** (>365 or <1)
3. **Send empty entity_uuids arrays**

**Evidence from code:**
- `patterns.py:54` - Pydantic validation enforces `window_days` between 1-365
- `ask_apex.py:115` - Pattern endpoint listed in available APIs
- Test report shows consistent 422 errors across sessions

---

## Subtasks

### Subtask 1: Direct API Test (30 minutes)

Test the endpoint directly with various payloads to understand validation.

**Commands:**
```bash
cd apex-memory-system

# Test 1: Valid payload
curl -X POST http://localhost:8000/api/v1/patterns/aggregation/change-frequency \
  -H "Content-Type: application/json" \
  -d '{
    "entity_uuids": ["entity-1", "entity-2"],
    "property_name": "status",
    "window_days": 30
  }'

# Test 2: Empty entity_uuids (should fail)
curl -X POST http://localhost:8000/api/v1/patterns/aggregation/change-frequency \
  -H "Content-Type: application/json" \
  -d '{
    "entity_uuids": [],
    "property_name": "status",
    "window_days": 30
  }'

# Test 3: Invalid window_days (should fail with 422)
curl -X POST http://localhost:8000/api/v1/patterns/aggregation/change-frequency \
  -H "Content-Type: application/json" \
  -d '{
    "entity_uuids": ["entity-1"],
    "property_name": "status",
    "window_days": 500
  }'

# Test 4: Missing required fields (should fail)
curl -X POST http://localhost:8000/api/v1/patterns/aggregation/change-frequency \
  -H "Content-Type: application/json" \
  -d '{
    "window_days": 30
  }'
```

**Expected Results:**
- Test 1: 200 or 500 (depends on data availability)
- Test 2: Possibly 200 (empty result) or 422 (validation error)
- Test 3: 422 (window_days validation)
- Test 4: 422 (missing required fields)

**Validation:**
- ✅ Identified which validation rule triggers 422

---

### Subtask 2: Review ask_apex Planning (30 minutes)

Examine how ask_apex generates pattern endpoint calls.

**File to Review:**
`apex-mcp-server/src/apex_mcp_server/tools/ask_apex.py:100-167`

**Questions:**
1. Does the planning prompt provide example payloads for pattern endpoint?
2. Does the LLM have enough context to know entity_uuids are required?
3. Is there validation before executing planned queries?

**Commands:**
```bash
# View the planning prompt
cat apex-mcp-server/src/apex_mcp_server/tools/ask_apex.py | grep -A 70 "planning_prompt ="

# Check if there's validation
grep -n "entity_uuids" apex-mcp-server/src/apex_mcp_server/tools/ask_apex.py
```

**Findings to Document:**
- Does prompt include pattern endpoint example? (Line 115)
- Are entity_uuids mentioned in prompt?
- Is there pre-execution validation?

---

### Subtask 3: Test ask_apex with Pattern Query (30 minutes)

Call ask_apex with a query that triggers pattern detection.

**Prerequisites:**
- API server running (`python -m uvicorn apex_memory.main:app --reload`)
- ask_apex configured with Anthropic API key

**Test Query:**
```python
# Create test script: scripts/debug/test-ask-apex-pattern.py
import asyncio
import sys
sys.path.insert(0, 'apex-mcp-server/src')

from apex_mcp_server.tools.ask_apex import ask_apex

async def test_pattern_query():
    result = await ask_apex(
        question="What patterns exist in entity changes?",
        include_raw_data=True,
        max_queries=6
    )

    print("Query Results:")
    print(f"Answer: {result['answer']}")
    print(f"\nQuery Count: {result['query_count']}")
    print(f"Data Sources: {result['data_sources_used']}")

    if result['raw_data']:
        for query_result in result['raw_data']:
            if 'change-frequency' in query_result['endpoint']:
                print(f"\nPattern Endpoint Called:")
                print(f"  Step: {query_result['step']}")
                print(f"  Result: {query_result['result']}")

asyncio.run(test_pattern_query())
```

**Run:**
```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
python scripts/debug/test-ask-apex-pattern.py
```

**Expected:**
- ask_apex calls pattern endpoint
- If 422 error: captured in result['raw_data'][X]['result']['error']

**Validation:**
- ✅ Confirmed ask_apex generates invalid payloads
- ✅ Documented exact payload that causes 422

---

### Subtask 4: Document Root Cause (10 minutes)

Summarize findings for fix implementation.

**Create:** `upgrades/active/query-router-enhancement/task-manager/phase-1-investigation/FINDINGS-1.1.md`

**Template:**
```markdown
# Task 1.1 Findings: Temporal Endpoint Error

## Root Cause
[Describe the exact cause of 422 error]

## Evidence
- Direct API test: [Result]
- ask_apex planning: [Findings]
- Example invalid payload: [JSON]

## Recommended Fix
Option A: Remove pattern endpoint from ask_apex
Option B: Fix LLM planning prompt to generate valid payloads
Option C: Add validation layer before API calls

Recommendation: [A/B/C] because [reason]
```

---

## Success Criteria

✅ **Task Complete When:**
1. 422 error reproduced with specific payload
2. Root cause identified (validation rule)
3. ask_apex planning issue documented
4. Fix recommendation provided

**Deliverables:**
- Test results from curl commands
- ask_apex test script output
- FINDINGS-1.1.md document

---

## Next Task

**After This Task:**
→ Task 1.2: Verify Qdrant Null Content (can run in parallel)
→ OR Phase 2: Temporal Fix (if root cause is clear)

---

## Files to Reference

**Code:**
- `apex-memory-system/src/apex_memory/api/patterns.py:114-162` (endpoint)
- `apex-memory-system/src/apex_memory/temporal/pattern_detector.py:362-435` (implementation)
- `apex-mcp-server/src/apex_mcp_server/tools/ask_apex.py:100-167` (planning prompt)

**Tests:**
- `apex-memory-system/tests/integration/test_patterns_api.py:29-65` (test cases)

**Report:**
- `upgrades/active/query-router-enhancement/apex-query-router-test-report.md:220-243`

---

**Created:** 2025-10-25
**Owner:** Query Router Enhancement
**Priority:** 🚨 Critical
