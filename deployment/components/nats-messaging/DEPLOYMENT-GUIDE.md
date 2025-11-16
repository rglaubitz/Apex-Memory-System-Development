# NATS Messaging - Deployment Guide

**Feature:** Lightweight Agent-to-Agent Messaging
**Status:** ⚠️ OPTIONAL - Verify Active Usage Before Deploying
**Impact:** Low - Only if inter-agent messaging is actively used
**Deployment Week:** Week 3 (OPTIONAL)

---

## ⚠️ IMPORTANT: Usage Verification Required

**Before deploying NATS, verify it's actively used in production code:**

```bash
# Check for NATS usage
cd apex-memory-system
grep -r "NATSService" src/ --include="*.py" | grep -v "test" | grep -v "__pycache__"
grep -r "nats_service" src/ --include="*.py" | grep -v "test"

# If no results (besides service definition), SKIP THIS DEPLOYMENT
```

**Current Finding:** Only found in service definition and config - **likely not actively used**.

**Recommendation:** Mark as OPTIONAL and deploy only if usage is confirmed.

---

## Overview

NATS Service provides lightweight pub/sub and request-reply messaging for agent-to-agent communication (<10ms latency).

**Use Cases:**
- Fire-and-forget notifications between agents
- Synchronous request-reply queries
- Subject-based routing (agent.{agent_id}.{message_type})

**Dependencies:**
- NATS server (self-hosted OR managed)
- Python package: `nats-py`

---

## Deployment Options

### Option A: Self-Hosted (Recommended for Cost)

Deploy NATS on existing Compute Engine VM:

```bash
# SSH to worker VM
gcloud compute ssh apex-worker-vm

# Run NATS Docker container
docker run -d \
  --name nats-server \
  -p 4222:4222 \
  --restart unless-stopped \
  nats:latest

# Configure firewall
exit  # Exit SSH

gcloud compute firewall-rules create allow-nats-from-cloud-run \
  --allow=tcp:4222 \
  --source-ranges=CLOUD_RUN_VPC_CIDR \
  --target-tags=apex-worker
```

**Set environment variable:**
```bash
# Get internal IP
export WORKER_INTERNAL_IP=$(gcloud compute instances describe apex-worker-vm --format="value(networkInterfaces[0].networkIP)")

gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="NATS_URL=nats://$WORKER_INTERNAL_IP:4222"
```

**Cost:** $0/month (uses existing VM)

### Option B: Managed NATS

Use external managed service (e.g., nats.io):

```bash
# Sign up at https://nats.io
# Get connection URL

gcloud run services update apex-api \
  --region=us-central1 \
  --set-secrets="NATS_URL=nats-url:latest"
```

**Cost:** $15-50/month depending on tier

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NATS_URL` | Yes | `nats://localhost:4222` | NATS server URL |

---

## Verification

```bash
cd apex-memory-system
python -c "
from apex_memory.services.nats_service import NATSService
import asyncio

async def test():
    service = NATSService()
    await service.connect()
    await service.publish('test.subject', {'message': 'hello'})
    await service.disconnect()
    print('✅ NATS connection successful')

asyncio.run(test())
"
```

---

## Troubleshooting

**Issue:** Connection refused
**Solution:**
```bash
# Verify NATS is running
gcloud compute ssh apex-worker-vm --command "docker ps | grep nats"

# Test connectivity from Cloud Run
gcloud compute ssh apex-worker-vm --command "curl -v $WORKER_INTERNAL_IP:4222"
```

---

## Rollback

```bash
# Self-hosted: Stop NATS
gcloud compute ssh apex-worker-vm --command "docker stop nats-server && docker rm nats-server"

# Remove env var
gcloud run services update apex-api --region=us-central1 --remove-env-vars="NATS_URL"
```

---

## Cost Breakdown

- **Self-hosted:** $0/month (uses existing VM)
- **Managed:** $15-50/month

---

**Deployment Status:** ⚠️ OPTIONAL - Verify Usage First
**Next Step:** Proceed to Authentication deployment
