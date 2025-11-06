# Task 2.1: Remove Pattern Endpoint from ask_apex

**Phase:** 2 - Temporal Fix
**Estimated Time:** 1 hour
**Dependencies:** Task 1.1 (root cause identified)
**Status:** 📝 Planned

---

## Objective

Remove `/api/v1/patterns/aggregation/change-frequency` from ask_apex planning prompt to prevent 422 errors.

**Rationale:** Pattern endpoint requires specific entity UUIDs which generic questions can't provide. Better to have a dedicated tool.

---

## Subtasks

### Subtask 1: Update Planning Prompt (20 minutes)

Remove pattern endpoint from available APIs list.

**File:** `apex-mcp-server/src/apex_mcp_server/tools/ask_apex.py`

**Change:**
```python
# Line 106-116 (planning_prompt)

# BEFORE:
Available Apex API endpoints:
1. POST /api/v1/query/ - General search
...
9. POST /api/v1/patterns/aggregation/change-frequency - Pattern detection

# AFTER:
Available Apex API endpoints:
1. POST /api/v1/query/ - General search
...
8. GET /api/v1/analytics/dashboard - Overall graph stats
# (Pattern endpoint removed - requires specific entity UUIDs, use dedicated tool)
```

**Validation:**
```bash
# Verify change
grep -n "patterns/aggregation" apex-mcp-server/src/apex_mcp_server/tools/ask_apex.py
# Should return no matches
```

---

### Subtask 2: Test ask_apex (20 minutes)

Verify ask_apex no longer attempts pattern calls.

**Test:**
```bash
cd apex-memory-system
python scripts/debug/test-ask-apex-pattern.py
```

**Expected:** No pattern endpoint calls in raw_data

---

### Subtask 3: Create Dedicated analyze_pattern Tool (Optional, 20 minutes)

Create new MCP tool for pattern analysis.

**File:** `apex-mcp-server/src/apex_mcp_server/tools/analyze_pattern.py`

**Code:**
```python
from ..mcp_instance import mcp
import httpx

@mcp.tool()
async def analyze_pattern(
    entity_uuids: list[str],
    property_name: str,
    window_days: int = 30
) -> dict:
    """
    Analyze change frequency patterns for specific entities.

    Args:
        entity_uuids: List of entity UUIDs to analyze
        property_name: Property to analyze (e.g., "status", "balance")
        window_days: Time window in days (1-365)

    Returns:
        Pattern analysis results
    """
    # Call pattern endpoint
    # ...implementation...
```

---

## Success Criteria

✅ **Task Complete:**
- Pattern endpoint removed from planning prompt
- ask_apex tested (no 422 errors)
- Optional: New analyze_pattern tool created

---

**Files Modified:**
- `apex-mcp-server/src/apex_mcp_server/tools/ask_apex.py`

---

**Created:** 2025-10-25
**Priority:** 🚨 Critical
