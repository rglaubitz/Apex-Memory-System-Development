# TESTING STRATEGY: Advanced Temporal Features

**Project:** Apex Memory System - Temporal Advanced Features
**Test Count:** 35 tests (10 + 15 + 10)
**Categories:** Integration tests
**Framework:** pytest with Temporal Python SDK

---

## 📊 Test Overview

| Section | Tests | Category | File |
|---------|-------|----------|------|
| Section 14: Search Attributes | 10 | Integration | `test_search_attributes.py` |
| Section 12: Polling Workflows | 15 | Integration | `test_polling_workflow.py` |
| Section 16: OpenTelemetry | 10 | Integration | `test_opentelemetry.py` |
| **Total** | **35** | **Integration** | **3 files** |

---

## Section 14: Search Attributes (10 Tests)

**File:** `apex-memory-system/tests/integration/test_search_attributes.py`

### TEST 1: Search attributes configured
**Purpose:** Verify all 4 search attributes registered in Temporal
**Test Method:**
- Query Temporal for registered attributes
- Verify Source, Priority, DocumentId, Status exist
**Success:** All 4 attributes present

### TEST 2: Document workflow tagged with Source attribute
**Purpose:** Verify DocumentIngestionWorkflow tagged with Source
**Test Method:**
- Start workflow with Source="frontapp"
- Search by `Source='frontapp'`
- Verify workflow found
**Success:** Workflow discoverable by source

### TEST 3: Workflow tagged with Priority attribute
**Purpose:** Verify workflows tagged with Priority
**Test Method:**
- Start workflow with Priority=3
- Search by `Priority>=3`
- Verify workflow found with correct priority
**Success:** High-priority workflows discoverable

### TEST 4: Workflow searchable by DocumentId
**Purpose:** Verify workflows findable by document ID
**Test Method:**
- Start workflow with DocumentId="test-doc-123"
- Search by `DocumentId='test-doc-123'`
- Verify exact match found
**Success:** Workflow found by document ID

### TEST 5: Status attribute updates
**Purpose:** Verify Status updates as workflow progresses
**Test Method:**
- Start workflow (Status="pending")
- Check status after parse (Status="processing")
- Verify final status (Status="completed")
**Success:** Status reflects workflow state

### TEST 6: Search by source works
**Purpose:** Validate Source search query
**Test Method:**
- Start 3 workflows (frontapp, turvo, api)
- Search `Source='turvo'`
- Verify only Turvo workflow returned
**Success:** Source filtering accurate

### TEST 7: Search by priority works
**Purpose:** Validate Priority range queries
**Test Method:**
- Start workflows with Priority 1, 2, 3, 4
- Search `Priority>=3`
- Verify only Priority 3+ workflows returned
**Success:** Priority filtering accurate

### TEST 8: Combined search works
**Purpose:** Validate multi-attribute search
**Test Method:**
- Start mixed workflows
- Search `Source='frontapp' AND Priority=3`
- Verify only matching workflows returned
**Success:** Combined queries work

### TEST 9: Label cardinality check
**Purpose:** Ensure no label explosion
**Test Method:**
- Start 100 workflows with various attributes
- Query Prometheus for label cardinality
- Verify <100 unique combinations
**Success:** No cardinality explosion

### TEST 10: Temporal UI search functional
**Purpose:** Verify search works in Temporal UI
**Test Method:**
- Start test workflow
- Query via Temporal UI API
- Verify results match expected
**Success:** UI search operational

---

## Section 12: Polling Workflows (15 Tests)

**File:** `apex-memory-system/tests/integration/test_polling_workflow.py`

### TEST 1: Polling workflow executes
**Purpose:** Verify PollingWorkflow runs successfully
**Test Method:**
- Start PollingWorkflow with 1-min interval
- Wait for first iteration
- Query stats (iteration_count >= 1)
**Success:** Workflow completes first poll

### TEST 2: Polling interval works
**Purpose:** Verify configurable polling interval
**Test Method:**
- Start workflow with 2-min interval
- Measure time between iterations
- Verify ~2 minutes elapsed
**Success:** Interval respected

### TEST 3: Child workflows spawned
**Purpose:** Verify child workflow creation for each record
**Test Method:**
- Mock fetch_new_records (return 3 records)
- Verify 3 child workflows created
- Check child workflow IDs
**Success:** 1 child per record

### TEST 4: Continue-as-new after 100 iterations
**Purpose:** Verify continue-as-new pattern
**Test Method:**
- Mock workflow to run 101 iterations quickly
- Verify new workflow started at iteration 100
- Verify state preserved (last_poll_timestamp)
**Success:** Continue-as-new executed

### TEST 5: Stats query returns data
**Purpose:** Verify statistics query accuracy
**Test Method:**
- Start workflow, let run 3 iterations
- Query stats
- Verify iteration_count=3, total_records accurate
**Success:** Stats accurate

### TEST 6: Empty result handled
**Purpose:** Verify empty API response handled gracefully
**Test Method:**
- Mock fetch (return 0 records)
- Verify no child workflows spawned
- Verify workflow continues polling
**Success:** No errors, polling continues

### TEST 7: Logging configured
**Purpose:** Verify structured logging
**Test Method:**
- Start workflow
- Check logs for workflow_id, iteration, source
- Verify JSON format
**Success:** Logs include context

### TEST 8: Fetch Samsara GPS events
**Purpose:** Verify Samsara API polling
**Test Method:**
- Mock Samsara API
- Call fetch_new_records_activity(source="samsara")
- Verify API called with correct params
**Success:** Samsara API integration works

### TEST 9: Fetch Turvo shipments
**Purpose:** Verify Turvo API polling
**Test Method:**
- Mock Turvo API
- Call fetch_new_records_activity(source="turvo")
- Verify API called
**Success:** Turvo API integration works

### TEST 10: Custom API polling
**Purpose:** Verify custom API support
**Test Method:**
- Mock custom API
- Call fetch_new_records_activity(source="custom")
- Verify extensibility
**Success:** Custom APIs supported

### TEST 11: Unsupported source rejected
**Purpose:** Verify unsupported sources raise error
**Test Method:**
- Call fetch_new_records_activity(source="unknown")
- Expect ValueError
**Success:** ValueError raised

### TEST 12: Empty list handled
**Purpose:** Verify empty response structure
**Test Method:**
- Mock API (return empty list)
- Verify result structure valid
- Verify count=0, has_more=False
**Success:** Empty list handled

### TEST 13: Retry on API failure
**Purpose:** Verify activity retry on HTTP errors
**Test Method:**
- Mock API (raise httpx.HTTPError first 2 calls)
- Verify retry policy kicks in
- Verify eventual success
**Success:** Activity retries

### TEST 14: Record count logged
**Purpose:** Verify record count in logs
**Test Method:**
- Mock API (return 5 records)
- Check logs for "Fetched 5 records"
**Success:** Count logged

### TEST 15: Activity heartbeat sent
**Purpose:** Verify activity sends heartbeats for long operations
**Test Method:**
- Mock API (slow response)
- Verify heartbeat recorded
**Success:** Heartbeat sent

---

## Section 16: OpenTelemetry (10 Tests)

**File:** `apex-memory-system/tests/integration/test_opentelemetry.py`

### TEST 1: Telemetry setup when enabled
**Purpose:** Verify OpenTelemetry configures correctly
**Test Method:**
- Set ENABLE_OPENTELEMETRY=true
- Call telemetry.configure()
- Verify no errors
**Success:** Configuration succeeds

### TEST 2: Telemetry disabled when flag is false
**Purpose:** Verify telemetry skipped when disabled
**Test Method:**
- Set ENABLE_OPENTELEMETRY=false
- Call telemetry.configure()
- Verify no-op
**Success:** No configuration performed

### TEST 3: TracerProvider configured
**Purpose:** Verify global tracer provider set
**Test Method:**
- Configure telemetry
- Get tracer via trace.get_tracer()
- Verify tracer is not None
**Success:** Tracer provider set

### TEST 4: OTLP exporter configured
**Purpose:** Verify OTLP exporter setup
**Test Method:**
- Configure telemetry
- Verify OTLPSpanExporter created
- Check endpoint set to localhost:4317
**Success:** Exporter configured

### TEST 5: Jaeger running and accessible
**Purpose:** Verify Jaeger service operational
**Test Method:**
- HTTP request to localhost:16686
- Verify Jaeger UI responds
- Check health endpoint
**Success:** Jaeger accessible

### TEST 6: Workflow traces exported
**Purpose:** Verify workflow execution creates traces
**Test Method:**
- Start DocumentIngestionWorkflow
- Wait for completion
- Query Jaeger API for traces
- Verify trace exists with workflow_id
**Success:** Workflow trace in Jaeger

### TEST 7: Activity traces exported
**Purpose:** Verify activity execution creates spans
**Test Method:**
- Start workflow (triggers activities)
- Query Jaeger for activity spans
- Verify parse_document_activity span exists
**Success:** Activity spans in Jaeger

### TEST 8: Trace correlation with workflow IDs
**Purpose:** Verify traces tagged with workflow IDs
**Test Method:**
- Start workflow with known ID
- Search Jaeger by workflow ID
- Verify trace found
**Success:** Workflow ID in trace attributes

### TEST 9: HTTP auto-instrumentation working
**Purpose:** Verify httpx auto-instrumentation
**Test Method:**
- Trigger HTTP request (OpenAI API call)
- Query Jaeger for HTTP span
- Verify span includes method, URL, status
**Success:** HTTP spans captured

### TEST 10: Database auto-instrumentation working
**Purpose:** Verify asyncpg auto-instrumentation
**Test Method:**
- Trigger database write
- Query Jaeger for PostgreSQL span
- Verify span includes query
**Success:** Database spans captured

---

## Test Execution

### Run All Tests
```bash
cd apex-memory-system

# All search attribute tests
pytest tests/integration/test_search_attributes.py -v

# All polling workflow tests
pytest tests/integration/test_polling_workflow.py -v

# All OpenTelemetry tests
pytest tests/integration/test_opentelemetry.py -v

# All 35 tests
pytest tests/integration/test_search_attributes.py tests/integration/test_polling_workflow.py tests/integration/test_opentelemetry.py -v
```

### Verify Baseline
```bash
# Ensure existing tests still pass
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/test_search_attributes.py --ignore=tests/integration/test_polling_workflow.py --ignore=tests/integration/test_opentelemetry.py -v

# Expected: 121 Enhanced Saga baseline tests pass
```

---

## Success Criteria

✅ **35/35 tests passing** (10 + 15 + 10)
✅ **121/121 baseline tests still passing**
✅ **Total: 156 tests passing** (35 new + 121 baseline)

✅ Search attributes functional in Temporal UI
✅ Polling workflows operational
✅ OpenTelemetry traces in Jaeger

✅ Zero breaking changes to existing workflows
✅ All features optional (configurable)

---

## Test Infrastructure Requirements

**Services Required:**
- Temporal Server (localhost:7233)
- Temporal UI (localhost:8088)
- Jaeger (localhost:16686) - Section 16 only
- Neo4j (localhost:7474)
- PostgreSQL (localhost:5432)
- Qdrant (localhost:6333)
- Redis (localhost:6379)

**Pytest Markers:**
```python
@pytest.mark.integration  # Integration tests (real services)
@pytest.mark.asyncio      # Async test support
```

**Test Fixtures:**
```python
@pytest.fixture
async def temporal_client():
    """Temporal client for tests."""
    client = await Client.connect("localhost:7233")
    yield client
    await client.close()
```

---

**Testing Strategy Version:** 1.0
**Created:** 2025-10-20
**Status:** Ready for Implementation
