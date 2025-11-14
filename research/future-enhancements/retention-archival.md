# Retention Policy & Automatic Archival (Tier 4)

**Status:** Future Enhancement - Not in MVP
**Timeline:** Phase 3 (Weeks 3-4) - if needed
**Priority:** Medium (cost optimization)

---

## Overview

Implement tiered retention based on message importance to reduce storage costs and improve query performance.

### The Problem

Without retention policies:
- Neo4j grows unbounded (50K+ episodes → $2000/month)
- PostgreSQL holds all messages forever ($500/month for historical data)
- Query performance degrades as graph size increases

### The Solution

Automatic archival to cold storage (S3) based on retention tiers.

---

## Retention Tiers

```python
RETENTION_TIERS = {
    "critical": None,          # Keep forever (user preferences, key facts)
    "important": 365,          # 1 year (valuable conversations)
    "normal": 90,              # 3 months (typical interactions)
    "ephemeral": 7             # 1 week (chit-chat, status checks)
}

def classify_message(message: Message) -> str:
    """Classify message importance for retention policy"""

    # Critical: User preferences, important entities
    if contains_preference(message) or mentions_key_entity(message):
        return "critical"

    # Important: Task assignments, decisions, approvals
    if is_task(message) or is_decision(message):
        return "important"

    # Ephemeral: Status checks, greetings
    if is_status_check(message) or is_greeting(message):
        return "ephemeral"

    # Normal: Everything else
    return "normal"
```

---

## Database Schema

```sql
-- Add retention columns to messages table
ALTER TABLE messages ADD COLUMN retention_tier VARCHAR(20) DEFAULT 'normal';
ALTER TABLE messages ADD COLUMN archive_after_date TIMESTAMP;
ALTER TABLE messages ADD COLUMN archived BOOLEAN DEFAULT FALSE;
ALTER TABLE messages ADD COLUMN archived_location TEXT;  -- S3 URL

-- Index for archival job (performance)
CREATE INDEX idx_messages_archive ON messages(archive_after_date)
WHERE archive_after_date IS NOT NULL AND archived = FALSE;

-- Set archive_after_date on insert (trigger)
CREATE OR REPLACE FUNCTION set_archive_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.retention_tier = 'ephemeral' THEN
        NEW.archive_after_date := NEW.created_at + INTERVAL '7 days';
    ELSIF NEW.retention_tier = 'normal' THEN
        NEW.archive_after_date := NEW.created_at + INTERVAL '90 days';
    ELSIF NEW.retention_tier = 'important' THEN
        NEW.archive_after_date := NEW.created_at + INTERVAL '365 days';
    ELSE  -- critical
        NEW.archive_after_date := NULL;  -- Never archive
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_archive_date_trigger
    BEFORE INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION set_archive_date();
```

---

## Archival Workflow (Temporal.io)

```python
from temporalio import workflow, activity
from datetime import timedelta
import boto3

@workflow.defn
class ArchivalWorkflow:
    """Runs weekly, moves old messages to S3 cold storage"""

    @workflow.run
    async def run(self) -> dict:
        # Find messages past archive_after_date
        messages = await workflow.execute_activity(
            fetch_archival_candidates,
            start_to_close_timeout=timedelta(minutes=5)
        )

        if not messages:
            return {"archived_count": 0}

        # Move to S3 (in batches of 100)
        s3_urls = await workflow.execute_activity(
            archive_messages_to_s3,
            args=[messages],
            start_to_close_timeout=timedelta(minutes=30)
        )

        # Mark as archived in PostgreSQL
        await workflow.execute_activity(
            mark_messages_archived,
            args=[message_ids, s3_urls],
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Optional: Remove from Neo4j (free up memory)
        await workflow.execute_activity(
            remove_archived_episodes_from_neo4j,
            args=[message_ids],
            start_to_close_timeout=timedelta(minutes=10)
        )

        return {
            "archived_count": len(messages),
            "cold_storage_bytes": sum(m.size for m in messages),
            "s3_cost_added": len(messages) * 0.023 / 1000  # $0.023/GB/month
        }


@activity.defn
async def fetch_archival_candidates() -> list[Message]:
    """Find messages past their archive_after_date"""
    query = """
        SELECT * FROM messages
        WHERE archive_after_date < NOW()
        AND archived = FALSE
        ORDER BY archive_after_date ASC
        LIMIT 1000
    """
    return await db.fetch_all(query)


@activity.defn
async def archive_messages_to_s3(messages: list[Message]) -> dict[UUID, str]:
    """Upload messages to S3, return message_uuid → S3 URL mapping"""
    s3 = boto3.client('s3')
    urls = {}

    for message in messages:
        key = f"archived-messages/{message.uuid}.json"
        s3.put_object(
            Bucket='apex-memory-archive',
            Key=key,
            Body=message.to_json(),
            StorageClass='GLACIER_IR'  # Instant retrieval, $0.004/GB/month
        )
        urls[message.uuid] = f"s3://apex-memory-archive/{key}"

    return urls


@activity.defn
async def mark_messages_archived(message_ids: list[UUID], s3_urls: dict[UUID, str]):
    """Mark messages as archived in PostgreSQL"""
    for message_id, s3_url in s3_urls.items():
        await db.execute(
            """
            UPDATE messages
            SET archived = TRUE,
                archived_location = $1,
                archived_at = NOW()
            WHERE uuid = $2
            """,
            s3_url, message_id
        )


@activity.defn
async def remove_archived_episodes_from_neo4j(message_ids: list[UUID]):
    """Optional: Remove archived episodes from Neo4j to free up memory"""
    query = """
        MATCH (e:Episode)
        WHERE e.source_message_uuid IN $message_ids
        DETACH DELETE e
    """
    await neo4j.run(query, message_ids=message_ids)
```

---

## Storage Tiers

| Tier | Storage | Retention | Cost/GB/Month | Retrieval |
|------|---------|-----------|---------------|-----------|
| **Hot** | Neo4j | Last 90 days + critical | $40 | Instant |
| **Warm** | PostgreSQL | Last 365 days | $0.023 | Instant |
| **Cold** | S3 Glacier IR | Everything older | $0.004 | Instant |

**Note:** Glacier Instant Retrieval costs $0.004/GB/month (vs $0.023/GB for S3 Standard)

---

## Cost Impact Analysis

### Without Archival (Current)

- Neo4j: 200,000 episodes × $0.01 = **$2,000/month**
- PostgreSQL: 500 GB × $1 = **$500/month**
- **Total: $2,500/month ($30,000/year)**

### With Archival (Optimized)

- Neo4j (hot): 50,000 episodes × $0.004 = **$200/month**
- PostgreSQL (warm): 100 GB × $0.023 = **$2.30/month**
- S3 Glacier (cold): 400 GB × $0.004 = **$1.60/month**
- **Total: $204/month ($2,448/year)**

**Savings: $2,296/month ($27,552/year) = 92% reduction**

---

## Retrieval Strategy

### When Archived Messages Are Needed

```python
async def get_message_with_archive(message_uuid: UUID) -> Message:
    """Fetch message from PostgreSQL or S3 if archived"""

    # Check PostgreSQL first (fast path)
    message = await db.fetch_one(
        "SELECT * FROM messages WHERE uuid = $1",
        message_uuid
    )

    if message and not message.archived:
        return message  # Hot/warm path (instant)

    # Cold path: Fetch from S3
    if message and message.archived:
        s3 = boto3.client('s3')
        bucket, key = parse_s3_url(message.archived_location)
        obj = s3.get_object(Bucket=bucket, Key=key)
        return Message.from_json(obj['Body'].read())

    raise MessageNotFound(message_uuid)
```

**Retrieval Performance:**
- Hot (Neo4j): <10ms
- Warm (PostgreSQL): 50-100ms
- Cold (S3 Glacier IR): 100-200ms (still instant)

---

## Metrics & Monitoring

### Grafana Dashboard Panels

1. **Archival Rate** - Messages archived per day
2. **Storage Distribution** - Hot/Warm/Cold breakdown
3. **Cost Savings** - Monthly savings vs. no archival
4. **Retrieval Latency** - P50/P95/P99 for cold retrievals
5. **Archival Job Success Rate** - Weekly job execution status

### Alerts

- **Archival job failed** (critical) - Weekly job didn't run
- **Cold retrieval slow** (warning) - S3 retrieval >500ms
- **Hot storage growing** (warning) - Neo4j >60K episodes (should be ~50K)

---

## Implementation Checklist

**Phase 1: Database Schema (Week 1)**
- [ ] Add retention_tier, archive_after_date, archived columns
- [ ] Create index on archive_after_date
- [ ] Create trigger to set archive_after_date on insert

**Phase 2: S3 Setup (Week 1)**
- [ ] Create S3 bucket (apex-memory-archive)
- [ ] Enable Glacier Instant Retrieval lifecycle policy
- [ ] Set up IAM roles (Temporal worker → S3 write access)

**Phase 3: Archival Workflow (Week 2)**
- [ ] Implement ArchivalWorkflow (Temporal.io)
- [ ] Implement 4 activities (fetch, archive to S3, mark archived, remove from Neo4j)
- [ ] Test with 10 sample messages

**Phase 4: Retrieval Strategy (Week 2)**
- [ ] Implement get_message_with_archive() function
- [ ] Update API endpoints to use retrieval function
- [ ] Test cold path retrieval (S3 Glacier)

**Phase 5: Monitoring (Week 3)**
- [ ] Add Grafana dashboard (5 panels)
- [ ] Add 3 alerts (archival job, cold retrieval, hot storage)
- [ ] Test alert firing

**Phase 6: Production Rollout (Week 3)**
- [ ] Schedule ArchivalWorkflow (weekly cron)
- [ ] Monitor first run (dry-run mode)
- [ ] Enable actual archival

**Total Timeline:** 3 weeks (part-time effort)

---

## Testing Strategy

### Unit Tests (10 tests)

1. `test_classify_message_critical()` - User preferences → critical
2. `test_classify_message_ephemeral()` - Greetings → ephemeral
3. `test_set_archive_date_trigger()` - DB trigger sets correct date
4. `test_fetch_archival_candidates()` - Finds messages past date
5. `test_archive_to_s3()` - Uploads message to S3
6. `test_mark_messages_archived()` - Updates PostgreSQL
7. `test_get_message_with_archive_hot()` - Fast path (no S3)
8. `test_get_message_with_archive_cold()` - S3 retrieval
9. `test_archival_workflow_empty()` - No messages to archive
10. `test_archival_workflow_success()` - Archives 100 messages

### Integration Tests (3 tests)

1. `test_full_archival_cycle()` - Create message → wait 7 days → archive → retrieve
2. `test_neo4j_cleanup()` - Archived episodes removed from graph
3. `test_cost_savings()` - Verify storage reduction >80%

---

## References

- **S3 Glacier Pricing:** https://aws.amazon.com/s3/pricing/
- **Temporal.io Cron Workflows:** https://docs.temporal.io/workflows#cron-workflows
- **PostgreSQL Triggers:** https://www.postgresql.org/docs/current/triggers.html

---

**Last Updated:** 2025-11-14
**Status:** Specification Complete - Ready for Implementation
**Estimated Effort:** 3 weeks (part-time)
