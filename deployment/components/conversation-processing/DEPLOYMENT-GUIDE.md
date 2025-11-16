# Conversation Processing - Deployment Guide

**Feature:** Background Conversation → Knowledge Graph Ingestion
**Status:** ✅ Production Ready
**Impact:** Critical - Conversational memory feedback loop (85%+ accuracy, <20s P95)
**Deployment Week:** Week 3 (Temporal Cloud & Testing)

---

## Overview

ConversationIngestionWorkflow runs asynchronously after user messages, extracting entities and enriching the knowledge graph without blocking responses.

**Key Features:**
- Agent-aware routing (Oscar, Sarah, Maya specific collections)
- GPT-5 nano for entity extraction ($0.05/$0.40 per 1M tokens, 40x cheaper than Claude)
- P95 <20s end-to-end, P50 <10s
- Estimated cost: <$0.01 per conversation

**Dependencies:**
- PostgreSQL (conversations/messages tables)
- Qdrant (agent-specific collections)
- Redis (agent-namespaced cache)
- Temporal Cloud
- Graphiti

---

## Setup Instructions

### Step 1: Run Database Migration

```bash
cd apex-memory-system
alembic upgrade head

# Verify tables
export PGPASSWORD=apexmemory2024
psql -h localhost -U apex -d apex_memory -c "\d conversations"
psql -h localhost -U apex -d apex_memory -c "\d messages"
```

**Migration:** `alembic/versions/12a9f72ec074_add_conversations_and_messages_tables.py`

### Step 2: Enable Feature Flag

```bash
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="ENABLE_CONVERSATION_INGESTION=true"
```

### Step 3: Verify Qdrant Collections

Agent-specific collections should already exist from Phase 2:
- `oscar_fleet_knowledge`
- `sarah_legal_knowledge`
- `maya_ops_knowledge`

```bash
# Verify collections exist
curl http://QDRANT_IP:6333/collections

# Should show agent-specific collections
```

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENABLE_CONVERSATION_INGESTION` | Yes | `false` | Enable workflow |

---

## Deployment

```bash
# 1. Migration
cd apex-memory-system && alembic upgrade head

# 2. Enable feature
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="ENABLE_CONVERSATION_INGESTION=true"

# 3. Restart worker (automatic on config change)
```

---

## Verification

### Test Workflow Execution

```bash
# Trigger conversation ingestion
cd apex-memory-system
python -c "
from temporalio.client import Client
from apex_memory.temporal.workflows.conversation_ingestion import ConversationIngestionWorkflow, ConversationIngestionInput
import asyncio

async def test():
    client = await Client.connect('localhost:7233')
    result = await client.execute_workflow(
        ConversationIngestionWorkflow.run,
        args=[ConversationIngestionInput(
            conversation_id='test-conv-001',
            agent_id='oscar'
        )],
        id='conv-test-001',
        task_queue='apex-ingestion-queue'
    )
    print(f'Extracted {result.entities_extracted} entities, {result.relationships_extracted} relationships')

asyncio.run(test())
"

# Expected: Entities and relationships extracted
```

### Verify Agent-Specific Routing

```bash
# Check Qdrant collection for Oscar's entities
curl "http://QDRANT_IP:6333/collections/oscar_fleet_knowledge/points/scroll" \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'

# Should show entities from test conversation
```

---

## Troubleshooting

**Issue:** Workflow not found
**Solution:**
```bash
# Check worker logs
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"ConversationIngestionWorkflow\"" --limit=20

# Verify registration in worker file
grep -n "ConversationIngestionWorkflow" src/apex_memory/temporal/workers/dev_worker.py
```

**Issue:** Entities not appearing in agent collections
**Solution:**
```bash
# Verify agent_id parameter is correct (oscar, sarah, maya)
# Check Qdrant collection names match agent_id + suffix
curl http://QDRANT_IP:6333/collections | jq '.result.collections[].name'
```

---

## Rollback

```bash
gcloud run services update apex-api \
  --region=us-central1 \
  --remove-env-vars="ENABLE_CONVERSATION_INGESTION"
```

---

## Cost Breakdown

**~$5-15/month** - GPT-5 nano usage
- $0.05 per 1M input tokens, $0.40 per 1M output tokens
- Estimated: 1,000 conversations/month = $5-10/month

---

**Deployment Status:** ✅ Ready for Production
**Tests:** `tests/integration/test_conversation_ingestion_workflow.py`
**Next Step:** Proceed to Memory Decay deployment
