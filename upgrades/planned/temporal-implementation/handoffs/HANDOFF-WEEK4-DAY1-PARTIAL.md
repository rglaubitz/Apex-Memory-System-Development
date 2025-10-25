# Week 4 Day 1 Partial - Handoff (Context Window Warning)

**Date:** October 19, 2025
**Upgrade:** Graphiti + JSON Integration (Week 4: Two Workflows)
**Status:** Week 4 Day 1 In Progress (20% complete) | Partial work done, needs completion

---

## 🎯 What Was Accomplished

### Week 3 Complete ✅
- ✅ **Week 3 Day 5:** Staging Metrics COMPLETE (100%)
  - 7 staging metrics added to `monitoring/metrics.py`
  - 7 Grafana dashboard panels added (ROW 7: STAGING LIFECYCLE)
  - 2 Prometheus alerts added to `monitoring/alerts/rules.yml`
  - 2 unit tests created in `test_staging_metrics.py` (2/2 passing)
  - All 15 staging tests passing (13 baseline + 2 new)

**Overall Progress:** 90% complete (Weeks 1-3 done, Week 4 remaining)

### Week 4 Day 1: DocumentIngestionWorkflow Update (PARTIAL - 20%)

**Goal:** Replace S3 download with local staging + add cleanup activity

**Progress:**
- ✅ Read current workflow structure
- ✅ Updated imports (pull_and_stage_document_activity, cleanup_staging_activity)
- ✅ Updated workflow docstring (6 steps instead of 5)
- ✅ Updated workflow signature (source_location instead of bucket/prefix)
- ✅ Updated Step 1: S3 download → Pull and stage
- ✅ Updated step numbers (1/6 through 5/6)
- ⏳ **INCOMPLETE:** Step 6 (cleanup_staging_activity) NOT ADDED YET
- ⏳ **INCOMPLETE:** Return statement NOT updated with staging_cleaned field
- ⏳ **INCOMPLETE:** Error handler NOT updated for cleanup
- ⏳ **INCOMPLETE:** Tests NOT created

**Test Count:** 179 total (121 baseline + 11 Graphiti + 32 JSON + 15 staging)
**Expected After Week 4:** ~190 total (integration tests to be added)

---

## 📂 Files Modified (Partial)

### PARTIAL: `src/apex_memory/temporal/workflows/ingestion.py`

**Lines Modified:** ~1-220 (INCOMPLETE, needs Step 6 + return updates)

**Changes Made:**
1. Updated imports:
```python
from apex_memory.temporal.activities.ingestion import (
    pull_and_stage_document_activity,  # NEW (was download_from_s3_activity)
    parse_document_activity,
    extract_entities_activity,
    generate_embeddings_activity,
    write_to_databases_activity,
    cleanup_staging_activity,  # NEW
)
```

2. Updated workflow signature:
```python
async def run(
    self,
    document_id: str,
    source: str,  # frontapp, local_upload, https
    source_location: str,  # API ID, file path, or URL
) -> dict:
```

3. Updated Step 1 (S3 → Staging):
```python
self.status = "staging"
workflow.logger.info(f"Step 1/6: Staging {document_id} from {source}")

self.file_path = await workflow.execute_activity(
    pull_and_stage_document_activity,
    args=[document_id, source, source_location],
    start_to_close_timeout=timedelta(seconds=30),
    retry_policy=RetryPolicy(
        initial_interval=timedelta(seconds=1),
        backoff_coefficient=2.0,
        maximum_interval=timedelta(seconds=30),
        maximum_attempts=3,
        non_retryable_error_types=["StagingError"],
    ),
)

self.status = "staged"
workflow.logger.info(f"Staged to: {self.file_path}")
```

4. Updated step numbers: 2/6, 3/6, 4/6, 5/6

5. Added staging status tracking:
```python
staging_status = "pending"  # Track staging cleanup status
```

**INCOMPLETE WORK (needs to be added):**

6. Step 6: Cleanup Staging Activity (AFTER line 230):
```python
            # ================================================================
            # Step 6: Cleanup Staging Directory
            # ================================================================

            self.status = "cleaning_staging"
            workflow.logger.info(f"Step 6/6: Cleaning up staging directory")

            await workflow.execute_activity(
                cleanup_staging_activity,
                args=[document_id, source, "success"],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    backoff_coefficient=2.0,
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=2,
                    non_retryable_error_types=["CleanupError"],
                ),
            )

            staging_status = "cleaned"
            workflow.logger.info("Staging directory cleaned successfully")
```

7. Update success return (line ~227):
```python
            self.status = "completed"
            workflow.logger.info(f"Ingestion complete for document: {document_id}")

            return {
                "status": "success",
                "document_id": document_id,
                "uuid": parsed_doc.get("uuid"),
                "source": source,
                "databases_written": result.get("databases_written", []),
                "staging_cleaned": (staging_status == "cleaned"),  # NEW
                "workflow_status": self.status,
            }
```

8. Update error handler to cleanup failed staging (before line ~236):
```python
        except Exception as e:
            # Attempt to cleanup failed staging (mark as FAILED, not remove)
            if self.status not in ["pending", "failed"]:
                try:
                    workflow.logger.info("Attempting to mark staging as FAILED for TTL cleanup")
                    await workflow.execute_activity(
                        cleanup_staging_activity,
                        args=[document_id, source, "failed"],
                        start_to_close_timeout=timedelta(seconds=10),
                        retry_policy=RetryPolicy(maximum_attempts=1),
                    )
                    staging_status = "marked_failed"
                except Exception as cleanup_error:
                    workflow.logger.warning(f"Staging cleanup failed: {cleanup_error}")
                    staging_status = "cleanup_failed"

            # Workflow failed after all retries
            self.status = "failed"
            self.error_message = str(e)

            workflow.logger.error(
                f"Ingestion workflow failed for {document_id}: {str(e)}"
            )

            return {
                "status": "failed",
                "document_id": document_id,
                "source": source,
                "error": str(e),
                "staging_cleaned": (staging_status in ["cleaned", "marked_failed"]),  # NEW
                "workflow_status": self.status,
            }
```

---

## 🔧 Implementation Patterns

### Pattern: Staging Cleanup After Success/Failure

**Success Path:**
```python
# After databases written successfully
await workflow.execute_activity(
    cleanup_staging_activity,
    args=[document_id, source, "success"],  # "success" = remove directory
    ...
)
```

**Failure Path:**
```python
# In exception handler
await workflow.execute_activity(
    cleanup_staging_activity,
    args=[document_id, source, "failed"],  # "failed" = mark for TTL cleanup
    ...
)
```

---

## 📋 What's Next: Week 4 Day 1 Completion

### Immediate Next Steps

1. **Complete DocumentIngestionWorkflow changes** (30 mins):
   - Add Step 6: cleanup_staging_activity (see code above)
   - Update success return statement (add staging_cleaned field)
   - Update error handler (cleanup failed staging)

2. **Create 3 integration tests** (1 hour):
   - `tests/integration/test_document_workflow_staging.py` (3 tests)
     - TEST 1: End-to-end with staging cleanup
     - TEST 2: Rollback triggers cleanup (mark as failed)
     - TEST 3: Multiple sources (frontapp, local_upload, https)

3. **Run tests** (15 mins):
   - Run new integration tests
   - Verify baseline tests (179 passing)

4. **Update PROGRESS.md** (10 mins):
   - Mark Week 4 Day 1-2 as complete
   - Update test count

**Estimated Time to Complete Day 1:** ~2 hours

---

## 📊 Progress Tracking

**Overall Project:** 90% complete
- Week 1: Graphiti Integration ✅ 100%
- Week 2: JSON Support ✅ 100%
- Week 3: Staging Lifecycle ✅ 100%
- **Week 4: Two Workflows 🚀 10%** (Day 1 partial, Days 2-5 remaining)

**Test Count:**
- **Current:** 179 total (121 baseline + 11 Graphiti + 32 JSON + 15 staging)
- **After Day 1:** ~182 total (+3 integration tests)
- **After Week 4:** ~190 total (+11 integration tests)

**Files Modified (Partial):**
- Modified: 1 file (workflows/ingestion.py - INCOMPLETE)
- Created: 0 files (tests NOT created yet)

---

## 🔗 Key References

**Documentation:**
- [PROGRESS.md](../graphiti-json-integration/PROGRESS.md) - Overall upgrade progress (90%)
- [PLANNING.md](../graphiti-json-integration/PLANNING.md) - Week 4 implementation plan
- [IMPLEMENTATION.md](../graphiti-json-integration/IMPLEMENTATION.md) - Step-by-step guide

**Code Locations:**
- **Workflow (INCOMPLETE):** `src/apex_memory/temporal/workflows/ingestion.py` (lines 1-220)
- **Activities (COMPLETE):** `src/apex_memory/temporal/activities/ingestion.py`
  - `pull_and_stage_document_activity` (lines 1762-1900)
  - `cleanup_staging_activity` (lines 1929-2046)
- **Tests (NOT CREATED):** Need to create `tests/integration/test_document_workflow_staging.py`

**Related Handoffs:**
- [HANDOFF-WEEK3-DAYS1-3.md](HANDOFF-WEEK3-DAYS1-3.md) - Week 3 complete
- [HANDOFF-SECTION-9.md](HANDOFF-SECTION-9.md) - Temporal integration (82% overall)

---

## 💡 Tips for Next Session

**Start Command:**
```
Continue Week 4 Day 1 - DocumentIngestionWorkflow update (partial work done).

**Context:**
- Week 3 COMPLETE (90% overall progress)
- Week 4 Day 1 started but INCOMPLETE
- Read HANDOFF-WEEK4-DAY1-PARTIAL.md for full details

**Immediate Tasks:**
1. Complete workflows/ingestion.py (add Step 6 + update returns)
2. Create 3 integration tests
3. Run tests (verify 179 baseline + 3 new)
4. Update PROGRESS.md

**Files to Reference:**
- Current partial work: src/apex_memory/temporal/workflows/ingestion.py
- Code snippets in HANDOFF-WEEK4-DAY1-PARTIAL.md (Step 6, returns, error handler)
```

**Key Files to Reference:**
- `workflows/ingestion.py` - INCOMPLETE, needs Step 6
- Handoff document has exact code to add (Step 6, return updates, error handler)

**Testing Strategy:**
- Create `tests/integration/test_document_workflow_staging.py`
- 3 tests: end-to-end, rollback, multiple sources
- Verify baseline: `pytest tests/unit/test_staging*.py -v --no-cov`

---

## 🚨 Important Reminders

**CRITICAL:**
1. ⚠️ **Context window approaching limits** - Create handoffs frequently
2. ⚠️ **Workflow is INCOMPLETE** - Step 6 NOT added yet
3. ⚠️ **Tests NOT created** - Need integration tests before completion
4. ⚠️ **Baseline must pass** - 179 tests must still pass after changes

**DO:**
- ✅ Complete Step 6 (cleanup_staging_activity) using code in this handoff
- ✅ Update return statements (add staging_cleaned field)
- ✅ Create integration tests (3 tests)
- ✅ Verify baseline tests (179 passing)

**DON'T:**
- ❌ Skip Step 6 (cleanup is critical for disk management)
- ❌ Skip error handler update (failed staging must be marked)
- ❌ Skip integration tests (need end-to-end validation)
- ❌ Break baseline tests (121 Enhanced Saga must pass)

---

**Total Duration (Week 4 Day 1 Partial):** ~45 minutes
**Lines of Code:** ~30 lines modified (INCOMPLETE)
**Test Pass Rate:** 179/179 baseline (100%) - new tests NOT created yet
**Status:** ⏳ INCOMPLETE - Needs Step 6, returns, error handler, tests

**Next Session:** Continue Day 1 completion (~2 hours remaining)
