# Phase 2: Temporal Endpoint Fix

**Goal:** Fix or remove pattern endpoint from ask_apex orchestration
**Estimated Time:** 2-3 hours
**Status:** 📝 Planned

---

## Overview

Fix the 422 error by either:
- **Option A:** Improving ask_apex LLM planning to generate valid payloads
- **Option B:** Removing pattern endpoint from ask_apex (create dedicated tool instead)

**Recommendation:** Option B (faster, cleaner separation of concerns)

---

## Task List

| Task | Description | Time | Status |
|------|-------------|------|--------|
| 2.1 | Remove Pattern Endpoint from ask_apex | 1 hour | 📝 Planned |
| 2.2 | Add Validation and Tests | 1-2 hours | 📝 Planned |

**Total:** 2 tasks, 2-3 hours

---

## Dependencies

**Blocks:** Phase 5 (Validation)
**Blocked By:** None (can start after Phase 1.1)

---

## Success Criteria

✅ **Phase 2 Complete:**
- ask_apex no longer calls pattern endpoint with invalid data
- Pattern endpoint works when called directly with valid entity UUIDs
- Integration test passes
- Optional: New `analyze_pattern()` tool created

---

**Created:** 2025-10-25
