# Section 3: Configuration Examples

**Author:** Apex Infrastructure Team
**Created:** 2025-10-18
**Section:** 3 - Python SDK & Configuration

---

## Quick Start

### 1. Create .env.temporal File

Copy the template to your project root:

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
# .env.temporal already exists (created in Section 3)
# Edit it to customize your configuration
```

### 2. Load Configuration in Python

```python
from apex_memory.config import TemporalConfig

# Load from environment variables (.env.temporal)
config = TemporalConfig.from_env()

print(f"Temporal Server: {config.server_url}")
print(f"Namespace: {config.namespace}")
print(f"Rollout: {config.rollout_percentage}%")
print(f"Use Temporal: {config.use_temporal}")
```

**Expected Output (with default .env.temporal):**
```
Temporal Server: localhost:7233
Namespace: default
Rollout: 0%
Use Temporal: False
```

---

## Example 1: Development Configuration

**Use Case:** Local development with Temporal disabled

**`.env.temporal` settings:**
```bash
TEMPORAL_HOST=localhost
TEMPORAL_PORT=7233
TEMPORAL_NAMESPACE=default
TEMPORAL_ROLLOUT=0  # Disabled for development
```

**Python code:**
```python
from apex_memory.config import TemporalConfig

config = TemporalConfig.from_env()

if config.use_temporal:
    print("Temporal is ENABLED")
    # Use Temporal workflow
else:
    print("Temporal is DISABLED")
    # Use legacy Saga pattern

# Output: "Temporal is DISABLED"
```

---

## Example 2: Gradual Rollout (10%)

**Use Case:** Testing Temporal with 10% of production traffic

**`.env.temporal` settings:**
```bash
TEMPORAL_HOST=temporal.production.svc.cluster.local
TEMPORAL_PORT=7233
TEMPORAL_NAMESPACE=production
TEMPORAL_ROLLOUT=10  # 10% rollout
TEMPORAL_ENABLE_TRACING=true
TEMPORAL_TRACING_ENDPOINT=http://jaeger:4317
```

**Python code:**
```python
from apex_memory.config import TemporalConfig
import hashlib

config = TemporalConfig.from_env()

def should_use_temporal(document_id: str) -> bool:
    """Deterministic routing based on document ID hash."""
    hash_value = int(hashlib.md5(document_id.encode()).hexdigest(), 16)
    percentage = hash_value % 100
    return percentage < config.rollout_percentage

# Test with sample documents
for doc_id in ["doc-001", "doc-002", "doc-003", "doc-004", "doc-005"]:
    use_temporal = should_use_temporal(doc_id)
    path = "Temporal" if use_temporal else "Saga"
    print(f"{doc_id}: {path}")

# Output (deterministic):
# doc-001: Saga
# doc-002: Temporal  (falls in 10%)
# doc-003: Saga
# doc-004: Saga
# doc-005: Saga
```

---

## Example 3: Full Rollout (100%)

**Use Case:** Complete migration to Temporal

**`.env.temporal` settings:**
```bash
TEMPORAL_HOST=temporal.production.svc.cluster.local
TEMPORAL_PORT=7233
TEMPORAL_NAMESPACE=production
TEMPORAL_ROLLOUT=100  # Full migration
TEMPORAL_MAX_WORKFLOW_TASKS=500  # Increased for production
TEMPORAL_MAX_ACTIVITIES=1000
TEMPORAL_ENABLE_TRACING=true
```

**Python code:**
```python
from apex_memory.config import TemporalConfig

config = TemporalConfig.from_env()

print(f"Rollout: {config.rollout_percentage}%")
print(f"Use Temporal: {config.use_temporal}")
print(f"Max Workflow Tasks: {config.max_concurrent_workflow_tasks}")
print(f"Max Activities: {config.max_concurrent_activities}")

# Output:
# Rollout: 100%
# Use Temporal: True
# Max Workflow Tasks: 500
# Max Activities: 1000
```

---

## Example 4: Validation and Error Handling

**Use Case:** Handling invalid configuration

**Python code:**
```python
from apex_memory.config import TemporalConfig

# Example 1: Invalid rollout percentage
try:
    config = TemporalConfig(rollout_percentage=150)
except ValueError as e:
    print(f"Error: {e}")
    # Output: "Error: TEMPORAL_ROLLOUT must be 0-100, got 150"

# Example 2: Invalid port
try:
    config = TemporalConfig(port=0)
except ValueError as e:
    print(f"Error: {e}")
    # Output: "Error: TEMPORAL_PORT must be 1-65535, got 0"

# Example 3: Invalid concurrency
try:
    config = TemporalConfig(max_concurrent_workflow_tasks=0)
except ValueError as e:
    print(f"Error: {e}")
    # Output: "Error: max_concurrent_workflow_tasks must be >= 1, got 0"

# Example 4: Valid configuration
config = TemporalConfig(rollout_percentage=50, port=7233)
print(f"Valid config: {config}")
# Output: "Valid config: TemporalConfig(host='localhost', port=7233, ...)"
```

---

## Example 5: Feature Flag Pattern

**Use Case:** Using `use_temporal` for conditional logic

**Python code:**
```python
from apex_memory.config import TemporalConfig

config = TemporalConfig.from_env()

async def ingest_document(document_id: str, content: str):
    """Ingest document using Temporal or Saga based on rollout."""
    if config.use_temporal:
        # Use Temporal workflow
        print(f"Ingesting {document_id} via Temporal")
        # await start_temporal_workflow(document_id, content)
    else:
        # Use legacy Saga pattern
        print(f"Ingesting {document_id} via Saga")
        # await execute_saga(document_id, content)

# Simulate ingestion
import asyncio

async def main():
    await ingest_document("doc-001", "Sample content")

asyncio.run(main())
```

---

## Example 6: Configuration Display

**Use Case:** Debugging and logging configuration

**Python code:**
```python
from apex_memory.config import TemporalConfig

config = TemporalConfig.from_env()

# Display all configuration
print("=" * 60)
print("Temporal Configuration")
print("=" * 60)
print(f"Server URL: {config.server_url}")
print(f"Namespace: {config.namespace}")
print(f"Task Queue: {config.task_queue}")
print(f"Worker Build ID: {config.worker_build_id}")
print(f"Max Workflow Tasks: {config.max_concurrent_workflow_tasks}")
print(f"Max Activities: {config.max_concurrent_activities}")
print(f"Rollout Percentage: {config.rollout_percentage}%")
print(f"Use Temporal: {config.use_temporal}")
print(f"Metrics Port: {config.metrics_port}")
print(f"Tracing Enabled: {config.enable_tracing}")
print(f"Tracing Endpoint: {config.tracing_endpoint}")
print("=" * 60)
```

**Expected Output:**
```
============================================================
Temporal Configuration
============================================================
Server URL: localhost:7233
Namespace: default
Task Queue: apex-ingestion-queue
Worker Build ID: v1.0.0
Max Workflow Tasks: 100
Max Activities: 200
Rollout Percentage: 0%
Use Temporal: False
Metrics Port: 8078
Tracing Enabled: False
Tracing Endpoint: None
============================================================
```

---

## Testing the Configuration

### Run Configuration Tests

```bash
cd /Users/richardglaubitz/Projects/apex-memory-system
python3 -m pytest /Users/richardglaubitz/Projects/Apex-Memory-System-Development/upgrades/active/temporal-implementation/tests/section-3-config/test_temporal_config.py -v
```

**Expected Output:**
```
test_config_loads_from_env PASSED             [ 12%]
test_config_defaults PASSED                   [ 25%]
test_rollout_percentage_validation PASSED     [ 37%]
test_use_temporal_property PASSED             [ 50%]
test_env_temporal_gitignored PASSED           [ 62%]
test_port_validation PASSED                   [ 75%]
test_concurrency_validation PASSED            [ 87%]
test_server_url_property PASSED               [100%]

==================== 8 passed ====================
```

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `TEMPORAL_HOST` | `localhost` | Temporal Server hostname |
| `TEMPORAL_PORT` | `7233` | Temporal Server gRPC port |
| `TEMPORAL_NAMESPACE` | `default` | Workflow namespace |
| `TEMPORAL_TASK_QUEUE` | `apex-ingestion-queue` | Task queue name |
| `TEMPORAL_WORKER_BUILD_ID` | `v1.0.0` | Worker version |
| `TEMPORAL_MAX_WORKFLOW_TASKS` | `100` | Max workflow task concurrency |
| `TEMPORAL_MAX_ACTIVITIES` | `200` | Max activity concurrency |
| `TEMPORAL_ROLLOUT` | `0` | Rollout percentage (0-100) |
| `TEMPORAL_METRICS_PORT` | `8078` | SDK metrics port |
| `TEMPORAL_ENABLE_TRACING` | `false` | Enable distributed tracing |
| `TEMPORAL_TRACING_ENDPOINT` | (none) | OTLP endpoint |

---

## Next Steps

Once configuration is complete:

1. ✅ Proceed to **Section 4: Worker Infrastructure**
2. Create `ApexTemporalWorker` class
3. Implement graceful shutdown
4. Test worker connectivity

---

**Files Created in Section 3:**
- `src/apex_memory/config/temporal_config.py` - TemporalConfig dataclass
- `.env.temporal` - Environment template
- `config/__init__.py` - Updated to load .env.temporal
- `.gitignore` - Added .env.temporal
- `tests/section-3-config/test_temporal_config.py` - 8 tests

**Section 3 Complete! Ready for Section 4.**
