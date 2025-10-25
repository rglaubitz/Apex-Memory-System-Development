# TEMPORAL DEPLOYMENT VALIDATION PROCEDURES

**Version:** 1.0
**Last Updated:** 2025-10-18
**Owner:** Apex Infrastructure Team

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Pre-Deployment Validation](#pre-deployment-validation)
3. [Test Execution Procedures](#test-execution-procedures)
4. [Validation Script Usage](#validation-script-usage)
5. [Performance Benchmarking](#performance-benchmarking)
6. [Metrics Validation](#metrics-validation)
7. [Alert Validation](#alert-validation)
8. [Troubleshooting](#troubleshooting)
9. [Sign-off Checklist](#sign-off-checklist)

---

## OVERVIEW

This document provides comprehensive procedures for validating the Temporal.io integration for the Apex Memory System. Use these procedures to ensure deployment readiness before going to production.

**Target Audience:**
- DevOps Engineers
- QA Engineers
- Site Reliability Engineers
- System Administrators

**Validation Scope:**
- ✅ All 4 databases (Neo4j, PostgreSQL, Qdrant, Redis)
- ✅ Temporal server and worker
- ✅ Monitoring infrastructure (Prometheus, Grafana)
- ✅ All 27 Temporal metrics
- ✅ All 12 alerts
- ✅ End-to-end workflow execution
- ✅ Load testing (100 concurrent workflows)
- ✅ Performance benchmarking

---

## PRE-DEPLOYMENT VALIDATION

### Prerequisites Checklist

**Before running any validation, ensure:**

- [ ] All services running:
  - [ ] Temporal server (localhost:7233)
  - [ ] Temporal UI (http://localhost:8088)
  - [ ] Neo4j (localhost:7474)
  - [ ] PostgreSQL (localhost:5432)
  - [ ] Qdrant (localhost:6333)
  - [ ] Redis (localhost:6379)
  - [ ] Prometheus (http://localhost:9090)
  - [ ] Grafana (http://localhost:3001)

- [ ] Environment configured:
  - [ ] Python 3.11+ installed
  - [ ] Virtual environment activated
  - [ ] All dependencies installed (`pip install -r requirements.txt`)
  - [ ] `.env` file configured
  - [ ] OpenAI API key set

- [ ] Infrastructure healthy:
  - [ ] Docker containers running (`docker ps`)
  - [ ] Network connectivity verified
  - [ ] Disk space available (>10GB)
  - [ ] CPU/memory resources sufficient

### Quick Health Check

Run the comprehensive health check script:

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Run health check
./scripts/temporal/health-check-comprehensive.sh
```

**Expected Output:**
```
✅ ALL CHECKS PASSED - DEPLOYMENT HEALTHY
```

**If any checks fail:**
1. Review error messages
2. Check service logs
3. Verify configuration
4. See [Troubleshooting](#troubleshooting) section

---

## TEST EXECUTION PROCEDURES

### Test Suite Overview

| Test Suite | File | Tests | Purpose |
|------------|------|-------|---------|
| Integration | `test_temporal_ingestion_workflow.py` | 6 | End-to-end with real DBs |
| Load (Mocked) | `test_temporal_workflow_performance.py` | 5 | Temporal performance |
| Load (Real DBs) | `test_temporal_ingestion_integration.py` | 5 | Full system load |
| Metrics | `test_temporal_metrics_recording.py` | 8 | Metrics validation |
| Alerts | `test_temporal_alerts.py` | 13 | Alert rules validation |

**Total:** 37 tests

---

### 1. Integration Tests

**Purpose:** Validate end-to-end workflow with real database writes

**Prerequisites:**
- All databases running
- Temporal server running
- S3 configured (or localstack)
- OpenAI API key configured

**Execution:**

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Run all integration tests
pytest tests/integration/test_temporal_ingestion_workflow.py -v -m integration

# Run specific test
pytest tests/integration/test_temporal_ingestion_workflow.py::test_full_ingestion_workflow -v
```

**Expected Results:**
- ✅ `test_full_ingestion_workflow` - PASS (full pipeline with real DBs)
- ⚠️  `test_ingestion_rollback_on_failure` - SKIPPED (requires failure injection)
- ✅ `test_ingestion_query_status` - PASS (status queries)
- ✅ `test_ingestion_with_different_sources` - PASS (multi-source)
- ✅ `test_ingestion_concurrent_status_queries` - PASS (concurrent queries)
- ✅ `test_ingestion_metrics_recording` - PASS (metrics recorded)

**Pass Criteria:** At least 5/6 tests passing (1 test skipped is acceptable)

---

### 2. Load Tests - Temporal Performance (Mocked DBs)

**Purpose:** Measure Temporal orchestration overhead (no real DB writes)

**Prerequisites:**
- Temporal server running
- Worker running (or started by test)

**Execution:**

```bash
# Run load tests with mocked DBs
pytest tests/load/test_temporal_workflow_performance.py -v -m load

# Run specific test
pytest tests/load/test_temporal_workflow_performance.py::test_100_concurrent_workflows -v
```

**Expected Results:**
- ✅ `test_100_concurrent_workflows` - PASS (100 workflows in parallel)
- ✅ `test_workflow_scheduling_latency` - PASS (P99 < 500ms)
- ✅ `test_worker_task_queue_handling` - PASS (queue handled)
- ⚠️  `test_activity_retry_under_load` - SKIPPED (requires custom workflow)
- ✅ `test_workflow_throughput` - PASS (>10 workflows/sec)

**Pass Criteria:**
- At least 4/5 tests passing
- 100 concurrent workflows complete successfully
- P99 latency < 5 seconds
- Throughput > 10 workflows/sec

---

### 3. Load Tests - Full Integration (Real DBs)

**Purpose:** Validate system performance with real database writes

**Prerequisites:**
- All databases running with sufficient capacity
- Temporal server and worker running
- S3 configured
- OpenAI API key configured

**Execution:**

```bash
# Run load tests with real DBs (takes longer!)
pytest tests/load/test_temporal_ingestion_integration.py -v -m "load and integration"

# Run specific test
pytest tests/load/test_temporal_ingestion_integration.py::test_concurrent_ingestion_real_databases -v
```

**Expected Results:**
- ✅ `test_concurrent_ingestion_real_databases` - PASS (50 concurrent with real DBs)
- ✅ `test_saga_under_load` - PASS (Enhanced Saga stable)
- ✅ `test_database_write_concurrency` - PASS (all 4 DBs)
- ✅ `test_end_to_end_latency` - PASS (P90 < 20s)
- ✅ `test_sustained_throughput_real_db` - PASS (10+ docs/min)

**Pass Criteria:**
- All 5/5 tests passing
- 50 concurrent workflows with real DBs succeed
- P90 latency < 20 seconds
- P99 latency < 30 seconds
- Throughput >= 10 docs/min
- Enhanced Saga baseline (121/121 tests) still passing

---

### 4. Metrics Validation

**Purpose:** Verify all 27 Temporal metrics are recording correctly

**Prerequisites:**
- Prometheus running
- Temporal server exposing metrics (localhost:8077)
- Worker exposing metrics (localhost:8078)
- Apex API exposing metrics (localhost:8000)
- At least one workflow executed (generates metrics)

**Execution:**

```bash
# Run metrics validation tests
pytest tests/integration/test_temporal_metrics_recording.py -v -m integration
```

**Expected Results:**
- ✅ `test_all_27_metrics_recording` - PASS (20+ metrics found)
- ✅ `test_workflow_metrics` - PASS (5 workflow metrics)
- ✅ `test_activity_metrics` - PASS (5 activity metrics)
- ✅ `test_data_quality_metrics` - PASS (6 data quality metrics)
- ✅ `test_infrastructure_metrics` - PASS (5 infrastructure metrics)
- ✅ `test_business_metrics` - PASS (4+ business metrics)
- ✅ `test_metrics_labels` - PASS (no label explosion)
- ✅ `test_metrics_prometheus_scraping` - PASS (all endpoints accessible)

**Pass Criteria:**
- All 8/8 tests passing
- At least 20/27 metrics discoverable
- At least 15/27 metrics have data
- No label explosion (cardinality < 100)
- All 3 metrics endpoints accessible

---

### 5. Alert Validation

**Purpose:** Verify all 12 alert rules are loaded and functional

**Prerequisites:**
- Prometheus running
- Alert rules loaded from `monitoring/alerts/rules.yml`

**Execution:**

```bash
# Run alert validation tests
pytest tests/integration/test_temporal_alerts.py -v -m alerts

# Run just alert rules validation
pytest tests/integration/test_temporal_alerts.py::test_alert_rules_loaded -v
```

**Expected Results:**
- ✅ `test_alert_rules_loaded` - PASS (all 12 alerts loaded)
- ⚠️  Other tests - PARTIAL/SKIPPED (metric recording validated, not actual alert firing)

**Pass Criteria:**
- `test_alert_rules_loaded` passes
- All 12 alert rules found in Prometheus
- Alert group `temporal_workflows` exists
- Alert syntax valid

**12 Alerts Validated:**
1. TemporalWorkflowFailureRateHigh
2. TemporalActivityRetryRateHigh
3. TemporalWorkerTaskSlotsExhausted
4. TemporalTaskQueueBacklog
5. TemporalZeroChunksExtracted
6. TemporalZeroEntitiesExtracted
7. TemporalSagaRollbackRateHigh
8. TemporalS3DownloadFailureRate
9. TemporalEmbeddingFailureRate
10. TemporalDatabaseWriteFailure
11. TemporalWorkflowDurationP99High
12. TemporalIngestionThroughputZero

---

## VALIDATION SCRIPT USAGE

### validate-deployment.py

**Purpose:** Comprehensive deployment validation (all services, metrics, test workflow)

**Usage:**

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Full validation (includes test workflow)
python scripts/temporal/validate-deployment.py

# Quick validation (skip test workflow)
python scripts/temporal/validate-deployment.py --quick

# JSON output (for CI/CD)
python scripts/temporal/validate-deployment.py --json
```

**Output Example:**

```
🔍 CRITICAL CHECKS
✓ Temporal Server: Connected successfully to localhost:7233
✓ Neo4j Database: Neo4j is accessible
✓ PostgreSQL Database: PostgreSQL is accessible
✓ Qdrant Database: Qdrant is accessible
✓ Redis Database: Redis is accessible

🔍 SERVICE CHECKS
✓ Prometheus: Prometheus is running on localhost:9090
✓ Grafana Dashboard: Grafana running with 1 Temporal dashboard(s)
✓ Metrics Endpoints: All 3 metrics endpoints accessible

🔍 MONITORING CHECKS
✓ Metrics Data: 6/6 key metrics have data
✓ Alert Rules: Alert rules loaded: 12 Temporal alerts

🔍 FUNCTIONALITY CHECKS
✓ Test Workflow: Test workflow executed successfully

============================================================
VALIDATION SUMMARY
============================================================

Total checks: 12
Passed: 12
Failed: 0

✅ ALL CHECKS PASSED - DEPLOYMENT HEALTHY
```

**Exit Codes:**
- `0` = All checks passed
- `1` = One or more checks failed
- `2` = Critical failure (Temporal server down, databases unreachable)

---

### health-check-comprehensive.sh

**Purpose:** Rapid health validation (for CI/CD pipelines)

**Usage:**

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Run health check
./scripts/temporal/health-check-comprehensive.sh

# Quiet mode (only errors)
./scripts/temporal/health-check-comprehensive.sh -q

# JSON output
./scripts/temporal/health-check-comprehensive.sh --json
```

**Output Example:**

```
🔍 Checking Temporal Server
✓ Temporal UI accessible at http://localhost:8088
✓ Temporal server metrics available

🔍 Checking Worker Process
✓ Worker process is running
✓ Worker SDK metrics available

🔍 Checking Database Connectivity
✓ Neo4j accessible (localhost:7474)
✓ PostgreSQL accessible (localhost:5432)
✓ Qdrant accessible (localhost:6333)
✓ Redis accessible (localhost:6379)

🔍 Checking Metrics Endpoints
✓ Prometheus accessible (http://localhost:9090)
✓ Apex API metrics available

🔍 Checking Recent Workflow Executions
✓ Recent workflow activity detected (5.2 workflows in last 5 min)

🔍 Checking Current Error Rate
✓ Error rate is acceptable (0.00% < 5%)

SUMMARY

Total checks: 14
Passed: 14
Failed: 0

✅ ALL CHECKS PASSED - DEPLOYMENT HEALTHY
```

---

## PERFORMANCE BENCHMARKING

### benchmark-ingestion.py

**Purpose:** Measure ingestion performance and track over time

**Usage:**

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system

# Basic benchmark (10 documents)
python scripts/temporal/benchmark-ingestion.py

# Benchmark with 50 documents
python scripts/temporal/benchmark-ingestion.py --count 50

# Benchmark different sizes
python scripts/temporal/benchmark-ingestion.py --sizes small,medium,large --count 30

# Export results for baseline
python scripts/temporal/benchmark-ingestion.py --export baseline-$(date +%Y%m%d).json

# Compare against baseline
python scripts/temporal/benchmark-ingestion.py --baseline baseline-20251018.json
```

**Output Example:**

```
============================================================
TEMPORAL INGESTION PERFORMANCE BENCHMARK
============================================================

📊 Configuration:
   Document count: 50
   Document sizes: medium

🚀 Starting benchmark...

📏 Benchmarking medium documents...
   ✓ benchmark-medium-0: 3.45s
   ✓ benchmark-medium-1: 3.52s
   ✓ benchmark-medium-2: 3.41s
   ...

============================================================
BENCHMARK RESULTS
============================================================

📈 Overall Statistics:
   Total workflows: 50
   Successful: 50

⏱️  Latency Statistics:
   P50: 3.48s
   P90: 3.89s
   P99: 4.12s
   Mean: 3.52s ± 0.15s
   Min: 3.21s
   Max: 4.15s

🔥 Throughput:
   34.23 documents/minute
   0.57 documents/second

🎯 Performance Targets:
   ✓ P90 latency < 10s: 3.89 seconds (target: 10 seconds)
   ✓ P99 latency < 20s: 4.12 seconds (target: 20 seconds)
   ✓ Throughput >= 10 docs/min: 34.23 docs/min (target: 10 docs/min)
```

**Performance Targets:**
- ✅ P50 latency < 5s
- ✅ P90 latency < 10s
- ✅ P99 latency < 20s
- ✅ Throughput >= 10 docs/min

**Baseline Establishment:**

```bash
# First run - establish baseline
python scripts/temporal/benchmark-ingestion.py --count 50 --export baseline-initial.json

# Later runs - compare against baseline
python scripts/temporal/benchmark-ingestion.py --count 50 --baseline baseline-initial.json
```

---

## METRICS VALIDATION

### Prometheus Query Validation

**Verify Key Metrics:**

```bash
# Query Prometheus for workflow metrics
curl -s "http://localhost:9090/api/v1/query?query=apex_temporal_workflow_started_total" | jq .

# Query for activity metrics
curl -s "http://localhost:9090/api/v1/query?query=apex_temporal_activity_completed_total" | jq .

# Query for data quality metrics
curl -s "http://localhost:9090/api/v1/query?query=apex_temporal_chunks_per_document" | jq .
```

### Grafana Dashboard Validation

**Access Dashboard:**

1. Open http://localhost:3001
2. Login: `admin` / `apexmemory2024`
3. Navigate to "Temporal Ingestion" dashboard
4. Verify all 33 panels showing data

**Dashboard Panels to Verify:**
- Workflow success rate (last 5m)
- Workflows in progress
- Workflow throughput
- Activity duration by step
- Chunks per document (data quality)
- Entities per document (data quality)
- Worker task slots
- Database writes by database

---

## ALERT VALIDATION

### Manual Alert Triggering (Optional)

**Trigger Test Alerts:**

```python
# Trigger zero chunks alert
from apex_memory.monitoring.metrics import temporal_chunks_per_document

for _ in range(100):
    temporal_chunks_per_document.observe(0)
```

**Monitor Alert Status:**

```bash
# Check active alerts in Prometheus
curl -s "http://localhost:9090/api/v1/alerts" | jq '.data.alerts[] | select(.labels.alertname | contains("Temporal"))'
```

**Alert Testing Best Practices:**
- ⚠️  DO NOT trigger alerts in production
- ✅ Test in development/staging environment only
- ✅ Document alert thresholds
- ✅ Validate alert notifications reach correct channels

---

## TROUBLESHOOTING

### Common Issues

#### 1. Temporal Server Not Running

**Symptoms:**
```
✗ Temporal Server: Cannot connect to Temporal: ConnectionRefusedError
```

**Solution:**
```bash
# Start Temporal via Docker Compose
cd docker
docker-compose up -d temporal
docker-compose up -d temporal-ui

# Verify
curl http://localhost:8088
```

---

#### 2. Databases Not Accessible

**Symptoms:**
```
✗ Neo4j Database: Neo4j not accessible
✗ PostgreSQL Database: PostgreSQL not accessible
```

**Solution:**
```bash
# Check database containers
docker ps | grep -E "neo4j|postgres|qdrant|redis"

# Start databases
cd docker
docker-compose up -d neo4j postgres qdrant redis

# Verify connectivity
# Neo4j
curl http://localhost:7474

# PostgreSQL
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT 1"

# Qdrant
curl http://localhost:6333/collections

# Redis
redis-cli ping
```

---

#### 3. Metrics Not Available

**Symptoms:**
```
⚠️  Metrics Data: Only 5/27 metrics have data
```

**Solution:**
```bash
# Run a test workflow to generate metrics
python scripts/temporal/benchmark-ingestion.py --count 5

# Verify metrics endpoints
curl http://localhost:8077/metrics  # Temporal server
curl http://localhost:8078/metrics  # Temporal SDK
curl http://localhost:8000/metrics  # Apex API

# Check Prometheus scraping
curl http://localhost:9090/api/v1/targets
```

---

#### 4. Worker Not Running

**Symptoms:**
```
⚠️  Worker process not found (dev_worker.py)
⚠️  Worker SDK metrics not available
```

**Solution:**
```bash
# Start worker manually
cd /Users/richardglaubitz/Projects/apex-memory-system
python -m apex_memory.temporal.workers.dev_worker

# Or check if worker should be started by supervisor/systemd
```

---

#### 5. Test Failures

**Symptoms:**
```
FAILED tests/integration/test_temporal_ingestion_workflow.py::test_full_ingestion_workflow
```

**Debug Steps:**
1. Check test logs for specific error
2. Verify all prerequisites met
3. Check Temporal UI for workflow errors: http://localhost:8088
4. Review service logs
5. Run individual test with verbose output: `pytest <test> -vv -s`

---

## SIGN-OFF CHECKLIST

### Pre-Production Deployment Validation

**Complete ALL items before production deployment:**

#### Infrastructure
- [ ] All services running and healthy
- [ ] `health-check-comprehensive.sh` returns 0 (all checks passed)
- [ ] `validate-deployment.py` returns 0 (all checks passed)
- [ ] Disk space sufficient (>10GB available)
- [ ] Network connectivity verified

#### Testing
- [ ] Integration tests: 5/6 passing (test_temporal_ingestion_workflow.py)
- [ ] Load tests (mocked): 4/5 passing (test_temporal_workflow_performance.py)
- [ ] Load tests (real DBs): 5/5 passing (test_temporal_ingestion_integration.py)
- [ ] Metrics validation: 8/8 passing (test_temporal_metrics_recording.py)
- [ ] Alert validation: test_alert_rules_loaded passing
- [ ] Enhanced Saga baseline: 121/121 tests still passing

#### Performance
- [ ] Benchmark executed: `benchmark-ingestion.py --count 50`
- [ ] P90 latency < 10 seconds (with real DBs)
- [ ] P99 latency < 20 seconds (with real DBs)
- [ ] Throughput >= 10 docs/min
- [ ] Baseline established and documented

#### Monitoring
- [ ] All 27 metrics recording (at least 20/27 discoverable)
- [ ] Grafana dashboard accessible and showing data
- [ ] All 12 alert rules loaded in Prometheus
- [ ] Alert notification channels configured
- [ ] Runbooks created for all alerts

#### Documentation
- [ ] Validation procedures reviewed (this document)
- [ ] Runbooks completed
- [ ] Team trained on validation procedures
- [ ] Rollback procedures documented
- [ ] On-call procedures updated

---

**Sign-Off:**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| QA Engineer | __________ | __________ | __________ |
| DevOps Engineer | __________ | __________ | __________ |
| SRE | __________ | __________ | __________ |
| Tech Lead | __________ | __________ | __________ |

---

**Validation Complete:** ☐

**Approved for Production:** ☐

**Date:** __________
