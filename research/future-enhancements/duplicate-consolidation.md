# Duplicate Fact Consolidation (Tier 5)

**Status:** Future Enhancement - Not in MVP
**Timeline:** Phase 3 (Weeks 3-4) - if needed
**Priority:** Medium (storage optimization, query performance)

---

## Overview

Detect and merge redundant information using semantic similarity to reduce knowledge graph bloat and improve query performance.

### The Problem

Without fact consolidation:
- User mentions "ACME Corp prefers aisle seats" in 10 conversations
- System creates 10 separate facts in Neo4j (duplicates)
- Knowledge graph grows 20-40% faster than necessary
- Query performance degrades (more facts to traverse)

### The Solution

Semantic similarity detection with automatic fact merging.

---

## Architecture

### Two-Stage Approach

**Stage 1: Real-time Detection (During Ingestion)**
- Before creating new episode, check for semantic duplicates
- If duplicate found: Update existing fact confidence, skip new episode

**Stage 2: Batch Consolidation (Weekly Cron)**
- Find fact clusters (semantic similarity > 0.9)
- Merge clusters into single canonical facts
- Update all references

---

## Implementation

### Stage 1: Real-Time Detection

```python
from graphiti import Graphiti
import numpy as np

class DuplicateFactDetector:
    """Detects duplicate facts during ingestion"""

    def __init__(self, graphiti: Graphiti):
        self.graphiti = graphiti
        self.neo4j = graphiti.neo4j
        self.similarity_threshold = 0.9

    async def detect_duplicates(self, new_episode: Episode) -> list[tuple[Fact, Fact]]:
        """Find existing episodes with same semantic meaning"""

        # Extract facts from new episode
        new_facts = await self.extract_facts(new_episode)

        duplicates = []
        for fact in new_facts:
            # Query knowledge graph for similar facts
            existing = await self.neo4j.query(
                """
                MATCH (e:Episode)-[:CONTAINS]->(f:Fact)
                WHERE vector.similarity(f.embedding, $embedding) > $threshold
                AND f.entity = $entity
                AND f.relationship = $relationship
                RETURN e, f
                ORDER BY f.confidence DESC
                LIMIT 1
                """,
                embedding=fact.embedding,
                entity=fact.entity,
                relationship=fact.relationship,
                threshold=self.similarity_threshold
            )

            if existing:
                duplicates.append((fact, existing['f']))

        return duplicates

    async def consolidate_or_skip(
        self,
        new_episode: Episode,
        duplicates: list[tuple[Fact, Fact]]
    ) -> str:
        """Decide: skip new episode or update existing fact"""

        if duplicates:
            # Update existing fact's confidence and recency
            for new_fact, existing_fact in duplicates:
                await self.neo4j.query(
                    """
                    MATCH (f:Fact {uuid: $uuid})
                    SET f.confidence = f.confidence + 1,
                        f.last_mentioned = $now,
                        f.mention_count = f.mention_count + 1,
                        f.last_message_uuid = $message_uuid
                    """,
                    uuid=existing_fact.uuid,
                    now=datetime.utcnow(),
                    message_uuid=new_episode.message_uuid
                )

            # Skip creating new episode (redundant)
            await self.db.update_message(
                message_uuid=new_episode.message_uuid,
                ingestion_skipped=True,
                skip_reason="duplicate_fact_consolidated"
            )

            return "consolidated"
        else:
            # Create new episode (novel information)
            await self.graphiti.create_episode(new_episode)
            return "created"
```

**Integration with Ingestion Workflow:**

```python
@workflow.defn
class ConversationIngestionWorkflow:
    """Enhanced with duplicate detection"""

    @workflow.run
    async def run(self, message_uuid: UUID) -> dict:
        # ... existing workflow steps ...

        # NEW: Check for duplicates before creating episode
        duplicates = await workflow.execute_activity(
            detect_duplicate_facts,
            args=[episode_data],
            start_to_close_timeout=timedelta(seconds=30)
        )

        if duplicates:
            # Update existing facts, skip new episode
            result = await workflow.execute_activity(
                update_existing_facts,
                args=[duplicates],
                start_to_close_timeout=timedelta(seconds=30)
            )
            return {"status": "consolidated", "duplicates": len(duplicates)}
        else:
            # Create new episode (original path)
            await workflow.execute_activity(
                create_graphiti_episode,
                args=[episode_data],
                start_to_close_timeout=timedelta(seconds=30)
            )
            return {"status": "created", "duplicates": 0}
```

---

### Stage 2: Batch Consolidation (Weekly)

```python
from temporalio import workflow, activity
from datetime import timedelta

@workflow.defn
class FactConsolidationWorkflow:
    """Runs weekly, identifies and merges duplicate fact clusters"""

    @workflow.run
    async def run(self) -> dict:
        # Find fact clusters (semantic similarity > 0.9)
        clusters = await workflow.execute_activity(
            identify_fact_clusters,
            start_to_close_timeout=timedelta(minutes=30)
        )

        if not clusters:
            return {"clusters_found": 0, "facts_consolidated": 0}

        consolidated_count = 0
        for cluster in clusters:
            # Merge cluster into single canonical fact
            await workflow.execute_activity(
                consolidate_fact_cluster,
                args=[cluster],
                start_to_close_timeout=timedelta(minutes=5)
            )
            consolidated_count += len(cluster) - 1  # N facts → 1 fact = N-1 consolidations

        return {
            "clusters_found": len(clusters),
            "facts_consolidated": consolidated_count
        }


@activity.defn
async def identify_fact_clusters() -> list[list[Fact]]:
    """Find groups of similar facts using DBSCAN clustering"""

    # Fetch all facts with embeddings
    query = """
        MATCH (f:Fact)
        WHERE f.embedding IS NOT NULL
        RETURN f.uuid, f.embedding, f.entity, f.confidence
    """
    facts = await neo4j.query(query)

    # Compute pairwise similarity matrix
    embeddings = np.array([f['embedding'] for f in facts])
    similarity_matrix = cosine_similarity(embeddings)

    # DBSCAN clustering (eps=0.1 for >0.9 similarity, min_samples=2)
    from sklearn.cluster import DBSCAN
    clustering = DBSCAN(eps=0.1, min_samples=2, metric='precomputed')
    labels = clustering.fit_predict(1 - similarity_matrix)  # Convert similarity to distance

    # Group facts by cluster
    clusters = {}
    for idx, label in enumerate(labels):
        if label == -1:  # Noise (no cluster)
            continue
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(facts[idx])

    return list(clusters.values())


@activity.defn
async def consolidate_fact_cluster(cluster: list[Fact]) -> Fact:
    """Merge N facts into 1 canonical fact"""

    # Select canonical fact (highest confidence)
    canonical = max(cluster, key=lambda f: f['confidence'])
    others = [f for f in cluster if f['uuid'] != canonical['uuid']]

    # Merge confidence scores
    total_confidence = sum(f['confidence'] for f in cluster)

    # Update canonical fact
    await neo4j.query(
        """
        MATCH (f:Fact {uuid: $uuid})
        SET f.confidence = $total_confidence,
            f.mention_count = $mention_count,
            f.consolidated_from = $other_uuids,
            f.last_consolidated = $now
        """,
        uuid=canonical['uuid'],
        total_confidence=total_confidence,
        mention_count=len(cluster),
        other_uuids=[f['uuid'] for f in others],
        now=datetime.utcnow()
    )

    # Delete redundant facts
    await neo4j.query(
        """
        MATCH (f:Fact)
        WHERE f.uuid IN $uuids
        DETACH DELETE f
        """,
        uuids=[f['uuid'] for f in others]
    )

    return canonical
```

---

## Database Schema Changes

```sql
-- Add consolidation tracking columns
ALTER TABLE facts ADD COLUMN mention_count INTEGER DEFAULT 1;
ALTER TABLE facts ADD COLUMN last_mentioned TIMESTAMP DEFAULT NOW();
ALTER TABLE facts ADD COLUMN consolidated_from UUID[];
ALTER TABLE facts ADD COLUMN last_consolidated TIMESTAMP;

-- Add skipped message tracking
ALTER TABLE messages ADD COLUMN ingestion_skipped BOOLEAN DEFAULT FALSE;
ALTER TABLE messages ADD COLUMN skip_reason TEXT;

-- Index for consolidation queries
CREATE INDEX idx_facts_entity_relationship ON facts(entity, relationship);
```

---

## Benefits & Metrics

### Storage Reduction

**Without Consolidation:**
- 100,000 facts in Neo4j
- 20-40% are duplicates
- Storage: 5 GB Neo4j

**With Consolidation:**
- 60,000-80,000 facts (20-40% reduction)
- Storage: 3-4 GB Neo4j
- Savings: 50-100 GB/year

### Query Performance

**Example Query: "What do we know about ACME Corp?"**

**Without Consolidation:**
- Traverse 50 facts (10 duplicates + 40 unique)
- Query time: 200ms

**With Consolidation:**
- Traverse 40 facts (all unique)
- Query time: 150ms
- **20-30% faster**

### Confidence Scoring

Facts mentioned multiple times gain higher confidence:

```python
# Single mention
fact.confidence = 1  # "ACME Corp prefers aisle seats" (mentioned once)

# After 5 consolidations
fact.confidence = 6  # "ACME Corp prefers aisle seats" (mentioned 6 times)
```

**Benefit:** Query router can prioritize high-confidence facts for context.

---

## Cost Analysis

### Implementation Cost

- **Week 1:** Real-time detection (20-24 hours)
  - Add duplicate detection to ingestion workflow
  - Implement consolidate_or_skip() logic
  - 5 unit tests

- **Week 2:** Batch consolidation (16-20 hours)
  - Implement FactConsolidationWorkflow (Temporal.io)
  - Implement DBSCAN clustering activity
  - 5 unit tests

- **Week 3:** Testing & validation (12-16 hours)
  - Integration tests (3 tests)
  - Load test (10K facts → consolidation)
  - Monitoring dashboard (3 panels)

**Total Effort:** 3 weeks (part-time)

### Operating Cost

- **Real-time:** +50ms per ingestion (negligible)
- **Batch:** 1 hour/week (weekly cron) = $0.10/week
- **Total:** <$5/month

### Cost Savings

- Neo4j storage: 20-40% reduction = $400-800/month saved
- Query performance: 20-30% faster = better user experience
- **ROI:** 80-160x return on $5/month cost

---

## Monitoring & Metrics

### Grafana Dashboard Panels

1. **Consolidation Rate** - Facts consolidated per day
2. **Duplicate Detection Rate** - % of ingestions skipped (duplicates)
3. **Fact Growth Rate** - Total facts in Neo4j over time
4. **Consolidation Job Duration** - Weekly job execution time
5. **Confidence Distribution** - Histogram of fact confidence scores

### Alerts

- **High duplicate rate** (warning) - >50% of ingestions skipped (possible config issue)
- **Consolidation job slow** (warning) - >1 hour execution (large cluster)
- **Fact growth anomaly** (critical) - Facts growing >10%/day (consolidation not working)

---

## Testing Strategy

### Unit Tests (10 tests)

1. `test_detect_duplicates_exact_match()` - Same text → duplicate
2. `test_detect_duplicates_semantic()` - Similar text → duplicate
3. `test_detect_duplicates_different_entity()` - Same text, diff entity → no duplicate
4. `test_consolidate_or_skip_duplicate()` - Updates confidence, skips episode
5. `test_consolidate_or_skip_novel()` - Creates new episode
6. `test_identify_fact_clusters()` - DBSCAN finds 3 clusters
7. `test_consolidate_fact_cluster()` - Merges 5 facts → 1
8. `test_consolidation_workflow_empty()` - No clusters → skip
9. `test_consolidation_workflow_success()` - Consolidates 100 facts → 60
10. `test_confidence_scoring()` - Confidence = mention_count

### Integration Tests (3 tests)

1. `test_real_time_duplicate_detection()` - Ingest duplicate → skipped
2. `test_batch_consolidation_full_cycle()` - 1000 facts → 600 (40% reduction)
3. `test_query_performance_improvement()` - Query 20-30% faster

---

## Implementation Checklist

**Phase 1: Real-Time Detection (Week 1)**
- [ ] Add detect_duplicate_facts activity to ConversationIngestionWorkflow
- [ ] Implement DuplicateFactDetector class
- [ ] Add consolidation columns to database
- [ ] Test with 10 duplicate messages

**Phase 2: Batch Consolidation (Week 2)**
- [ ] Implement FactConsolidationWorkflow (Temporal.io)
- [ ] Implement identify_fact_clusters activity (DBSCAN)
- [ ] Implement consolidate_fact_cluster activity
- [ ] Test with 1000 sample facts

**Phase 3: Monitoring (Week 3)**
- [ ] Add Grafana dashboard (5 panels)
- [ ] Add 3 alerts
- [ ] Test alert firing

**Phase 4: Production Rollout (Week 3)**
- [ ] Enable real-time detection (gradual rollout)
- [ ] Schedule weekly batch consolidation
- [ ] Monitor first run

**Total Timeline:** 3 weeks (part-time effort)

---

## References

- **Semantic Similarity:** https://en.wikipedia.org/wiki/Cosine_similarity
- **DBSCAN Clustering:** https://scikit-learn.org/stable/modules/clustering.html#dbscan
- **Neo4j Vector Similarity:** https://neo4j.com/docs/cypher-manual/current/functions/vector/
- **Temporal.io Cron Workflows:** https://docs.temporal.io/workflows#cron-workflows

---

**Last Updated:** 2025-11-14
**Status:** Specification Complete - Ready for Implementation
**Estimated Effort:** 3 weeks (part-time)
**Dependencies:** Requires Neo4j vector similarity (already in Graphiti)
