# 13 - Utilities & Scripts

## 🎯 Purpose

Provides development tools, debugging scripts, health checks, and maintenance utilities. Supports local development, testing, and troubleshooting.

## 🛠 Technical Stack

- **Python Scripts:** Automation and debugging
- **Bash Scripts:** Service management
- **Temporal CLI (tctl):** Workflow debugging

## 📂 Key Files & Directories

### Temporal Debugging Scripts
**Location:** `apex-memory-system/scripts/temporal/`

**1. check-workflow-status.py**
```bash
# Check status of specific workflow
python scripts/temporal/check-workflow-status.py --workflow-id doc-ingestion-DOC-123
```

**2. list-failed-workflows.py**
```bash
# List all failed workflows in last 24 hours
python scripts/temporal/list-failed-workflows.py --hours 24
```

**3. compare-metrics.py**
```bash
# Compare Temporal metrics before/after change
python scripts/temporal/compare-metrics.py --baseline baseline.json --current current.json
```

**4. worker-health-check.sh**
```bash
# Check if Temporal worker is running and healthy
bash scripts/temporal/worker-health-check.sh
```

**5. validate-deployment.py**
```bash
# Comprehensive deployment validation
python scripts/temporal/validate-deployment.py --quick
```

### Development Scripts
**Location:** `apex-memory-system/scripts/dev/`

**1. health_check.py**
```bash
# Check all services (databases, Temporal, API)
python scripts/dev/health_check.py -v
```

**2. run_api.py**
```bash
# Start API server with convenience wrapper
python scripts/dev/run_api.py
```

### Maintenance Scripts
**Location:** `apex-memory-system/scripts/maintenance/`

**1. rebuild_indices.py**
```bash
# Rebuild Neo4j and PostgreSQL indices
python scripts/maintenance/rebuild_indices.py
```

**2. clear_caches.py**
```bash
# Clear Redis cache and restart
python scripts/maintenance/clear_caches.py
```

### Setup Scripts
**Location:** `apex-memory-system/scripts/setup/`

**1. verify_sprint1.sh**
```bash
# Verify Sprint 1 infrastructure (databases)
bash scripts/setup/verify_sprint1.sh
```

**2. verify_sprint2.py**
```bash
# Verify Sprint 2 ingestion pipeline
python scripts/setup/verify_sprint2.py
```

### Query Router Testing
**Location:** `apex-memory-system/scripts/query-router/`

- Intent classification testing
- Accuracy benchmarking
- Performance profiling

### Preflight Checks
**Location:** `apex-memory-system/scripts/preflight/`

- Database connectivity
- API key validation
- Service availability

### Community Building
**apex-memory-system/scripts/build_communities.py**
```bash
# Build GraphRAG-style communities from Neo4j graph
python scripts/build_communities.py
```

## Example Usage

### Full System Health Check

```bash
cd apex-memory-system

# 1. Check database services
python scripts/dev/health_check.py -v

# 2. Check Temporal worker
bash scripts/temporal/worker-health-check.sh

# 3. Check API health
curl http://localhost:8000/health

# 4. View Temporal metrics
curl http://localhost:9091/metrics | grep temporal
```

### Debugging Failed Workflow

```bash
# 1. List failed workflows
python scripts/temporal/list-failed-workflows.py --hours 24

# 2. Check specific workflow details
python scripts/temporal/check-workflow-status.py --workflow-id doc-ingestion-DOC-123

# 3. View workflow in Temporal UI
open http://localhost:8088

# 4. View workflow history with tctl
docker exec temporal-admin-tools tctl workflow show -w doc-ingestion-DOC-123
```

### Maintenance Operations

```bash
# Clear all caches
python scripts/maintenance/clear_caches.py

# Rebuild search indices
python scripts/maintenance/rebuild_indices.py

# Restart all services
cd docker
docker-compose restart
```

## Common Utilities

### Logger
**apex-memory-system/src/apex_memory/utils/logger.py**
```python
from apex_memory.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Document ingested successfully")
logger.error("Failed to connect to Neo4j", exc_info=True)
```

### Retry Logic
**apex-memory-system/src/apex_memory/utils/retry.py**
```python
from apex_memory.utils.retry import retry_on_exception

@retry_on_exception(max_attempts=3, backoff=2.0)
def flaky_operation():
    # Automatically retries 3 times with exponential backoff
    call_external_api()
```

## Development Workflow

### Starting Fresh

```bash
# 1. Reset all databases
cd apex-memory-system/docker
docker-compose down -v  # WARNING: Destroys all data
docker-compose up -d

# 2. Initialize databases
cd ..
python init-scripts/qdrant/init.py

# 3. Run health check
python scripts/dev/health_check.py -v

# 4. Start worker
python src/apex_memory/temporal/workers/dev_worker.py &

# 5. Start API
python -m uvicorn apex_memory.main:app --reload
```

### Running Tests

```bash
# All tests
pytest

# Specific category
pytest tests/unit/ -v
pytest tests/integration/ -v

# Single test file
pytest tests/unit/test_query_router.py -v

# With coverage
pytest --cov=src/apex_memory --cov-report=html
```

---

**Previous Component:** [12-Authentication-Security](../12-Authentication-Security/README.md)

**All 13 Components Complete!**
