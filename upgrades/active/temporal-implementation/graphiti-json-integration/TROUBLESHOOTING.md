# Graphiti + JSON Integration - Troubleshooting Guide

**Project:** Apex Memory System - Temporal Implementation
**Document Type:** Common Issues & Solutions
**Status:** Living Document
**Created:** 2025-10-19

---

## Table of Contents

1. [Graphiti Issues](#graphiti-issues)
2. [Saga Rollback Issues](#saga-rollback-issues)
3. [Temporal Workflow Issues](#temporal-workflow-issues)
4. [Database Connection Issues](#database-connection-issues)
5. [Staging Issues](#staging-issues)
6. [JSON Ingestion Issues](#json-ingestion-issues)
7. [Debugging Tools](#debugging-tools)

---

## Graphiti Issues

### Issue 1.1: "Episode not found" Error

**Symptom:**
```
GraphitiError: Episode with UUID 'doc-123' not found
```

**Cause:** Passing UUID to `graphiti.add_document_episode()` when Graphiti auto-generates episode IDs

**Solution:**
```python
# ❌ WRONG
result = await graphiti.add_document_episode(
    uuid=document_uuid,  # Don't pass uuid!
    document_content=content
)

# ✅ CORRECT
result = await graphiti.add_document_episode(
    document_uuid=document_uuid,  # Pass as document_uuid parameter
    document_content=content
)
```

**Reference:** `graphiti_service.py:190` - See comment: "Don't pass uuid - let Graphiti auto-generate episode IDs"

---

### Issue 1.2: Neo4j Connection Timeout

**Symptom:**
```
Neo4jError: Failed to establish connection in 30s
```

**Diagnostic:**
```bash
# Check Neo4j is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs neo4j-apex

# Test connection
python3 -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'apexmemory2024')); driver.verify_connectivity(); print('✅ Connected')"
```

**Solution:**
1. Ensure Neo4j container is running:
   ```bash
   cd apex-memory-system/docker
   docker-compose up -d neo4j
   ```

2. Verify credentials in `.env`:
   ```bash
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=apexmemory2024
   ```

3. Check Neo4j health:
   ```bash
   curl http://localhost:7474/db/neo4j/tx/commit
   ```

---

### Issue 1.3: LLM Extraction Fails

**Symptom:**
```
ApplicationError: Graphiti extraction failed: OpenAI API timeout
```

**Diagnostic:**
```bash
# Verify OpenAI API key
python3 -c "from openai import OpenAI; client = OpenAI(); print('✅ Key valid')"

# Check Graphiti service initialization
python3 -c "from apex_memory.services.graphiti_service import GraphitiService; from apex_memory.config.settings import Settings; s = Settings(); g = GraphitiService(s.neo4j_uri, s.neo4j_user, s.neo4j_password); print(f'Enabled: {g.enabled}')"
```

**Solutions:**

1. **API Key Issue:**
   ```bash
   # Verify key in .env
   echo $OPENAI_API_KEY

   # Or check Settings
   python3 -c "from apex_memory.config.settings import Settings; print(Settings().openai_api_key)"
   ```

2. **Rate Limiting:**
   - Graphiti uses GPT-4.1-mini by default
   - Check OpenAI dashboard: https://platform.openai.com/usage
   - Solution: Reduce concurrent extractions or switch model

3. **Timeout:**
   - Increase activity timeout in workflow:
   ```python
   entities = await workflow.execute_activity(
       extract_entities_activity,
       start_to_close_timeout=timedelta(minutes=10),  # Increase from 5
   )
   ```

---

### Issue 1.4: Entity Extraction Returns Empty

**Symptom:**
```python
result['entities'] == []
# But document has clear entities
```

**Diagnostic:**
```python
# Check Graphiti result directly
result = await graphiti.add_document_episode(...)
print(f"Entities: {result.entities_extracted}")
print(f"Success: {result.success}")
print(f"Error: {result.error}")
```

**Causes:**

1. **Document too short:**
   - Graphiti requires minimum ~50 words for meaningful extraction
   - Solution: Skip extraction for very short documents

2. **Content format issue:**
   - Graphiti expects plain text
   - Solution: Ensure Docling parse returns clean text (not HTML/markup)

3. **LLM model issue:**
   - GPT-4.1-mini may miss entities in specialized domains
   - Solution: Use GPT-4.1 (higher quality):
   ```python
   graphiti = GraphitiService(
       llm_model="gpt-4.1",  # More expensive but better quality
   )
   ```

---

## Saga Rollback Issues

### Issue 2.1: Orphaned Graphiti Episodes

**Symptom:**
- Saga fails (e.g., Neo4j timeout)
- Graphiti episode NOT rolled back
- Neo4j contains orphaned Episode nodes

**Diagnostic:**
```cypher
// Check for orphaned episodes (Neo4j Browser)
MATCH (e:Episode)
WHERE NOT (e)<-[:HAS_EPISODE]-(:Document)
RETURN count(e)
```

**Causes:**

1. **Rollback function not called:**
   ```python
   # Check write_to_databases_activity
   # Ensure rollback_graphiti_episode() is called on failure
   ```

2. **Rollback failed silently:**
   ```python
   # Check logs for rollback failures
   grep "Failed to rollback Graphiti episode" apex-memory-system/logs/worker.log
   ```

**Solutions:**

1. **Manual cleanup:**
   ```bash
   python3 scripts/cleanup_orphaned_episodes.py
   ```

2. **Add to DLQ:**
   ```python
   # In rollback_graphiti_episode()
   if not success:
       # Send to DLQ
       await dlq_service.send({
           'type': 'graphiti_rollback_failure',
           'episode_uuid': episode_uuid,
           'timestamp': datetime.utcnow().isoformat()
       })
   ```

3. **Verify rollback in tests:**
   ```bash
   pytest tests/unit/test_graphiti_rollback.py::test_orphaned_episode_cleanup -v
   ```

---

### Issue 2.2: Partial Database Writes

**Symptom:**
- PostgreSQL has record
- Qdrant does NOT have vector
- Rollback didn't clean up Postgres

**Diagnostic:**
```bash
# Check write result
tail -f apex-memory-system/logs/worker.log | grep "Saga result"

# Check databases manually
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT uuid FROM documents WHERE uuid='problem-uuid'"

curl http://localhost:6333/collections/apex_documents/points/problem-uuid
```

**Cause:** Rollback mechanism incomplete for structured data

**Solution:**

1. **Verify _rollback_writes() works:**
   ```bash
   pytest tests/unit/test_saga_rollback.py -v
   ```

2. **Check rollback implementation:**
   ```python
   # apex-memory-system/src/apex_memory/services/database_writer.py
   async def _rollback_writes(self, uuid: str, ...):
       # Ensure all 4 databases have delete methods
   ```

3. **Manual cleanup:**
   ```sql
   -- PostgreSQL
   DELETE FROM documents WHERE uuid='problem-uuid';
   DELETE FROM structured_data WHERE uuid='problem-uuid';
   ```

---

## Temporal Workflow Issues

### Issue 3.1: Workflow Stuck in "Running"

**Symptom:**
- Temporal UI shows workflow "Running" for hours
- No activity progress

**Diagnostic:**
```bash
# Check Temporal UI
open http://localhost:8088

# Check worker logs
tail -f apex-memory-system/logs/worker.log

# Check worker is running
ps aux | grep dev_worker
```

**Causes:**

1. **Worker not running:**
   ```bash
   # Start worker
   cd apex-memory-system
   python -m apex_memory.temporal.workers.dev_worker
   ```

2. **Activity hanging:**
   - Check if activity is waiting for external resource
   - Check if Neo4j/PostgreSQL is responsive

3. **Deadlock:**
   - Check distributed lock table:
   ```sql
   SELECT * FROM distributed_locks WHERE is_locked=true;
   ```

**Solutions:**

1. **Cancel stuck workflow:**
   ```bash
   temporal workflow cancel --workflow-id ingest-doc-123
   ```

2. **Restart worker:**
   ```bash
   pkill -f dev_worker
   python -m apex_memory.temporal.workers.dev_worker
   ```

3. **Clear locks:**
   ```sql
   -- PostgreSQL
   UPDATE distributed_locks SET is_locked=false WHERE acquired_at < NOW() - INTERVAL '10 minutes';
   ```

---

### Issue 3.2: Activity Timeout

**Symptom:**
```
WorkflowExecutionError: Activity 'extract_entities_activity' timed out after 300s
```

**Diagnostic:**
```bash
# Check activity execution time
grep "extract_entities_activity completed" apex-memory-system/logs/worker.log | tail -1
```

**Solution:**

1. **Increase timeout:**
   ```python
   # In workflow
   entities = await workflow.execute_activity(
       extract_entities_activity,
       start_to_close_timeout=timedelta(minutes=10),  # Increase
   )
   ```

2. **Optimize activity:**
   - For Graphiti: Use smaller LLM model
   - For embeddings: Reduce chunk count
   - For Saga: Investigate database slowness

3. **Add retry policy:**
   ```python
   retry_policy=RetryPolicy(
       initial_interval=timedelta(seconds=2),
       maximum_interval=timedelta(seconds=30),
       maximum_attempts=5,  # Increase attempts
   )
   ```

---

### Issue 3.3: Worker Not Picking Up Activities

**Symptom:**
- Workflow starts
- Activities not executed
- Worker logs show no activity

**Diagnostic:**
```bash
# Check worker registration
python3 -c "from apex_memory.temporal.workers.dev_worker import main; import asyncio; asyncio.run(main())"
# Should print: "✅ Activities: 10 total"

# Check task queue name
grep "task_queue" apex-memory-system/src/apex_memory/temporal/workers/dev_worker.py
```

**Causes:**

1. **Task queue mismatch:**
   ```python
   # Worker
   worker = Worker(client, task_queue="apex-ingestion-queue")

   # Workflow execution
   await client.execute_workflow(..., task_queue="DIFFERENT-QUEUE")  # ❌ Wrong
   ```

2. **Activity not registered:**
   ```python
   # Check worker activities list
   worker = Worker(
       activities=[
           extract_entities_activity,  # Ensure this is present
       ]
   )
   ```

**Solution:**

1. **Verify task queue:**
   ```python
   # Workflow execution
   await client.execute_workflow(
       DocumentIngestionWorkflow.run,
       task_queue="apex-ingestion-queue",  # Match worker
   )
   ```

2. **Restart worker:**
   ```bash
   pkill -f dev_worker
   python -m apex_memory.temporal.workers.dev_worker
   ```

---

## Database Connection Issues

### Issue 4.1: PostgreSQL Pool Exhausted

**Symptom:**
```
asyncpg.exceptions.TooManyConnectionsError: sorry, too many clients already
```

**Diagnostic:**
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE datname='apex_memory';

-- Check connection limit
SHOW max_connections;
```

**Solution:**

1. **Increase pool size:**
   ```python
   # apex-memory-system/src/apex_memory/database/postgres_writer.py
   self.pool = await asyncpg.create_pool(
       min_size=5,
       max_size=20,  # Increase from 10
   )
   ```

2. **Close idle connections:**
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE datname='apex_memory' AND state='idle' AND state_change < NOW() - INTERVAL '5 minutes';
   ```

3. **Increase PostgreSQL limit:**
   ```bash
   # In docker-compose.yml
   postgres:
       command: postgres -c max_connections=200
   ```

---

### Issue 4.2: Qdrant Collection Not Found

**Symptom:**
```
QdrantException: Collection 'apex_structured_data' not found
```

**Diagnostic:**
```bash
# List collections
curl http://localhost:6333/collections

# Check collection exists
curl http://localhost:6333/collections/apex_structured_data
```

**Solution:**

1. **Create collection manually:**
   ```bash
   curl -X PUT http://localhost:6333/collections/apex_structured_data \
     -H "Content-Type: application/json" \
     -d '{
       "vectors": {
         "size": 1536,
         "distance": "Cosine"
       }
     }'
   ```

2. **Ensure _ensure_json_collection_exists() is called:**
   ```python
   # In qdrant_writer.py:write_json_record()
   self._ensure_json_collection_exists()  # Must be called first
   ```

---

### Issue 4.3: Neo4j Authentication Failed

**Symptom:**
```
Neo4jError: The client is unauthorized due to authentication failure
```

**Diagnostic:**
```bash
# Test connection
python3 -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'apexmemory2024')); driver.verify_connectivity()"
```

**Solution:**

1. **Reset Neo4j password:**
   ```bash
   docker exec -it neo4j-apex neo4j-admin set-initial-password apexmemory2024
   docker restart neo4j-apex
   ```

2. **Verify credentials in .env:**
   ```bash
   cat apex-memory-system/.env | grep NEO4J
   ```

---

## Staging Issues

### Issue 5.1: Disk Space Exhausted

**Symptom:**
```
OSError: [Errno 28] No space left on device
```

**Diagnostic:**
```bash
# Check staging disk usage
du -sh /tmp/apex-staging/

# Check total disk usage
df -h /tmp
```

**Solution:**

1. **Manual cleanup:**
   ```bash
   # Remove old staging folders (>24 hours)
   find /tmp/apex-staging/ -type d -mtime +1 -exec rm -rf {} +
   ```

2. **Run cleanup manager:**
   ```python
   from apex_memory.services.staging_manager import StagingManager

   manager = StagingManager()
   cleaned = manager.cleanup_old_failed_ingestions()
   print(f"Cleaned {cleaned} folders")
   ```

3. **Reduce retention period:**
   ```bash
   # In .env
   STAGING_FAILED_RETENTION_HOURS=12  # Reduce from 24
   ```

---

### Issue 5.2: Staging Cleanup Fails

**Symptom:**
- Staging folders not removed after successful ingestion
- `/tmp/apex-staging/` grows continuously

**Diagnostic:**
```bash
# Check cleanup activity logs
grep "cleanup_staging_activity" apex-memory-system/logs/worker.log

# Check permissions
ls -la /tmp/apex-staging/
```

**Cause:** cleanup_staging_activity not called in workflow

**Solution:**

1. **Verify workflow includes cleanup:**
   ```python
   # In DocumentIngestionWorkflow
   await workflow.execute_activity(
       cleanup_staging_activity,  # Must be called
       args=[self.staging_path],
   )
   ```

2. **Check cleanup succeeds:**
   ```bash
   pytest tests/unit/test_cleanup_staging_activity.py -v
   ```

---

## JSON Ingestion Issues

### Issue 6.1: Graphiti JSON Extraction Returns Empty

**Symptom:**
```python
result['entities'] == []
# But JSON has clear entities
```

**Diagnostic:**
```python
# Test Graphiti directly
result = await graphiti.add_json_episode(
    json_id='test',
    json_data={'shipment_id': 'SHIP-123', 'customer': 'Acme Corp'},
)
print(f"Entities: {result.entities_extracted}")
```

**Cause:** JSON not converted to readable text for LLM

**Solution:**

1. **Improve text representation:**
   ```python
   # In extract_entities_from_json_activity
   # Convert JSON to natural language
   if data_type == "shipment":
       text = f"Shipment {raw_json['shipment_id']} from {raw_json['origin']} to {raw_json['destination']}"
   ```

2. **Provide context to Graphiti:**
   ```python
   result = await graphiti.add_json_episode(
       json_data=raw_json,
       metadata={
           'source': 'turvo',
           'context': 'This is shipment tracking data'  # Add context
       }
   )
   ```

---

### Issue 6.2: PostgreSQL JSONB Column Error

**Symptom:**
```sql
ERROR: column "raw_json" does not exist
```

**Diagnostic:**
```sql
-- Check table exists
\d structured_data

-- Check column type
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name='structured_data';
```

**Solution:**

1. **Run migration:**
   ```bash
   PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -f schemas/postgres_structured_data.sql
   ```

2. **Verify table:**
   ```sql
   \d structured_data
   -- Should show: raw_json | jsonb
   ```

---

## Debugging Tools

### Temporal UI

**URL:** http://localhost:8088

**Features:**
- View workflow execution history
- See activity retry attempts
- Inspect workflow state
- Cancel stuck workflows

### Neo4j Browser

**URL:** http://localhost:7474

**Useful Queries:**
```cypher
// Count Graphiti episodes
MATCH (e:Episode) RETURN count(e)

// Find orphaned episodes
MATCH (e:Episode)
WHERE NOT (e)<-[:HAS_EPISODE]-(:Document)
RETURN e LIMIT 10

// View recent entities
MATCH (e:Entity)
RETURN e.name, e.created_at
ORDER BY e.created_at DESC
LIMIT 20
```

### Prometheus Queries

**URL:** http://localhost:9090

**Useful Queries:**
```promql
# Graphiti extraction rate
rate(apex_temporal_entities_per_document_count[5m])

# Saga rollback rate
rate(apex_temporal_saga_rollback_total{database="graphiti"}[5m])

# Staging cleanup rate
rate(apex_temporal_staging_cleanups_total[5m])
```

### Grafana Dashboard

**URL:** http://localhost:3001/d/temporal-ingestion

**Panels to Watch:**
- Workflow Execution Rate
- Activity Success Rate
- Graphiti Entity Extraction
- Staging Operations

### Log Analysis

```bash
# Tail worker logs
tail -f apex-memory-system/logs/worker.log

# Search for errors
grep "ERROR" apex-memory-system/logs/worker.log | tail -20

# Search for Graphiti issues
grep "Graphiti" apex-memory-system/logs/worker.log | grep -E "ERROR|WARN"

# Search for rollback events
grep "Rolled back Graphiti episode" apex-memory-system/logs/worker.log
```

### Python REPL Debugging

```python
# Test Graphiti service
from apex_memory.services.graphiti_service import GraphitiService
from apex_memory.config.settings import Settings

settings = Settings()
graphiti = GraphitiService(
    neo4j_uri=settings.neo4j_uri,
    neo4j_user=settings.neo4j_user,
    neo4j_password=settings.neo4j_password,
)

# Test extraction
import asyncio
result = asyncio.run(graphiti.add_document_episode(
    document_uuid='test-123',
    document_title='Test',
    document_content='John Smith works at Acme Corp',
    document_type='test'
))

print(f"Success: {result.success}")
print(f"Entities: {result.entities_extracted}")
```

---

## Getting Help

**If issue persists:**

1. **Check logs:**
   - Worker logs: `apex-memory-system/logs/worker.log`
   - Temporal server logs: `docker logs temporal`
   - Database logs: `docker logs neo4j-apex`, `docker logs postgres-apex`

2. **Run diagnostics:**
   ```bash
   python3 scripts/temporal/worker-health-check.sh
   ```

3. **Check documentation:**
   - IMPLEMENTATION.md for step-by-step guide
   - TESTING.md for test specifications
   - Research references for official docs

4. **Search existing issues:**
   - Graphiti: https://github.com/getzep/graphiti/issues
   - Temporal: https://github.com/temporalio/temporal/issues

5. **Create issue report:**
   - Include error message
   - Include relevant logs
   - Include steps to reproduce
   - Include environment details

---

**Document Version:** 1.0
**Last Updated:** 2025-10-19
**Author:** Claude Code
**Status:** Living Document (will be updated as new issues discovered)
