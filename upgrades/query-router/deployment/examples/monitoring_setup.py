#!/usr/bin/env python3
"""
Monitoring Setup Script

Sets up monitoring dashboards and alerts for Phase 4 deployment.
Configures Prometheus metrics and Grafana dashboards.
"""

import os
import json
from pathlib import Path


def create_prometheus_rules():
    """Create Prometheus alerting rules for Phase 4."""

    rules = """
groups:
  - name: query_router_phase4
    interval: 30s
    rules:
      # High error rate alert
      - alert: HighErrorRate
        expr: rate(query_router_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      # High latency alert
      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(query_router_latency_seconds_bucket[5m])) > 2.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High query latency (P99)"
          description: "P99 latency is {{ $value }}s"

      # Low cache hit rate
      - alert: LowCacheHitRate
        expr: rate(query_router_cache_hits_total[10m]) / rate(query_router_cache_requests_total[10m]) < 0.70
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Cache hit rate below 70%"
          description: "Hit rate is {{ $value | humanizePercentage }}"

      # Phase 4: Low average reward
      - alert: LowAverageReward
        expr: query_router_online_learning_avg_reward < 0.40
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Online learning avg reward too low"
          description: "Avg reward is {{ $value }}"

      # Phase 4: Feedback queue overflow
      - alert: FeedbackQueueOverflow
        expr: query_router_feedback_queue_size > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Feedback queue backing up"
          description: "Queue size is {{ $value }} items"
"""

    rules_file = Path("docker/prometheus/phase4_rules.yml")
    rules_file.parent.mkdir(parents=True, exist_ok=True)
    rules_file.write_text(rules)

    print(f"✓ Created Prometheus rules: {rules_file}")
    return rules_file


def create_grafana_dashboard():
    """Create Grafana dashboard for Phase 4 monitoring."""

    dashboard = {
        "dashboard": {
            "title": "Query Router - Phase 4 Monitoring",
            "tags": ["query-router", "phase4", "online-learning"],
            "timezone": "browser",
            "panels": [
                # Row 1: Overview
                {
                    "title": "Query Latency (P50, P90, P99)",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'histogram_quantile(0.50, rate(query_router_latency_seconds_bucket[5m]))',
                            "legendFormat": "P50"
                        },
                        {
                            "expr": 'histogram_quantile(0.90, rate(query_router_latency_seconds_bucket[5m]))',
                            "legendFormat": "P90"
                        },
                        {
                            "expr": 'histogram_quantile(0.99, rate(query_router_latency_seconds_bucket[5m]))',
                            "legendFormat": "P99"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                },
                {
                    "title": "Error Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(query_router_errors_total[5m])',
                            "legendFormat": "Error rate"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                },

                # Row 2: Phase 4 Specific
                {
                    "title": "Phase 4 Rollout Percentage",
                    "type": "singlestat",
                    "targets": [
                        {
                            "expr": 'query_router_feature_flag_rollout_percentage{flag="phase4_online_learning"}',
                        }
                    ],
                    "gridPos": {"h": 4, "w": 6, "x": 0, "y": 8}
                },
                {
                    "title": "Online Learning Avg Reward",
                    "type": "gauge",
                    "targets": [
                        {
                            "expr": 'query_router_online_learning_avg_reward',
                        }
                    ],
                    "gridPos": {"h": 4, "w": 6, "x": 6, "y": 8}
                },
                {
                    "title": "Feedback Queue Size",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'query_router_feedback_queue_size',
                        }
                    ],
                    "gridPos": {"h": 4, "w": 12, "x": 12, "y": 8}
                },

                # Row 3: Per-Database Performance
                {
                    "title": "Per-Database Avg Reward",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'query_router_online_learning_db_reward{database="neo4j"}',
                            "legendFormat": "Neo4j"
                        },
                        {
                            "expr": 'query_router_online_learning_db_reward{database="postgres"}',
                            "legendFormat": "PostgreSQL"
                        },
                        {
                            "expr": 'query_router_online_learning_db_reward{database="qdrant"}',
                            "legendFormat": "Qdrant"
                        },
                        {
                            "expr": 'query_router_online_learning_db_reward{database="graphiti"}',
                            "legendFormat": "Graphiti"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 12}
                },

                # Row 4: Cache Performance
                {
                    "title": "Cache Hit Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(query_router_cache_hits_total[5m]) / rate(query_router_cache_requests_total[5m])',
                            "legendFormat": "Hit rate"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 20}
                },
                {
                    "title": "Batch Update Count",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'query_router_batch_updates_total',
                            "legendFormat": "Total updates"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 20}
                }
            ]
        }
    }

    dashboard_file = Path("monitoring/dashboards/phase4-monitoring.json")
    dashboard_file.parent.mkdir(parents=True, exist_ok=True)

    with open(dashboard_file, 'w') as f:
        json.dump(dashboard, f, indent=2)

    print(f"✓ Created Grafana dashboard: {dashboard_file}")
    return dashboard_file


def create_metrics_exporter():
    """Create example metrics exporter for router."""

    exporter_code = '''
"""
Prometheus Metrics Exporter for Phase 4

Add this to your router to export metrics.
"""

from prometheus_client import Counter, Histogram, Gauge

# Query metrics
query_counter = Counter('query_router_queries_total', 'Total queries')
query_errors = Counter('query_router_errors_total', 'Total errors')
query_latency = Histogram('query_router_latency_seconds', 'Query latency')

# Cache metrics
cache_requests = Counter('query_router_cache_requests_total', 'Cache requests')
cache_hits = Counter('query_router_cache_hits_total', 'Cache hits')

# Phase 4: Feature flags
feature_flag_rollout = Gauge(
    'query_router_feature_flag_rollout_percentage',
    'Feature flag rollout percentage',
    ['flag']
)

# Phase 4: Online learning
online_learning_avg_reward = Gauge(
    'query_router_online_learning_avg_reward',
    'Average reward from user feedback'
)

feedback_queue_size = Gauge(
    'query_router_feedback_queue_size',
    'Feedback queue size'
)

batch_updates_total = Counter(
    'query_router_batch_updates_total',
    'Total batch weight updates'
)

per_db_reward = Gauge(
    'query_router_online_learning_db_reward',
    'Per-database average reward',
    ['database']
)


def export_phase4_metrics(router):
    """Export Phase 4 metrics to Prometheus."""

    # Feature flag metrics
    if router.feature_flags:
        flag_state = await router.feature_flags.get_flag("phase4_online_learning")
        feature_flag_rollout.labels(flag="phase4_online_learning").set(
            flag_state.rollout_percentage
        )

    # Online learning metrics
    if router.online_learning_router:
        stats = router.online_learning_router.get_stats()

        online_learning_avg_reward.set(stats['avg_reward'])
        feedback_queue_size.set(stats['queue_size'])
        batch_updates_total.inc(stats['batch_update_count'])

        # Per-database rewards
        for db_name, db_stats in stats['databases'].items():
            per_db_reward.labels(database=db_name).set(db_stats['avg_reward'])
'''

    exporter_file = Path("src/apex_memory/query_router/metrics_exporter.py")
    exporter_file.parent.mkdir(parents=True, exist_ok=True)
    exporter_file.write_text(exporter_code)

    print(f"✓ Created metrics exporter template: {exporter_file}")
    return exporter_file


def setup_monitoring():
    """Set up all monitoring components."""

    print("📊 Setting up Phase 4 monitoring...\n")

    # Create Prometheus rules
    print("Step 1: Creating Prometheus alerting rules...")
    create_prometheus_rules()
    print()

    # Create Grafana dashboard
    print("Step 2: Creating Grafana dashboard...")
    create_grafana_dashboard()
    print()

    # Create metrics exporter template
    print("Step 3: Creating metrics exporter template...")
    create_metrics_exporter()
    print()

    print("✅ Monitoring setup complete!\n")

    print("Next steps:")
    print("   1. Restart Prometheus to load new rules:")
    print("      docker-compose restart prometheus")
    print()
    print("   2. Import Grafana dashboard:")
    print("      - Go to http://localhost:3001")
    print("      - Dashboards → Import")
    print("      - Upload: monitoring/dashboards/phase4-monitoring.json")
    print()
    print("   3. Add metrics exporter to router:")
    print("      - Copy code from src/apex_memory/query_router/metrics_exporter.py")
    print("      - Integrate into router.py")
    print()
    print("   4. Monitor dashboards during rollout:")
    print("      - Grafana: http://localhost:3001")
    print("      - Prometheus: http://localhost:9090")


if __name__ == "__main__":
    setup_monitoring()
