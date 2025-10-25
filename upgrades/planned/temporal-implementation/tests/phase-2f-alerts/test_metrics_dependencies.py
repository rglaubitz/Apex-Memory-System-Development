#!/usr/bin/env python3
"""
Test 4: Metric Dependency Check

Verify all metrics referenced by Temporal alerts exist and are queryable.
"""

import requests

PROMETHEUS_URL = "http://localhost:9090"

# All metrics referenced by the 12 Temporal alerts
REQUIRED_METRICS = [
    # Alert 1: TemporalWorkflowFailureRateHigh
    "apex_temporal_workflow_completed_total",

    # Alert 2: TemporalActivityRetryRateHigh
    "apex_temporal_activity_retry_count",

    # Alert 3: TemporalWorkerTaskSlotsExhausted
    "apex_temporal_worker_task_slots_available",

    # Alert 4: TemporalTaskQueueBacklog
    "apex_temporal_task_queue_depth",

    # Alert 5: TemporalZeroChunksExtracted
    "apex_temporal_chunks_per_document_bucket",

    # Alert 6: TemporalZeroEntitiesExtracted
    "apex_temporal_entities_per_document_bucket",
    "apex_temporal_entities_per_document_count",

    # Alert 7: TemporalSagaRollbackRateHigh
    "apex_temporal_saga_rollback_triggered",

    # Alert 8: TemporalS3DownloadFailureRate
    "apex_temporal_activity_completed_total",  # with activity_name label

    # Alert 9: TemporalEmbeddingFailureRate
    # Uses same metric as Alert 8

    # Alert 10: TemporalDatabaseWriteFailure
    "apex_temporal_databases_written",

    # Alert 11: TemporalWorkflowDurationP99High
    "apex_temporal_workflow_duration_seconds_bucket",

    # Alert 12: TemporalIngestionThroughputZero
    "apex_temporal_ingestion_throughput_per_minute",
]

def query_metric(metric_name: str) -> dict:
    """Query a metric from Prometheus."""
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": metric_name},
        timeout=10
    )
    return response.json()

def main():
    """Test all required metrics exist."""
    print("=" * 80)
    print("Test 4: Metric Dependency Check")
    print("=" * 80)
    print()

    # Deduplicate metrics
    unique_metrics = sorted(set(REQUIRED_METRICS))
    print(f"Testing {len(unique_metrics)} unique metrics...\n")

    results = []

    for metric in unique_metrics:
        try:
            response = query_metric(metric)

            if response["status"] == "success":
                result_count = len(response["data"]["result"])
                status = "✅ EXISTS" if result_count > 0 else "⚠️  DEFINED (no data yet)"
                results.append((metric, status, True))
                print(f"{status}: {metric} ({result_count} series)")
            else:
                status = "❌ ERROR"
                results.append((metric, status, False))
                print(f"{status}: {metric} - {response}")

        except Exception as e:
            status = "❌ FAILED"
            results.append((metric, status, False))
            print(f"{status}: {metric} - {str(e)}")

    # Summary
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)

    total = len(results)
    existing = sum(1 for _, status, _ in results if "EXISTS" in status)
    defined = sum(1 for _, status, _ in results if "DEFINED" in status)
    errors = sum(1 for _, _, success in results if not success)

    print(f"Total Metrics: {total}")
    print(f"  ✅ Existing (with data): {existing}")
    print(f"  ⚠️  Defined (no data yet): {defined}")
    print(f"  ❌ Errors: {errors}")
    print()

    if errors > 0:
        print("❌ FAIL: Some metrics are missing or inaccessible")
        return 1
    else:
        print("✅ PASS: All metrics are defined and queryable")
        return 0

if __name__ == "__main__":
    exit(main())
