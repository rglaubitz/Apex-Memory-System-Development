# Google Drive Monitoring - Troubleshooting Runbook

**Author:** Apex Infrastructure Team
**Created:** November 7, 2025 (Week 4 Day 1)
**Version:** 1.0

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues](#common-issues)
3. [Monitor Workflow Issues](#monitor-workflow-issues)
4. [File Processing Failures](#file-processing-failures)
5. [Dead Letter Queue Management](#dead-letter-queue-management)
6. [Performance Issues](#performance-issues)
7. [Database Queries](#database-queries)
8. [Recovery Procedures](#recovery-procedures)

---

## Quick Diagnostics

### Health Check Commands

```bash
# 1. Check all services
python scripts/dev/health_check.py -v

# 2. Check Temporal worker
python scripts/temporal/worker-health-check.sh

# 3. Check monitor workflow status
python scripts/temporal/check-workflow-status.py --workflow-id "monitor-google-drive-folder"

# 4. Check recent failures
python scripts/temporal/list-failed-workflows.py --workflow-type "GoogleDriveMonitorWorkflow"

# 5. Check Prometheus metrics
curl http://localhost:9090/api/v1/query?query=apex_google_drive_monitor_polls_total
```

### Quick Status Check

```sql
-- Check recent monitor activity (PostgreSQL)
SELECT
    COUNT(*) FILTER (WHERE processed_at > NOW() - INTERVAL '1 hour') as last_hour,
    COUNT(*) FILTER (WHERE processed_at > NOW() - INTERVAL '24 hours') as last_day,
    MAX(processed_at) as last_processed
FROM google_drive_processed_files;

-- Check Dead Letter Queue size
SELECT
    COUNT(*) as total_dlq,
    COUNT(*) FILTER (WHERE reprocessed = FALSE) as pending_dlq,
    error_type,
    COUNT(*) as count
FROM google_drive_dead_letter_queue
WHERE reprocessed = FALSE
GROUP BY error_type
ORDER BY count DESC;
```

### Temporal UI

Open: http://localhost:8233

- View workflow execution history
- Check failed workflows
- Query workflow status
- View activity retries

---

## Common Issues

### Issue 1: Monitor Workflow Not Running

**Symptoms:**
- No new files detected in last 30+ minutes
- `apex_google_drive_monitor_polls_total` not increasing
- No recent entries in `google_drive_processed_files`

**Possible Causes:**
1. Temporal worker is down
2. Scheduled workflow is paused
3. Worker is not registered for monitor workflow

**Diagnosis:**

```bash
# Check if worker is running
ps aux | grep dev_worker.py

# Check Temporal schedules
temporal schedule list

# Check workflow registration in Temporal
temporal workflow describe --workflow-id "monitor-google-drive-folder"
```

**Resolution:**

```bash
# 1. Restart Temporal worker
killall python
python src/apex_memory/temporal/workers/dev_worker.py &

# 2. Verify schedule exists
temporal schedule describe --schedule-id "monitor-google-drive-schedule"

# 3. If schedule doesn't exist, create it:
python scripts/temporal/create_monitor_schedule.py --folder-id "YOUR_FOLDER_ID"

# 4. Trigger manual run (for testing)
temporal workflow start \
  --type "GoogleDriveMonitorWorkflow" \
  --task-queue "apex-ingestion-queue" \
  --workflow-id "test-monitor-once" \
  --input '["YOUR_FOLDER_ID", null, 100]'
```

---

### Issue 2: Google Drive Authentication Failed

**Symptoms:**
- Monitor workflow fails with "permission denied" or "unauthorized"
- `apex_google_drive_monitor_polls_total{status="failed"}` increasing

**Possible Causes:**
1. Service account key is invalid or expired
2. Service account doesn't have access to folder
3. OAuth scopes are insufficient

**Diagnosis:**

```bash
# Check service account configuration
python -c "
from apex_memory.config import get_settings
settings = get_settings()
print(f'Google Drive enabled: {settings.google_drive_enabled}')
print(f'Service account key configured: {bool(settings.google_drive_service_account_key)}')
"

# Test Google Drive connectivity
python scripts/dev/test_google_drive.py --folder-id "YOUR_FOLDER_ID"
```

**Resolution:**

1. **Verify service account key:**
   ```bash
   # Check .env file
   grep GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY .env

   # Key should be valid JSON (starts with {"type": "service_account", ...})
   ```

2. **Verify folder permissions:**
   - Open Google Drive folder in web browser
   - Share folder with service account email: `service-account@project.iam.gserviceaccount.com`
   - Grant "Viewer" or "Editor" permissions

3. **Regenerate service account key (if expired):**
   - Go to Google Cloud Console
   - Navigate to IAM & Admin → Service Accounts
   - Select service account → Keys → Add Key → Create new key
   - Download JSON key
   - Update `.env`: `GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY='<json content>'`

---

### Issue 3: All Files Failing Ingestion

**Symptoms:**
- `apex_google_drive_files_failed_total` increasing rapidly
- Most/all files in Dead Letter Queue
- Monitor workflow status = "partial" or "failed"

**Possible Causes:**
1. DocumentIngestionWorkflow is broken
2. Databases are down (Neo4j, PostgreSQL, Qdrant, Redis)
3. OpenAI API is failing
4. Docling parser error

**Diagnosis:**

```bash
# 1. Check all database services
python scripts/dev/health_check.py -v

# 2. Check DocumentIngestionWorkflow
temporal workflow describe --workflow-id "ingest-drive-FILE_ID"

# 3. Check DLQ for error patterns
psql -U apex -d apex_memory -c "
SELECT error_type, error_message, COUNT(*)
FROM google_drive_dead_letter_queue
WHERE failed_at > NOW() - INTERVAL '1 hour'
GROUP BY error_type, error_message
ORDER BY COUNT(*) DESC
LIMIT 10;
"

# 4. Test ingestion manually
python -c "
from temporalio.client import Client
import asyncio

async def test():
    client = await Client.connect('localhost:7233')
    result = await client.execute_workflow(
        'DocumentIngestionWorkflow',
        args=['test-doc-123', 'google_drive', 'FILE_ID', None],
        id='test-ingest',
        task_queue='apex-ingestion-queue'
    )
    print(result)

asyncio.run(test())
"
```

**Resolution:**

1. **If databases are down:**
   ```bash
   cd docker && docker-compose up -d
   # Wait 30-60 seconds for services to be ready
   python scripts/dev/health_check.py -v
   ```

2. **If OpenAI API failing:**
   ```bash
   # Check OpenAI API key
   grep OPENAI_API_KEY .env

   # Test OpenAI connectivity
   python -c "
   import openai
   from apex_memory.config import get_settings
   settings = get_settings()
   client = openai.OpenAI(api_key=settings.openai_api_key)
   response = client.embeddings.create(input='test', model='text-embedding-3-small')
   print('OpenAI API working')
   "
   ```

3. **If Docling parser failing:**
   - Check Docling version: `pip show docling`
   - Review file types in DLQ (corrupted files?)
   - Test specific file manually

---

## Monitor Workflow Issues

### Monitor Workflow Stuck in "polling" Status

**Diagnosis:**

```bash
# Check workflow status
temporal workflow query \
  --workflow-id "monitor-google-drive-folder" \
  --query-type "get_status"

# Check if poll activity is hanging
temporal workflow describe --workflow-id "monitor-google-drive-folder"
```

**Resolution:**

```bash
# 1. Cancel stuck workflow
temporal workflow cancel --workflow-id "monitor-google-drive-folder"

# 2. Wait for scheduled workflow to restart (or trigger manually)
temporal schedule trigger --schedule-id "monitor-google-drive-schedule"

# 3. If issue persists, check poll activity logs
grep "poll_google_drive_folder_activity" logs/apex-memory.log | tail -n 50
```

---

### Monitor Workflow Timing Out

**Symptoms:**
- Workflow status = "failed" with timeout error
- `apex_google_drive_monitor_duration_seconds` > 600s (10 minutes)

**Possible Causes:**
- Too many files in folder (>100)
- DocumentIngestionWorkflow taking too long per file
- Network latency to Google Drive API

**Resolution:**

1. **Increase workflow timeout:**
   ```python
   # Update schedule with longer timeout
   await client.create_schedule(
       # ... other params ...
       action=ScheduleActionStartWorkflow(
           # ... other params ...
           execution_timeout=timedelta(minutes=30),  # Increase from 10
       )
   )
   ```

2. **Reduce max_results:**
   ```python
   # Process fewer files per poll
   args=["FOLDER_ID", None, 50],  # Reduce from 100 to 50
   ```

3. **Optimize DocumentIngestionWorkflow:**
   - Check database write performance
   - Review Docling parsing time
   - Consider increasing parallelism

---

## File Processing Failures

### Specific Files Always Failing

**Diagnosis:**

```sql
-- Find files that failed multiple times
SELECT file_id, file_name, error_type, error_message, retry_count
FROM google_drive_dead_letter_queue
WHERE reprocessed = FALSE
ORDER BY retry_count DESC, failed_at DESC
LIMIT 20;
```

**Resolution:**

1. **For "not_found" errors:**
   - File was deleted from Google Drive
   - Mark as reprocessed to ignore:
     ```sql
     UPDATE google_drive_dead_letter_queue
     SET reprocessed = TRUE, reprocessed_at = NOW()
     WHERE file_id = 'FILE_ID';
     ```

2. **For "permission_denied" errors:**
   - Service account lost access
   - Re-share folder with service account
   - Reprocess from DLQ after fixing

3. **For "invalid_request" errors:**
   - File ID is malformed
   - Investigate how file was added to processed queue
   - Mark as reprocessed if unfixable

4. **For "timeout" errors (retryable):**
   - File is very large or processing is slow
   - Increase DocumentIngestionWorkflow timeout
   - Retry from DLQ

---

### High Failure Rate for Specific File Type

**Diagnosis:**

```sql
-- Check DLQ by MIME type
SELECT
    metadata->>'mime_type' as mime_type,
    error_type,
    COUNT(*)
FROM google_drive_dead_letter_queue
WHERE reprocessed = FALSE
GROUP BY metadata->>'mime_type', error_type
ORDER BY COUNT(*) DESC;
```

**Resolution:**

1. **Unsupported file types:**
   - Add MIME type to DocumentParser supported types
   - Or filter these files in poll activity

2. **Corrupted files:**
   - Try downloading file manually
   - Check file integrity
   - Consider skipping these files

---

## Dead Letter Queue Management

### Query DLQ for Investigation

```sql
-- All unprocessed DLQ entries
SELECT * FROM google_drive_dead_letter_queue
WHERE reprocessed = FALSE
ORDER BY failed_at DESC;

-- DLQ by error type
SELECT error_type, COUNT(*), ARRAY_AGG(file_name)
FROM google_drive_dead_letter_queue
WHERE reprocessed = FALSE
GROUP BY error_type;

-- Recent DLQ entries (last hour)
SELECT * FROM google_drive_dead_letter_queue
WHERE failed_at > NOW() - INTERVAL '1 hour'
ORDER BY failed_at DESC;
```

### Reprocess Files from DLQ

```python
# Example: Reprocess file after fixing issue

import asyncio
from temporalio.client import Client

async def reprocess_file(file_id: str, folder_id: str):
    client = await Client.connect("localhost:7233")

    # Trigger DocumentIngestionWorkflow
    result = await client.execute_workflow(
        "DocumentIngestionWorkflow",
        args=[f"drive-{file_id}", "google_drive", file_id, None],
        id=f"reprocess-{file_id}",
        task_queue="apex-ingestion-queue",
    )

    if result["status"] == "success":
        # Mark as reprocessed in DLQ
        await client.execute_workflow(
            "mark_dlq_file_reprocessed_activity",
            args=[file_id, "FAILED_AT_TIMESTAMP"],
            id=f"mark-reprocessed-{file_id}",
            task_queue="apex-ingestion-queue",
        )
        print(f"✓ File {file_id} reprocessed successfully")
    else:
        print(f"✗ File {file_id} failed again: {result.get('error')}")

# Run for multiple files
file_ids = ["FILE_ID_1", "FILE_ID_2", "FILE_ID_3"]
for file_id in file_ids:
    asyncio.run(reprocess_file(file_id, "FOLDER_ID"))
```

### Bulk Reprocess from DLQ

```bash
# Get all DLQ entries
psql -U apex -d apex_memory -t -c "
SELECT file_id FROM google_drive_dead_letter_queue
WHERE reprocessed = FALSE AND error_type IN ('timeout', 'network_error');
" | while read file_id; do
    echo "Reprocessing $file_id"
    python scripts/temporal/reprocess_file.py --file-id "$file_id"
done
```

---

## Performance Issues

### Monitor Workflow Running Slowly

**Diagnosis:**

```promql
# Check P95 workflow duration
histogram_quantile(0.95,
  rate(apex_google_drive_monitor_duration_seconds_bucket[10m])
)

# Check average files detected per poll
avg_over_time(apex_google_drive_files_detected_total[1h])

# Check DocumentIngestionWorkflow duration
histogram_quantile(0.95,
  rate(apex_temporal_workflow_duration_seconds_bucket{workflow_type="DocumentIngestionWorkflow"}[10m])
)
```

**Resolution:**

1. **Too many files per poll:**
   - Reduce `max_results` from 100 to 50 or 25
   - Files will be processed across multiple polls

2. **Slow DocumentIngestionWorkflow:**
   - Check database query performance
   - Review Docling parsing time
   - Optimize embeddings generation
   - Consider caching

3. **Network latency:**
   - Check Google Drive API response times
   - Consider using pagination more aggressively

---

## Database Queries

### Check Processed Files

```sql
-- Total processed files
SELECT COUNT(*) FROM google_drive_processed_files;

-- Recent processed files
SELECT file_name, processed_at, document_id
FROM google_drive_processed_files
ORDER BY processed_at DESC
LIMIT 20;

-- Files processed per hour (last 24 hours)
SELECT
    DATE_TRUNC('hour', processed_at) as hour,
    COUNT(*) as files_processed
FROM google_drive_processed_files
WHERE processed_at > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', processed_at)
ORDER BY hour;
```

### Check Dead Letter Queue

```sql
-- DLQ summary
SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE reprocessed = FALSE) as pending,
    COUNT(*) FILTER (WHERE reprocessed = TRUE) as reprocessed
FROM google_drive_dead_letter_queue;

-- Error type breakdown
SELECT
    error_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM google_drive_dead_letter_queue
WHERE reprocessed = FALSE
GROUP BY error_type
ORDER BY count DESC;

-- Recent failures
SELECT
    file_name,
    error_type,
    error_message,
    retry_count,
    failed_at
FROM google_drive_dead_letter_queue
WHERE reprocessed = FALSE
ORDER BY failed_at DESC
LIMIT 20;
```

---

## Recovery Procedures

### Recover from Worker Crash

```bash
# 1. Check if worker is running
ps aux | grep dev_worker.py

# 2. If not, restart worker
python src/apex_memory/temporal/workers/dev_worker.py &

# 3. Verify worker registered
temporal worker list

# 4. Check for stuck workflows
temporal workflow list --workflow-type "GoogleDriveMonitorWorkflow" --query "ExecutionStatus='Running'"

# 5. If workflows stuck, cancel and let schedule restart
temporal workflow cancel --workflow-id "monitor-google-drive-folder"
```

### Recover from Database Outage

```bash
# 1. Restart databases
cd docker && docker-compose restart neo4j postgres qdrant redis

# 2. Wait for services to be ready (30-60 seconds)
python scripts/dev/health_check.py -v

# 3. Check for workflows that failed during outage
python scripts/temporal/list-failed-workflows.py --start-time "2025-11-07T10:00:00Z"

# 4. Retry failed workflows (Temporal will auto-retry retryable errors)
# Non-retryable errors will be in DLQ, reprocess manually
```

### Reprocess All Files in Folder

```python
# Emergency: Reprocess all files (ignore processed status)

import asyncio
from temporalio.client import Client

async def reprocess_folder(folder_id: str):
    client = await Client.connect("localhost:7233")

    # Trigger monitor workflow with force_reprocess flag
    result = await client.execute_workflow(
        "GoogleDriveMonitorWorkflow",
        args=[folder_id, None, 1000],  # Process up to 1000 files
        id=f"emergency-reprocess-{folder_id}",
        task_queue="apex-ingestion-queue",
    )

    print(f"Reprocess result: {result}")

asyncio.run(reprocess_folder("YOUR_FOLDER_ID"))
```

**Warning:** This will attempt to reprocess all files, including already-processed ones. Use only in emergencies.

---

## Contact & Escalation

**For critical issues:**
1. Check Temporal UI: http://localhost:8233
2. Review Prometheus alerts: http://localhost:9090/alerts
3. Check Grafana dashboards: http://localhost:3001
4. Escalate to infrastructure team

**Useful Resources:**
- Temporal documentation: https://docs.temporal.io
- Google Drive API docs: https://developers.google.com/drive/api
- Prometheus alerting: https://prometheus.io/docs/alerting/
- Project documentation: `../README.md`

---

**Runbook Version:** 1.0
**Last Updated:** November 7, 2025
**Maintainer:** Apex Infrastructure Team
