# Task 2.2: Add Validation and Tests

**Phase:** 2 - Temporal Fix
**Estimated Time:** 1-2 hours
**Dependencies:** Task 2.1
**Status:** 📝 Planned

---

## Objective

Add tests to ensure pattern endpoint works when called correctly, and add validation to prevent future 422 errors.

---

## Subtasks

### Subtask 1: Add API Validation (30 minutes)

Add pre-execution validation in execute_query_strategy.

**File:** `apex-mcp-server/src/apex_mcp_server/tools/ask_apex.py:190-289`

**Add validation:**
```python
# Before executing query
if "patterns/aggregation" in step_config["endpoint"]:
    payload = step_config.get("payload", {})

    # Validate required fields
    if not payload.get("entity_uuids"):
        logger.warning(f"Skipping pattern endpoint: missing entity_uuids")
        continue
    if not payload.get("property_name"):
        logger.warning(f"Skipping pattern endpoint: missing property_name")
        continue
    if payload.get("window_days", 0) > 365:
        logger.warning(f"Skipping pattern endpoint: invalid window_days")
        continue
```

---

### Subtask 2: Create Integration Test (1 hour)

**File:** `apex-memory-system/tests/integration/test_query_router_temporal_fix.py`

**Test cases:**
1. Pattern endpoint with valid payload (should work)
2. ask_apex doesn't call pattern endpoint
3. Direct pattern call works

---

## Success Criteria

✅ **Task Complete:**
- Validation added
- Integration tests pass
- No 422 errors

---

**Created:** 2025-10-25
