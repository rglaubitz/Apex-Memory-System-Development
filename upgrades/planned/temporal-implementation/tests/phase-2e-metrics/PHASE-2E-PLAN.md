# Phase 2E: Metrics Validation

**Date:** October 18, 2025
**Session:** Section 11 Testing - Phase 2E
**Status:** 🚧 IN PROGRESS

---

## 📋 Overview

**Phase 2E validates that all Temporal metrics are being collected, scraped by Prometheus, and displayed in Grafana.**

Unlike Phase 2C/2D (workflow execution), Phase 2E validates observability infrastructure.

**Goal:** Ensure complete visibility into Temporal workflow execution through metrics.

---

## 🎯 Objectives

### 1. Metrics Collection Validation
- ✅ Verify all 26 Temporal metrics are defined
- ⏳ Verify metrics are instrumented in activities
- ⏳ Verify metrics increment when workflows execute
- ⏳ Verify metrics have correct labels

### 2. Prometheus Scraping Validation
- ⏳ Verify Prometheus can scrape metrics endpoint
- ⏳ Verify all metrics appear in Prometheus
- ⏳ Verify metric values update in real-time
- ⏳ Verify no stale metrics

### 3. Grafana Dashboard Validation
- ⏳ Verify all 33 dashboard panels query correct metrics
- ⏳ Verify panels display data correctly
- ⏳ Verify time ranges work (Last 15m, 1h, 6h, 24h)
- ⏳ Verify variable substitution works

---

## 📊 26 Temporal Metrics to Validate

### Workflow Metrics (5)
1. `apex_temporal_workflow_started_total` - Counter
2. `apex_temporal_workflow_completed_total` - Counter (labels: workflow_type, status)
3. `apex_temporal_workflow_duration_seconds` - Histogram
4. `apex_temporal_workflow_in_progress` - Gauge
5. `apex_temporal_workflow_retries_total` - Counter

### Activity Metrics (5)
6. `apex_temporal_activity_started_total` - Counter
7. `apex_temporal_activity_completed_total` - Counter (labels: activity_name, status)
8. `apex_temporal_activity_duration_seconds` - Histogram
9. `apex_temporal_activity_retry_count` - Counter
10. `apex_temporal_activity_failure_reasons` - Counter

### Data Quality Metrics (6)
11. `apex_temporal_chunks_per_document` - Histogram
12. `apex_temporal_entities_per_document` - Histogram
13. `apex_temporal_entities_by_type` - Counter
14. `apex_temporal_embeddings_per_document` - Histogram
15. `apex_temporal_databases_written` - Counter (labels: database, status)
16. `apex_temporal_saga_rollback_triggered` - Counter

### Infrastructure Metrics (5)
17. `apex_temporal_worker_task_slots_available` - Gauge
18. `apex_temporal_worker_task_slots_used` - Gauge
19. `apex_temporal_task_queue_depth` - Gauge
20. `apex_temporal_workflow_task_latency_seconds` - Histogram
21. `apex_temporal_worker_poll_success` - Counter

### Business Metrics (5)
22. `apex_temporal_documents_by_source` - Counter
23. `apex_temporal_document_size_bytes` - Histogram
24. `apex_temporal_s3_download_duration_seconds` - Histogram
25. `apex_temporal_ingestion_throughput_per_minute` - Gauge
26. `apex_temporal_relationships_total` - Counter

---

## 🧪 Test Strategy

### Test 1: Metrics Definition Validation
**Goal:** Verify all metrics are defined in metrics.py

**Approach:**
```python
def test_all_temporal_metrics_defined():
    """Verify all 26 Temporal metrics are defined in metrics.py"""
    expected_metrics = [
        "apex_temporal_workflow_started_total",
        "apex_temporal_workflow_completed_total",
        # ... all 26 metrics
    ]

    # Read metrics.py and verify each metric is defined
    for metric in expected_metrics:
        assert metric in metrics_module, f"Missing metric: {metric}"
```

### Test 2: Metrics Instrumentation Validation
**Goal:** Verify metrics are instrumented in activities

**Approach:**
```python
def test_activities_instrumented():
    """Verify all 5 activities record metrics"""
    activities = [
        "download_from_s3_activity",
        "parse_document_activity",
        "extract_entities_activity",
        "generate_embeddings_activity",
        "write_to_databases_activity",
    ]

    # Check that each activity imports and uses metrics
    for activity in activities:
        source = read_activity_source(activity)
        assert "temporal_activity_started_total" in source
        assert "temporal_activity_completed_total" in source
        assert "temporal_activity_duration_seconds" in source
```

### Test 3: Metrics Increment Validation
**Goal:** Verify metrics increment when workflows execute

**Approach:**
```python
def test_metrics_increment_on_workflow_execution():
    """Run workflow and verify metrics increment"""
    # Get baseline metric values
    baseline = fetch_prometheus_metrics()

    # Run a single DocumentIngestionWorkflow
    run_test_workflow()

    # Get updated metric values
    updated = fetch_prometheus_metrics()

    # Verify increments
    assert updated["apex_temporal_workflow_started_total"] > baseline
    assert updated["apex_temporal_workflow_completed_total"] > baseline
    assert updated["apex_temporal_activity_started_total"] > baseline
    # ... etc
```

### Test 4: Prometheus Scraping Validation
**Goal:** Verify Prometheus can scrape metrics endpoint

**Approach:**
```python
def test_prometheus_scraping():
    """Verify Prometheus scrapes metrics successfully"""
    # Query Prometheus for Temporal metrics
    response = requests.get("http://localhost:9090/api/v1/query", params={
        "query": "apex_temporal_workflow_started_total"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["result"]) > 0
```

### Test 5: Grafana Dashboard Validation
**Goal:** Verify Grafana dashboard panels work

**Approach:**
```python
def test_grafana_dashboard_panels():
    """Verify all 33 Grafana panels query successfully"""
    dashboard = load_dashboard("/monitoring/dashboards/temporal-ingestion.json")

    for panel in dashboard["panels"]:
        # Execute panel query against Prometheus
        query = panel["targets"][0]["expr"]
        response = execute_prometheus_query(query)

        # Verify query succeeds
        assert response["status"] == "success"

        # Verify data returned (after workflows have run)
        assert len(response["data"]["result"]) > 0
```

### Test 6: Metric Label Validation
**Goal:** Verify metrics have correct labels

**Approach:**
```python
def test_metric_labels():
    """Verify metrics have expected labels"""
    # Run test workflow
    run_test_workflow()

    # Verify workflow_type label
    workflow_started = fetch_metric("apex_temporal_workflow_started_total")
    assert "workflow_type" in workflow_started.labels
    assert "DocumentIngestionWorkflow" in workflow_started.labels["workflow_type"]

    # Verify activity_name label
    activity_started = fetch_metric("apex_temporal_activity_started_total")
    assert "activity_name" in activity_started.labels
    assert "parse_document_activity" in activity_started.labels["activity_name"]
```

### Test 7: Histogram Bucket Validation
**Goal:** Verify histogram metrics have correct buckets

**Approach:**
```python
def test_histogram_buckets():
    """Verify histograms have appropriate buckets"""
    # Check workflow duration buckets
    workflow_duration = fetch_metric("apex_temporal_workflow_duration_seconds")
    expected_buckets = [0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
    assert workflow_duration.buckets == expected_buckets

    # Check activity duration buckets
    activity_duration = fetch_metric("apex_temporal_activity_duration_seconds")
    expected_buckets = [0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
    assert activity_duration.buckets == expected_buckets
```

### Test 8: Metrics Endpoint Availability
**Goal:** Verify /metrics endpoint is accessible

**Approach:**
```python
def test_metrics_endpoint():
    """Verify /metrics endpoint returns Prometheus metrics"""
    response = requests.get("http://localhost:8000/metrics")

    assert response.status_code == 200
    assert "apex_temporal_workflow_started_total" in response.text
    assert "# HELP apex_temporal_workflow_started_total" in response.text
    assert "# TYPE apex_temporal_workflow_started_total counter" in response.text
```

---

## 🧰 Test Infrastructure Requirements

**Services:**
- ✅ Temporal server (port 7233)
- ✅ Temporal worker (dev_worker.py)
- ✅ Prometheus (port 9090)
- ✅ Grafana (port 3001)
- ✅ All 4 databases (Neo4j, PostgreSQL, Qdrant, Redis)
- ✅ LocalStack S3 (port 4566)
- ✅ API server with /metrics endpoint (port 8000)

**Test Dependencies:**
```bash
pip install requests prometheus-api-client
```

---

## 📁 Test Files to Create

1. **test_metrics_definition.py**
   - Validate all 26 metrics are defined
   - Validate metric types (Counter, Gauge, Histogram)
   - Validate metric labels

2. **test_metrics_instrumentation.py**
   - Validate activities use metrics
   - Validate workflow uses metrics
   - Validate API uses metrics

3. **test_prometheus_integration.py**
   - Validate Prometheus scraping
   - Validate metric values increment
   - Validate time-series data

4. **test_grafana_dashboard.py**
   - Validate all 33 panels
   - Validate panel queries
   - Validate data sources

5. **test_metrics_e2e.py**
   - End-to-end test: run workflow, verify all metrics update
   - Validate metric correctness (values match expected behavior)

---

## 🎯 Success Criteria

**Phase 2E passes if:**
- ✅ All 26 Temporal metrics are defined
- ✅ All 5 activities are instrumented
- ✅ Metrics increment correctly when workflows run
- ✅ Prometheus scrapes metrics successfully
- ✅ All 33 Grafana panels query successfully
- ✅ Histogram buckets are appropriate for expected values
- ✅ Metric labels are correct and useful
- ✅ /metrics endpoint is accessible

---

## 🔮 Future Considerations

**Metrics to Add (Future):**
- Alert rule firing metrics
- Grafana dashboard view counts
- Metric cardinality (label combinations)
- Metric export latency

**Testing Enhancements (Future):**
- Load test with high cardinality (many workflows)
- Test metric retention (Prometheus storage)
- Test metric aggregation (rate, sum, avg)
- Test alert evaluation based on metrics

---

**Phase 2E Status:** 🚧 IN PROGRESS
**Estimated Duration:** 1-2 hours
**Dependencies:** Phase 2D complete (all infrastructure running)

---

**Last Updated:** October 18, 2025
**Next Review:** After test implementation
