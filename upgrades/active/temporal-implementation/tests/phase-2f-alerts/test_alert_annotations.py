#!/usr/bin/env python3
"""
Test 5: Alert Annotation Validation

Verify all Temporal alerts have complete documentation (summary, description, runbook).
"""

import requests

PROMETHEUS_URL = "http://localhost:9090"

REQUIRED_ANNOTATIONS = ["summary", "description", "runbook_url"]
REQUIRED_LABELS = ["severity", "component"]

def get_temporal_alerts() -> list:
    """Get all Temporal-specific alerts from Prometheus."""
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/rules?type=alert",
        timeout=10
    )
    data = response.json()

    groups = data.get("data", {}).get("groups", [])
    temporal_group = [g for g in groups if g["name"] == "temporal_workflows"][0]

    # Filter to only Temporal-specific alerts
    temporal_alerts = [r for r in temporal_group["rules"] if "Temporal" in r["name"]]

    return temporal_alerts

def main():
    """Test all Temporal alerts have complete annotations."""
    print("=" * 80)
    print("Test 5: Alert Annotation Validation")
    print("=" * 80)
    print()

    alerts = get_temporal_alerts()
    print(f"Validating {len(alerts)} Temporal alerts...\n")

    results = []

    for alert in alerts:
        alert_name = alert["name"]
        annotations = alert.get("annotations", {})
        labels = alert.get("labels", {})

        # Check required annotations
        missing_annotations = [a for a in REQUIRED_ANNOTATIONS if a not in annotations]

        # Check required labels
        missing_labels = [l for l in REQUIRED_LABELS if l not in labels]

        # Check annotation content
        empty_annotations = [
            a for a in REQUIRED_ANNOTATIONS
            if a in annotations and not annotations[a].strip()
        ]

        # Overall status
        if not missing_annotations and not missing_labels and not empty_annotations:
            status = "✅ PASS"
            success = True
        else:
            status = "❌ FAIL"
            success = False

        results.append((alert_name, status, success))

        print(f"{status}: {alert_name}")

        # Print details
        print(f"  Severity: {labels.get('severity', 'MISSING')}")
        print(f"  Component: {labels.get('component', 'MISSING')}")
        print(f"  Summary: {'✅' if 'summary' in annotations else '❌ MISSING'}")
        print(f"  Description: {'✅' if 'description' in annotations else '❌ MISSING'}")
        print(f"  Runbook URL: {'✅' if 'runbook_url' in annotations else '❌ MISSING'}")

        if missing_annotations:
            print(f"  ⚠️  Missing annotations: {', '.join(missing_annotations)}")

        if missing_labels:
            print(f"  ⚠️  Missing labels: {', '.join(missing_labels)}")

        if empty_annotations:
            print(f"  ⚠️  Empty annotations: {', '.join(empty_annotations)}")

        print()

    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)

    total = len(results)
    passed = sum(1 for _, _, success in results if success)
    failed = total - passed

    print(f"Total Alerts: {total}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print()

    if failed > 0:
        print("❌ FAIL: Some alerts have incomplete documentation")
        return 1
    else:
        print("✅ PASS: All alerts have complete documentation")
        return 0

if __name__ == "__main__":
    exit(main())
