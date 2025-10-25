# Query Router Enhancement - Task Manager

**Project:** Fix Critical Query Router Issues from October 25, 2025 Test Report
**Status:** 📝 Planning Complete | 🚀 Ready to Execute
**Overall Grade:** B- → Target: B+ or A-
**Total Tasks:** 12 | **Estimated Time:** 15-20 hours

---

## Executive Summary

The Apex Memory Query Router test revealed 3 critical issues:

1. **🚨 CRITICAL: Temporal Pattern Endpoint (422 Error)** - `/api/v1/patterns/aggregation/change-frequency` returns validation errors
2. **🚨 CRITICAL: Qdrant Returns Null Content** - Semantic search returns UUIDs but `content: null`
3. **⚠️ HIGH: Metadata Routing Bias** - Router defaults to documents instead of extracted entities/facts

This task manager provides a systematic approach to fixing all three issues.

---

## Overall Progress

| Phase | Tasks | Status | Progress |
|-------|-------|--------|----------|
| Phase 1: Investigation | 3 | 📝 Planned | 0/3 |
| Phase 2: Temporal Fix | 2 | 📝 Planned | 0/2 |
| Phase 3: Qdrant Fix | 3 | 📝 Planned | 0/3 |
| Phase 4: Metadata Bias | 2 | 📝 Planned | 0/2 |
| Phase 5: Validation | 2 | 📝 Planned | 0/2 |
| **TOTAL** | **12** | - | **0/12 (0%)** |

---

## Quick Start

### Day 1: Investigation (3-4 hours)
```bash
cd upgrades/active/query-router-enhancement/task-manager/phase-1-investigation
cat README.md
# Start with task-1.1-verify-temporal-endpoint-error.md
```

### Day 2: Critical Fixes (6-8 hours)
```bash
# Phase 2: Fix temporal endpoint (2-3 hours)
cd phase-2-temporal-fix

# Phase 3: Fix Qdrant content (3-4 hours)
cd ../phase-3-qdrant-fix
```

### Day 3: Metadata Bias & Validation (6-8 hours)
```bash
# Phase 4: Retune intent classification (4-5 hours)
cd phase-4-metadata-bias-fix

# Phase 5: Validate all fixes (2-3 hours)
cd ../phase-5-validation
```

---

## Phase Breakdown

### Phase 1: Investigation & Diagnosis 🔍
**Goal:** Verify all 3 issues and understand root causes
**Time:** 3-4 hours
**Tasks:**
- [x] task-1.1-verify-temporal-endpoint-error.md (1-2 hours)
- [ ] task-1.2-verify-qdrant-null-content.md (1 hour)
- [ ] task-1.3-analyze-metadata-routing-bias.md (1 hour)

**Success Criteria:**
- ✅ Confirmed 422 error reproduces with specific payload
- ✅ Qdrant data storage verified (content exists or missing)
- ✅ Metadata bias quantified (% of queries classified as "metadata")

---

### Phase 2: Temporal Endpoint Fix ⚡
**Goal:** Fix or remove pattern endpoint from ask_apex orchestration
**Time:** 2-3 hours
**Tasks:**
- [ ] task-2.1-remove-pattern-endpoint-from-ask-apex.md (1 hour)
- [ ] task-2.2-add-validation-and-tests.md (1-2 hours)

**Success Criteria:**
- ✅ ask_apex no longer calls pattern endpoint with invalid data
- ✅ Pattern endpoint works when called with valid entity UUIDs
- ✅ Integration test passes

---

### Phase 3: Qdrant Content Fix 🔧
**Goal:** Ensure semantic search returns full content from Qdrant
**Time:** 4-5 hours
**Tasks:**
- [ ] task-3.1-verify-data-storage.md (1 hour)
- [ ] task-3.2-fix-query-router-content-retrieval.md (2-3 hours)
- [ ] task-3.3-add-postgresql-fallback.md (1 hour)

**Success Criteria:**
- ✅ Semantic search returns `content` field (not null)
- ✅ 15+ Qdrant results have valid content
- ✅ PostgreSQL fallback works when Qdrant lacks content

---

### Phase 4: Metadata Bias Fix 🎯
**Goal:** Retune intent classification to surface entity facts
**Time:** 4-5 hours
**Tasks:**
- [ ] task-4.1-retune-intent-classification.md (3-4 hours)
- [ ] task-4.2-add-entity-type-detection.md (1 hour)

**Success Criteria:**
- ✅ Generic queries classify as "graph" when entities mentioned
- ✅ Test query "drivers, cargo, locations" returns entities (not PDFs)
- ✅ Metadata classification reduced from 75% to <40%

---

### Phase 5: Validation & Testing ✅
**Goal:** Verify all fixes work and update test report
**Time:** 2-3 hours
**Tasks:**
- [ ] task-5.1-rerun-test-queries.md (1-2 hours)
- [ ] task-5.2-update-test-report.md (1 hour)

**Success Criteria:**
- ✅ Both original test queries return correct results
- ✅ Query Router grade improves to B+ or A-
- ✅ Updated test report documents improvements

---

## Dependencies

```
Phase 1 (Investigation)
    ↓
Phase 2 (Temporal Fix) ← Independent
Phase 3 (Qdrant Fix)   ← Independent
Phase 4 (Metadata Bias) ← Depends on Phase 1.3
    ↓
Phase 5 (Validation) ← Depends on Phases 2, 3, 4
```

**Critical Path:** Phase 1 → Phase 4 → Phase 5 (metadata bias is most complex)

**Parallel Work:** Phases 2 and 3 can be done in parallel after Phase 1

---

## Key Files to Modify

### Temporal Fix (Phase 2)
- `apex-mcp-server/src/apex_mcp_server/tools/ask_apex.py` (planning prompt)
- `apex-memory-system/src/apex_memory/api/patterns.py` (validation)

### Qdrant Fix (Phase 3)
- `apex-memory-system/src/apex_memory/query_router/qdrant_queries.py` (content retrieval)
- `apex-memory-system/src/apex_memory/database/qdrant_writer.py` (verify storage)

### Metadata Bias Fix (Phase 4)
- `apex-memory-system/src/apex_memory/query_router/analyzer.py` (intent classification)
- Entity type detection logic (new or updated)

### Testing
- `apex-memory-system/tests/integration/test_patterns_api.py`
- New: `tests/integration/test_query_router_fixes.py`

---

## Success Metrics

**Before (from test report):**
- Temporal endpoint: F (422 errors)
- Semantic search: F (null content)
- Generic queries: C (wrong data type)
- Overall grade: B- (70/100)

**After (target):**
- Temporal endpoint: A (works correctly or removed safely)
- Semantic search: A (content retrieved)
- Generic queries: B+ (returns entities)
- Overall grade: B+ to A- (85-92/100)

---

## Testing Strategy

**Phase 1-4:** Unit tests for each fix
**Phase 5:** Integration tests with original failing queries

**Test Queries to Re-run:**
1. "What shipments and logistics data exist? Tell me about drivers, cargo, and locations."
2. "What are the relationships between Equipment entities and Customer entities?"
3. "What cargo data exists in the system?" (new - metadata bias test)

**Expected Improvements:**
- Query 1: Returns entities (not PDFs) ✨
- Query 2: Still works (no regression) ✨
- Query 3: Returns structured cargo entities ✨

---

## Next Steps

1. **Start with Phase 1, Task 1.1** - Verify temporal endpoint error
2. **Read each task file** for detailed instructions
3. **Update this README** as you complete tasks (mark ✅)
4. **Run validation tests** after each phase

**Good luck! 🚀**

---

**Created:** 2025-10-25
**Source:** apex-query-router-test-report.md
**Owner:** Query Router Enhancement Team
