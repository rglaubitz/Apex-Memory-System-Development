# Temporal Intelligence - Quick Reference

**For:** Executives, Developers, Research Team
**Purpose:** Fast lookup of key concepts and decisions
**Full Details:** See README.md and INTEGRATION_GUIDE.md

---

## TL;DR - Executive Summary

**Found:** 2 high-quality repositories demonstrating temporal intelligence patterns
- **Graphiti:** 18,600 stars, Python + Neo4j, bi-temporal knowledge graphs
- **XTDB:** 2,600 stars, Clojure + SQL, production-proven temporal database

**Recommendation:** Adopt Graphiti for temporal layer (aligns with Python + Neo4j stack)

**Key Pattern:** Bi-temporal tracking (valid time + transaction time) enables:
- Time-travel queries: "What did we know on date X about reality on date Y?"
- Conflict resolution: Handle contradicting information intelligently
- Compliance: Complete audit trail with no data loss
- Historical analysis: Track how knowledge evolves over time

**Timeline:** Ready for Phase 4 (Implementation)

---

## Bi-Temporal Model - 30 Second Explanation

**Two independent time dimensions:**

1. **Valid Time (Real-World Timeline)**
   - When something is/was/will be TRUE in reality
   - Example: "John became VP on January 15, 2024"
   - Fields: `valid_at`, `invalid_at`

2. **Transaction Time (Database Timeline)**
   - When we LEARNED about something
   - Example: "We recorded the promotion on January 15, 2024"
   - Fields: `created_at`, `expired_at`

**Why both matter:**
- Valid time: "What was true when?" (business domain)
- Transaction time: "What did we know when?" (audit trail)
- Together: Complete temporal intelligence

---

## Repository Scorecard

| Metric | Graphiti | XTDB |
|--------|----------|------|
| **Stars** | 18,600+ | 2,600+ |
| **Quality Gate** | ✅ PASS | ✅ PASS |
| **Active (6mo)** | ✅ Sep 2025 | ✅ Oct 2025 |
| **License** | Apache 2.0 | MIT |
| **Language** | Python | Clojure |
| **Integration** | HIGH (Python+Neo4j) | MEDIUM (Clojure) |
| **Maturity** | v0.20 (Pre-1.0) | v2.0 (GA) |
| **Best For** | AI agent memory | General temporal DB |
| **Apex Fit** | ⭐⭐⭐⭐⭐ Perfect | ⭐⭐⭐ Reference |

---

## Graphiti - Key Features

**What it does:**
- Builds temporal knowledge graphs automatically from text
- Tracks entities and relationships with bi-temporal metadata
- Resolves conflicts intelligently using LLMs
- Enables time-travel queries

**Why we want it:**
- Python + Neo4j (matches our stack)
- 18,600 stars (proven community adoption)
- Active development (release Sep 2025)
- Apache 2.0 license (permissive)

**Bi-temporal fields on every relationship:**
```python
{
    "created_at": "2024-01-15T10:00:00Z",  # Database time
    "expired_at": null,
    "valid_at": "2024-01-15T00:00:00Z",    # Real-world time
    "invalid_at": null
}
```

**Code example:**
```python
# Add episode with temporal context
await graphiti.add_episode(
    name="promotion_notice",
    episode_body="John became VP on January 15, 2024",
    reference_time=datetime(2024, 1, 15)
)

# Query with time-travel
results = await graphiti.search(
    query="What was John's role in December 2023?",
    valid_time=datetime(2023, 12, 1)
)
# Returns: "Senior Engineering Manager" (not VP yet)
```

---

## XTDB - Key Features

**What it does:**
- Production-ready bi-temporal SQL database
- Implements SQL:2011 temporal standard
- Automatic tracking of both time dimensions
- Time-travel queries with standard SQL

**Why it matters:**
- Reference implementation of bi-temporal SQL
- Proven in production (v2.0 GA)
- Query patterns we can adapt
- Validation that bi-temporal works at scale

**SQL example:**
```sql
-- Query data as it existed on specific date
SELECT * FROM employees
FOR VALID_TIME AS OF '2024-01-01'
FOR SYSTEM_TIME AS OF '2024-01-01';
```

**Value for Apex:**
- Pattern reference (not direct integration)
- SQL query inspiration for PostgreSQL
- Architecture validation
- Temporal indexing strategies

---

## Integration Architecture

```
Apex Memory System
├── Graphiti Temporal Layer
│   ├── Bi-temporal knowledge graph
│   ├── LLM entity extraction
│   └── Conflict resolution
│
├── Neo4j (Storage)
│   ├── Temporal relationships
│   └── Historical snapshots
│
├── PostgreSQL + pgvector
│   ├── Temporal entity tables
│   └── Bi-temporal indexes
│
├── Qdrant (Vectors)
│   └── Temporal filtering
│
└── Redis (Cache)
    └── Temporal query cache
```

---

## Query Examples - What Temporal Enables

**1. Point-in-Time Query**
```python
# What did we know on March 1 about employees as-of January 1?
query_at_time(
    entity="employees",
    valid_time="2024-01-01",
    transaction_time="2024-03-01"
)
```

**2. Historical Tracking**
```python
# Show me John's complete job history
get_entity_history(
    entity_id="john_smith",
    start_time="2020-01-01",
    end_time="2024-12-31"
)
```

**3. Temporal Join**
```cypher
// Who reported to Alice on specific date?
MATCH (p:Person)-[r:REPORTS_TO]->(m:Person {name: "Alice"})
WHERE r.valid_at <= datetime('2024-06-01')
  AND (r.invalid_at IS NULL OR r.invalid_at > datetime('2024-06-01'))
RETURN p.name
```

**4. Conflict Resolution**
```python
# Late-arriving data: Correct past error
ingest_document(
    content="John's actual 2023 salary was $95k",
    reference_time=datetime(2023, 1, 1)  # Backdated
)
# Old record preserved with updated invalid_at
# New record created with corrected information
```

---

## Schema Quick Reference

### PostgreSQL Temporal Entity
```sql
CREATE TABLE temporal_entities (
    id UUID PRIMARY KEY,
    entity_id VARCHAR NOT NULL,
    properties JSONB,
    embedding vector(1536),

    -- Transaction time
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    -- Valid time
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,

    -- Metadata
    source VARCHAR,
    confidence REAL
);
```

### Neo4j Temporal Relationship
```cypher
CREATE (p:Person)-[r:HAS_ROLE {
    // Transaction time
    created_at: datetime(),
    expired_at: null,

    // Valid time
    valid_at: datetime('2024-01-15'),
    invalid_at: null,

    // Metadata
    fact: "John is VP of Engineering",
    source: "HR System",
    confidence: 1.0
}]->(role:Role)
```

---

## Performance Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| Point-in-time query | <500ms | Temporal indexes + caching |
| History retrieval | <1s | Composite indexes |
| Cache hit rate | >70% | Redis temporal cache |
| Conflict resolution | <100ms | LLM-based semantic match |
| Storage overhead | <30% | Partition old data |

---

## Implementation Checklist

**Phase 4 (Implementation):**
- [ ] Install Graphiti (`pip install graphiti-core`)
- [ ] Configure Neo4j connection
- [ ] Add temporal columns to PostgreSQL
- [ ] Create temporal indexes
- [ ] Implement TemporalIntelligenceService
- [ ] Build temporal query API endpoints
- [ ] Configure Redis caching

**Phase 5 (Testing):**
- [ ] Unit tests for temporal validation
- [ ] Integration tests for bi-temporal queries
- [ ] Performance benchmarks
- [ ] Conflict resolution testing
- [ ] Time-travel query validation

---

## Common Temporal Patterns

### Pattern 1: Track Property Changes
```python
# Store each change with temporal bounds
entity_properties = [
    {
        "key": "title",
        "value": "Engineer",
        "valid_from": "2020-01-01",
        "valid_to": "2022-06-30"
    },
    {
        "key": "title",
        "value": "Senior Engineer",
        "valid_from": "2022-07-01",
        "valid_to": "2024-01-14"
    },
    {
        "key": "title",
        "value": "VP Engineering",
        "valid_from": "2024-01-15",
        "valid_to": null  # Current
    }
]
```

### Pattern 2: Retroactive Correction
```python
# Correct historical error without losing audit trail
correct_past_data(
    entity_id="john_smith",
    property="salary",
    corrected_value=95000,
    valid_from=datetime(2023, 1, 1),  # Backdated
    correction_reason="Data entry error discovered"
)
# Old value preserved with updated invalid_at
# New value created with valid_from in past
```

### Pattern 3: Temporal Aggregation
```sql
-- Average salary by quarter over time
SELECT
    DATE_TRUNC('quarter', valid_from) AS quarter,
    AVG(salary) AS avg_salary
FROM temporal_entities
WHERE entity_type = 'employee'
GROUP BY quarter
ORDER BY quarter;
```

---

## Risk Assessment

**Graphiti Adoption Risks:**

| Risk | Severity | Mitigation |
|------|----------|------------|
| Pre-1.0 API changes | MEDIUM | Pin version, monitor releases |
| Performance at scale | MEDIUM | Benchmark early, optimize indexes |
| LLM dependency | LOW | Configurable LLM provider |
| Learning curve | LOW | Good documentation, examples |

**Overall Risk:** LOW-MEDIUM (benefits outweigh risks)

---

## Decision Matrix

**When to use Graphiti:**
- ✅ Temporal knowledge graphs
- ✅ AI agent memory
- ✅ Automatic entity extraction
- ✅ Real-time updates with conflicts

**When to use PostgreSQL temporal:**
- ✅ Structured data with known schema
- ✅ Hybrid semantic + temporal queries
- ✅ High-performance point lookups
- ✅ SQL compatibility required

**When to use Neo4j temporal:**
- ✅ Complex graph traversals over time
- ✅ Relationship-heavy queries
- ✅ Temporal graph analytics
- ✅ Integration with Graphiti

**When to reference XTDB:**
- ✅ Learning bi-temporal SQL patterns
- ✅ Validating temporal architecture
- ✅ Understanding immutable storage
- ❌ Not for direct integration (Clojure)

---

## Key Citations

1. **Graphiti GitHub:** https://github.com/getzep/graphiti (18.6k stars)
2. **Graphiti Docs:** https://help.getzep.com/graphiti/
3. **Graphiti Paper:** https://blog.getzep.com/content/files/2025/01/ZEP__USING_KNOWLEDGE_GRAPHS_TO_POWER_LLM_AGENT_MEMORY_2025011700.pdf
4. **XTDB GitHub:** https://github.com/xtdb/xtdb (2.6k stars)
5. **XTDB Docs:** https://docs.xtdb.com/
6. **XTDB Bitemporal:** https://v1-docs.xtdb.com/concepts/bitemporality/

---

## Glossary

**Bi-temporal:** Two independent time dimensions (valid + transaction)
**Valid Time:** When a fact is true in the real world
**Transaction Time:** When a fact was recorded in the database
**Point-in-Time Query:** Query data as it existed at specific moment
**Temporal Join:** Join entities at consistent point in time
**Retroactive Write:** Insert data with valid time in the past
**Conflict Resolution:** Handle contradicting information about same entity
**Time-Travel Query:** Query historical states of data
**Temporal Range:** Query all changes during a time period

---

## FAQ

**Q: Why two time dimensions instead of one?**
A: Valid time tracks real-world truth, transaction time tracks knowledge. Separating them enables both "what was true when?" and "what did we know when?" queries.

**Q: What's the storage overhead?**
A: Typically 20-30% for temporal metadata. Mitigated by partitioning and archiving old data.

**Q: Can we query current data without temporal filtering?**
A: Yes. Temporal filtering is optional. Default behavior returns current state.

**Q: How do we handle late-arriving data?**
A: Set valid_at to past date when ingesting. Graphiti handles temporal alignment automatically.

**Q: What about performance?**
A: Temporal indexes + caching keep queries fast. Target <500ms for point-in-time queries.

**Q: Is Graphiti production-ready?**
A: Yes, but pre-1.0. 25k weekly downloads, active development. Pin version for stability.

**Q: Do we need Graphiti AND custom temporal tables?**
A: Recommend Graphiti for knowledge graphs, PostgreSQL temporal for structured data. Both use same bi-temporal pattern.

**Q: What if Graphiti API changes?**
A: Pin version, monitor releases. Core bi-temporal concepts stable (based on SQL:2011).

---

## Next Steps by Role

**CIO (Information Officer):**
- [ ] Validate research quality (sources, citations)
- [ ] Verify GitHub stats (stars, activity, license)
- [ ] Review documentation completeness
- [ ] Approve for Phase 3.5 Review Board

**CTO (Technology Officer):**
- [ ] Assess technical feasibility
- [ ] Review integration architecture
- [ ] Validate performance targets
- [ ] Design temporal schema
- [ ] Approve for implementation

**COO (Operations Officer):**
- [ ] Estimate implementation timeline
- [ ] Assess team capability
- [ ] Plan resource allocation
- [ ] Define success metrics
- [ ] Approve operational plan

**Development Team:**
- [ ] Study Graphiti examples
- [ ] Design temporal service API
- [ ] Create migration plan
- [ ] Write integration tests
- [ ] Prepare Phase 4 tasks

---

## Resources

**Documentation:**
- Full research: `README.md`
- Integration guide: `INTEGRATION_GUIDE.md`
- Graphiti docs: `research/documentation/graphiti/`

**Code Examples:**
- Graphiti examples: https://github.com/getzep/graphiti/tree/main/examples
- XTDB examples: https://docs.xtdb.com/

**Support:**
- Graphiti discussions: https://github.com/getzep/graphiti/discussions
- XTDB forums: https://github.com/orgs/xtdb/discussions

---

**Document Version:** 1.0
**Last Updated:** October 6, 2025
**Status:** Ready for Review
**Companion Docs:** README.md, INTEGRATION_GUIDE.md
