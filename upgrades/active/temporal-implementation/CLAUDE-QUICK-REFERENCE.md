# Claude Quick Reference - Apex Memory System

**Last Updated:** October 19, 2025
**Current Work:** Week 3 Staging Lifecycle (Days 4-5 remaining)

---

## 🚀 Starting a New Session

### 1. Read These Files First (in order):

1. **Project Structure:**
   - `CLAUDE.md` (root) - Main project guidance
   - `README.md` (root) - Project overview
   - `apex-memory-system/CLAUDE.md` - Main codebase guidance

2. **Current Upgrade:**
   - `upgrades/active/temporal-implementation/graphiti-json-integration/README.md` - Entry point
   - `upgrades/active/temporal-implementation/graphiti-json-integration/PROGRESS.md` - Current status
   - `upgrades/active/temporal-implementation/graphiti-json-integration/PLANNING.md` - Implementation plan

3. **Latest Handoff:**
   - `upgrades/active/temporal-implementation/handoffs/HANDOFF-WEEK3-DAYS1-3.md` - Most recent work

4. **Reference Documentation:**
   - This file (`CLAUDE-QUICK-REFERENCE.md`) - Quick patterns and locations

---

## 📂 Key Directory Locations

### Main Codebase (symlinked)
```
apex-memory-system/
├── src/apex_memory/
│   ├── temporal/                      # Temporal.io integration
│   │   ├── activities/
│   │   │   └── ingestion.py          # ⭐ ALL ACTIVITIES (9 so far)
│   │   ├── workflows/
│   │   │   └── ingestion.py          # DocumentIngestionWorkflow
│   │   └── workers/
│   │       └── dev_worker.py         # Worker registration
│   │
│   ├── services/                      # Business logic services
│   │   ├── database_writer.py        # Enhanced Saga with 4 databases
│   │   ├── staging_manager.py        # ⭐ NEW: Staging lifecycle (Week 3)
│   │   ├── graphiti_service.py       # Graphiti integration
│   │   ├── embedding_service.py      # OpenAI embeddings
│   │   └── entity_extractor.py       # Legacy regex extractor
│   │
│   ├── models/                        # Pydantic models
│   │   ├── document.py               # Document, WriteResult
│   │   └── structured_data.py        # ⭐ NEW: StructuredData (Week 2)
│   │
│   ├── database/                      # Database clients
│   │   ├── neo4j_client.py
│   │   ├── postgres_client.py
│   │   ├── qdrant_client.py
│   │   └── redis_client.py
│   │
│   ├── config/
│   │   └── settings.py               # ⭐ Pydantic Settings (all config)
│   │
│   ├── monitoring/
│   │   └── metrics.py                # ⭐ 27 Temporal metrics
│   │
│   └── api/
│       └── ingestion.py              # FastAPI routes (Temporal-integrated)
│
├── tests/
│   ├── unit/                          # ⭐ Unit tests (fast, mocked)
│   │   ├── test_pull_and_stage_activity.py       # Week 3 Day 1
│   │   ├── test_fetch_structured_data_activity.py # Week 3 Day 2
│   │   └── test_staging_manager.py               # Week 3 Day 3
│   │
│   └── integration/                   # Integration tests (real DBs)
│       └── test_json_integration_e2e.py           # Week 2
│
├── monitoring/
│   ├── dashboards/
│   │   └── temporal-ingestion.json   # ⭐ 33-panel Grafana dashboard
│   └── alerts/
│       └── rules.yml                 # ⭐ 12 Temporal alerts
│
└── scripts/
    └── temporal/                      # Debugging scripts
        ├── check-workflow-status.py
        ├── list-failed-workflows.py
        ├── compare-metrics.py
        └── worker-health-check.sh
```

### Upgrade Documentation
```
upgrades/active/temporal-implementation/
├── graphiti-json-integration/         # ⭐ CURRENT ACTIVE WORK
│   ├── README.md                      # Entry point
│   ├── PROGRESS.md                    # ⭐ UPDATE AFTER EACH DAY
│   ├── PLANNING.md                    # 4-week plan
│   ├── IMPLEMENTATION.md              # Step-by-step guide
│   ├── TESTING.md                     # Test specifications
│   ├── TROUBLESHOOTING.md             # Common issues
│   └── RESEARCH-REFERENCES.md         # Bibliography
│
├── handoffs/                          # ⭐ Session handoff documents
│   ├── INDEX.md                       # ⭐ UPDATE WHEN ADDING HANDOFFS
│   ├── HANDOFF-WEEK3-DAYS1-3.md      # ⭐ LATEST (read first!)
│   ├── HANDOFF-SECTION-9.md
│   └── ...
│
├── tests/                             # Test artifacts
│   ├── STRUCTURE.md                   # Complete test organization
│   ├── phase-2b-saga-baseline/       # 121 Enhanced Saga tests
│   └── section-*/                     # Section-based tests
│
└── PROJECT-STATUS-SNAPSHOT.md         # Macro project view
```

---

## 🎯 Common Patterns

### Pattern 1: Adding a New Temporal Activity

**File:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

```python
# =============================================================================
# Activity N: activity_name (Week X Day Y)
# =============================================================================

@activity.defn
async def activity_name(
    param1: str,
    param2: Optional[str] = None,
) -> ReturnType:
    """Brief description.

    Handles:
    - Use case 1
    - Use case 2

    References:
        API Docs: https://...

    Args:
        param1: Description
        param2: Description (optional)

    Returns:
        Description of return value

    Raises:
        ApplicationError: If ... fails
    """
    import required_modules  # Import inside function
    from apex_memory.config.settings import get_settings

    record_temporal_activity_started('activity_name')

    try:
        settings = get_settings()

        # Activity logic here
        result = do_something()

        # Emit metrics
        record_temporal_data_quality(
            metric_type='metric_name',
            value=123,
            source='source_name'
        )

        activity.logger.info(
            f"Activity succeeded",
            extra={
                "param1": param1,
                "result_key": result.key,
            }
        )

        record_temporal_activity_completed('activity_name', success=True)

        return result

    except ApplicationError:
        record_temporal_activity_completed('activity_name', success=False)
        raise
    except Exception as e:
        activity.logger.error(
            f"Activity failed: {str(e)}",
            extra={
                "param1": param1,
                "error": str(e),
            },
            exc_info=True
        )
        record_temporal_activity_completed('activity_name', success=False)
        raise ApplicationError(
            f"Activity failed: {str(e)}",
            type="ErrorType",
            non_retryable=False  # True if should not retry
        )
```

**Corresponding Test Pattern:**

**File:** `tests/unit/test_activity_name.py`

```python
"""Unit tests for activity_name (Week X Day Y).

Tests:
- Test case 1
- Test case 2
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from apex_memory.temporal.activities.ingestion import activity_name


@pytest.mark.asyncio
async def test_activity_success_case():
    """TEST 1: Description.

    Success Criteria:
    - Criterion 1
    - Criterion 2
    """
    with patch('apex_memory.temporal.activities.ingestion.record_temporal_activity_started'), \
         patch('apex_memory.temporal.activities.ingestion.record_temporal_activity_completed'), \
         patch('apex_memory.temporal.activities.ingestion.record_temporal_data_quality') as mock_metric, \
         patch('apex_memory.temporal.activities.ingestion.activity') as mock_activity:

        mock_activity.logger = MagicMock()

        # Setup mocks
        # ... mock external dependencies

        # Execute activity
        result = await activity_name(param1="value1")

        # Assertions
        assert result == expected_result
        mock_metric.assert_called_once()
        assert mock_metric.call_args.kwargs['metric_type'] == 'metric_name'
```

---

### Pattern 2: Adding Configuration to Settings

**File:** `apex-memory-system/src/apex_memory/config/settings.py`

```python
# =============================================================================
# Feature Configuration
# =============================================================================

feature_setting: str = Field(
    default="default_value",
    description="Description of setting"
)
feature_optional: Optional[str] = Field(
    default=None,
    description="Optional setting description"
)

@property
def computed_property(self) -> str:
    """Compute derived value from settings."""
    return f"{self.feature_setting}_computed"
```

**Corresponding .env:**

**File:** `apex-memory-system/.env`

```bash
# =============================================================================
# Feature Configuration
# =============================================================================
FEATURE_SETTING=value
FEATURE_OPTIONAL=optional_value
```

---

### Pattern 3: Using StagingManager

**Import:**
```python
from apex_memory.services.staging_manager import StagingManager, StagingStatus
```

**Create Staging Directory:**
```python
manager = StagingManager()
staging_dir = manager.create_staging_directory(document_id, source)
# Result: /tmp/apex-staging/{source}/{document_id}/
```

**Write File and Metadata:**
```python
file_path = staging_dir / "document.pdf"
file_path.write_bytes(content)

manager.write_metadata(
    document_id=document_id,
    source=source,
    file_path=str(file_path),
    status=StagingStatus.ACTIVE
)
```

**Update Status:**
```python
# After successful ingestion
manager.update_status(document_id, source, StagingStatus.SUCCESS)

# After failed ingestion
manager.update_status(document_id, source, StagingStatus.FAILED)
```

**Cleanup (Scheduled Worker):**
```python
# Remove FAILED directories older than 24 hours
stats = manager.cleanup_failed_ingestions()
# Returns: {'failed_cleaned': 5, 'bytes_freed': 12345}
```

**Monitoring:**
```python
# Get disk usage
usage = manager.get_disk_usage()
# Returns: {'total_bytes': 12345, 'total_gb': 0.01, 'total_documents': 10, 'by_source': {...}}

# Get statistics
stats = manager.get_staging_statistics()
# Returns: {'total_documents': 10, 'by_status': {...}, 'by_source': {...}, 'disk_usage': {...}}
```

---

### Pattern 4: Mock Testing with httpx

**For Synchronous Methods (response.json()):**
```python
mock_response = MagicMock()
mock_response.json.return_value = {"data": "value"}
mock_response.raise_for_status = MagicMock()
```

**For Async Context Managers:**
```python
mock_client = AsyncMock()
mock_client.__aenter__.return_value = mock_client
mock_client.__aexit__.return_value = AsyncMock()
mock_client.get.return_value = mock_response

with patch('httpx.AsyncClient') as mock_httpx:
    mock_httpx.return_value = mock_client
```

**Important:** Patch at import level (`httpx.AsyncClient`) NOT module attribute level!

---

## 📊 Test Execution Commands

### Run Specific Test File
```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
PYTHONPATH=src:$PYTHONPATH pytest tests/unit/test_file_name.py -v --no-cov
```

### Run Multiple Test Files
```bash
PYTHONPATH=src:$PYTHONPATH pytest tests/unit/test_file1.py tests/unit/test_file2.py -v --no-cov
```

### Run All Unit Tests
```bash
PYTHONPATH=src:$PYTHONPATH pytest tests/unit/ -v --no-cov
```

### Run Integration Tests
```bash
PYTHONPATH=src:$PYTHONPATH pytest tests/integration/ -v -m integration
```

### Run All Tests (with coverage)
```bash
PYTHONPATH=src:$PYTHONPATH pytest tests/ --cov=apex_memory --cov-report=term-missing
```

---

## 📝 Progress Tracking Workflow

### After Each Day Completion:

1. **Update PROGRESS.md:**
   - Change status from "pending" to "completed" ✅
   - Add implementation details
   - Update test count
   - Add test results

2. **Update Test Count:**
   - Current: X tests
   - Expected Final: Y tests

3. **Create Handoff (at natural break points):**
   - Save to `handoffs/HANDOFF-WEEKX-DAYSX-Y.md`
   - Update `handoffs/INDEX.md`

---

## 🔑 Key Metrics to Track

### Current Project Status
- **Overall Progress:** 80% (Week 1-2: 100%, Week 3: 60%, Week 4: 0%)
- **Test Count:** 175 total (121 baseline + 11 Graphiti + 32 JSON + 11 staging)
- **Expected Final:** 179 total

### Week 3 Progress
- ✅ Day 1: pull_and_stage_document_activity (3 tests)
- ✅ Day 2: fetch_structured_data_activity (3 tests)
- ✅ Day 3: StagingManager service (5 tests)
- ⏳ Day 4: cleanup_staging_activity (2 tests planned)
- ⏳ Day 5: Staging metrics (2 tests planned)

---

## 🚨 Important Reminders

### Always Do:
1. **Read handoff document first** - `handoffs/HANDOFF-WEEK3-DAYS1-3.md`
2. **Update PROGRESS.md after each day** - Keep status current
3. **Run baseline tests** - Ensure no regressions
4. **Follow existing patterns** - Consistency is key
5. **Write comprehensive tests** - Document success criteria

### Never Do:
1. **Skip reading CLAUDE.md files** - Critical project context
2. **Modify production code without tests** - Test-first approach
3. **Create new patterns** - Use existing patterns from handoffs
4. **Skip updating documentation** - PROGRESS.md must stay current
5. **Commit without running tests** - All tests must pass

---

## 🔗 Quick Links

### Essential Reading (Start Here)
1. [CLAUDE.md (root)](../../../CLAUDE.md)
2. [graphiti-json-integration/README.md](graphiti-json-integration/README.md)
3. [graphiti-json-integration/PROGRESS.md](graphiti-json-integration/PROGRESS.md)
4. [handoffs/HANDOFF-WEEK3-DAYS1-3.md](handoffs/HANDOFF-WEEK3-DAYS1-3.md)

### Implementation Guides
- [PLANNING.md](graphiti-json-integration/PLANNING.md) - 4-week plan
- [IMPLEMENTATION.md](graphiti-json-integration/IMPLEMENTATION.md) - Step-by-step guide
- [TESTING.md](graphiti-json-integration/TESTING.md) - Test specifications

### Reference Documentation
- [TROUBLESHOOTING.md](graphiti-json-integration/TROUBLESHOOTING.md) - Common issues
- [RESEARCH-REFERENCES.md](graphiti-json-integration/RESEARCH-REFERENCES.md) - Bibliography
- [tests/STRUCTURE.md](tests/STRUCTURE.md) - Test organization

### Project Status
- [PROJECT-STATUS-SNAPSHOT.md](PROJECT-STATUS-SNAPSHOT.md) - Macro view
- [EXECUTION-ROADMAP.md](EXECUTION-ROADMAP.md) - 11-section plan

---

## 🎯 Current Session Template

**When starting a new session, paste this:**

```
Continue Week 3 Staging Lifecycle. Days 1-3 complete (60%).

**Just Completed:**
- Day 1: pull_and_stage_document_activity ✅
- Day 2: fetch_structured_data_activity ✅
- Day 3: StagingManager service ✅

**Next: Day 4 - cleanup_staging_activity**
- Implement Activity 10 in ingestion.py
- Remove staging after success
- Update metadata for failed ingestions
- Tests: 2 unit tests

**Context:**
- 175/179 tests passing
- 80% overall project complete
- All previous tests green
- Read HANDOFF-WEEK3-DAYS1-3.md for full context
```

---

**Last Updated:** October 19, 2025
**Next Review:** After Week 3 Day 5 completion
