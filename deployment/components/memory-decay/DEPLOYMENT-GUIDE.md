# Memory Decay - Deployment Guide

**Feature:** Daily Memory Importance Decay & Tier Transitions
**Status:** ✅ Production Ready
**Impact:** Medium - Automated memory lifecycle management
**Deployment Week:** Week 3 (Temporal Cloud & Testing)

---

## Overview

MemoryDecayWorkflow runs daily at 2 AM UTC, recalculating importance scores and managing memory tiers (critical/important/normal/ephemeral). Archives ephemeral messages >7 days old.

**Workflow Steps:**
1. Query aged messages (>1 day old)
2. Recalculate importance scores (age-adjusted)
3. Update tier assignments
4. Archive ephemeral messages (>7 days old)

**Execution Time:** 5-15 minutes for 10,000 messages

**Dependencies:**
- Temporal Cloud (for scheduling)
- PostgreSQL (messages table with retention fields)

---

## Setup Instructions

### Step 1: Run Database Migration

```bash
cd apex-memory-system
alembic upgrade head

# Verify retention fields exist
export PGPASSWORD=apexmemory2024
psql -h localhost -U apex -d apex_memory -c "\d messages" | grep -E "importance|tier"
```

**Migration:** `alembic/versions/6a6b5859ca8c_add_retention_policy_fields_to_messages.py`

### Step 2: Set Environment Variables

```bash
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="MEMORY_DECAY_THRESHOLD=0.3,MEMORY_TTL_DAYS=365"
```

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_DECAY_THRESHOLD` | `0.3` | Importance threshold for decay |
| `MEMORY_TTL_DAYS` | `365` | Time-to-live for ephemeral memories |

### Step 3: Create Temporal Schedule

```bash
cd apex-memory-system

# Create schedule via Python script
python -c "
from temporalio.client import Client, Schedule, ScheduleActionStartWorkflow, ScheduleSpec
from apex_memory.temporal.workflows.memory_decay import MemoryDecayWorkflow, MemoryDecayInput
import asyncio

async def create_schedule():
    client = await Client.connect('temporal-cloud-url')  # Use your Temporal Cloud URL

    await client.create_schedule(
        'memory-decay-daily',
        Schedule(
            action=ScheduleActionStartWorkflow(
                MemoryDecayWorkflow.run,
                args=[MemoryDecayInput()],
                id='memory-decay',
                task_queue='apex-ingestion-queue'
            ),
            spec=ScheduleSpec(
                cron_expressions=['0 2 * * *']  # 2 AM UTC daily
            )
        )
    )
    print('✅ Schedule created: memory-decay-daily')

asyncio.run(create_schedule())
"
```

### Step 4: Verify Schedule in Temporal UI

- Navigate to Temporal Cloud UI: https://cloud.temporal.io
- Go to Schedules tab
- Find: `memory-decay-daily`
- Verify: Cron expression `0 2 * * *`

---

## Configuration

**Schedule Frequency:** Daily at 2:00 AM UTC

**Parameters:**
- `min_age_days`: 1 (process messages >1 day old)
- `batch_size`: 100 (process in batches)
- `archive_age_days`: 7 (archive ephemeral >7 days)

---

## Deployment

```bash
# 1. Migration
cd apex-memory-system && alembic upgrade head

# 2. Set env vars
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="MEMORY_DECAY_THRESHOLD=0.3,MEMORY_TTL_DAYS=365"

# 3. Create schedule (run Python script from Step 3)
```

---

## Verification

### Test Manual Execution

```bash
cd apex-memory-system
python -c "
from temporalio.client import Client
from apex_memory.temporal.workflows.memory_decay import MemoryDecayWorkflow, MemoryDecayInput
import asyncio

async def test():
    client = await Client.connect('localhost:7233')
    result = await client.execute_workflow(
        MemoryDecayWorkflow.run,
        args=[MemoryDecayInput(min_age_days=1, batch_size=50)],
        id='memory-decay-test',
        task_queue='apex-ingestion-queue'
    )
    print(f'Processed {result.messages_queried} messages, {result.tier_changes} tier changes')

asyncio.run(test())
"
```

### Verify Schedule Execution

```bash
# Check Temporal UI for schedule executions
# Navigate to: Schedules → memory-decay-daily → Recent Runs

# Or check via CLI
temporal schedule describe --schedule-id memory-decay-daily
```

### Verify Tier Transitions

```bash
export PGPASSWORD=apexmemory2024
psql -h POSTGRES_IP -U apex -d apex_memory -c "
  SELECT tier, COUNT(*) as count
  FROM messages
  GROUP BY tier
  ORDER BY count DESC;
"

# Expected: Distribution across critical/important/normal/ephemeral
```

---

## Troubleshooting

**Issue:** Schedule not executing
**Solution:**
```bash
# Verify schedule exists
temporal schedule describe --schedule-id memory-decay-daily

# Check schedule is not paused
# If paused, unpause:
temporal schedule update --schedule-id memory-decay-daily --unpause

# Check worker is running
gcloud run services describe apex-api --region=us-central1
```

**Issue:** No messages being decayed
**Solution:**
```bash
# Check message ages
psql -h POSTGRES_IP -U apex -d apex_memory -c "
  SELECT age(NOW(), created_at) as age, COUNT(*)
  FROM messages
  GROUP BY age
  LIMIT 10;
"

# Verify messages are >1 day old before decay applies
```

---

## Rollback

```bash
# Delete schedule
temporal schedule delete --schedule-id memory-decay-daily

# Remove env vars
gcloud run services update apex-api \
  --region=us-central1 \
  --remove-env-vars="MEMORY_DECAY_THRESHOLD,MEMORY_TTL_DAYS"
```

---

## Cost Breakdown

**$0/month** - Uses existing Temporal Cloud subscription

---

**Deployment Status:** ✅ Ready for Production
**Tests:** `tests/unit/test_memory_decay_workflow.py`
**Next Step:** Proceed to GCS Archival deployment
