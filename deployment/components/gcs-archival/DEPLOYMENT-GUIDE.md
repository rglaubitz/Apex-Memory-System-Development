# GCS Archival Service - Deployment Guide

**Feature:** Long-Term Message Archival to Google Cloud Storage
**Status:** ✅ Production Ready
**Impact:** Medium - Cold storage for low-importance messages
**Deployment Week:** Week 2 (Dockerization & Configuration)

---

## Overview

GCS Archival Service archives messages (importance <0.3, age >7 days) to Google Cloud Storage for long-term cold storage.

**Architecture:**
- Bucket structure: `messages/YYYY/MM/agent/msg-{uuid}.json`
- Automatic lifecycle: Standard → Nearline (30d) → Coldline (90d) → Archive (365d)
- Integrated with MemoryDecayWorkflow

**Dependencies:**
- GCS bucket (`apex-memory-archive`)
- Service account authentication
- PostgreSQL (messages table)

---

## Setup Instructions

### Step 1: Create GCS Bucket

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1

# Create bucket
gcloud storage buckets create gs://apex-memory-archive \
  --location=$REGION \
  --uniform-bucket-level-access

# Set lifecycle policy
cat > message-lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
        "condition": {"age": 365}
      }
    ]
  }
}
EOF

gcloud storage buckets update gs://apex-memory-archive \
  --lifecycle-file=message-lifecycle.json

# Grant Cloud Run service account access
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud storage buckets add-iam-policy-binding gs://apex-memory-archive \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/storage.objectCreator"

gcloud storage buckets add-iam-policy-binding gs://apex-memory-archive \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### Step 2: Enable Feature

```bash
gcloud run services update apex-api \
  --region=$REGION \
  --update-env-vars="GCS_ENABLED=true,GCS_BUCKET_NAME=apex-memory-archive"
```

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GCS_ENABLED` | Yes | `false` | Enable GCS archival |
| `GCS_BUCKET_NAME` | Yes | `apex-memory-archive` | Bucket name |

---

## Deployment

```bash
# 1. Create bucket and set lifecycle
# (Run commands from Step 1)

# 2. Enable feature
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="GCS_ENABLED=true,GCS_BUCKET_NAME=apex-memory-archive"
```

---

## Verification

### Test Archival Service

```bash
cd apex-memory-system
python -c "
from apex_memory.services.gcs_archival_service import GCSArchivalService
from datetime import datetime
import asyncio

async def test():
    service = GCSArchivalService('apex-memory-archive')
    result = await service.archive_message(
        'test-uuid-001',
        {'content': 'Test message', 'agent': 'oscar', 'created_at': '2025-11-15'},
        agent_id='oscar'
    )
    print(f'Archived to: {result[\"gcs_path\"]}')

asyncio.run(test())
"

# Expected: messages/2025/11/oscar/msg-test-uuid-001.json
```

### Verify in GCS

```bash
# List archived messages
gcloud storage ls gs://apex-memory-archive/messages/2025/11/

# Download test message
gcloud storage cp gs://apex-memory-archive/messages/2025/11/oscar/msg-test-uuid-001.json -

# Should show JSON message content
```

---

## Troubleshooting

**Issue:** Permission denied when archiving
**Solution:**
```bash
# Verify service account has correct roles
gcloud storage buckets get-iam-policy gs://apex-memory-archive

# Should show ${PROJECT_NUMBER}-compute@... with roles/storage.objectCreator and objectViewer
```

**Issue:** Lifecycle policy not applying
**Solution:**
```bash
# Verify lifecycle policy
gcloud storage buckets describe gs://apex-memory-archive --format="value(lifecycle)"

# Reapply policy
gcloud storage buckets update gs://apex-memory-archive --lifecycle-file=message-lifecycle.json
```

---

## Rollback

```bash
# Disable feature
gcloud run services update apex-api \
  --region=us-central1 \
  --remove-env-vars="GCS_ENABLED,GCS_BUCKET_NAME"

# (Optional) Delete bucket
# gcloud storage rm -r gs://apex-memory-archive
```

---

## Cost Breakdown

**~$5-10/month** (moderate usage)
- FREE up to 5GB
- Standard storage: $0.020/GB/month
- Nearline (30+ days): $0.010/GB/month
- Coldline (90+ days): $0.004/GB/month
- Archive (365+ days): $0.0012/GB/month

**Estimated usage:** 50-100 GB messages = $2-8/month

---

**Deployment Status:** ✅ Ready for Production
**Tests:** `tests/unit/test_retention_policies_gcs.py`
**Next Step:** Proceed to Google Drive Archive update
