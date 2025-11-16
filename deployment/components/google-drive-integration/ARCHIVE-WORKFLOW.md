# Google Drive Archive Workflow - Deployment Addendum

**Feature:** Archive Processed Files to Google Cloud Storage
**Status:** ✅ Production Ready (Implemented Nov 7, 2025)
**Impact:** Medium - Long-term backup and storage
**Deployment Week:** Week 2 (with Google Drive Monitor)

---

## Overview

Google Drive Archive Workflow (`GoogleDriveArchiveWorkflow`) automatically archives ingested documents to Google Cloud Storage after successful processing, providing long-term backup and reducing Google Drive storage usage.

**Integration Point:** Triggered by `cleanup_staging_activity` after document ingestion completes

**Workflow Pipeline:**
1. Determine archive folder based on domain
2. Upload file to GCS
3. Verify upload succeeded
4. Record archive metadata in PostgreSQL

**Status Progression:** `pending → determining_folder → uploading → verifying → recording_metadata → completed`

**Dependencies:**
- Google Drive Monitor (already deployed)
- GCS bucket (`apex-document-archive`)
- Service account with GCS write permissions

---

## Prerequisites

This workflow extends the existing Google Drive Integration. Ensure the following are already deployed:

- ✅ Google Drive Monitor workflow (see main `DEPLOYMENT-GUIDE.md`)
- ✅ Google Cloud Service Account with Drive API access
- ✅ PostgreSQL database with processed files tracking

**New Requirements:**
- GCS bucket for document archival
- Service account permissions: `roles/storage.objectCreator`

---

## Setup Instructions

### Step 1: Create GCS Bucket

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1

# Create bucket
gcloud storage buckets create gs://apex-document-archive \
  --location=$REGION \
  --uniform-bucket-level-access

# Set lifecycle policy (transition to Coldline after 30 days)
cat > archive-lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [{
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {"age": 30}
    }]
  }
}
EOF

gcloud storage buckets update gs://apex-document-archive \
  --lifecycle-file=archive-lifecycle.json
```

### Step 2: Grant Service Account Permissions

```bash
# Get service account email (from Google Drive Monitor setup)
export SERVICE_ACCOUNT_EMAIL="apex-drive-monitor@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant storage permissions
gcloud storage buckets add-iam-policy-binding gs://apex-document-archive \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/storage.objectCreator"

gcloud storage buckets add-iam-policy-binding gs://apex-document-archive \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/storage.objectViewer"
```

### Step 3: Set Environment Variable

```bash
gcloud run services update apex-api \
  --region=$REGION \
  --update-env-vars="GCS_ARCHIVE_BUCKET=apex-document-archive"
```

### Step 4: Verify Workflow Registration

The Archive Workflow is automatically registered with the Temporal worker (same as Monitor workflow).

**Verify in Temporal UI:**
- Navigate to: http://localhost:8088 (or Temporal Cloud URL)
- Search workflows: `GoogleDriveArchiveWorkflow`
- Should appear in registered workflows list

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GCS_ARCHIVE_BUCKET` | Yes | `apex-document-archive` | GCS bucket for archival |

### Archive Folder Structure

Files are archived to GCS with this structure:
```
gs://apex-document-archive/
├── logistics/
│   ├── frontapp/
│   │   └── DOC-12345.pdf
│   └── google_drive/
│       └── DOC-67890.pdf
├── personal/
│   └── local_upload/
│       └── notes-2025-11.md
└── manufacturing/
    └── ...
```

---

## Deployment

### Production Checklist

- [ ] GCS bucket created (`apex-document-archive`)
- [ ] Lifecycle policy set (Coldline after 30 days)
- [ ] Service account has `roles/storage.objectCreator` and `objectViewer`
- [ ] Environment variable set (`GCS_ARCHIVE_BUCKET`)
- [ ] Workflow registered in Temporal worker
- [ ] Integration with cleanup activity verified

### Deployment Commands Summary

```bash
# 1. Create bucket and lifecycle policy (Step 1)
gcloud storage buckets create gs://apex-document-archive --location=us-central1 --uniform-bucket-level-access
gcloud storage buckets update gs://apex-document-archive --lifecycle-file=archive-lifecycle.json

# 2. Grant permissions (Step 2)
gcloud storage buckets add-iam-policy-binding gs://apex-document-archive \
  --member="serviceAccount:apex-drive-monitor@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectCreator"

# 3. Set env var (Step 3)
gcloud run services update apex-api --region=us-central1 --update-env-vars="GCS_ARCHIVE_BUCKET=apex-document-archive"
```

---

## Verification

### Test 1: Manual Archive Trigger

```bash
cd apex-memory-system
python -c "
from temporalio.client import Client
from apex_memory.temporal.workflows.google_drive_archive import GoogleDriveArchiveWorkflow
import asyncio

async def test():
    client = await Client.connect('localhost:7233')
    result = await client.execute_workflow(
        GoogleDriveArchiveWorkflow.run,
        args=[
            'DOC-TEST-001',
            '/tmp/test-document.pdf',
            'frontapp',
            'logistics'
        ],
        id='archive-test-001',
        task_queue='apex-ingestion-queue'
    )
    print(f'Archive result: {result}')

asyncio.run(test())
"

# Expected: {"status": "success", "document_id": "DOC-TEST-001", "file_id": "..."}
```

### Test 2: Verify GCS Upload

```bash
# List files in bucket
gcloud storage ls gs://apex-document-archive/logistics/frontapp/

# Should show: DOC-TEST-001.pdf

# Download and verify
gcloud storage cp gs://apex-document-archive/logistics/frontapp/DOC-TEST-001.pdf /tmp/verify.pdf
file /tmp/verify.pdf
# Should show: PDF document
```

### Test 3: Verify Archive Metadata

```bash
export PGPASSWORD=apexmemory2024
psql -h POSTGRES_IP -U apex -d apex_memory -c "
  SELECT document_id, source, gcs_path, archived_at
  FROM archive_metadata
  WHERE document_id = 'DOC-TEST-001';
"

# Should show archive metadata record
```

### Test 4: End-to-End Integration

Upload a file to Google Drive monitored folder and verify complete pipeline:

```bash
# 1. Upload test file to monitored folder
# (Use Google Drive web interface or Drive API)

# 2. Wait for monitor workflow to detect (up to 15 minutes)

# 3. Check workflow execution in Temporal UI
# Navigate to: Workflows → Filter by "google-drive"
# Should see: GoogleDriveMonitorWorkflow → GoogleDriveArchiveWorkflow (child workflow)

# 4. Verify file in GCS
gcloud storage ls gs://apex-document-archive/ --recursive | grep "your-filename"
```

---

## Troubleshooting

### Issue 1: Permission Denied on GCS Upload

**Symptom:** Workflow fails with "403 Forbidden" error

**Solution:**
```bash
# Verify service account has correct roles
gcloud storage buckets get-iam-policy gs://apex-document-archive

# Should show:
# - roles/storage.objectCreator
# - roles/storage.objectViewer

# If missing, re-grant:
gcloud storage buckets add-iam-policy-binding gs://apex-document-archive \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/storage.objectCreator"
```

### Issue 2: Archive Workflow Not Triggered

**Symptom:** Documents are processed but not archived

**Solution:**
```bash
# Check cleanup_staging_activity integration
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"cleanup_staging_activity\"" --limit=20

# Verify workflow registration
cd apex-memory-system
python -c "
from apex_memory.temporal.workflows.google_drive_archive import GoogleDriveArchiveWorkflow
print(f'Workflow name: {GoogleDriveArchiveWorkflow.__name__}')
"

# Check worker logs for registration
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"GoogleDriveArchiveWorkflow\"" --limit=10
```

### Issue 3: Lifecycle Policy Not Applying

**Symptom:** Files remain in Standard storage after 30 days

**Solution:**
```bash
# Verify lifecycle policy exists
gcloud storage buckets describe gs://apex-document-archive --format="value(lifecycle)"

# If empty, reapply:
gcloud storage buckets update gs://apex-document-archive --lifecycle-file=archive-lifecycle.json

# Note: Lifecycle policies apply ~24 hours after object creation
```

---

## Integration with Document Ingestion

The Archive Workflow is automatically triggered by the cleanup_staging_activity after successful document ingestion:

```python
# In cleanup_staging_activity (src/apex_memory/temporal/activities/document_ingestion.py)

# After marking document as processed
if workflow.in_workflow_context():
    # Trigger archive workflow asynchronously (non-blocking)
    workflow.start_child_workflow(
        GoogleDriveArchiveWorkflow.run,
        args=[document_id, file_path, source, domain_name],
        id=f"archive-{document_id}",
        task_queue="apex-ingestion-queue"
    )
```

**Key Design Points:**
- Archive runs **asynchronously** - doesn't block ingestion workflow
- **Child workflow** - Complete visibility in Temporal UI
- **Automatic retry** - Temporal handles transient GCS failures
- **Complete observability** - Status queries available via Temporal UI

---

## Monitoring

### Check Archive Success Rate

```bash
# Query archive_metadata table
export PGPASSWORD=apexmemory2024
psql -h POSTGRES_IP -U apex -d apex_memory -c "
  SELECT
    DATE(archived_at) as date,
    COUNT(*) as total_archived,
    COUNT(*) FILTER (WHERE gcs_path IS NOT NULL) as successful
  FROM archive_metadata
  WHERE archived_at > NOW() - INTERVAL '7 days'
  GROUP BY DATE(archived_at)
  ORDER BY date DESC;
"
```

### Monitor GCS Storage Costs

```bash
# Get bucket storage metrics
gcloud storage buckets describe gs://apex-document-archive --format="value(storageClass,size)"

# Estimate monthly cost
# Standard: $0.020/GB/month
# Coldline (30+ days): $0.004/GB/month
```

### Temporal UI Monitoring

Navigate to Temporal UI and search for archive workflows:
- Filter: `WorkflowType = 'GoogleDriveArchiveWorkflow'`
- Check: Success rate, average duration, failure patterns

---

## Rollback

### Disable Archive Workflow

```bash
# Remove GCS bucket environment variable
gcloud run services update apex-api \
  --region=us-central1 \
  --remove-env-vars="GCS_ARCHIVE_BUCKET"

# Archive workflow will skip if bucket not configured
```

### Complete Removal

```bash
# 1. Remove env var
gcloud run services update apex-api --region=us-central1 --remove-env-vars="GCS_ARCHIVE_BUCKET"

# 2. Remove service account permissions
gcloud storage buckets remove-iam-policy-binding gs://apex-document-archive \
  --member="serviceAccount:apex-drive-monitor@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectCreator"

# 3. (Optional) Delete bucket
# WARNING: This deletes all archived files permanently
# gcloud storage rm -r gs://apex-document-archive
```

---

## Cost Breakdown

**Estimated: $0-5/month** (moderate document volume)

- **GCS Storage:**
  - Standard (0-30 days): $0.020/GB/month
  - Coldline (30+ days): $0.004/GB/month
  - Estimated usage: 10-50 GB = $0.20-$2/month

- **GCS Operations:**
  - Class A (uploads): $0.05/10,000 operations
  - Class B (reads): $0.004/10,000 operations
  - Estimated: 500 uploads/month = $0.0025/month (negligible)

- **Network Egress:** $0 (same region as Cloud Run)

**Total:** ~$0.20-$2/month for storage

---

## References

- **Main Guide:** `deployment/components/google-drive-integration/DEPLOYMENT-GUIDE.md`
- **Workflow Implementation:** `src/apex_memory/temporal/workflows/google_drive_archive.py`
- **Activities:** `src/apex_memory/temporal/activities/google_drive_archive.py`
- **Tests:** `tests/unit/test_google_drive_archive_workflow.py`
- **GCS Documentation:** https://cloud.google.com/storage/docs

---

**Deployment Status:** ✅ Ready for Production
**Integration:** Automatic (via cleanup_staging_activity)
**Last Updated:** 2025-11-15
**Next Step:** Proceed to Phases 3-6 (Prerequisites, Workflow Integration, QA, Future Process)
