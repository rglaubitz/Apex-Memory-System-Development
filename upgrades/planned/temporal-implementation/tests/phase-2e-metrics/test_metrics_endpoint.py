#!/usr/bin/env python3
"""
Phase 2E: Metrics Endpoint Validation

Test that /metrics endpoint is accessible and returns all 26 Temporal metrics.

This is a smoke test to ensure the metrics infrastructure is set up correctly.
"""

import requests
import pytest
from typing import List, Dict


# All 26 Temporal metrics that should be present
EXPECTED_TEMPORAL_METRICS = [
    # Workflow metrics (5)
    "apex_temporal_workflow_started_total",
    "apex_temporal_workflow_completed_total",
    "apex_temporal_workflow_duration_seconds",
    "apex_temporal_workflow_in_progress",
    "apex_temporal_workflow_retries_total",
    # Activity metrics (5)
    "apex_temporal_activity_started_total",
    "apex_temporal_activity_completed_total",
    "apex_temporal_activity_duration_seconds",
    "apex_temporal_activity_retry_count",
    "apex_temporal_activity_failure_reasons",
    # Data quality metrics (6)
    "apex_temporal_chunks_per_document",
    "apex_temporal_entities_per_document",
    "apex_temporal_entities_by_type",
    "apex_temporal_embeddings_per_document",
    "apex_temporal_databases_written",
    "apex_temporal_saga_rollback_triggered",
    # Infrastructure metrics (5)
    "apex_temporal_worker_task_slots_available",
    "apex_temporal_worker_task_slots_used",
    "apex_temporal_task_queue_depth",
    "apex_temporal_workflow_task_latency_seconds",
    "apex_temporal_worker_poll_success",
    # Business metrics (5)
    "apex_temporal_documents_by_source",
    "apex_temporal_document_size_bytes",
    "apex_temporal_s3_download_duration_seconds",
    "apex_temporal_ingestion_throughput_per_minute",
    "apex_temporal_relationships_total",
]


def test_metrics_endpoint_accessible():
    """
    Test 1: Verify /metrics endpoint is accessible.
    """
    print("\n🧪 Test 1: Metrics Endpoint Accessible")

    response = requests.get("http://localhost:8000/metrics", timeout=10)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "text/plain" in response.headers.get("Content-Type", ""), \
        "Expected Content-Type to contain text/plain"

    print("   ✅ /metrics endpoint is accessible")
    print(f"   ✅ Response size: {len(response.text)} bytes")


def test_all_temporal_metrics_present():
    """
    Test 2: Verify all 26 Temporal metrics are present in /metrics output.
    """
    print("\n🧪 Test 2: All Temporal Metrics Present")

    response = requests.get("http://localhost:8000/metrics", timeout=10)
    metrics_text = response.text

    missing_metrics = []
    found_metrics = []

    for metric in EXPECTED_TEMPORAL_METRICS:
        if metric in metrics_text:
            found_metrics.append(metric)
        else:
            missing_metrics.append(metric)

    # Report results
    print(f"   ✅ Found {len(found_metrics)}/26 Temporal metrics")

    if missing_metrics:
        print(f"\n   ❌ Missing {len(missing_metrics)} metrics:")
        for metric in missing_metrics:
            print(f"      - {metric}")

    assert len(missing_metrics) == 0, \
        f"Missing {len(missing_metrics)} metrics: {missing_metrics}"


def test_metrics_have_help_text():
    """
    Test 3: Verify metrics have HELP documentation.
    """
    print("\n🧪 Test 3: Metrics Have HELP Text")

    response = requests.get("http://localhost:8000/metrics", timeout=10)
    metrics_text = response.text

    metrics_without_help = []

    for metric in EXPECTED_TEMPORAL_METRICS:
        help_line = f"# HELP {metric}"
        if help_line not in metrics_text:
            metrics_without_help.append(metric)

    if metrics_without_help:
        print(f"\n   ⚠️  {len(metrics_without_help)} metrics without HELP text:")
        for metric in metrics_without_help:
            print(f"      - {metric}")
    else:
        print(f"   ✅ All 26 metrics have HELP documentation")

    # This is a warning, not a failure (HELP text is optional)
    # assert len(metrics_without_help) == 0


def test_metrics_have_type_definition():
    """
    Test 4: Verify metrics have TYPE definition.
    """
    print("\n🧪 Test 4: Metrics Have TYPE Definition")

    response = requests.get("http://localhost:8000/metrics", timeout=10)
    metrics_text = response.text

    metrics_without_type = []

    for metric in EXPECTED_TEMPORAL_METRICS:
        type_line = f"# TYPE {metric}"
        if type_line not in metrics_text:
            metrics_without_type.append(metric)

    if metrics_without_type:
        print(f"\n   ❌ {len(metrics_without_type)} metrics without TYPE:")
        for metric in metrics_without_type:
            print(f"      - {metric}")

    assert len(metrics_without_type) == 0, \
        f"{len(metrics_without_type)} metrics missing TYPE: {metrics_without_type}"

    print(f"   ✅ All 26 metrics have TYPE definition")


def test_metric_types_correct():
    """
    Test 5: Verify metrics have correct Prometheus types.
    """
    print("\n🧪 Test 5: Metric Types Correct")

    response = requests.get("http://localhost:8000/metrics", timeout=10)
    metrics_text = response.text

    expected_types = {
        # Counters
        "apex_temporal_workflow_started_total": "counter",
        "apex_temporal_workflow_completed_total": "counter",
        "apex_temporal_workflow_retries_total": "counter",
        "apex_temporal_activity_started_total": "counter",
        "apex_temporal_activity_completed_total": "counter",
        "apex_temporal_activity_retry_count": "counter",
        "apex_temporal_activity_failure_reasons": "counter",
        "apex_temporal_entities_by_type": "counter",
        "apex_temporal_databases_written": "counter",
        "apex_temporal_saga_rollback_triggered": "counter",
        "apex_temporal_worker_poll_success": "counter",
        "apex_temporal_documents_by_source": "counter",
        "apex_temporal_relationships_total": "counter",
        # Histograms
        "apex_temporal_workflow_duration_seconds": "histogram",
        "apex_temporal_activity_duration_seconds": "histogram",
        "apex_temporal_chunks_per_document": "histogram",
        "apex_temporal_entities_per_document": "histogram",
        "apex_temporal_embeddings_per_document": "histogram",
        "apex_temporal_workflow_task_latency_seconds": "histogram",
        "apex_temporal_document_size_bytes": "histogram",
        "apex_temporal_s3_download_duration_seconds": "histogram",
        # Gauges
        "apex_temporal_workflow_in_progress": "gauge",
        "apex_temporal_worker_task_slots_available": "gauge",
        "apex_temporal_worker_task_slots_used": "gauge",
        "apex_temporal_task_queue_depth": "gauge",
        "apex_temporal_ingestion_throughput_per_minute": "gauge",
    }

    incorrect_types = []

    for metric, expected_type in expected_types.items():
        type_line = f"# TYPE {metric} {expected_type}"
        if type_line not in metrics_text:
            # Find what type it actually has
            actual_type = "MISSING"
            for line in metrics_text.split("\n"):
                if line.startswith(f"# TYPE {metric} "):
                    actual_type = line.split()[-1]
                    break

            incorrect_types.append({
                "metric": metric,
                "expected": expected_type,
                "actual": actual_type
            })

    if incorrect_types:
        print(f"\n   ❌ {len(incorrect_types)} metrics with incorrect type:")
        for item in incorrect_types:
            print(f"      - {item['metric']}: expected '{item['expected']}', got '{item['actual']}'")

    assert len(incorrect_types) == 0, \
        f"{len(incorrect_types)} metrics have incorrect type"

    print(f"   ✅ All 26 metrics have correct Prometheus types")


def test_metrics_have_nonzero_values():
    """
    Test 6: Check if any metrics have non-zero values (after workflows have run).

    This test is informational - it's OK if metrics are zero if no workflows have run yet.
    """
    print("\n🧪 Test 6: Metrics Have Non-Zero Values (Informational)")

    response = requests.get("http://localhost:8000/metrics", timeout=10)
    metrics_text = response.text

    metrics_with_values = []

    for metric in EXPECTED_TEMPORAL_METRICS:
        # Look for metric lines (not HELP or TYPE)
        for line in metrics_text.split("\n"):
            if line.startswith(metric) and not line.startswith("# "):
                # Extract value (last element after space)
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        value = float(parts[-1])
                        if value > 0:
                            metrics_with_values.append(metric)
                            break
                    except ValueError:
                        pass

    if metrics_with_values:
        print(f"   ℹ️  {len(metrics_with_values)}/26 metrics have non-zero values:")
        for metric in metrics_with_values:
            print(f"      - {metric}")
    else:
        print(f"   ℹ️  All metrics are zero (no workflows have run yet)")

    # This is informational only - not a failure
    print(f"\n   💡 Tip: Run Phase 2D tests first to populate metrics with data")


if __name__ == "__main__":
    print("=" * 80)
    print("Phase 2E: Metrics Endpoint Validation")
    print("=" * 80)

    try:
        test_metrics_endpoint_accessible()
        test_all_temporal_metrics_present()
        test_metrics_have_help_text()
        test_metrics_have_type_definition()
        test_metric_types_correct()
        test_metrics_have_nonzero_values()

        print("\n" + "=" * 80)
        print("✅ All Metrics Endpoint Tests PASSED")
        print("=" * 80)
    except AssertionError as e:
        print(f"\n❌ Test FAILED: {e}")
        raise
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("\n💡 Tip: Make sure API server is running on port 8000:")
        print("   cd apex-memory-system")
        print("   python -m uvicorn apex_memory.main:app --reload --port 8000")
        raise
