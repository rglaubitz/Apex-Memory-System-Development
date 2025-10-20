# Advanced Temporal Features

**Complete observability and operational enhancements for Temporal.io workflows**

## 🎯 Overview

This upgrade implements 3 critical advanced features for the Temporal implementation:

1. **Search Attributes** - Find workflows by source, priority, document ID, or status in Temporal UI
2. **Polling Workflows** - Periodic API polling with continue-as-new pattern for non-webhook integrations
3. **OpenTelemetry** - Distributed tracing for complete observability (metrics + logs + traces)

**Status:** 📝 Ready for Implementation
**Timeline:** 7-8 hours (3 sections)
**Test Coverage:** 35 tests planned

---

## 📚 Documentation Suite

This folder contains 6 comprehensive documents:

### 1. **README.md** (this file)
- Quick start guide
- Overview and goals
- Section summary

### 2. **[IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md)** (~2,500 lines)
- Complete step-by-step implementation for all 3 sections
- Code examples and file locations
- Testing procedures
- Success criteria

### 3. **[PROGRESS.md](PROGRESS.md)**
- Real-time progress tracking
- Deliverables status
- Test results
- Next steps

### 4. **[TESTING.MD](TESTING.md)**
- 35 test specifications across 3 sections
- Test categories (integration, unit)
- Success metrics

### 5. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
- Common issues and solutions
- Debugging procedures
- Production incident response

### 6. **[RESEARCH-REFERENCES.md](RESEARCH-REFERENCES.md)**
- Complete bibliography
- Official documentation links
- Internal ADRs

---

## 🚀 Quick Start

### Prerequisites

✅ **Sections 1-10 complete** (Temporal foundation + testing infrastructure)
✅ **graphiti-json-integration complete** (DocumentIngestionWorkflow + StructuredDataIngestionWorkflow)
✅ **All services running:**
- Temporal Server (localhost:7233)
- Temporal UI (localhost:8088)
- Neo4j (localhost:7474)
- PostgreSQL (localhost:5432)
- Qdrant (localhost:6333)
- Redis (localhost:6379)

---

### Implementation Order

**Follow this sequence for optimal dependency management:**

#### **Section 14: Search Attributes** (2 hours) ✅ START HERE
- Enables workflow searchability in Temporal UI
- **Prerequisite for Section 16** (OpenTelemetry benefits from searchable traces)
- Quick operational win

#### **Section 12: Polling Workflows** (3 hours)
- Independent of other sections (can implement in parallel)
- Enables periodic API polling for Samsara, Turvo, custom APIs
- Business capability for non-webhook integrations

#### **Section 16: OpenTelemetry** (3 hours)
- **Requires Section 14** (search attributes enhance trace correlation)
- Adds distributed tracing for complete observability
- Final observability layer (metrics + logs + traces)

---

## 📋 What You'll Build

### Section 14: Search Attributes (2 hours)

**Deliverables:**
- Configuration script: `scripts/temporal/configure-search-attributes.sh`
- 4 search attributes: Source, Priority, DocumentId, Status
- Updated DocumentIngestionWorkflow with attribute tagging
- Updated StructuredDataIngestionWorkflow with attribute tagging
- Search query examples: `examples/search/search-workflows.py`
- 10 integration tests

**Benefits:**
- Find workflows by source: `Source='frontapp'`
- Find specific documents: `DocumentId='doc-abc-123'`
- Filter by priority: `Priority>=3`
- Track workflow status: `Status='failed'`
- Combined queries: `Source='turvo' AND Priority=3`

**Before:** Search by workflow ID only (e.g., `ingest-doc-abc-123`)
**After:** Search by any custom attribute (source, document, priority, status)

---

### Section 12: Polling Workflows (3 hours)

**Deliverables:**
- PollingWorkflow: `src/apex_memory/temporal/workflows/polling.py`
- Polling activity: `src/apex_memory/temporal/activities/polling.py`
- Worker registration updates: `src/apex_memory/temporal/workers/dev_worker.py`
- Polling examples: `examples/polling/start-polling-workflow.py`
- 15 integration tests

**Features:**
- Configurable polling interval (default: 15 minutes)
- Continue-as-new after 100 iterations (prevents unbounded history)
- Child workflow spawning for each fetched record
- Support for Samsara, Turvo, and custom API endpoints
- Statistics query (iteration count, records processed)

**Use Cases:**
- Poll Samsara API for new GPS events every 15 minutes
- Fetch Turvo shipment updates hourly
- Periodic data sync from external systems without webhook support

---

### Section 16: OpenTelemetry (3 hours)

**Deliverables:**
- Telemetry configuration: `src/apex_memory/config/telemetry.py`
- Settings updates: `ENABLE_OPENTELEMETRY`, `OTLP_ENDPOINT`
- Jaeger Docker service: `docker/docker-compose.yml`
- Workflow/activity instrumentation (manual spans)
- Auto-instrumentation (httpx, asyncpg)
- 10 integration tests

**Observability Stack:**
```
Before:  Prometheus (metrics) + Grafana (dashboards) + Logs
After:   + OpenTelemetry (traces) + Jaeger (trace UI)
Result:  Complete observability (metrics + logs + traces)
```

**Benefits:**
- Visualize end-to-end workflow execution
- Trace activity execution across workers
- Correlate traces with workflow IDs
- Debug performance bottlenecks
- Service dependency maps

**Jaeger UI:** http://localhost:16686

---

## 🧪 Testing Summary

**Total Tests:** 35 tests across 3 sections

| Section | Tests | Category |
|---------|-------|----------|
| Search Attributes | 10 | Integration |
| Polling Workflows | 15 | Integration |
| OpenTelemetry | 10 | Integration |

**All tests created during implementation with step-by-step instructions in IMPLEMENTATION-PLAN.md**

---

## 📊 Success Criteria

### Section 14: Search Attributes
✅ Configuration script runs without errors
✅ 4 search attributes registered (Source, Priority, DocumentId, Status)
✅ Both workflows tagged with attributes
✅ Status updates as workflows progress
✅ Search queries work in Temporal UI
✅ All 10 tests passing

### Section 12: Polling Workflows
✅ PollingWorkflow runs indefinitely
✅ Continue-as-new after 100 iterations
✅ Child workflows spawned for each record
✅ Polling interval configurable
✅ Statistics query returns accurate data
✅ All 15 tests passing

### Section 16: OpenTelemetry
✅ OpenTelemetry dependencies installed
✅ OTLP exporter configured
✅ Jaeger running and accessible
✅ Workflows instrumented with spans
✅ Traces visible in Jaeger UI
✅ All 10 tests passing

---

## 🔗 Related Documentation

**Previous Work:**
- [PROJECT-STATUS-SNAPSHOT.md](../PROJECT-STATUS-SNAPSHOT.md) - Sections 1-10 complete
- [graphiti-json-integration/](../graphiti-json-integration/) - Completed upgrade
- [EXECUTION-ROADMAP.md](../EXECUTION-ROADMAP.md) - Original 17-section plan

**Reference Documents:**
- [EXECUTION-ROADMAP.md](../EXECUTION-ROADMAP.md) - Sections 12, 14, 16 original specs
- [tests/STRUCTURE.md](../tests/STRUCTURE.md) - Test organization
- [PROJECT-STATUS-SNAPSHOT.md](../PROJECT-STATUS-SNAPSHOT.md) - Current state (82% complete)

---

## 💡 Why These Sections?

### Why Search Attributes (Section 14)?
**Problem:** Finding workflows in Temporal UI requires knowing exact workflow IDs
**Solution:** Search by source, document, priority, or status
**Value:** Better debugging, faster incident response, improved operational visibility

### Why Polling Workflows (Section 12)?
**Problem:** Some integrations don't support webhooks (Samsara, legacy systems)
**Solution:** Periodic polling with continue-as-new pattern
**Value:** Enables new business capabilities, completes integration options

### Why OpenTelemetry (Section 16)?
**Problem:** Metrics and logs don't show end-to-end request flow
**Solution:** Distributed tracing with trace correlation
**Value:** Complete observability stack, better debugging, performance optimization

---

## 🛠️ Development Workflow

### Step 1: Read Documentation
```bash
# Review implementation plan
cat IMPLEMENTATION-PLAN.md

# Review testing strategy
cat TESTING.md
```

### Step 2: Execute Section 14 (2 hours)
```bash
# Follow IMPLEMENTATION-PLAN.md Section 14

# 1. Create configuration script
./scripts/temporal/configure-search-attributes.sh

# 2. Update workflows (DocumentIngestionWorkflow, StructuredDataIngestionWorkflow)
# 3. Create search examples
# 4. Run tests
pytest tests/integration/test_search_attributes.py -v
```

### Step 3: Execute Section 12 (3 hours)
```bash
# Follow IMPLEMENTATION-PLAN.md Section 12

# 1. Create polling activity
# 2. Implement PollingWorkflow
# 3. Update worker registration
# 4. Start polling workflow
python examples/polling/start-polling-workflow.py --source samsara --interval 15

# 5. Run tests
pytest tests/integration/test_polling_workflow.py -v
```

### Step 4: Execute Section 16 (3 hours)
```bash
# Follow IMPLEMENTATION-PLAN.md Section 16

# 1. Install OpenTelemetry dependencies
pip install -r requirements.txt

# 2. Start Jaeger
cd docker && docker-compose up -d jaeger

# 3. Configure telemetry
# 4. Instrument workflows
# 5. View traces
open http://localhost:16686

# 6. Run tests
pytest tests/integration/test_opentelemetry.py -v
```

---

## 📈 Monitoring & Observability

### Current Observability (Sections 1-10)
- ✅ 27 Temporal metrics (Prometheus)
- ✅ 33-panel Grafana dashboard
- ✅ 12 critical alerts
- ✅ Structured logging (JSON)

### After This Upgrade
- ✅ Search attributes (Temporal UI)
- ✅ Distributed tracing (Jaeger)
- ✅ Trace correlation with metrics
- ✅ Complete observability stack

**Full Stack:**
```
Metrics:  Prometheus → Grafana (27 metrics, 33 panels)
Logs:     Structured JSON → CloudWatch/Splunk
Traces:   OpenTelemetry → Jaeger (distributed tracing)
Search:   Temporal UI (custom search attributes)
```

---

## 🚨 Known Limitations

### Section 14: Search Attributes
- Search attribute cardinality limits (Temporal restriction)
- No retroactive tagging (only new workflows)
- Search attribute types immutable after creation

### Section 12: Polling Workflows
- Polling interval minimum: 1 minute (Temporal sleep limitation)
- Continue-as-new has brief downtime (milliseconds)
- Child workflow spawning limited by worker concurrency

### Section 16: OpenTelemetry
- Local development uses insecure OTLP (production should use TLS)
- Trace sampling may be needed for high-volume systems
- Manual instrumentation required for custom spans

---

## 📞 Getting Help

**Documentation:**
- Start with this README
- Review IMPLEMENTATION-PLAN.md for step-by-step guide
- Check TROUBLESHOOTING.md for common issues
- See RESEARCH-REFERENCES.md for official docs

**Debugging Tools:**
- Temporal UI: http://localhost:8088
- Jaeger UI: http://localhost:16686 (after Section 16)
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090

**Test Validation:**
```bash
# Run all new tests
pytest tests/integration/test_search_attributes.py -v
pytest tests/integration/test_polling_workflow.py -v
pytest tests/integration/test_opentelemetry.py -v

# Verify baseline (should still pass)
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v
```

---

## ✅ Completion Checklist

### Section 14: Search Attributes
- [ ] Configuration script created and executed
- [ ] 4 search attributes registered
- [ ] DocumentIngestionWorkflow updated
- [ ] StructuredDataIngestionWorkflow updated
- [ ] Search examples created
- [ ] 10 tests passing

### Section 12: Polling Workflows
- [ ] Polling activity implemented
- [ ] PollingWorkflow created
- [ ] Worker registration updated
- [ ] Polling examples created
- [ ] 15 tests passing

### Section 16: OpenTelemetry
- [ ] Dependencies installed
- [ ] Telemetry configuration created
- [ ] Jaeger running
- [ ] Workflows instrumented
- [ ] Traces visible in Jaeger UI
- [ ] 10 tests passing

### Overall Completion
- [ ] All 35 tests passing
- [ ] Documentation updated
- [ ] Baseline tests still passing (121/121)
- [ ] Production-ready for deployment

---

**Status:** 📝 Ready for Implementation
**Next Step:** Begin Section 14 (Search Attributes - 2 hours)

For detailed implementation instructions, see **[IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md)**.
