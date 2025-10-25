# Phase 2F: Alert Validation - Test Plan

**Date:** October 18, 2025
**Phase:** Section 11 Testing - Phase 2F
**Status:** 🚀 IN PROGRESS

---

## 📋 Phase Objectives

**Goal:** Validate that all 12 Temporal alerts are correctly configured, can trigger when conditions are met, and integrate properly with Prometheus.

**Success Criteria:**
1. ✅ Prometheus successfully scrapes worker metrics endpoint (port 9091)
2. ✅ All 12 Temporal alert rules are syntactically valid
3. ✅ Alert rules reference existing metrics
4. ✅ Alert conditions can be evaluated by Prometheus
5. ✅ Documentation exists for each alert (runbook URLs)

---

## 🎯 12 Temporal Alerts to Validate

### Critical Alerts (8)

| # | Alert Name | Metric | Condition | Severity | Component |
|---|------------|--------|-----------|----------|-----------|
| 1 | `TemporalWorkflowFailureRateHigh` | `apex_temporal_workflow_completed_total` | > 5% failed | critical | temporal_ingestion |
| 2 | `TemporalWorkerTaskSlotsExhausted` | `apex_temporal_worker_task_slots_available` | == 0 | critical | temporal_worker |
| 3 | `TemporalSagaRollbackRateHigh` | `apex_temporal_saga_rollback_triggered` | > 2% | critical | temporal_databases |
| 4 | `TemporalDatabaseWriteFailure` | `apex_temporal_databases_written` | > 1% failed | critical | temporal_databases |
| 5 | `TemporalIngestionThroughputZero` | `apex_temporal_ingestion_throughput_per_minute` | == 0 for 15m | critical | temporal_worker |

### Warning Alerts (7)

| # | Alert Name | Metric | Condition | Severity | Component |
|---|------------|--------|-----------|----------|-----------|
| 6 | `TemporalActivityRetryRateHigh` | `apex_temporal_activity_retry_count` | > 10% | warning | temporal_ingestion |
| 7 | `TemporalTaskQueueBacklog` | `apex_temporal_task_queue_depth` | > 1000 | warning | temporal_worker |
| 8 | `TemporalZeroChunksExtracted` | `apex_temporal_chunks_per_document_bucket` | > 0.1 docs/sec with 0 chunks | warning | temporal_data_quality |
| 9 | `TemporalZeroEntitiesExtracted` | `apex_temporal_entities_per_document_bucket` | > 50% with 0 entities | warning | temporal_data_quality |
| 10 | `TemporalS3DownloadFailureRate` | `apex_temporal_activity_completed_total{activity_name="download_from_s3_activity"}` | > 5% failed | warning | temporal_s3 |
| 11 | `TemporalEmbeddingFailureRate` | `apex_temporal_activity_completed_total{activity_name="generate_embeddings_activity"}` | > 10% failed | warning | temporal_openai |
| 12 | `TemporalWorkflowDurationP99High` | `apex_temporal_workflow_duration_seconds_bucket` | P99 > 5 min | warning | temporal_performance |

---

## 🧪 Test Strategy

### Test 1: Prometheus Worker Scraping

**Objective:** Verify Prometheus can scrape worker metrics endpoint

**Test Steps:**
1. Check Prometheus targets page (http://localhost:9090/targets)
2. Verify worker endpoint is configured and UP
3. Query worker metrics via Prometheus
4. Validate metrics appear with correct labels

**Expected Result:**
- Worker endpoint (localhost:9091) shows as "UP" in Prometheus
- Temporal metrics queryable via Prometheus API
- Metrics have correct labels (activity_name, status, etc.)

**Test Command:**
```bash
# Check Prometheus can reach worker
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="apex-temporal-worker")'

# Query worker metrics via Prometheus
curl 'http://localhost:9090/api/v1/query?query=apex_temporal_activity_started_total'
```

### Test 2: Alert Rule Syntax Validation

**Objective:** Verify all alert rules are syntactically valid

**Test Steps:**
1. Use Prometheus promtool to validate rules.yml
2. Check for syntax errors
3. Verify all referenced metrics exist

**Expected Result:**
- `promtool check rules` passes with 0 errors
- All 12 Temporal alerts are valid

**Test Command:**
```bash
promtool check rules /path/to/monitoring/alerts/rules.yml
```

### Test 3: Alert Rule Evaluation

**Objective:** Verify Prometheus can evaluate alert conditions

**Test Steps:**
1. Check Prometheus alerts page (http://localhost:9090/alerts)
2. Verify all 12 Temporal alerts are loaded
3. Check alert evaluation state (inactive/pending/firing)
4. Verify alert metadata (severity, component, annotations)

**Expected Result:**
- All 12 alerts appear in Prometheus UI
- Alerts show as "Inactive" (no conditions met)
- Alert metadata displays correctly

### Test 4: Metric Dependency Check

**Objective:** Verify all metrics referenced by alerts exist

**Test Steps:**
1. Extract all metrics from alert rules
2. Query each metric via Prometheus
3. Verify metrics are defined and accessible

**Expected Result:**
- All metrics referenced by alerts are defined
- Metrics return data (or empty result if not populated)
- No "unknown metric" errors

**Metrics to Check:**
- `apex_temporal_workflow_completed_total`
- `apex_temporal_activity_retry_count`
- `apex_temporal_worker_task_slots_available`
- `apex_temporal_task_queue_depth`
- `apex_temporal_chunks_per_document_bucket`
- `apex_temporal_entities_per_document_bucket`
- `apex_temporal_saga_rollback_triggered`
- `apex_temporal_databases_written`
- `apex_temporal_activity_completed_total` (with activity_name labels)
- `apex_temporal_workflow_duration_seconds_bucket`
- `apex_temporal_ingestion_throughput_per_minute`

### Test 5: Alert Annotation Validation

**Objective:** Verify all alerts have proper documentation

**Test Steps:**
1. Check each alert has `summary` annotation
2. Check each alert has `description` annotation
3. Verify runbook URLs are present
4. Validate severity and component labels

**Expected Result:**
- All 12 alerts have summary and description
- All 12 alerts have runbook URLs
- Severity labels are correct (critical/warning)
- Component labels are descriptive

### Test 6: Prometheus Configuration Check

**Objective:** Verify Prometheus is configured to scrape worker endpoint

**Test Steps:**
1. Check Prometheus configuration
2. Verify worker scrape job exists
3. Validate scrape interval and timeout

**Expected Config:**
```yaml
scrape_configs:
  - job_name: 'apex-api'
    static_configs:
      - targets: ['localhost:8000']

  - job_name: 'apex-temporal-worker'
    static_configs:
      - targets: ['localhost:9091']
```

### Test 7: Alert Triggering Test (Optional)

**Objective:** Trigger a test alert to verify end-to-end alerting

**Test Steps:**
1. Stop Temporal worker
2. Wait 15+ minutes
3. Verify `TemporalIngestionThroughputZero` alert fires
4. Restart worker
5. Verify alert clears

**Note:** This test is optional as it requires stopping production services.

---

## 📊 Test Execution Plan

### Phase 2F.1: Prometheus Integration (30 min)

1. ✅ Check Prometheus configuration
2. ✅ Verify worker endpoint scraping
3. ✅ Query worker metrics via Prometheus
4. ✅ Validate metrics with correct labels

### Phase 2F.2: Alert Rule Validation (15 min)

1. ✅ Validate alert syntax with promtool
2. ✅ Check Prometheus alerts page
3. ✅ Verify all 12 alerts loaded
4. ✅ Check alert metadata

### Phase 2F.3: Metric Dependency Check (15 min)

1. ✅ Extract metrics from alert rules
2. ✅ Query each metric via Prometheus
3. ✅ Document any missing metrics
4. ✅ Verify metric labels match alert queries

### Phase 2F.4: Documentation Validation (10 min)

1. ✅ Verify alert annotations
2. ✅ Check runbook URLs
3. ✅ Validate severity levels
4. ✅ Check component labels

---

## ✅ Success Criteria

**Phase 2F is complete when:**

1. ✅ Prometheus successfully scrapes worker endpoint (port 9091)
2. ✅ All 12 Temporal alerts pass syntax validation
3. ✅ All alerts appear in Prometheus UI
4. ✅ All metrics referenced by alerts exist and are queryable
5. ✅ All alerts have complete documentation (summary, description, runbook)
6. ✅ Alert severity and component labels are correct
7. ✅ Test results documented

---

## 🚨 Known Limitations

### Limitation #1: Alert Triggering Requires Real Failures

**Issue:** Can't easily trigger alerts without causing real failures.

**Workaround:** Validate alert configuration and metrics, but don't require triggering all alerts.

**Tests to Skip:**
- Actually triggering workflow failures
- Simulating worker capacity exhaustion
- Triggering saga rollbacks

**What We CAN Test:**
- Alert rules are valid
- Metrics exist
- Prometheus can evaluate conditions
- Alert metadata is complete

### Limitation #2: Runbook URLs Don't Exist Yet

**Issue:** Runbook URLs point to non-existent docs (e.g., `https://docs.apex-memory.com/runbooks/...`)

**Impact:** Low - runbooks are documentation, not functional

**Resolution:** Document this as tech debt, create runbooks in future phase

---

## 📂 Test Artifacts

**Files to Create:**
1. `test_prometheus_integration.py` - Prometheus scraping tests
2. `test_alert_validation.py` - Alert syntax and metadata tests
3. `test_metrics_dependencies.py` - Metric existence checks
4. `RUN_TESTS.sh` - Test execution script
5. `PHASE-2F-RESULTS.md` - Test results summary
6. `INDEX.md` - Phase overview

---

## 🎯 Expected Timeline

**Total Estimated Time:** 1-2 hours

- Phase 2F.1 (Prometheus Integration): 30 minutes
- Phase 2F.2 (Alert Validation): 15 minutes
- Phase 2F.3 (Metric Dependencies): 15 minutes
- Phase 2F.4 (Documentation): 10 minutes
- Documentation: 20 minutes

---

**Last Updated:** October 18, 2025
**Status:** Ready to execute
**Next Step:** Test 1 - Prometheus Worker Scraping
