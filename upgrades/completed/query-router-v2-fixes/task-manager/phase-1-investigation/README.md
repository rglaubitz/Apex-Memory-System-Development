# Phase 1: Investigation & Diagnosis

**Goal:** Verify all 3 critical issues from test report and understand root causes
**Estimated Time:** 3-4 hours
**Status:** 📝 Planned

---

## Overview

Before fixing the issues, we need to:
1. Reproduce the temporal endpoint 422 error
2. Verify whether Qdrant content is stored or missing
3. Quantify the metadata routing bias

This phase provides diagnostic data to guide fix implementation.

---

## Task List

| Task | Description | Time | Status |
|------|-------------|------|--------|
| 1.1 | Verify Temporal Endpoint Error | 1-2 hours | 📝 Planned |
| 1.2 | Verify Qdrant Null Content | 1 hour | 📝 Planned |
| 1.3 | Analyze Metadata Routing Bias | 1 hour | 📝 Planned |

**Total:** 3 tasks, 3-4 hours

---

## Dependencies

**Blocks:**
- Phase 4 (Metadata Bias Fix) - depends on Task 1.3 analysis

**Blocked By:** None (can start immediately)

---

## Success Criteria

✅ **Task 1.1 Complete:**
- 422 error reproduced with specific payload
- Root cause identified (validation error or missing data)
- Confirmed: ask_apex calls pattern endpoint incorrectly

✅ **Task 1.2 Complete:**
- Qdrant data verified (content exists or confirmed missing)
- Identified: storage issue vs retrieval issue
- Tested direct Qdrant query returns content

✅ **Task 1.3 Complete:**
- Metadata bias quantified (X% of queries)
- Entity type queries identified (should be "graph" not "metadata")
- Intent classification logic reviewed

---

## Tasks

### Task 1.1: Verify Temporal Endpoint Error
**File:** `task-1.1-verify-temporal-endpoint-error.md`
**Time:** 1-2 hours

Reproduce the 422 error by calling the pattern endpoint with invalid payloads.

**Subtasks:**
1. Call endpoint with empty entity_uuids
2. Call endpoint with window_days > 365
3. Review ask_apex planning prompt
4. Identify why LLM generates invalid payloads

---

### Task 1.2: Verify Qdrant Null Content
**File:** `task-1.2-verify-qdrant-null-content.md`
**Time:** 1 hour

Determine if Qdrant content is stored but not retrieved, or never stored.

**Subtasks:**
1. Query Qdrant directly (bypass router)
2. Check payload structure for 15 sample results
3. Verify qdrant_writer.py stores content
4. Test content retrieval in query router

---

### Task 1.3: Analyze Metadata Routing Bias
**File:** `task-1.3-analyze-metadata-routing-bias.md`
**Time:** 1 hour

Quantify how often generic entity queries are misclassified as "metadata".

**Subtasks:**
1. Test 10 entity queries (drivers, customers, equipment)
2. Record intent classification results
3. Calculate metadata classification rate
4. Review intent classification rules

---

## Validation

**Phase 1 Complete When:**
- All 3 issues confirmed and understood
- Root causes documented
- Fix strategy validated

**Deliverables:**
- Diagnostic script: `scripts/debug/verify-query-router-issues.py`
- Investigation notes in each task file
- Updated task-manager/README.md with findings

---

## Next Phase

**After Phase 1:**
→ **Phase 2: Temporal Fix** (can start immediately)
→ **Phase 3: Qdrant Fix** (can start in parallel)
→ **Phase 4: Metadata Bias** (requires Task 1.3 complete)

---

**Created:** 2025-10-25
**Dependencies:** None
**Critical Path:** Yes (blocks Phase 4)
