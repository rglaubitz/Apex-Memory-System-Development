# TROUBLESHOOTING GUIDE: Advanced Temporal Features

**Project:** Apex Memory System - Temporal Advanced Features
**Version:** 1.0
**Last Updated:** 2025-10-20

---

## 🔍 Quick Diagnostics

### Check Service Health
```bash
# Temporal Server
temporal server health

# Jaeger (Section 16)
curl http://localhost:16686

# Search attributes registered
temporal operator search-attribute list --namespace default
```

### Check Logs
```bash
# Temporal worker logs
docker logs apex-worker

# Jaeger logs
docker logs apex-jaeger
```

---

## Section 14: Search Attributes Issues

### Issue 1: Search attributes not registered

**Symptoms:**
- Error: "unknown search attribute: Source"
- Search queries return empty results

**Causes:**
- Configuration script not executed
- Wrong Temporal namespace
- Temporal Server restart needed

**Solutions:**
```bash
# Execute configuration script
cd apex-memory-system
./scripts/temporal/configure-search-attributes.sh

# Verify registration
temporal operator search-attribute list --namespace default

# If attributes missing, re-run script
./scripts/temporal/configure-search-attributes.sh

# Restart Temporal Server if needed
cd docker && docker-compose restart temporal
```

---

### Issue 2: Workflows not tagged with attributes

**Symptoms:**
- Search returns no workflows despite workflows running
- Workflows visible in UI but not searchable

**Causes:**
- Workflow start code missing search_attributes parameter
- Search attribute keys not imported
- Worker using old code (not restarted)

**Solutions:**
```python
# Verify search attributes in workflow start
from temporalio.common import SearchAttributeKey

SOURCE_ATTR = SearchAttributeKey.for_keyword("Source")
PRIORITY_ATTR = SearchAttributeKey.for_int("Priority")

handle = await client.start_workflow(
    DocumentIngestionWorkflow.run,
    args=[...],
    search_attributes={
        SOURCE_ATTR: [source],
        PRIORITY_ATTR: [priority],
    },
)
```

```bash
# Restart worker to load new code
docker-compose restart worker
```

---

### Issue 3: Status attribute not updating

**Symptoms:**
- Status stays "pending" throughout workflow
- Status never changes to "processing" or "completed"

**Causes:**
- Missing workflow.upsert_search_attributes() calls
- Worker restart needed

**Solutions:**
```python
# Add status updates in workflow
from temporalio import workflow

# After parse activity
workflow.upsert_search_attributes({
    STATUS_ATTR: ["processing"],
})

# On completion
workflow.upsert_search_attributes({
    STATUS_ATTR: ["completed"],
})
```

---

### Issue 4: Search attribute type mismatch

**Symptoms:**
- Error: "type mismatch for search attribute"
- Search query fails

**Causes:**
- Passing string for Int attribute
- Passing int for Keyword attribute

**Solutions:**
```python
# Correct types
search_attributes={
    SOURCE_ATTR: ["frontapp"],         # Keyword = list of strings
    PRIORITY_ATTR: [3],                # Int = list of ints
    DOCUMENT_ID_ATTR: ["doc-123"],     # Keyword = list of strings
    STATUS_ATTR: ["pending"],          # Keyword = list of strings
}

# WRONG - will fail
search_attributes={
    PRIORITY_ATTR: "3",  # Should be [3] not "3"
}
```

---

## Section 12: Polling Workflows Issues

### Issue 5: Polling workflow not starting

**Symptoms:**
- Workflow fails to start
- Error: "unknown workflow type: PollingWorkflow"

**Causes:**
- PollingWorkflow not registered in worker
- Worker not restarted after code change

**Solutions:**
```python
# Verify worker registration (dev_worker.py)
from apex_memory.temporal.workflows.polling import PollingWorkflow

worker = Worker(
    client,
    task_queue="apex-ingestion-queue",
    workflows=[
        GreetingWorkflow,
        DocumentIngestionWorkflow,
        StructuredDataIngestionWorkflow,
        PollingWorkflow,  # Must be here
    ],
)
```

```bash
# Restart worker
docker-compose restart worker
```

---

### Issue 6: Continue-as-new not working

**Symptoms:**
- Workflow history grows unbounded
- Workflow exceeds max history size

**Causes:**
- Missing workflow.continue_as_new() call
- Continue-as-new iteration count not incrementing

**Solutions:**
```python
# Verify continue-as-new logic
if self.iteration_count >= MAX_ITERATIONS:
    workflow.logger.info("Using continue-as-new...")

    workflow.continue_as_new(
        args=[
            source,
            interval_minutes,
            0,  # Reset iteration count
            self.last_poll_timestamp,  # Preserve state
        ]
    )
```

---

### Issue 7: Child workflows not spawning

**Symptoms:**
- Records fetched but no child workflows created
- Zero child workflows visible in Temporal UI

**Causes:**
- await workflow.start_child_workflow() not called
- Child workflow ID collision
- Task queue mismatch

**Solutions:**
```python
# Verify child workflow creation
for record in records:
    child_handle = await workflow.start_child_workflow(
        StructuredDataIngestionWorkflow.run,
        args=[...],
        id=f"{workflow.info().workflow_id}-child-{record_id}",  # Unique ID
        task_queue="apex-ingestion-queue",  # Must match worker
    )
```

---

### Issue 8: API polling failures

**Symptoms:**
- Activity fails: httpx.HTTPError
- "Connection refused" or "Timeout"

**Causes:**
- API endpoint unreachable
- Missing API keys
- Rate limiting

**Solutions:**
```python
# Add retry policy
retry_policy=RetryPolicy(
    initial_interval=timedelta(seconds=10),
    maximum_interval=timedelta(minutes=2),
    maximum_attempts=3,
)

# Check API keys
echo $SAMSARA_API_KEY
echo $TURVO_API_KEY

# Test API manually
curl -H "Authorization: Bearer $SAMSARA_API_KEY" \
  https://api.samsara.com/fleet/locations
```

---

## Section 16: OpenTelemetry Issues

### Issue 9: Traces not appearing in Jaeger

**Symptoms:**
- Jaeger UI shows no traces
- Workflows execute but no traces

**Causes:**
- ENABLE_OPENTELEMETRY=false
- OTLP exporter not configured
- Jaeger not running

**Solutions:**
```bash
# Check environment
echo $ENABLE_OPENTELEMETRY  # Should be 'true'
echo $OTLP_ENDPOINT         # Should be 'http://localhost:4317'

# Verify Jaeger running
docker ps | grep jaeger
curl http://localhost:16686

# Restart Jaeger if needed
docker-compose restart jaeger

# Restart worker to reinitialize telemetry
docker-compose restart worker
```

---

### Issue 10: OTLP connection refused

**Symptoms:**
- Error: "failed to export spans: connection refused"
- Logs show OTLP exporter errors

**Causes:**
- Jaeger not running
- Wrong OTLP endpoint
- Port conflict

**Solutions:**
```bash
# Verify Jaeger OTLP port
docker ps | grep jaeger
# Should show 4317:4317

# Check port binding
lsof -i :4317

# Verify docker-compose.yml
services:
  jaeger:
    ports:
      - "4317:4317"  # OTLP gRPC
      - "16686:16686"  # Jaeger UI

# Restart Jaeger
docker-compose restart jaeger
```

---

### Issue 11: Auto-instrumentation not working

**Symptoms:**
- HTTP requests not traced
- Database queries not traced

**Causes:**
- Instrumentation not enabled
- Dependencies not installed

**Solutions:**
```bash
# Install instrumentation packages
pip install opentelemetry-instrumentation-httpx
pip install opentelemetry-instrumentation-asyncpg

# Verify instrumentation (telemetry.py)
HTTPXClientInstrumentor().instrument()
AsyncPGInstrumentor().instrument()

# Restart worker
docker-compose restart worker
```

---

### Issue 12: Missing trace context

**Symptoms:**
- Traces appear as separate spans, not connected
- Parent-child relationship missing

**Causes:**
- Manual span creation incorrect
- Context propagation broken

**Solutions:**
```python
# Use start_as_current_span for automatic context
with tracer.start_as_current_span("operation_name"):
    # Nested operations automatically linked
    with tracer.start_as_current_span("nested_operation"):
        pass

# Verify trace context propagated
from opentelemetry import trace

current_span = trace.get_current_span()
print(f"Current span: {current_span.get_span_context()}")
```

---

## General Issues

### Issue 13: Worker not picking up new code

**Symptoms:**
- Code changes not reflected
- Old behavior persists

**Solutions:**
```bash
# Rebuild worker container
docker-compose build worker

# Restart worker
docker-compose restart worker

# Check worker logs
docker logs apex-worker --tail 50
```

---

### Issue 14: Port conflicts

**Symptoms:**
- Service fails to start: "address already in use"

**Solutions:**
```bash
# Check what's using the port
lsof -i :4317  # Jaeger OTLP
lsof -i :16686 # Jaeger UI

# Kill conflicting process
kill -9 <PID>

# Or change port in docker-compose.yml
```

---

## Debugging Tools

### Temporal CLI
```bash
# Search workflows
temporal workflow list --query "Source='frontapp'"

# Describe workflow
temporal workflow describe --workflow-id <WORKFLOW_ID>

# Query workflow
temporal workflow query --workflow-id polling-samsara --query-type get_stats
```

### Jaeger UI
```
http://localhost:16686

# Search traces by workflow ID
# Search traces by service: apex-memory-system
# View trace timeline
# Inspect span attributes
```

### Python Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add print statements
print(f"Search attributes: {search_attributes}")

# Check Temporal SDK logs
from temporalio import logger as temporal_logger
temporal_logger.setLevel(logging.DEBUG)
```

---

## Getting Help

**Documentation:**
- IMPLEMENTATION-PLAN.md - Step-by-step implementation
- TESTING.md - Test specifications
- RESEARCH-REFERENCES.md - Official documentation

**Debugging:**
- Temporal UI: http://localhost:8088
- Jaeger UI: http://localhost:16686
- Worker logs: `docker logs apex-worker`
- Temporal logs: `docker logs apex-temporal`

**Common Fixes:**
1. Restart worker: `docker-compose restart worker`
2. Rebuild worker: `docker-compose build worker && docker-compose up -d worker`
3. Check services: `docker-compose ps`
4. View logs: `docker-compose logs -f worker`

---

**Troubleshooting Version:** 1.0
**Last Updated:** 2025-10-20
