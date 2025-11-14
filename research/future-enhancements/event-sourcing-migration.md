# Event Sourcing Migration (NATS JetStream)

**Status:** Future Enhancement - Not in MVP
**Timeline:** Months 6-12 (if needed)
**Priority:** Low (premature optimization for <10K msgs/hour)

---

## Overview

Migrate from PostgreSQL primary storage to NATS JetStream event sourcing architecture.

### When to Consider This Migration

**Only migrate if you need:**
- **>10,000 messages/hour sustained** - PostgreSQL can handle this, but event sourcing scales better
- **Multiple consumer teams** - Analytics, ML, audit logs want real-time stream access
- **Event replay capability** - Reprocess historical events (debugging, retraining models)
- **Decoupled consumers** - Each team maintains their own consumer (no shared database)

**Current capacity:**
- PostgreSQL handles 10,000+ messages/hour with proper indexing
- Redis caching reduces load by 60-95%
- Horizontal scaling available (read replicas)

---

## Migration Path: 3 Phases

### Phase 1 (Weeks 1-8): PostgreSQL Primary ✅

**Current architecture - already implemented:**
```
Message → PostgreSQL → Temporal → Graphiti
```

**Pros:**
- 90% implemented (conversations table exists)
- ACID guarantees (reliable)
- Fast to ship (2-3 weeks)

**Cons:**
- Two-stage storage (write twice: PostgreSQL + Neo4j)
- Limited replay capability (can query PostgreSQL, but not streaming)

**Status:** This is the finalized architecture for MVP.

---

### Phase 2 (Months 3-6): Hybrid (Add NATS Publisher)

**Add event streaming without breaking existing system:**
```
Message → PostgreSQL → (NEW) NATS Publisher Job
                ↓              ↓
            Temporal     NATS JetStream
                                ↓
                        (Optional Analytics Consumers)
```

**Benefits:**
- Event streaming for analytics (real-time dashboards)
- Replay capability (debug production issues)
- No breaking changes (PostgreSQL still primary)

**Implementation:**
```python
@workflow.defn
class NATSPublisherWorkflow:
    """Publishes PostgreSQL changes to NATS JetStream"""

    @workflow.run
    async def run(self, message_uuid: UUID) -> dict:
        # Fetch message from PostgreSQL
        message = await workflow.execute_activity(
            fetch_message,
            args=[message_uuid],
            start_to_close_timeout=timedelta(seconds=30)
        )

        # Publish to NATS JetStream (persistent)
        await workflow.execute_activity(
            publish_to_nats_jetstream,
            args=[message],
            start_to_close_timeout=timedelta(seconds=30)
        )

        return {"published": True}


@activity.defn
async def publish_to_nats_jetstream(message: Message):
    """Publish message to NATS JetStream stream"""
    import nats

    nc = await nats.connect("nats://localhost:4222")
    js = nc.jetstream()

    # Create stream if not exists
    try:
        await js.add_stream(
            name="conversational-memory",
            subjects=["messages.*"],
            storage="file",  # Persistent storage
            retention="limits",  # Retain based on limits
            max_age=86400 * 365,  # 1 year retention
        )
    except nats.js.errors.StreamNameAlreadyInUseError:
        pass  # Stream already exists

    # Publish message
    await js.publish(
        subject=f"messages.{message.conversation_uuid}",
        payload=message.to_json().encode(),
        headers={"message-uuid": str(message.uuid)}
    )
```

**Cons:**
- Adds operational complexity (NATS cluster management)
- Duplicate storage (PostgreSQL + NATS JetStream)
- Extra latency (50-100ms to publish to NATS)

**Decision:** Only implement if analytics team needs real-time stream access.

---

### Phase 3 (Months 6-12): Event Sourcing Primary (Optional)

**Migrate to NATS JetStream as primary source:**
```
Message → NATS JetStream (primary)
               ↓              ↓              ↓
       PostgreSQL      Graphiti          Analytics
       (Consumer)      (Consumer)        (Consumer)
```

**Benefits:**
- Complete event sourcing (single source of truth)
- Horizontal scaling (add consumers independently)
- Full replay capability (reprocess any timeframe)
- Decoupled consumers (teams don't share database)

**Architecture:**

```python
# Producer (Slack/NATS → JetStream)
async def ingest_message(message: Message):
    """Write to NATS JetStream (primary source)"""
    import nats

    nc = await nats.connect("nats://nats.apex-memory.com:4222")
    js = nc.jetstream()

    # Publish to stream
    ack = await js.publish(
        subject=f"messages.{message.conversation_uuid}",
        payload=message.to_json().encode(),
        headers={"message-uuid": str(message.uuid), "source": "slack"}
    )

    return {"stream_sequence": ack.seq}


# Consumer 1: PostgreSQL Writer
@nats.consumer
async def postgresql_consumer(msg):
    """Write messages to PostgreSQL (queryable storage)"""
    message = Message.from_json(msg.data)
    await db.insert_message(message)
    await msg.ack()


# Consumer 2: Graphiti Ingestion
@nats.consumer
async def graphiti_consumer(msg):
    """Extract entities and create knowledge graph episodes"""
    message = Message.from_json(msg.data)

    # Trigger Temporal workflow (same as today)
    await temporal_client.start_workflow(
        ConversationIngestionWorkflow.run,
        args=[message.uuid],
        id=f"ingestion-{message.uuid}",
        task_queue="ingestion"
    )

    await msg.ack()


# Consumer 3: Analytics (Optional)
@nats.consumer
async def analytics_consumer(msg):
    """Stream messages to data warehouse for analytics"""
    message = Message.from_json(msg.data)
    await bigquery.insert_message(message)
    await msg.ack()
```

**Cons:**
- Complex setup (NATS clustering, monitoring, rebalancing)
- Operational overhead (learning curve, runbooks)
- Extra cost (NATS cluster: $200-500/month)
- Single point of failure (if NATS down, entire system down)

**Decision point:** Only migrate if:
- Traffic >10,000 messages/hour sustained
- Multiple consumer teams need real-time access
- Event replay is critical business requirement

---

## Cost Analysis

### Phase 1 (PostgreSQL Primary) - Current

- PostgreSQL: $100/month (managed RDS, 100 GB)
- Redis: $50/month (6 GB cache)
- **Total: $150/month**

### Phase 2 (Hybrid)

- PostgreSQL: $100/month
- Redis: $50/month
- NATS JetStream: $200/month (3-node cluster)
- **Total: $350/month (+$200)**

### Phase 3 (Event Sourcing Primary)

- NATS JetStream: $200/month (primary storage)
- PostgreSQL: $50/month (consumer storage, smaller)
- Redis: $50/month
- **Total: $300/month (+$150)**

**Recommendation:** Stay on Phase 1 (PostgreSQL primary) until cost is justified by scale (>10K msgs/hour).

---

## Performance Comparison

| Metric | PostgreSQL Primary | Event Sourcing |
|--------|-------------------|----------------|
| **Write latency** | 50-100ms | 10-20ms (NATS) + 50-100ms (consumer) |
| **Read latency** | 50-100ms | 50-100ms (same, reads from PostgreSQL consumer) |
| **Throughput** | 10,000 msgs/hour | 100,000+ msgs/hour |
| **Replay capability** | Query PostgreSQL (slow) | Stream replay (fast) |
| **Horizontal scaling** | Read replicas only | Unlimited consumers |
| **Operational complexity** | Low (1 database) | High (cluster management) |

**Verdict:** PostgreSQL primary is simpler and sufficient for <10K msgs/hour.

---

## Implementation Checklist (Phase 2 Only)

**If you decide to proceed with Phase 2 (Hybrid):**

**Week 1: NATS JetStream Setup**
- [ ] Deploy NATS cluster (3 nodes, production setup)
- [ ] Create "conversational-memory" stream
- [ ] Configure retention (1 year, 100 GB limit)
- [ ] Test pub/sub with sample messages

**Week 2: Publisher Implementation**
- [ ] Implement NATSPublisherWorkflow (Temporal.io)
- [ ] Integrate with existing ConversationService
- [ ] Test end-to-end (PostgreSQL → NATS)

**Week 3: Consumer Setup (Optional)**
- [ ] Implement analytics consumer (BigQuery)
- [ ] Set up monitoring (Grafana dashboard)
- [ ] Test replay capability

**Week 4: Production Rollout**
- [ ] Gradual rollout (10% → 50% → 100%)
- [ ] Monitor NATS cluster health
- [ ] Validate dual-write correctness (PostgreSQL = NATS)

**Total Timeline:** 4 weeks (full-time effort)

---

## Risks & Mitigation

### Risk 1: NATS Cluster Downtime

**Impact:** Entire system down (all ingestion stops)

**Mitigation:**
- 3-node cluster (high availability)
- Monitoring & alerts (PagerDuty integration)
- Fallback to PostgreSQL-only mode (disable NATS publisher)

### Risk 2: Dual-Write Inconsistency

**Impact:** PostgreSQL and NATS have different data

**Mitigation:**
- Reconciliation job (daily cron, compare PostgreSQL vs NATS)
- Alerts on inconsistency (>0.1% mismatch)
- Manual repair process (republish from PostgreSQL)

### Risk 3: Operational Complexity

**Impact:** Team needs to learn NATS, runbooks, troubleshooting

**Mitigation:**
- Training (2-day workshop on NATS)
- Runbooks (incident response, scaling, backups)
- Managed NATS option (Synadia Cloud, $500/month)

---

## References

- **NATS JetStream Docs:** https://docs.nats.io/nats-concepts/jetstream
- **Event Sourcing Pattern:** https://martinfowler.com/eaaDev/EventSourcing.html
- **Temporal.io + NATS Integration:** https://community.temporal.io/t/nats-jetstream-integration/
- **Synadia Cloud (Managed NATS):** https://www.synadia.com/cloud

---

## Decision Tree

**Should you migrate to event sourcing?**

```
START
   ↓
Is traffic >10K msgs/hour sustained?
   ├─ NO → Stay on PostgreSQL primary (current architecture) ✅
   └─ YES
       ↓
   Do multiple teams need real-time stream access?
       ├─ NO → Consider Phase 2 (Hybrid) for analytics only
       └─ YES
           ↓
       Is event replay a critical business requirement?
           ├─ NO → Consider Phase 2 (Hybrid) - cheaper than Phase 3
           └─ YES → Proceed with Phase 3 (Event Sourcing Primary)
```

**Current Recommendation:** Stay on PostgreSQL primary until traffic justifies complexity.

---

**Last Updated:** 2025-11-14
**Status:** Specification Complete - Not Recommended for MVP
**Estimated Effort:** 4-8 weeks (Phase 2: 4 weeks, Phase 3: 8 weeks)
**Dependencies:** NATS cluster setup, team training
