# 02 - Workflow Orchestration (Temporal.io)

## 🎯 Purpose

Orchestrates all document and structured data ingestion workflows with fault tolerance, automatic retries, and complete observability. **Critical component** - ingestion will not work without the Temporal worker running.

**Why Temporal?**
- Durable workflow execution survives service restarts
- Automatic retries with exponential backoff
- Complete execution history and debugging
- Activity-level monitoring and metrics
- Saga pattern support for rollbacks

## 🛠 Technical Stack

### Temporal Server Infrastructure
- **Temporal Server:** `temporalio/auto-setup:1.28.0` - Workflow orchestration engine
- **Temporal UI:** `temporalio/ui:2.38.0` - Web interface for workflow visualization
- **Temporal Admin Tools:** `temporalio/admin-tools:latest` - CLI (tctl) for debugging
- **PostgreSQL:** `postgres:16` - Temporal state persistence
- **Port Mapping:**
  - 7233: gRPC frontend (worker connections)
  - 8088: Temporal UI
  - 8077: Prometheus metrics
  - 5433: Temporal PostgreSQL (avoid conflict with apex-postgres:5432)

### Python SDK
- **temporalio:** SDK for workflow/activity development
- **prometheus_client:** Worker metrics on port 9091

## 📂 Key Files

### Workflows (Orchestration Logic)
- `apex-memory-system/src/apex_memory/temporal/workflows/hello_world.py` (~100 lines)
  - Simple greeting workflow for testing Temporal setup

- `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py` (~400 lines)
  - **DocumentIngestionWorkflow:** 6-activity pipeline for document processing
  - **StructuredDataIngestionWorkflow:** 4-activity pipeline for JSON/API data

### Activities (Task Implementations)
- `apex-memory-system/src/apex_memory/temporal/activities/hello_world.py` (~50 lines)
  - `greet_activity` - Simple test activity

- `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py` (~800 lines)
  - **Document Activities (6):**
    - `pull_and_stage_document_activity` - Download/stage from source
    - `parse_document_activity` - Docling parsing
    - `extract_entities_activity` - OpenAI entity extraction
    - `generate_embeddings_activity` - Vector generation
    - `write_to_databases_activity` - Saga pattern multi-DB write
    - `cleanup_staging_activity` - Remove staging files

  - **Structured Data Activities (4):**
    - `fetch_structured_data_activity` - Pull JSON from API
    - `extract_entities_from_json_activity` - JSON entity extraction
    - `generate_embeddings_from_json_activity` - JSON embeddings
    - `write_structured_data_activity` - JSON multi-DB write

### Workers (Activity Execution)
- `apex-memory-system/src/apex_memory/temporal/workers/base_worker.py` (~150 lines)
  - `ApexTemporalWorker` base class with connection management

- `apex-memory-system/src/apex_memory/temporal/workers/dev_worker.py` (~200 lines)
  - Development worker with all 3 workflows + 11 activities
  - Prometheus metrics server on port 9091
  - **Must be running for any ingestion to work!**

### Infrastructure
- `apex-memory-system/docker/temporal-compose.yml` (~100 lines)
  - Temporal Server + UI + PostgreSQL + Admin Tools
  - Health checks and networking

- `apex-memory-system/docker/temporal-dynamicconfig/development.yaml`
  - Temporal Server dynamic configuration

## 🔗 Dependencies

### Depends On:
1. **Database Infrastructure** (01) - All 4 databases for activity execution
2. **Core Services** (05) - DocumentParser, EmbeddingService, etc.
3. **Database Writers** (07) - DatabaseWriteOrchestrator for multi-DB saga

### Requires:
- Temporal Server running (`docker-compose -f docker/temporal-compose.yml up -d`)
- Worker process running (`python src/apex_memory/temporal/workers/dev_worker.py`)

## 🔌 Interfaces

### Consumed By:
1. **Backend API** (03) - Ingestion endpoints trigger workflows:
   ```python
   # From apex-memory-system/src/apex_memory/api/ingestion.py

   workflow_handle = await client.start_workflow(
       DocumentIngestionWorkflow.run,
       args=[document_info],
       id=f"doc-ingestion-{document_id}",
       task_queue="apex-ingestion-queue"
   )
   ```

2. **Monitoring** (10) - Temporal metrics scraped by Prometheus

### Provides:
- Workflow execution API (gRPC on port 7233)
- Web UI for debugging (http://localhost:8088)
- Prometheus metrics (http://localhost:8077)
- Worker metrics (http://localhost:9091/metrics)

## ⚙️ Configuration

### Temporal Server Environment

```yaml
# From docker/temporal-compose.yml

DB: postgres12
DB_PORT: 5432
POSTGRES_USER: temporal
POSTGRES_PWD: temporal
POSTGRES_SEEDS: temporal-postgres

DYNAMIC_CONFIG_FILE_PATH: config/dynamicconfig/development.yaml
PROMETHEUS_ENDPOINT: 0.0.0.0:8077
ENABLE_ES: "false"  # SQL visibility instead of Elasticsearch
LOG_LEVEL: info
```

### Worker Configuration

```python
# From src/apex_memory/temporal/workers/dev_worker.py

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost")
TEMPORAL_PORT = os.getenv("TEMPORAL_PORT", "7233")
TEMPORAL_TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "apex-ingestion-queue")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
```

### Activity Retry Policies

```python
# Default retry policy for all activities
start_to_close_timeout=timedelta(minutes=10)
retry_policy=RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=60),
    backoff_coefficient=2.0
)
```

## 🚀 Deployment

### Start Temporal Infrastructure

```bash
# Terminal 1: Start Temporal Server + UI
cd apex-memory-system/docker
docker-compose -f temporal-compose.yml up -d

# Verify services healthy (wait 30s)
docker ps | grep temporal

# Access Temporal UI
open http://localhost:8088
```

### Start Worker (REQUIRED for ingestion)

```bash
# Terminal 2: Start worker process
cd apex-memory-system
source venv/bin/activate
python src/apex_memory/temporal/workers/dev_worker.py

# Output should show:
# ✅ Registered workflows: 3 total
# ✅ Registered activities: 11 total
# Metrics available at http://localhost:9091/metrics
```

### Trigger Workflow (via API or CLI)

```bash
# Via API (POST to ingestion endpoint)
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@document.pdf" \
  -F "source=local_upload"

# Via tctl (direct workflow start)
docker exec temporal-admin-tools tctl workflow start \
  --taskqueue apex-ingestion-queue \
  --type GreetingWorkflow \
  --input '"World"'
```

## 📊 Workflow Execution Flow

### DocumentIngestionWorkflow (6 Activities)

```
┌─────────────────────────────────────────────────────┐
│ DocumentIngestionWorkflow                           │
│                                                     │
│  1. pull_and_stage_document_activity                │
│     ↓ (Download to /tmp/apex-staging/)             │
│  2. parse_document_activity                         │
│     ↓ (Docling → chunks)                           │
│  3. extract_entities_activity                       │
│     ↓ (OpenAI GPT-4o → entities)                   │
│  4. generate_embeddings_activity                    │
│     ↓ (OpenAI text-embedding-3-small)              │
│  5. write_to_databases_activity                     │
│     ↓ (Saga: Neo4j + PostgreSQL + Qdrant + Redis)  │
│  6. cleanup_staging_activity                        │
│     ↓ (Remove /tmp/apex-staging/{id}/)             │
│                                                     │
│  Result: {success, document_id, chunks, entities}   │
└─────────────────────────────────────────────────────┘
```

### Fault Tolerance Example

```
Activity 4 (generate_embeddings) fails → OpenAI rate limit

Temporal automatically:
1. Retries after 1 second (backoff)
2. Retries after 2 seconds
3. Retries after 4 seconds
... up to 3 attempts total

If all 3 fail:
- Workflow marks activity as failed
- Cleanup activity runs (remove staging)
- Entire workflow state preserved in Temporal
- User can retry workflow from UI or API
```

## 📈 Metrics & Monitoring

### Temporal Workflow Metrics (Prometheus)

```python
# From apex-memory-system/src/apex_memory/monitoring/metrics.py

temporal_workflow_executions_total = Counter(
    "apex_temporal_workflow_executions_total",
    "Total workflow executions",
    ["workflow_name", "status"]  # DocumentIngestionWorkflow, success/failed
)

temporal_workflow_duration_seconds = Histogram(
    "apex_temporal_workflow_duration_seconds",
    "Workflow execution duration",
    ["workflow_name"]
)

temporal_activity_executions_total = Counter(
    "apex_temporal_activity_executions_total",
    "Total activity executions",
    ["activity_name", "status"]
)

temporal_activity_duration_seconds = Histogram(
    "apex_temporal_activity_duration_seconds",
    "Activity execution duration",
    ["activity_name"]
)
```

### Worker Health Metrics (port 9091)

- Active workflow executions
- Activity task latency
- Worker CPU/memory usage
- Queue depth

### Temporal UI Insights

**Access:** http://localhost:8088

- Workflow execution history (all runs)
- Activity retry details
- Payload inspection (inputs/outputs)
- Timeline visualization
- Error stack traces

## 🔧 Debugging Workflows

### View Workflow Status

```bash
# List all workflows
docker exec temporal-admin-tools tctl workflow list

# Describe specific workflow
docker exec temporal-admin-tools tctl workflow describe \
  -w doc-ingestion-DOC-123

# Show workflow history
docker exec temporal-admin-tools tctl workflow show \
  -w doc-ingestion-DOC-123
```

### Check Worker Health

```bash
# Worker metrics
curl http://localhost:9091/metrics | grep temporal

# Worker logs
# (View terminal where dev_worker.py is running)
```

### Common Issues

**"Workflow execution timeout"**
- Check activity timeouts in workflow definition
- Increase `start_to_close_timeout` if activities legitimately take longer

**"Task queue not found"**
- Ensure worker is running with correct task queue name
- Default: "apex-ingestion-queue"

**"Activity failed after retries"**
- Check Temporal UI for error details
- Review activity logs for root cause
- Verify database connections in activity code

## 🚨 Critical Notes

### Worker Must Be Running!

**Without the worker process, ingestion will NOT work:**

```bash
# Bad: No worker running
POST /api/v1/ingest → Returns 202 Accepted
Workflow starts in Temporal → NO WORKER TO EXECUTE
Tasks sit in queue indefinitely ❌

# Good: Worker running
POST /api/v1/ingest → Returns 202 Accepted
Workflow starts in Temporal → Worker executes activities
Document successfully ingested ✅
```

### Production Deployment Recommendations

1. **Multiple Workers** - Run 3-5 worker processes for redundancy
2. **Auto-restart** - Use systemd, supervisord, or Kubernetes
3. **Metrics** - Scrape worker metrics (port 9091) into Prometheus
4. **Alerting** - Alert if worker count drops to 0
5. **Database Backup** - Backup temporal-postgres (workflow history)

## 🔍 Performance Characteristics

### Workflow Latency (P50/P90/P99)

- **DocumentIngestionWorkflow:**
  - P50: 8s (10-page PDF)
  - P90: 15s (50-page PDF)
  - P99: 45s (complex 200-page document)

- **StructuredDataIngestionWorkflow:**
  - P50: 2s (small JSON)
  - P90: 5s (large JSON 10MB)
  - P99: 15s (very large JSON)

### Activity Breakdown (typical document)

1. Pull & Stage: 100-500ms
2. Parse: 2-10s (depends on page count)
3. Extract Entities: 1-3s (OpenAI API)
4. Generate Embeddings: 500ms-2s (chunk count)
5. Write to Databases: 1-3s (parallel writes)
6. Cleanup: 50-100ms

**Total:** 5-20s per document

---

**Previous Component:** [01-Database-Infrastructure](../01-Database-Infrastructure/README.md)
**Next Component:** [03-Backend-API](../03-Backend-API/README.md)
