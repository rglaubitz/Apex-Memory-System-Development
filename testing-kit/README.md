# Apex Memory System - Testing Kit

**Purpose:** Pre-deployment validation to ensure system readiness
**Status:** Active
**Last Updated:** 2025-10-20

---

## Overview

The Testing Kit provides comprehensive validation of the Apex Memory System before deployment. It tests all 6 architectural layers bottom-up, validates integration points, and provides a clear GO/NO-GO deployment decision.

## What This Kit Tests

✅ **Layer 1:** Database Writers (PostgreSQL, Neo4j, Qdrant, Redis)
✅ **Layer 2:** Services (Enhanced Saga, Graphiti, Parsers, Embeddings)
✅ **Layer 3:** Temporal Activities (9 activities)
✅ **Layer 4:** Workflows (DocumentIngestion + StructuredDataIngestion)
✅ **Layer 5:** API Endpoints (REST interface)
✅ **Layer 6:** Query Router (Intent classification, caching)
✅ **Integration:** Cross-layer connections
✅ **Load & Chaos:** Stress testing and failure scenarios

## Time Estimates

| Testing Path | Duration | Description |
|-------------|----------|-------------|
| **Quick Validation** | 1 hour | Critical path only (Pre-flight + Enhanced Saga + E2E workflows) |
| **Comprehensive** | 3-4 hours | All layers + integration + load testing |
| **Full Suite** | 5-6 hours | Comprehensive + chaos testing + detailed troubleshooting |

## Documentation

### 🚀 Start Here

**[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Step-by-step execution guide

This is your primary guide. Follow it sequentially to:
1. Validate prerequisites
2. Run pre-flight checks
3. Test each layer systematically
4. Record results
5. Make GO/NO-GO decision

### 📚 Reference Materials

**[TESTING-KIT.md](TESTING-KIT.md)** - Comprehensive testing reference

Detailed documentation covering:
- Testing strategy and philosophy
- All test commands with expected outputs
- Known issues and gotchas
- Debugging procedures
- Deployment readiness checklist
- Quick reference commands

### 📝 Results Recording

**[results/RESULTS-TEMPLATE.md](results/RESULTS-TEMPLATE.md)** - Test results template

Use this to record:
- Pre-flight validation results
- Layer-by-layer test outcomes
- Performance metrics
- Integration test results
- Final GO/NO-GO decision

## Quick Start

**Prerequisites:**
- All services running (PostgreSQL, Neo4j, Qdrant, Redis, Temporal, Worker, API)
- Environment configured (`.env` file)
- Testing environment (Python 3.11+, pytest, curl)

**For Experienced Users (1 hour):**

```bash
# 1. Pre-flight checks
cd apex-memory-system
docker ps | grep -E "postgres|neo4j|qdrant|redis"
temporal server health
curl http://localhost:8000/api/v1/health

# 2. Critical baseline (Enhanced Saga)
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v
# Expected: 121/121 passing

# 3. Integration tests
pytest tests/integration/ -v -m integration

# 4. API smoke test
echo "Test" > /tmp/test.txt
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/test.txt" \
  -F "source=api"

# 5. Check metrics
open http://localhost:3001/d/temporal-ingestion

# 6. Make GO/NO-GO decision
# See IMPLEMENTATION.md "Deployment Decision" section
```

**For First-Time Users (3-4 hours):**

Follow [IMPLEMENTATION.md](IMPLEMENTATION.md) step-by-step from beginning to end.

## What You'll Know After Testing

After completing this testing kit, you'll have definitive answers to:

### System Health
- ✅/❌ Each of 4 databases independently writable
- ✅/❌ Enhanced Saga pattern (121 tests) still working
- ✅/❌ All 9 Temporal activities executing correctly
- ✅/❌ Both workflows completing E2E successfully
- ✅/❌ API endpoints functional
- ✅/❌ Query router classifying intents accurately

### Integration
- ✅/❌ API → Temporal workflow triggering
- ✅/❌ Saga → 4 databases parallel writes
- ✅/❌ Graphiti → Neo4j entity storage
- ✅/❌ Redis → Distributed locking and caching

### Performance
- **Actual vs. Target Metrics:**
  - Query latency (target: <1s P90)
  - Cache hit rate (target: >60%)
  - Throughput (target: 10+ docs/sec)
  - Workflow duration (target: <60s)

### Known Issues
- Which of 7 known issues affect your deployment
- Exact failure points with debugging procedures
- Resource leaks (staging files, Graphiti episodes, Redis locks)

### Deployment Readiness
- **Clear GO/NO-GO decision** based on concrete criteria
- Confidence level (HIGH/MEDIUM/LOW)
- Risk assessment
- Blockers identified with fix procedures

## Critical Success Criteria

### ✅ GO FOR DEPLOYMENT

**ALL of these must be true:**
- Enhanced Saga: 121/121 tests passing
- All databases: Healthy and connectable
- Workflows: Both E2E workflows succeeding
- API: All endpoints responding correctly
- Metrics: Recording in Prometheus
- Zero critical errors in logs

### ❌ NO-GO - DO NOT DEPLOY

**If ANY of these are true:**
- Enhanced Saga tests failing (data integrity risk)
- Any database unreachable (system won't function)
- Workflows not completing E2E (ingestion broken)
- Graphiti extraction failing (accuracy <90%)
- Metrics not recording (no observability)

## File Structure

```
testing-kit/
├── README.md                    # This file (entry point)
├── IMPLEMENTATION.md            # Step-by-step execution guide ⭐
├── TESTING-KIT.md              # Comprehensive reference
├── scripts/                    # Helper scripts (optional)
│   ├── pre-flight-check.sh
│   ├── run-all-tests.sh
│   └── deployment-checklist.sh
└── results/                    # Test results storage
    ├── .gitkeep
    └── RESULTS-TEMPLATE.md     # Results recording template
```

## Testing Approach

### Bottom-Up Strategy

We test from the foundation up:

**Layer 1: Database Writers** → Test each DB independently
**Layer 2: Services** → Test business logic (Enhanced Saga critical!)
**Layer 3: Activities** → Test Temporal activity execution
**Layer 4: Workflows** → Test complete orchestration
**Layer 5: API** → Test REST interface
**Layer 6: Query Router** → Test intent classification

**Why?** If Layer 1 fails, everything else will fail. Fix foundation first.

### Test Categories

1. **Unit Tests** - Individual functions/classes (mocked dependencies)
2. **Integration Tests** - Component interactions (real dependencies)
3. **E2E Tests** - Full workflows (API → Temporal → Databases)
4. **Load Tests** - Concurrent operations (10+ docs/sec)
5. **Chaos Tests** - Failure scenarios (DB down, network partitions)

## Key Documents

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **README.md** | Overview and quick start | Starting point, understand scope |
| **IMPLEMENTATION.md** | Step-by-step execution | Running tests sequentially |
| **TESTING-KIT.md** | Detailed reference | Debugging, troubleshooting, commands |
| **RESULTS-TEMPLATE.md** | Results recording | During testing, record outcomes |

## Common Questions

### Q: How long does comprehensive testing take?

**A:** 3-4 hours for all layers + integration. 1 hour for quick validation (critical path only).

### Q: Can I skip layers if I'm confident they work?

**A:** Not recommended. Each layer builds on previous layers. Skipping risks missing integration failures.

### Q: What if Enhanced Saga tests fail?

**A:** **STOP immediately.** Saga pattern protects data integrity. Deployment is a NO-GO until all 121 tests pass.

### Q: Can I run tests in production?

**A:** **NO.** This testing kit is for pre-production environments only. Never run against production databases.

### Q: What if only load tests fail?

**A:** Load tests are **optional**. You can deploy if critical tests pass, but monitor performance closely.

### Q: How do I record results?

**A:** Use `results/RESULTS-TEMPLATE.md` to check off each test and record metrics.

## Getting Help

**If tests fail:**
1. Check [IMPLEMENTATION.md](IMPLEMENTATION.md) "Troubleshooting" section
2. Check [TESTING-KIT.md](TESTING-KIT.md) "Known Issues & Gotchas"
3. Review [TESTING-KIT.md](TESTING-KIT.md) "Debugging Procedures"

**For system architecture questions:**
- See `../SYSTEM-MANUAL.html` (visual component manual)
- See `../apex-memory-system/CLAUDE.md` (development guide)
- See `../apex-memory-system/README.md` (project overview)

**For deployment questions:**
- See [TESTING-KIT.md](TESTING-KIT.md) "Deployment Readiness Checklist"
- See [IMPLEMENTATION.md](IMPLEMENTATION.md) "Deployment Decision"

## Next Steps

1. **Read IMPLEMENTATION.md** - Understand the testing process
2. **Prepare environment** - Ensure all services running
3. **Run pre-flight validation** - Verify infrastructure healthy
4. **Execute layer-by-layer tests** - Follow IMPLEMENTATION.md sequentially
5. **Record results** - Use RESULTS-TEMPLATE.md
6. **Make GO/NO-GO decision** - Based on concrete criteria
7. **Deploy or fix issues** - Proceed based on decision

---

## Ready to Begin?

👉 **Start with [IMPLEMENTATION.md](IMPLEMENTATION.md)**

Follow the step-by-step guide to validate your system is ready for deployment.

---

**Last Updated:** 2025-10-20
**Version:** 1.0
**Status:** Active
