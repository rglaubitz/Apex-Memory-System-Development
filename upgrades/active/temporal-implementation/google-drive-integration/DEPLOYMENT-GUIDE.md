# Google Drive Integration - Production Deployment Guide

**Author:** Apex Infrastructure Team
**Created:** November 7, 2025 (Week 4 Day 2)
**Version:** 1.0

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google Cloud Setup](#google-cloud-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Temporal Configuration](#temporal-configuration)
6. [Worker Deployment](#worker-deployment)
7. [Monitoring & Alerting](#monitoring--alerting)
8. [Verification](#verification)
9. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### System Requirements

- **Python:** 3.11+ (tested with 3.11, 3.12)
- **PostgreSQL:** 14+ (for processed files tracking and DLQ)
- **Temporal Server:** 1.22+ (workflow orchestration)
- **Prometheus:** Latest (metrics collection)
- **Alertmanager:** Latest (alert routing)

### Network Requirements

- **Google Drive API:** HTTPS outbound to `www.googleapis.com`
- **Temporal Server:** gRPC connection to Temporal cluster
- **PostgreSQL:** TCP connection to database
- **Prometheus:** HTTP endpoint for metrics scraping

### Access Requirements

- **Google Cloud Console** access (to create service account)
- **Google Drive folder** with Editor permissions
- **PostgreSQL** database with CREATE TABLE permissions
- **Temporal cluster** access (namespace: `default`)

---

## Google Cloud Setup

### Step 1: Create Service Account

1. **Navigate to Google Cloud Console:**
   - Go to: https://console.cloud.google.com
   - Select your project (or create new project)

2. **Create Service Account:**
   ```
   IAM & Admin → Service Accounts → Create Service Account

   Service account name: apex-google-drive-monitor
   Service account ID: apex-google-drive-monitor
   Description: Service account for Apex Memory System Google Drive monitoring

   Click: CREATE AND CONTINUE
   ```

3. **Grant Roles (Optional):**
   - For this use case, no GCP roles are needed
   - Permissions are managed at Google Drive folder level
   - Click: CONTINUE → DONE

4. **Create Key:**
   ```
   Click on service account → Keys → Add Key → Create new key
   Key type: JSON
   Click: CREATE
   ```

   **⚠️ Important:** Download will start automatically. Save as `google-drive-service-account.json`

### Step 2: Share Google Drive Folder

1. **Open Google Drive:**
   - Navigate to the folder you want to monitor
   - Right-click → Share

2. **Add Service Account:**
   ```
   Email: apex-google-drive-monitor@YOUR_PROJECT_ID.iam.gserviceaccount.com

   Permission: Viewer (for read-only monitoring)
            OR Editor (if you want to archive/move files)

   Uncheck: Notify people

   Click: Share
   ```

3. **Get Folder ID:**
   ```
   Open folder in Google Drive web UI
   URL: https://drive.google.com/drive/folders/1abc...xyz
                                                  ^^^^^^^^^^^^
                                                  This is folder_id

   Save this folder_id for configuration
   ```

### Step 3: Enable Google Drive API

1. **Navigate to APIs & Services:**
   ```
   APIs & Services → Library
   Search: "Google Drive API"
   Click: Google Drive API
   Click: ENABLE
   ```

2. **Verify API Enabled:**
   ```
   APIs & Services → Enabled APIs
   Confirm: "Google Drive API" is listed
   ```

---

## Environment Configuration

### Step 1: Prepare Service Account Key

```bash
# Convert JSON key to single-line string (for .env file)
cat google-drive-service-account.json | jq -c . > google-drive-service-account-oneline.json

# Copy contents
cat google-drive-service-account-oneline.json
```

### Step 2: Configure Environment Variables

**File:** `.env`

```bash
# ========================================
# Google Drive Configuration
# ========================================

# Enable Google Drive monitoring
GOOGLE_DRIVE_ENABLED=true

# Service account key (JSON as single-line string)
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY='{"type":"service_account","project_id":"...","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"apex-google-drive-monitor@....iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"...","universe_domain":"googleapis.com"}'

# Folder to monitor (from Step 2 of Google Cloud Setup)
GOOGLE_DRIVE_MONITOR_FOLDER_ID=1abc...xyz

# ========================================
# Temporal Configuration
# ========================================

# Temporal cluster address
TEMPORAL_HOST=localhost
TEMPORAL_PORT=7233
TEMPORAL_NAMESPACE=default

# Task queue for Google Drive workflows
TEMPORAL_TASK_QUEUE=apex-ingestion-queue

# ========================================
# PostgreSQL Configuration
# ========================================

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=apex_memory
POSTGRES_USER=apex
POSTGRES_PASSWORD=apexmemory2024

# ========================================
# Monitoring Configuration
# ========================================

# Prometheus metrics port
PROMETHEUS_PORT=9090

# Alertmanager
ALERTMANAGER_URL=http://localhost:9093
```

### Step 3: Validate Configuration

```bash
# Test service account authentication
python scripts/dev/test_google_drive.py --folder-id "${GOOGLE_DRIVE_MONITOR_FOLDER_ID}"

# Expected output:
# ✓ Google Drive service initialized
# ✓ Service account authenticated
# ✓ Folder accessible: YOUR_FOLDER_NAME
# ✓ Found X files in folder
```

---

## Database Setup

### Step 1: Create PostgreSQL Tables

The monitoring system requires two PostgreSQL tables:

1. **google_drive_processed_files** - Track successfully processed files
2. **google_drive_dead_letter_queue** - Track permanently failed files

**Automatic Creation:**
Tables are created automatically by activities on first run (idempotent CREATE TABLE IF NOT EXISTS).

**Manual Creation (Optional):**

```sql
-- Connect to PostgreSQL
psql -U apex -d apex_memory

-- Create processed files table
CREATE TABLE IF NOT EXISTS google_drive_processed_files (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) NOT NULL UNIQUE,
    file_name VARCHAR(500) NOT NULL,
    modified_time TIMESTAMP NOT NULL,
    processed_at TIMESTAMP NOT NULL,
    document_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_processed_files_file_id
ON google_drive_processed_files(file_id);

-- Create Dead Letter Queue table
CREATE TABLE IF NOT EXISTS google_drive_dead_letter_queue (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    folder_id VARCHAR(255) NOT NULL,
    error_message TEXT NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    retry_count INTEGER NOT NULL,
    metadata JSONB,
    failed_at TIMESTAMP NOT NULL,
    reprocessed BOOLEAN DEFAULT FALSE,
    reprocessed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(file_id, failed_at)
);

CREATE INDEX IF NOT EXISTS idx_dlq_file_id
ON google_drive_dead_letter_queue(file_id);

CREATE INDEX IF NOT EXISTS idx_dlq_error_type
ON google_drive_dead_letter_queue(error_type);

CREATE INDEX IF NOT EXISTS idx_dlq_reprocessed
ON google_drive_dead_letter_queue(reprocessed);
```

### Step 2: Verify Tables Created

```sql
-- List tables
\dt

-- Check google_drive_processed_files schema
\d google_drive_processed_files

-- Check google_drive_dead_letter_queue schema
\d google_drive_dead_letter_queue

-- Verify indexes
\di
```

---

## Temporal Configuration

### Step 1: Register Worker Workflows

The worker must be running to process workflows. Workflows/activities to register:

**Workflows:**
- `GoogleDriveMonitorWorkflow` - Main monitoring workflow
- `DocumentIngestionWorkflow` - Triggered for each new file
- `GoogleDriveArchiveWorkflow` - Archive processed files

**Activities:**
- `poll_google_drive_folder_activity`
- `mark_file_as_processed_activity`
- `add_to_dead_letter_queue_activity`
- `mark_dlq_file_reprocessed_activity`
- `get_dlq_files_activity`

**Worker File:** `src/apex_memory/temporal/workers/dev_worker.py`

### Step 2: Create Temporal Schedule

**Production Schedule:** Runs every 15 minutes

```python
# File: scripts/temporal/create_monitor_schedule.py

from temporalio.client import Client, ScheduleActionStartWorkflow, ScheduleSpec, ScheduleIntervalSpec
from datetime import timedelta
import asyncio
import os

async def create_schedule():
    # Connect to Temporal
    client = await Client.connect(
        f"{os.getenv('TEMPORAL_HOST')}:{os.getenv('TEMPORAL_PORT')}",
        namespace=os.getenv('TEMPORAL_NAMESPACE', 'default')
    )

    # Get folder ID from environment
    folder_id = os.getenv('GOOGLE_DRIVE_MONITOR_FOLDER_ID')
    if not folder_id:
        raise ValueError("GOOGLE_DRIVE_MONITOR_FOLDER_ID not set in .env")

    # Create schedule
    schedule = await client.create_schedule(
        id="monitor-google-drive-schedule",
        schedule=ScheduleSpec(
            intervals=[ScheduleIntervalSpec(every=timedelta(minutes=15))]
        ),
        action=ScheduleActionStartWorkflow(
            "GoogleDriveMonitorWorkflow",
            args=[folder_id, None, 100],  # folder_id, modified_after, max_results
            id=f"monitor-google-drive-{folder_id}",
            task_queue=os.getenv('TEMPORAL_TASK_QUEUE', 'apex-ingestion-queue')
        )
    )

    print(f"✓ Schedule created: {schedule.id}")
    print(f"  Folder: {folder_id}")
    print(f"  Interval: Every 15 minutes")
    print(f"  Task queue: {os.getenv('TEMPORAL_TASK_QUEUE')}")

if __name__ == "__main__":
    asyncio.run(create_schedule())
```

**Execute:**

```bash
# Load environment variables
source .env

# Create schedule
python scripts/temporal/create_monitor_schedule.py

# Verify schedule created
temporal schedule list

# Expected output:
# Schedule ID: monitor-google-drive-schedule
# Workflow Type: GoogleDriveMonitorWorkflow
# Next Run: [timestamp]
```

### Step 3: Configure Schedule Options

**Overlap Policy:** Buffer new runs (default)
- If previous run still executing, queue next run
- Prevents concurrent monitor workflows for same folder

**Pause on Failure:** No (default)
- Continue scheduling even if individual runs fail
- Failures tracked in Temporal UI and Prometheus alerts

**Timezone:** UTC (recommended for distributed systems)

---

## Worker Deployment

### Production Worker Configuration

**File:** `src/apex_memory/temporal/workers/prod_worker.py` (create from dev_worker.py)

```python
"""Production Temporal Worker for Apex Memory System.

Differences from dev_worker.py:
- No hot reload
- Structured logging to JSON
- Error reporting to Sentry (optional)
- Health check endpoint
"""

import asyncio
import logging
import signal
from temporalio.client import Client
from temporalio.worker import Worker

# Import workflows
from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow
from apex_memory.temporal.workflows.google_drive_monitor import GoogleDriveMonitorWorkflow
from apex_memory.temporal.workflows.google_drive_archive import GoogleDriveArchiveWorkflow

# Import activities
from apex_memory.temporal.activities.ingestion import (
    pull_and_stage_document_activity,
    parse_document_activity,
    extract_entities_activity,
    generate_embeddings_activity,
    write_to_databases_activity,
    cleanup_staging_activity,
)
from apex_memory.temporal.activities.google_drive_monitor import (
    poll_google_drive_folder_activity,
    mark_file_as_processed_activity,
)
from apex_memory.temporal.activities.google_drive_error_handling import (
    add_to_dead_letter_queue_activity,
    mark_dlq_file_reprocessed_activity,
    get_dlq_files_activity,
)
from apex_memory.temporal.activities.google_drive_archive import (
    determine_archive_folder_activity,
    upload_to_google_drive_activity,
    verify_upload_activity,
    record_archive_metadata_activity,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S%z'
)
logger = logging.getLogger(__name__)


async def main():
    # Connect to Temporal
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost")
    temporal_port = os.getenv("TEMPORAL_PORT", "7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "apex-ingestion-queue")

    logger.info(f"Connecting to Temporal: {temporal_host}:{temporal_port}")

    client = await Client.connect(
        f"{temporal_host}:{temporal_port}",
        namespace=temporal_namespace
    )

    logger.info(f"Starting worker on task queue: {task_queue}")

    # Create worker
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[
            DocumentIngestionWorkflow,
            GoogleDriveMonitorWorkflow,
            GoogleDriveArchiveWorkflow,
        ],
        activities=[
            # Ingestion activities
            pull_and_stage_document_activity,
            parse_document_activity,
            extract_entities_activity,
            generate_embeddings_activity,
            write_to_databases_activity,
            cleanup_staging_activity,
            # Google Drive monitoring activities
            poll_google_drive_folder_activity,
            mark_file_as_processed_activity,
            # Error handling activities
            add_to_dead_letter_queue_activity,
            mark_dlq_file_reprocessed_activity,
            get_dlq_files_activity,
            # Archive activities
            determine_archive_folder_activity,
            upload_to_google_drive_activity,
            verify_upload_activity,
            record_archive_metadata_activity,
        ],
    )

    logger.info("Worker started successfully")
    logger.info("Waiting for workflows and activities...")

    # Graceful shutdown
    stop_event = asyncio.Event()

    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}. Shutting down gracefully...")
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run worker until stop signal
    await asyncio.gather(
        worker.run(),
        stop_event.wait()
    )

    logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
```

### Deployment Methods

#### Option 1: Systemd Service (Linux)

**File:** `/etc/systemd/system/apex-temporal-worker.service`

```ini
[Unit]
Description=Apex Memory System Temporal Worker
After=network.target postgresql.service

[Service]
Type=simple
User=apex
Group=apex
WorkingDirectory=/opt/apex-memory-system
EnvironmentFile=/opt/apex-memory-system/.env
ExecStart=/opt/apex-memory-system/venv/bin/python src/apex_memory/temporal/workers/prod_worker.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Commands:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable apex-temporal-worker

# Start service
sudo systemctl start apex-temporal-worker

# Check status
sudo systemctl status apex-temporal-worker

# View logs
sudo journalctl -u apex-temporal-worker -f
```

#### Option 2: Docker Container

**File:** `docker/Dockerfile.worker`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/

# Set environment
ENV PYTHONPATH=/app/src

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run worker
CMD ["python", "src/apex_memory/temporal/workers/prod_worker.py"]
```

**Commands:**

```bash
# Build image
docker build -f docker/Dockerfile.worker -t apex-temporal-worker:latest .

# Run container
docker run -d \
  --name apex-temporal-worker \
  --env-file .env \
  --network apex-network \
  --restart unless-stopped \
  apex-temporal-worker:latest

# View logs
docker logs -f apex-temporal-worker

# Check health
docker inspect --format='{{.State.Health.Status}}' apex-temporal-worker
```

#### Option 3: Kubernetes Deployment

**File:** `k8s/worker-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apex-temporal-worker
  namespace: apex-memory
spec:
  replicas: 2
  selector:
    matchLabels:
      app: apex-temporal-worker
  template:
    metadata:
      labels:
        app: apex-temporal-worker
    spec:
      containers:
      - name: worker
        image: apex-temporal-worker:latest
        envFrom:
        - configMapRef:
            name: apex-config
        - secretRef:
            name: apex-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 30
          periodSeconds: 30
```

**Commands:**

```bash
# Apply deployment
kubectl apply -f k8s/worker-deployment.yaml

# Check status
kubectl get pods -n apex-memory

# View logs
kubectl logs -f -n apex-memory deployment/apex-temporal-worker

# Scale workers
kubectl scale deployment apex-temporal-worker --replicas=4 -n apex-memory
```

---

## Monitoring & Alerting

### Step 1: Configure Prometheus Scraping

**File:** `monitoring/prometheus.yml`

```yaml
scrape_configs:
  - job_name: 'apex-memory-api'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
    scrape_timeout: 10s
```

### Step 2: Load Alert Rules

```bash
# Copy alert rules to Prometheus configuration
cp monitoring/alerts/google_drive_monitoring_rules.yml /etc/prometheus/rules/

# Update prometheus.yml
# Add under rule_files:
rule_files:
  - 'rules/google_drive_monitoring_rules.yml'

# Reload Prometheus configuration
curl -X POST http://localhost:9090/-/reload

# Or restart Prometheus
sudo systemctl restart prometheus
```

### Step 3: Configure Alertmanager

**File:** `/etc/alertmanager/alertmanager.yml`

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourcompany.com'
  smtp_auth_username: 'alerts@yourcompany.com'
  smtp_auth_password: 'YOUR_PASSWORD'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-email'

  routes:
  - match:
      severity: critical
    receiver: 'pagerduty'
    continue: true

  - match:
      severity: warning
    receiver: 'slack'

receivers:
- name: 'team-email'
  email_configs:
  - to: 'team@yourcompany.com'

- name: 'pagerduty'
  pagerduty_configs:
  - service_key: 'YOUR_PAGERDUTY_KEY'

- name: 'slack'
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK'
    channel: '#apex-alerts'
```

---

## Verification

### Step 1: Test Schedule

```bash
# Trigger schedule manually (for testing)
temporal schedule trigger --schedule-id monitor-google-drive-schedule

# Check Temporal UI for workflow execution
# Open: http://localhost:8233
# Navigate to: Workflows → Filter by "GoogleDriveMonitorWorkflow"
```

### Step 2: Check Metrics

```bash
# Check if metrics are being recorded
curl http://localhost:9090/api/v1/query?query=apex_google_drive_monitor_polls_total

# Expected: {"status":"success","data":{"resultType":"vector","result":[...]}}
```

### Step 3: Verify Alerts

```bash
# Check alert rules loaded
curl http://localhost:9090/api/v1/rules

# Check active alerts
curl http://localhost:9090/api/v1/alerts
```

### Step 4: Test File Processing

```bash
# Upload test file to Google Drive folder
# (Use Google Drive web UI)

# Wait for next scheduled run (up to 15 minutes)
# Or trigger manually:
temporal schedule trigger --schedule-id monitor-google-drive-schedule

# Check processed files table
psql -U apex -d apex_memory -c "SELECT * FROM google_drive_processed_files ORDER BY processed_at DESC LIMIT 10;"

# Check Temporal UI for DocumentIngestionWorkflow execution
```

---

## Rollback Procedures

### Rollback Worker

```bash
# Systemd
sudo systemctl stop apex-temporal-worker
sudo systemctl disable apex-temporal-worker

# Docker
docker stop apex-temporal-worker
docker rm apex-temporal-worker

# Kubernetes
kubectl delete deployment apex-temporal-worker -n apex-memory
```

### Pause Schedule

```bash
# Pause schedule (stop monitoring)
temporal schedule toggle --schedule-id monitor-google-drive-schedule --pause

# Resume schedule
temporal schedule toggle --schedule-id monitor-google-drive-schedule --unpause
```

### Delete Schedule

```bash
# Delete schedule completely
temporal schedule delete --schedule-id monitor-google-drive-schedule

# Confirm deletion
temporal schedule list
```

### Remove Database Tables

```sql
-- Drop tables (careful! data loss)
DROP TABLE IF EXISTS google_drive_dead_letter_queue;
DROP TABLE IF EXISTS google_drive_processed_files;
```

---

## Production Checklist

Before going to production:

- [ ] Google service account created and key downloaded
- [ ] Google Drive folder shared with service account
- [ ] Google Drive API enabled in GCP project
- [ ] Environment variables configured in `.env`
- [ ] PostgreSQL tables created
- [ ] Temporal schedule created
- [ ] Worker deployed (systemd/Docker/k8s)
- [ ] Worker running and registered (check Temporal UI)
- [ ] Prometheus scraping metrics
- [ ] Alert rules loaded in Prometheus
- [ ] Alertmanager configured (email/Slack/PagerDuty)
- [ ] Test file processed successfully
- [ ] Monitoring dashboard created (Grafana)
- [ ] Team trained on troubleshooting runbook
- [ ] Rollback procedures documented and tested

---

**Deployment Status:** Ready for production with monitoring, alerting, and error handling.
