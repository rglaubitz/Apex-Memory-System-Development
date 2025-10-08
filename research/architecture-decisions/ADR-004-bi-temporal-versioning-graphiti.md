# ADR-004: Bi-Temporal Versioning with Graphiti

## Status
**Proposed**

## Context

The Apex Memory System needs sophisticated temporal intelligence to track how knowledge evolves over time. This requirement arises from several critical use cases:

1. **Knowledge Evolution Tracking**: Understanding how facts, relationships, and entities change over time as new information arrives
2. **Retroactive Corrections**: Handling situations where we discover past information was incorrect and need to update historical records without losing the original data
3. **Audit Trail & Compliance**: Maintaining complete audit trails for regulatory compliance and debugging purposes
4. **Time-Travel Queries**: Enabling queries like "What did we know about Entity X on date Y?" or "When did Relationship R become valid?"
5. **Conflict Resolution**: Intelligently handling contradictions between new and existing knowledge based on temporal metadata

Traditional timestamp-only approaches (single `created_at` field) are insufficient because they conflate two distinct temporal dimensions:
- **When something happened in the real world** (valid time)
- **When we learned about it** (transaction time)

### Real-World Example

Consider a customer relationship management scenario:
- **Day 1**: Customer changes address on January 15th, but notifies us on January 20th
- **Day 2**: We discover the address was actually changed on January 10th, not 15th
- **Day 3**: We need to query "What was the customer's address on January 12th?"

A single timestamp cannot capture:
1. When the address change occurred (January 10th - valid time)
2. When we first learned about it (January 20th - first transaction time)
3. When we corrected our knowledge (Day 2 - second transaction time)

## Options Considered

### Option A: Single Timestamp (created_at only)

**Description**: Store only a single `created_at` timestamp on each entity and relationship.

**Pros**:
- Simplest implementation
- Minimal storage overhead
- Fast queries (single timestamp comparison)
- No additional indexing complexity

**Cons**:
- Cannot distinguish between when events happened vs. when they were recorded
- No support for retroactive corrections
- Cannot reconstruct historical knowledge states accurately
- Poor audit trail capabilities
- Cannot handle out-of-order data ingestion

**Verdict**: ❌ Insufficient for our requirements

---

### Option B: Bi-Temporal Model (Transaction Time + Valid Time)

**Description**: Track two independent time dimensions:
- **Transaction Time (TT)**: When a fact was inserted/updated in the database (system-controlled)
- **Valid Time (VT)**: When a fact was/is/will be true in the real world (application-controlled)

**Pros**:
- Complete temporal fidelity - can reconstruct any historical state
- Supports retroactive corrections without data loss
- Enables time-travel queries across both dimensions
- Excellent audit trail (who knew what, when)
- Handles out-of-order data ingestion gracefully
- Industry-standard approach (SQL:2011, XTDB, MarkLogic)

**Cons**:
- Increased storage overhead (2-4x for highly volatile data)
- More complex query patterns
- Requires careful indexing strategy
- Steeper learning curve for developers

**Implementation Examples**:
- **Graphiti** (18.6k+ stars on GitHub) - Native bi-temporal support for knowledge graphs
- **XTDB** (2.6k+ stars) - Immutable bi-temporal database
- **SQL:2011** - Standardized temporal table support

**Verdict**: ✅ **Selected** - Provides necessary capabilities with manageable tradeoffs

---

### Option C: Event Sourcing (Full Event Log)

**Description**: Store every state change as an immutable event with timestamps, rebuild current state by replaying events.

**Pros**:
- Complete audit trail of all changes
- Can reconstruct any historical state
- Natural fit for event-driven architectures
- Supports complex temporal queries

**Cons**:
- Significant storage overhead (stores every mutation)
- Query performance degrades without snapshotting
- High complexity for simple read queries
- Requires event replay infrastructure
- Overkill for our use case (we need temporal reasoning, not full event history)

**Verdict**: ❌ Over-engineered for our requirements

---

### Option D: No Temporal Tracking

**Description**: Only store current state, no historical information.

**Pros**:
- Simplest possible approach
- Minimal storage
- Fastest queries

**Cons**:
- Cannot answer "when" questions
- No audit trail
- Cannot handle corrections
- Incompatible with knowledge evolution requirements

**Verdict**: ❌ Does not meet requirements

## Decision

**We will adopt Graphiti's bi-temporal versioning model for the Apex Memory System.**

### Rationale

1. **Research-Backed Industry Standard**: Bi-temporal modeling is a well-established pattern with standardization in SQL:2011 and proven implementations in production systems (XTDB, MarkLogic, Teradata).

2. **Native Integration**: Graphiti (18.6k+ stars) is already part of our tech stack and provides bi-temporal versioning as a core feature, not a bolt-on addition.

3. **Knowledge Graph Fit**: Unlike traditional relational databases, Graphiti's bi-temporal model works at the graph edge level, tracking relationship validity over time - essential for knowledge evolution.

4. **Practical Performance**: Storage overhead is manageable with proper archival policies and compression strategies (see Consequences section).

5. **Future-Proof**: Supports advanced temporal reasoning capabilities we may need as the system evolves (trend detection, pattern analysis, predictive modeling).

### How Graphiti Implements Bi-Temporal Versioning

#### Two Time Dimensions

Every graph edge (relationship) in Graphiti tracks:

1. **Valid Time** (`valid_at`, `invalid_at`): When the relationship was/is/will be true in reality
2. **Transaction Time** (`created_at`, `expired_at`): When the relationship was recorded/invalidated in the system

#### Edge Validity Intervals

```python
# Example from Graphiti documentation
EntityEdge(
    uuid='3133258f738e487383f07b04e15d4ac0',
    source_node_uuid='2a85789b318d4e418050506879906e62',
    target_node_uuid='baf7781f445945989d6e4f927f881556',
    name='HELD_POSITION',
    fact='Kamala Harris was the Attorney General of California',

    # Valid Time: When this relationship was true in reality
    valid_at=datetime(2011, 1, 3, 0, 0, tzinfo=UTC),
    invalid_at=datetime(2017, 1, 3, 0, 0, tzinfo=UTC),

    # Transaction Time: When we learned/invalidated this fact
    created_at=datetime(2024, 8, 26, 13, 13, 24, 861097),
    expired_at=datetime(2024, 8, 26, 20, 18, 1, 53812)
)
```

#### Temporal Conflict Resolution

When new information arrives that conflicts with existing knowledge, Graphiti:

1. Uses semantic, keyword, and graph search to identify conflicts
2. Compares temporal metadata to determine which fact is more recent
3. **Invalidates** (not deletes) the old relationship by setting `expired_at`
4. Preserves history for future queries and audit purposes

This approach enables **point-in-time reconstruction**: "What did we know on August 26th at 15:00?"

## Research Support

### Tier 1: Official Documentation

1. **Graphiti Framework** (Primary Implementation)
   - GitHub Repository: https://github.com/getzep/graphiti (18.6k+ stars)
   - Official Documentation: https://www.graphiti.dev/
   - Neo4j Blog: "Graphiti: Knowledge Graph Memory for an Agentic World"
   - Key Feature: "Bi-temporal data model explicitly tracks event occurrence times and ingestion times, allowing accurate point-in-time queries"

2. **SQL:2011 Temporal Tables Standard**
   - PostgreSQL Wiki: https://wiki.postgresql.org/wiki/SQL2011Temporal
   - Standard includes: Application-time period tables (valid time), system-versioned tables (transaction time), and bi-temporal tables
   - Industry adoption: Teradata, MarkLogic, SQL Server

3. **Neo4j Temporal Support**
   - Cypher Manual: https://neo4j.com/docs/cypher-manual/current/values-and-types/temporal/
   - Native temporal data types: DATE, DATETIME, DURATION
   - Indexing support for range queries on temporal values

### Tier 2: Verified Examples

1. **XTDB Bi-Temporal Database** (2.6k+ stars)
   - GitHub: https://github.com/xtdb/xtdb
   - Documentation: https://v1-docs.xtdb.com/concepts/bitemporality/
   - Use case: "Recording bi-temporal information is essential when dealing with lag, corrections, and efficient auditability"
   - Features: Transaction time for audit, valid time for business logic, retroactive/proactive operations

2. **Temporal Database Patterns**
   - Martin Fowler: "Bitemporal History" (https://martinfowler.com/articles/bitemporal-history.html)
   - Key insight: "Bitemporal history treats time as two dimensions - actual time (valid time) and record time (transaction time)"
   - Pattern: Record history is append-only, allowing retroactive changes without losing original context

### Tier 3: Technical Standards

1. **Wikipedia: Bitemporal Modeling**
   - URL: https://en.wikipedia.org/wiki/Bitemporal_modeling
   - Definition: "Temporal database technique to handle historical data along two timelines: 'as it actually was' + 'as it was recorded'"

2. **Academic: Bi-VAKs Framework**
   - TU Delft Repository: "Bi-Temporal Versioning Approach for Knowledge Graphs"
   - Research on temporal versioning specifically for knowledge graphs

## Implementation Details

### Database Schema Changes

#### Neo4j (via Graphiti)

All relationships will include temporal fields:

```cypher
// Example relationship with bi-temporal fields
CREATE (person:Person {name: 'Alice', uuid: 'uuid-1'})
CREATE (company:Company {name: 'Acme Corp', uuid: 'uuid-2'})
CREATE (person)-[r:WORKS_FOR {
    fact: 'Alice works for Acme Corp as Senior Engineer',

    // Valid Time (business time)
    valid_at: datetime('2023-01-15T00:00:00Z'),
    invalid_at: NULL,  // Still valid

    // Transaction Time (system time)
    created_at: datetime('2023-01-20T10:30:00Z'),
    expired_at: NULL   // Not yet invalidated
}]->(company)
```

#### PostgreSQL (Metadata Tables)

For entities and documents stored in PostgreSQL, we'll use SQL:2011-style temporal tables:

```sql
CREATE TABLE entities (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,

    -- Valid Time (Application Time)
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ DEFAULT 'infinity',

    -- Transaction Time (System Time)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    PERIOD FOR valid_time (valid_from, valid_to)
);

-- Index for temporal queries
CREATE INDEX idx_entities_valid_time
    ON entities USING GIST (tstzrange(valid_from, valid_to));

CREATE INDEX idx_entities_created_at
    ON entities (created_at);
```

### Python Integration Example

```python
from datetime import datetime, timezone
from graphiti_core import Graphiti
from graphiti_core.edges import EntityEdge

# Initialize Graphiti client
client = Graphiti(neo4j_uri="bolt://localhost:7687")

# Add a temporal fact
await client.add_episode(
    content="Alice was promoted to VP of Engineering on January 15, 2024",
    reference_time=datetime(2024, 1, 15, tzinfo=timezone.utc)
)

# Query: "What did we know about Alice's position on February 1?"
results = await client.search(
    query="Alice's job position",
    # Point-in-time query using valid time
    valid_at=datetime(2024, 2, 1, tzinfo=timezone.utc)
)

# Retroactive correction: Alice was actually promoted on January 10
await client.add_episode(
    content="Correction: Alice's promotion was effective January 10, 2024",
    reference_time=datetime(2024, 1, 10, tzinfo=timezone.utc)
)

# The old edge is invalidated (expired_at set), new edge created
# Both remain in the database for audit purposes
```

### Temporal Query Patterns

```python
# 1. Current state query (default)
current = await client.search("Alice's job title")

# 2. Historical query ("What was true on date X?")
historical = await client.search(
    "Alice's job title",
    valid_at=datetime(2023, 6, 1, tzinfo=timezone.utc)
)

# 3. Audit query ("When did we learn about X?")
audit = await client.search(
    "Alice's job title",
    transaction_at=datetime(2024, 1, 20, tzinfo=timezone.utc)
)

# 4. Time-range query ("Show all changes between dates")
changes = await client.get_entity_edges(
    entity_uuid="alice-uuid",
    valid_from=datetime(2023, 1, 1, tzinfo=timezone.utc),
    valid_to=datetime(2024, 1, 1, tzinfo=timezone.utc)
)
```

## Consequences

### Positive Consequences

1. **Time-Travel Queries**: ✅
   - Can reconstruct knowledge state at any point in history
   - Supports "What did we know about X on date Y?" queries
   - Essential for debugging and understanding knowledge evolution

2. **Retroactive Corrections**: ✅
   - Can correct past mistakes without losing original data
   - Maintains complete audit trail of all corrections
   - Critical for data quality and compliance

3. **Audit Compliance**: ✅
   - Full visibility into when facts were learned and when they changed
   - Supports regulatory requirements (GDPR, SOC 2, HIPAA)
   - Enables "who knew what when" analysis

4. **Conflict Resolution**: ✅
   - Temporal metadata disambiguates conflicting information
   - Graphiti intelligently invalidates outdated edges
   - Preserves history for reasoning and analysis

5. **Out-of-Order Ingestion**: ✅
   - Can handle late-arriving data gracefully
   - Valid time allows backdating facts to when they actually occurred
   - Essential for batch processing and data migrations

### Negative Consequences

1. **Storage Overhead**: ⚠️
   - Bi-temporal data can grow 2-4x faster than single-timestamp data
   - Each correction creates new edge rather than updating in-place
   - Historical edges accumulate over time

2. **Query Complexity**: ⚠️
   - Temporal queries require understanding of valid vs. transaction time
   - More complex Cypher queries with temporal predicates
   - Developers need training on bi-temporal concepts

3. **Performance Impact**: ⚠️
   - Temporal range queries can be slower than exact matches
   - More indexes required (valid_from, valid_to, created_at)
   - Join complexity increases with temporal predicates

### Mitigation Strategies

#### 1. Storage Overhead Mitigation

**Partitioning by Time**:
```sql
-- Partition historical edges by year
CREATE TABLE entity_edges_2024 PARTITION OF entity_edges
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE entity_edges_2023 PARTITION OF entity_edges
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
```

**Compression**:
- Enable page-level compression on historical data: `ALTER TABLE entity_edges_2023 SET (compression = 'lz4');`
- Use clustered columnstore indexes for highly compressed historical storage (10:1 compression ratio typical)
- Graphiti automatically handles compression in Neo4j through native graph storage optimizations

**Archival Policies** (Based on Microsoft SQL Server temporal table best practices):

```python
# Configuration for Apex Memory System
TEMPORAL_RETENTION_POLICY = {
    "hot_data_days": 90,        # Last 90 days: full bi-temporal query support
    "warm_data_days": 365,      # 90-365 days: compressed, slower queries OK
    "cold_data_days": 1825,     # 1-5 years: archived to object storage (S3)
    "deletion_after_days": 2555 # >7 years: deleted (compliance permitting)
}

# Automated cleanup task (runs daily)
async def archive_old_edges():
    """Archive edges older than warm_data_threshold to cold storage"""
    warm_threshold = datetime.now() - timedelta(days=365)

    # Find expired edges older than threshold
    old_edges = await db.query("""
        MATCH ()-[r]->()
        WHERE r.expired_at < $threshold
        RETURN r
    """, threshold=warm_threshold)

    # Export to S3 (compressed JSON)
    await export_to_s3(old_edges, bucket="apex-memory-cold-archive")

    # Delete from hot storage
    await db.query("""
        MATCH ()-[r]->()
        WHERE r.expired_at < $threshold
        DELETE r
    """, threshold=warm_threshold)
```

**Sliding Window Approach**:
- Maintain fixed retention window (e.g., 5 years)
- Automatically drop oldest partition when adding new partition
- Keeps storage growth constant over time

#### 2. Query Complexity Mitigation

**Developer Education**:
- Provide bi-temporal query cookbook with common patterns
- Include examples in API documentation
- Create helper functions for common temporal queries

**Abstraction Layer**:
```python
class TemporalQueryHelper:
    """Helper class to simplify bi-temporal queries"""

    @staticmethod
    def get_current_state(entity_uuid: str):
        """Get current valid state (most common query)"""
        return client.search(
            entity_uuid=entity_uuid,
            valid_at=datetime.now(timezone.utc),
            transaction_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def get_historical_state(entity_uuid: str, as_of_date: datetime):
        """Get state as it was known on a specific date"""
        return client.search(
            entity_uuid=entity_uuid,
            valid_at=as_of_date,
            transaction_at=as_of_date
        )

    @staticmethod
    def get_audit_trail(entity_uuid: str):
        """Get complete history of changes"""
        return client.get_entity_edges(
            entity_uuid=entity_uuid,
            include_expired=True
        )
```

**Smart Defaults**:
- Default to current state queries (most common use case)
- Require explicit `as_of_date` parameter for historical queries
- Provide clear error messages when temporal predicates are ambiguous

#### 3. Performance Impact Mitigation

**Indexing Strategy**:

Based on Microsoft Learn guidance for temporal table indexing:

```sql
-- Primary temporal indexes
CREATE INDEX idx_valid_time_range ON entity_edges
    USING GIST (tstzrange(valid_from, valid_to));

CREATE INDEX idx_transaction_time ON entity_edges (created_at);

-- Composite index for common queries
CREATE INDEX idx_entity_temporal ON entity_edges
    (entity_uuid, valid_from, valid_to, created_at);

-- Covering index for audit queries
CREATE INDEX idx_audit_covering ON entity_edges
    (entity_uuid, created_at)
    INCLUDE (valid_from, valid_to, expired_at);
```

**Query Optimization**:
- Use partition elimination for time-range queries
- Leverage Neo4j's native graph indexes for relationship traversal
- Cache frequently accessed historical states in Redis

**Performance Targets**:
- Current state queries: <100ms (P95)
- Historical queries (last 90 days): <500ms (P95)
- Audit trail queries: <2s (P95)
- Archival queries (cold storage): <10s (P95)

**Monitoring**:
```python
# Track query performance by temporal pattern
TEMPORAL_QUERY_METRICS = {
    "current_state": histogram("temporal_query_latency", ["current"]),
    "historical": histogram("temporal_query_latency", ["historical"]),
    "audit_trail": histogram("temporal_query_latency", ["audit"]),
    "time_range": histogram("temporal_query_latency", ["range"])
}
```

## References

### Official Documentation
- [Graphiti GitHub Repository](https://github.com/getzep/graphiti) - Primary implementation (18.6k+ stars)
- [Graphiti Official Docs](https://www.graphiti.dev/) - API reference and guides
- [PostgreSQL SQL:2011 Temporal](https://wiki.postgresql.org/wiki/SQL2011Temporal) - Standard temporal table support
- [Neo4j Temporal Values](https://neo4j.com/docs/cypher-manual/current/values-and-types/temporal/) - Cypher temporal data types

### Verified Examples
- [XTDB Bitemporality Docs](https://v1-docs.xtdb.com/concepts/bitemporality/) - Reference bi-temporal implementation (2.6k+ stars)
- [Martin Fowler: Bitemporal History](https://martinfowler.com/articles/bitemporal-history.html) - Design patterns

### Technical Standards
- [SQL:2011 Standard - Wikipedia](https://en.wikipedia.org/wiki/SQL:2011) - Temporal table standardization
- [Bitemporal Modeling - Wikipedia](https://en.wikipedia.org/wiki/Bitemporal_modeling) - Conceptual overview
- [Microsoft Learn: Temporal Tables](https://learn.microsoft.com/en-us/sql/relational-databases/tables/manage-retention-of-historical-data-in-system-versioned-temporal-tables) - Retention and archival best practices

### Research Papers
- [TU Delft: Bi-VAKs Framework](https://repository.tudelft.nl/islandora/object/uuid:63aeab75-64a5-4b59-9cb0-241b603bd00d) - Bi-temporal versioning for knowledge graphs

---

**Document Metadata**:
- **ADR Number**: 004
- **Created**: 2025-10-06
- **Author**: Deep Researcher (research-first team)
- **Reviewers**: CIO (research quality), CTO (technical architecture), COO (operational feasibility)
- **Status**: Proposed (pending Phase 3.5 Review Board approval)
