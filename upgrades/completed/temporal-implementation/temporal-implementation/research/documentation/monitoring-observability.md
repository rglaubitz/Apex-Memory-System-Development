# Temporal Monitoring & Observability

**Last Updated:** 2025-10-17  
**Sources:** Temporal docs, OpenTelemetry integration, Prometheus/Grafana setup

## Observability Stack

```
┌─────────────────────────────────────────────────────────┐
│                  Temporal Workflows                      │
│              (emit metrics, logs, traces)               │
└──────────────┬────────────────────────────────────────┘
               │
               ├─> Temporal UI (http://localhost:8088)
               ├─> Prometheus (metrics, port 8000)
               ├─> OpenTelemetry Collector (traces)
               └─> Grafana (dashboards)
```

## Temporal UI

**Access:** http://localhost:8088

**Key Features:**
- Real-time workflow execution tracking
- Event history browser
- Workflow search and filtering
- Manual workflow termination/retry
- Stack trace viewer

**Example Queries:**
```
# Find failed workflows
WorkflowType='IngestionWorkflow' AND ExecutionStatus='Failed'

# Find long-running workflows
WorkflowType='PollingWorkflow' AND StartTime < '2025-10-01'

# Search by custom attribute
CustomKeywordField='doc-123'
```

## Prometheus Metrics

### Temporal Server Metrics

```yaml
# Temporal Server exposes metrics on port 8000
scrape_configs:
  - job_name: 'temporal-server'
    static_configs:
      - targets: ['localhost:8000']
```

**Key Metrics:**
```
# Workflow metrics
temporal_workflow_success_count
temporal_workflow_failed_count
temporal_workflow_timeout_count
temporal_workflow_execution_latency

# Activity metrics  
temporal_activity_execution_latency
temporal_activity_scheduled_to_start_latency
temporal_activity_task_error_count

# Task queue metrics
temporal_task_queue_length
temporal_task_queue_latency
```

### SDK Metrics (Python)

```python
from temporalio.runtime import Runtime, PrometheusConfig
from temporalio.client import Client
from prometheus_client import start_http_server

# Start Prometheus scrape endpoint
start_http_server(8077)

# Configure runtime with Prometheus
runtime = Runtime(telemetry=PrometheusConfig(bind_address="0.0.0.0:8077"))

client = await Client.connect(
    "localhost:7233",
    runtime=runtime
)
```

**Scrape config:**
```yaml
scrape_configs:
  - job_name: 'temporal-python-sdk'
    static_configs:
      - targets: ['localhost:8077']
```

## OpenTelemetry Tracing

### Setup

```python
from temporalio.runtime import Runtime, OpenTelemetryConfig
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure OpenTelemetry
provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
)
trace.set_tracer_provider(provider)

# Configure Temporal runtime
runtime = Runtime(
    telemetry=OpenTelemetryConfig(
        url="http://localhost:4318",  # OTLP HTTP endpoint
    )
)

client = await Client.connect("localhost:7233", runtime=runtime)
```

### Distributed Tracing

```
Trace: document-ingestion-abc-123
├─ Span: IngestionWorkflow.run (5.2s)
│  ├─ Span: parse_document_activity (0.8s)
│  ├─ Span: extract_entities_activity (1.2s)
│  ├─ Span: generate_embeddings_activity (0.5s)
│  └─ Span: write_to_databases_activity (2.7s)
│     ├─ Span: acquire_lock (0.01s)
│     ├─ Span: check_idempotency (0.005s)
│     └─ Span: parallel_db_writes (2.6s)
│        ├─ Span: neo4j_write (0.8s)
│        ├─ Span: postgres_write (0.9s)
│        ├─ Span: qdrant_write (0.7s)
│        └─ Span: redis_write (0.2s)
```

## Grafana Dashboards

### Import Temporal Dashboards

```bash
# 1. Clone Temporal dashboards repo
git clone https://github.com/temporalio/dashboards.git

# 2. Import to Grafana
# - Open Grafana (http://localhost:3000)
# - Import dashboards/temporal-server.json
# - Import dashboards/temporal-sdk.json
```

### Custom Dashboard Panels

**Workflow Success Rate:**
```promql
sum(rate(temporal_workflow_success_count[5m]))
/
sum(rate(temporal_workflow_success_count[5m]) + rate(temporal_workflow_failed_count[5m]))
* 100
```

**P99 Workflow Latency:**
```promql
histogram_quantile(0.99, 
  sum(rate(temporal_workflow_execution_latency_bucket[5m])) by (le, workflow_type)
)
```

**Active Workflows by Type:**
```promql
sum by (workflow_type) (temporal_workflow_active_count)
```

**Circuit Breaker State:**
```promql
# Custom metric from Enhanced Saga
apex_circuit_breaker_state{database="postgres"}
# 0 = CLOSED, 1 = OPEN, 2 = HALF_OPEN
```

## Logging

### Structured Logging

```python
import structlog
from temporalio import workflow, activity

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

@workflow.defn
class LoggingWorkflow:
    @workflow.run
    async def run(self, doc_id: str):
        workflow.logger.info(
            "Starting ingestion",
            document_id=doc_id,
            workflow_id=workflow.info().workflow_id
        )
        
        try:
            result = await workflow.execute_activity(parse_document, doc_id)
            workflow.logger.info("Parse complete", chunks=len(result.chunks))
        except Exception as e:
            workflow.logger.error(
                "Parse failed",
                error=str(e),
                document_id=doc_id
            )
            raise
```

**Output (JSON):**
```json
{
  "event": "Starting ingestion",
  "level": "info",
  "timestamp": "2025-10-17T10:30:00.123Z",
  "document_id": "doc-123",
  "workflow_id": "ingest-doc-123"
}
```

## Alerts

### Prometheus Alert Rules

```yaml
# prometheus/alerts.yml
groups:
  - name: temporal_alerts
    rules:
      - alert: HighWorkflowFailureRate
        expr: |
          sum(rate(temporal_workflow_failed_count[5m]))
          /
          sum(rate(temporal_workflow_success_count[5m]) + rate(temporal_workflow_failed_count[5m]))
          > 0.05
        for: 5m
        annotations:
          summary: "Workflow failure rate > 5%"
          
      - alert: TemporalServerDown
        expr: up{job="temporal-server"} == 0
        for: 1m
        annotations:
          summary: "Temporal Server unreachable"
          
      - alert: HighDLQEntryRate
        expr: rate(apex_dlq_entries_total[5m]) > 10
        for: 5m
        annotations:
          summary: "DLQ receiving >10 entries/sec"
```

### Slack/PagerDuty Integration

```yaml
# alertmanager.yml
route:
  receiver: 'slack-notifications'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      
receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#apex-alerts'
        text: '{{ .GroupLabels.alertname }}: {{ .Annotations.summary }}'
        
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<PAGERDUTY_KEY>'
```

## Related Documentation

- [Temporal Overview](temporal-io-overview.md)
- [Deployment Guide](deployment-guide.md)
- [Integration Patterns](integration-patterns.md)

## Resources

- Temporal UI Guide: https://docs.temporal.io/web-ui
- Prometheus Metrics: https://docs.temporal.io/self-hosted-guide/production-checklist#metrics
- OpenTelemetry Integration: https://github.com/temporal-community/temporal-otel
