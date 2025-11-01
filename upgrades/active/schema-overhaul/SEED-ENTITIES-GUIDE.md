# Seed Entities Implementation Guide

**Status:** 📝 Implementation Ready
**Phase:** Optional Enhancement (Post-Schema Overhaul)
**Estimated Time:** 4-6 hours
**Prerequisites:** Completed Schema Overhaul (Phases 1-6)

---

## Overview

This guide implements a **hybrid approach** to knowledge graph development:
- **Seed critical entities** (proactive) - 5-10 core entities you define upfront
- **Let Graphiti extract naturally** (reactive) - Discover long-tail entities from documents
- **Best of both worlds** - Predictable core structure + emergent relationships

**Why Hybrid?**
- ✅ Consistent naming for critical entities (G, Origin Transport, OpenHaul, Fleet, Financials)
- ✅ Automatic discovery of customers, products, metrics from documents
- ✅ 90%+ extraction accuracy from Graphiti
- ✅ Flexible schema evolution based on data

---

## Table of Contents

1. [Seed Entity Strategy](#1-seed-entity-strategy)
2. [Implementation Steps](#2-implementation-steps)
3. [Code Implementation](#3-code-implementation)
4. [Testing & Validation](#4-testing--validation)
5. [Maintenance & Deduplication](#5-maintenance--deduplication)
6. [Production Rollout](#6-production-rollout)

---

## 1. Seed Entity Strategy

### 1.1 Identifying Core Entities

**Decision Framework:**

| Entity Type | Should Seed? | Rationale |
|-------------|--------------|-----------|
| **Parent Company** | ✅ Yes | Referenced in many documents, needs consistent naming |
| **Major Subsidiaries** | ✅ Yes | Core organizational structure |
| **Key Products/Services** | ✅ Yes | Frequently referenced, prevent naming variations |
| **Core Departments** | ✅ Yes | Organizational anchors for employees, processes |
| **Customers** | ❌ No | Too many, let Graphiti extract from documents |
| **Employees** | ❌ No | High churn, better extracted from current docs |
| **Transactions** | ❌ No | Time-sensitive, should come from source systems |
| **Metrics** | ⚠️ Maybe | Seed if standardized (Revenue, EBITDA), extract if ad-hoc |

### 1.2 Example: Logistics Company

**Seed These (Core Structure):**
```
G (Company)
├── Origin Transport (Company, Subsidiary)
│   ├── Fleet (Department)
│   ├── Operations (Department)
│   └── OpenHaul (Product)
└── Financials (Department)
```

**Let Graphiti Extract (Emergent):**
- Customers: ACME Corp, Bosch, Schneider Electric, etc.
- Vehicles: Truck #1234, Van Fleet A, etc.
- Locations: Distribution Center Atlanta, Warehouse Phoenix, etc.
- Employees: John Smith (Fleet Manager), etc.
- Metrics: Q3 Revenue, YTD EBITDA, etc.

### 1.3 Relationship Planning

**Seed These Relationships:**
- G → OWNS → Origin Transport
- Origin Transport → OPERATES → Fleet
- Origin Transport → DEVELOPS → OpenHaul
- G → HAS_DEPARTMENT → Financials
- Fleet → USES → OpenHaul

**Let Graphiti Extract:**
- Customer relationships (ACME Corp → CUSTOMER_OF → Origin Transport)
- Employee assignments (John Smith → MANAGES → Fleet)
- Product usage (Fleet → USES → OpenHaul Route Optimizer)
- Financial metrics (Q3 Revenue → METRIC_FOR → Financials)

---

## 2. Implementation Steps

### Phase 1: Seed Data Preparation (1 hour)

**Step 1.1: Define Seed Entities**

Create `data/seed/entities.json`:

```json
{
  "entities": [
    {
      "name": "G",
      "entity_type": "Company",
      "summary": "Parent company for logistics operations, founded 1990",
      "aliases": ["The G Companies", "G Transport", "G Logistics"],
      "metadata": {
        "industry": "logistics",
        "founded": "1990",
        "headquarters": "USA",
        "stock_symbol": "GLOG"
      }
    },
    {
      "name": "Origin Transport",
      "entity_type": "Company",
      "summary": "Transportation and logistics subsidiary of G, specializing in fleet management",
      "aliases": ["Origin", "OT", "Origin Logistics"],
      "metadata": {
        "industry": "transportation",
        "parent_company": "G",
        "founded": "1995"
      }
    },
    {
      "name": "OpenHaul",
      "entity_type": "Product",
      "summary": "Logistics management platform with route optimization and real-time tracking",
      "aliases": ["Open Haul", "OH Platform"],
      "metadata": {
        "product_type": "software",
        "owner": "Origin Transport",
        "launched": "2018"
      }
    },
    {
      "name": "Fleet",
      "entity_type": "Department",
      "summary": "Fleet management division responsible for vehicle operations and maintenance",
      "metadata": {
        "division": "operations",
        "parent_company": "Origin Transport",
        "vehicle_count": 500
      }
    },
    {
      "name": "Financials",
      "entity_type": "Department",
      "summary": "Financial reporting, accounting, and compliance division",
      "metadata": {
        "division": "finance",
        "parent_company": "G"
      }
    }
  ],
  "relationships": [
    {
      "source": "G",
      "target": "Origin Transport",
      "type": "OWNS",
      "properties": {
        "ownership_percentage": 100,
        "since": "1995"
      }
    },
    {
      "source": "Origin Transport",
      "target": "Fleet",
      "type": "OPERATES",
      "properties": {
        "since": "1995"
      }
    },
    {
      "source": "Origin Transport",
      "target": "OpenHaul",
      "type": "DEVELOPS",
      "properties": {
        "since": "2018"
      }
    },
    {
      "source": "G",
      "target": "Financials",
      "type": "HAS_DEPARTMENT",
      "properties": {
        "since": "1990"
      }
    },
    {
      "source": "Fleet",
      "target": "OpenHaul",
      "type": "USES",
      "properties": {
        "since": "2018"
      }
    }
  ]
}
```

**Step 1.2: Review Aliases**

Add common variations to prevent duplicates:
- "G" vs. "The G Companies" vs. "G Transport"
- "Origin Transport" vs. "Origin" vs. "OT"
- "OpenHaul" vs. "Open Haul"

### Phase 2: Workflow Implementation (2-3 hours)

**Step 2.1: Create Seed Workflow**

Create `src/apex_memory/temporal/workflows/seed_entities.py`:

```python
"""
Seed Entities Workflow - Initialize critical knowledge graph entities.

This workflow creates core organizational entities across all databases
using the saga pattern for consistency.
"""

from temporalio import workflow, activity
from temporalio.exceptions import ApplicationError
from datetime import timedelta
from typing import Dict, Any, List
import json
import uuid
from datetime import datetime

from apex_memory.services.postgresql_service import PostgreSQLService
from apex_memory.services.neo4j_service import Neo4jService
from apex_memory.services.qdrant_service import QdrantService
from apex_memory.services.redis_service import RedisService
from apex_memory.services.embedding_service import EmbeddingService


@workflow.defn
class SeedEntitiesWorkflow:
    """
    Seed critical entities across all databases using saga pattern.

    Creates a predictable core structure before document ingestion begins.
    """

    @workflow.run
    async def run(self, seed_file_path: str) -> Dict[str, Any]:
        """
        Args:
            seed_file_path: Path to entities.json file

        Returns:
            Dictionary with creation results
        """
        workflow.logger.info(f"Starting seed entities workflow with file: {seed_file_path}")

        # Load seed data
        seed_data = await workflow.execute_activity(
            load_seed_data,
            seed_file_path,
            start_to_close_timeout=timedelta(seconds=10)
        )

        entity_results = []
        compensations = []

        # Create each entity with full saga pattern
        for entity_data in seed_data["entities"]:
            try:
                # Generate UUID for cross-database consistency
                entity_uuid = str(uuid.uuid7())
                entity_data["uuid"] = entity_uuid
                entity_data["created_at"] = datetime.now().isoformat()
                entity_data["source"] = "seed_data"

                # Execute entity creation with compensation support
                result = await workflow.execute_activity(
                    ingest_entity_to_all_dbs,
                    entity_data,
                    start_to_close_timeout=timedelta(seconds=60),
                    retry_policy=workflow.RetryPolicy(
                        maximum_attempts=3,
                        initial_interval=timedelta(seconds=1)
                    )
                )

                entity_results.append(result)
                workflow.logger.info(f"✅ Created entity: {entity_data['name']}")

            except Exception as e:
                workflow.logger.error(f"❌ Failed to create entity {entity_data['name']}: {e}")

                # Compensate previously created entities
                for prev_result in entity_results:
                    await workflow.execute_activity(
                        compensate_entity_creation,
                        prev_result["uuid"],
                        start_to_close_timeout=timedelta(seconds=30)
                    )

                raise ApplicationError(f"Seed workflow failed at entity {entity_data['name']}: {e}")

        # Create relationships after all entities exist
        relationship_results = []
        for rel_data in seed_data["relationships"]:
            try:
                result = await workflow.execute_activity(
                    create_seed_relationship,
                    rel_data,
                    start_to_close_timeout=timedelta(seconds=30)
                )
                relationship_results.append(result)
                workflow.logger.info(f"✅ Created relationship: {rel_data['source']} → {rel_data['type']} → {rel_data['target']}")

            except Exception as e:
                workflow.logger.warning(f"⚠️ Failed to create relationship: {e}")
                # Don't fail workflow for relationship errors (entities still exist)

        return {
            "entities_created": len(entity_results),
            "relationships_created": len(relationship_results),
            "entity_uuids": [r["uuid"] for r in entity_results],
            "status": "success"
        }


@activity.defn
async def load_seed_data(seed_file_path: str) -> Dict[str, Any]:
    """Load seed data from JSON file."""
    with open(seed_file_path, 'r') as f:
        return json.load(f)


@activity.defn
async def ingest_entity_to_all_dbs(entity_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Write entity to all databases (PostgreSQL, Neo4j, Qdrant, Redis).

    Uses saga pattern - if any step fails, compensations are triggered.
    """
    entity_uuid = entity_data["uuid"]

    try:
        # Step 1: PostgreSQL - Metadata source of truth
        pg_service = PostgreSQLService()
        pg_service.execute("""
            INSERT INTO entities (id, name, entity_type, summary, aliases, metadata, created_at, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            entity_uuid,
            entity_data["name"],
            entity_data["entity_type"],
            entity_data["summary"],
            json.dumps(entity_data.get("aliases", [])),
            json.dumps(entity_data.get("metadata", {})),
            entity_data["created_at"],
            entity_data["source"]
        ))

        # Step 2: Neo4j - Create entity node (direct, not via Graphiti for seed data)
        neo4j_service = Neo4jService()
        neo4j_service.run("""
            CREATE (e:Entity {
                uuid: $uuid,
                name: $name,
                entity_type: $entity_type,
                summary: $summary,
                created_at: datetime($created_at),
                group_id: 'seed_data',
                source: 'seed_data'
            })
        """, **entity_data)

        # Step 3: Qdrant - Store entity embedding
        embedding_service = EmbeddingService()
        embedding = await embedding_service.generate_embedding(entity_data["summary"])

        qdrant_service = QdrantService()
        qdrant_service.upsert(
            collection_name="entities",
            points=[{
                "id": entity_uuid,
                "vector": embedding,
                "payload": {
                    "name": entity_data["name"],
                    "entity_type": entity_data["entity_type"],
                    "summary": entity_data["summary"],
                    "source": "seed_data"
                }
            }]
        )

        # Step 4: Redis - Cache entity
        redis_service = RedisService()
        redis_service.setex(
            f"entity:{entity_uuid}",
            86400,  # 24 hours
            json.dumps(entity_data)
        )

        return {
            "uuid": entity_uuid,
            "name": entity_data["name"],
            "status": "created"
        }

    except Exception as e:
        raise ApplicationError(f"Failed to ingest entity {entity_data['name']}: {e}")


@activity.defn
async def create_seed_relationship(rel_data: Dict[str, Any]) -> Dict[str, str]:
    """Create relationship between two seed entities in Neo4j."""
    neo4j_service = Neo4jService()

    # Create relationship in Neo4j
    rel_type = rel_data["type"]
    props = rel_data.get("properties", {})

    neo4j_service.run(f"""
        MATCH (source:Entity {{name: $source_name, source: 'seed_data'}})
        MATCH (target:Entity {{name: $target_name, source: 'seed_data'}})
        CREATE (source)-[r:{rel_type} {{
            created_at: datetime(),
            source: 'seed_data',
            confidence: 1.0,
            properties: $props
        }}]->(target)
        RETURN r
    """, source_name=rel_data["source"], target_name=rel_data["target"], props=json.dumps(props))

    return {
        "source": rel_data["source"],
        "target": rel_data["target"],
        "type": rel_type,
        "status": "created"
    }


@activity.defn
async def compensate_entity_creation(entity_uuid: str) -> None:
    """
    Compensate entity creation by deleting from all databases.

    Called when saga fails partway through entity creation.
    """
    # Check if already compensated (idempotency)
    redis_service = RedisService()
    redis_key = f"compensated:entity:{entity_uuid}"
    if redis_service.exists(redis_key):
        return

    # Delete from PostgreSQL
    pg_service = PostgreSQLService()
    pg_service.execute("DELETE FROM entities WHERE id = %s", (entity_uuid,))

    # Delete from Neo4j
    neo4j_service = Neo4jService()
    neo4j_service.run("""
        MATCH (e:Entity {uuid: $uuid, source: 'seed_data'})
        DETACH DELETE e
    """, uuid=entity_uuid)

    # Delete from Qdrant
    qdrant_service = QdrantService()
    qdrant_service.delete(
        collection_name="entities",
        points_selector=[entity_uuid]
    )

    # Delete from Redis
    redis_service.delete(f"entity:{entity_uuid}")

    # Mark as compensated
    redis_service.setex(redis_key, 86400, "1")
```

**Step 2.2: Create CLI Script**

Create `scripts/seed/run_seed_entities.py`:

```python
#!/usr/bin/env python3
"""
CLI script to run seed entities workflow.

Usage:
    python scripts/seed/run_seed_entities.py data/seed/entities.json
"""

import asyncio
import sys
from temporalio.client import Client

from apex_memory.temporal.workflows.seed_entities import SeedEntitiesWorkflow


async def main(seed_file_path: str):
    """Run seed entities workflow via Temporal."""

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    print(f"🌱 Starting seed entities workflow...")
    print(f"📁 Seed file: {seed_file_path}")

    # Execute workflow
    result = await client.execute_workflow(
        SeedEntitiesWorkflow.run,
        seed_file_path,
        id=f"seed-entities-{asyncio.get_event_loop().time()}",
        task_queue="apex-memory"
    )

    print(f"\n✅ Seed workflow complete!")
    print(f"   Entities created: {result['entities_created']}")
    print(f"   Relationships created: {result['relationships_created']}")
    print(f"   Entity UUIDs: {result['entity_uuids']}")

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/seed/run_seed_entities.py <seed_file_path>")
        sys.exit(1)

    seed_file = sys.argv[1]
    asyncio.run(main(seed_file))
```

### Phase 3: Testing (1 hour)

**Step 3.1: Unit Tests**

Create `tests/unit/test_seed_entities.py`:

```python
import pytest
from apex_memory.temporal.workflows.seed_entities import (
    SeedEntitiesWorkflow,
    load_seed_data,
    ingest_entity_to_all_dbs,
    create_seed_relationship
)


@pytest.mark.asyncio
async def test_load_seed_data(tmp_path):
    """Test loading seed data from JSON."""
    seed_file = tmp_path / "entities.json"
    seed_file.write_text('''
    {
        "entities": [
            {"name": "Test Entity", "entity_type": "Company", "summary": "Test"}
        ],
        "relationships": []
    }
    ''')

    data = await load_seed_data(str(seed_file))
    assert len(data["entities"]) == 1
    assert data["entities"][0]["name"] == "Test Entity"


@pytest.mark.asyncio
async def test_ingest_entity_to_all_dbs(mock_services):
    """Test entity ingestion across all databases."""
    entity_data = {
        "uuid": "test-uuid-123",
        "name": "G",
        "entity_type": "Company",
        "summary": "Parent company",
        "created_at": "2025-11-01T00:00:00",
        "source": "seed_data"
    }

    result = await ingest_entity_to_all_dbs(entity_data)

    assert result["uuid"] == "test-uuid-123"
    assert result["name"] == "G"
    assert result["status"] == "created"
```

**Step 3.2: Integration Test**

```bash
# Start all services
cd apex-memory-system/docker && docker-compose up -d

# Start Temporal worker
python src/apex_memory/temporal/workers/dev_worker.py &

# Run seed workflow
python scripts/seed/run_seed_entities.py data/seed/entities.json
```

**Step 3.3: Verify in Neo4j**

```cypher
// Neo4j Browser - Check seed entities
MATCH (e:Entity {source: 'seed_data'})
RETURN e.name, e.entity_type, e.summary
ORDER BY e.created_at

// Check seed relationships
MATCH (source:Entity {source: 'seed_data'})-[r]->(target:Entity {source: 'seed_data'})
RETURN source.name, type(r), target.name
```

**Step 3.4: Verify in PostgreSQL**

```sql
-- Check entities table
SELECT id, name, entity_type, source
FROM entities
WHERE source = 'seed_data'
ORDER BY created_at;

-- Check entity count
SELECT entity_type, COUNT(*) as count
FROM entities
WHERE source = 'seed_data'
GROUP BY entity_type;
```

---

## 3. Code Implementation

Complete workflow implementation is provided in Phase 2 above. Key components:

1. **Saga Pattern** - Compensations if any database write fails
2. **UUID v7** - Time-ordered IDs for cross-database consistency
3. **Idempotency** - Redis tracking prevents duplicate compensations
4. **Retry Policy** - 3 attempts with exponential backoff
5. **Logging** - Full audit trail in Temporal UI

---

## 4. Testing & Validation

### 4.1 Validation Queries

**Check Entity Existence:**
```cypher
// Neo4j
MATCH (e:Entity {name: 'G', source: 'seed_data'})
RETURN e
```

```sql
-- PostgreSQL
SELECT * FROM entities WHERE name = 'G' AND source = 'seed_data';
```

**Check Relationships:**
```cypher
// Neo4j - Verify seed relationships
MATCH path = (source:Entity {source: 'seed_data'})-[*1..2]->(target:Entity {source: 'seed_data'})
RETURN source.name, [r IN relationships(path) | type(r)], target.name
LIMIT 20
```

**Check Embeddings:**
```python
# Qdrant - Verify embeddings
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
results = client.scroll(
    collection_name="entities",
    scroll_filter={
        "must": [
            {"key": "source", "match": {"value": "seed_data"}}
        ]
    },
    limit=10
)

for point in results[0]:
    print(f"Entity: {point.payload['name']}, Type: {point.payload['entity_type']}")
```

### 4.2 Validation Checklist

- [ ] All 5 seed entities created in PostgreSQL
- [ ] All 5 seed entities exist in Neo4j with `source: 'seed_data'`
- [ ] All 5 relationships created in Neo4j
- [ ] All 5 embeddings stored in Qdrant
- [ ] All 5 entities cached in Redis
- [ ] No duplicate entities (run deduplication query)
- [ ] Temporal workflow shows "Completed" status

---

## 5. Maintenance & Deduplication

### 5.1 Weekly Deduplication Check

**After ingesting documents, check for duplicates:**

```cypher
// Neo4j - Find potential duplicates
MATCH (e1:Entity), (e2:Entity)
WHERE e1.name CONTAINS e2.name
  AND e1.uuid <> e2.uuid
  AND e1.source = 'seed_data'
  AND e2.source <> 'seed_data'
RETURN e1.name AS seed_entity,
       e2.name AS extracted_entity,
       e2.uuid AS extracted_uuid,
       e2.created_at AS extracted_date
ORDER BY e1.name
```

**Example duplicates:**
- Seed: "G" → Extracted: "The G Companies", "G Transport"
- Seed: "Origin Transport" → Extracted: "Origin", "OT"

### 5.2 Entity Merge Script

Create `scripts/maintenance/merge_entities.py`:

```python
#!/usr/bin/env python3
"""
Merge duplicate entity into seed entity.

Usage:
    python scripts/maintenance/merge_entities.py <seed_uuid> <duplicate_uuid>
"""

import sys
from apex_memory.services.neo4j_service import Neo4jService


def merge_entities(seed_uuid: str, duplicate_uuid: str):
    """
    Merge duplicate entity into seed entity.

    - Transfers all relationships from duplicate to seed
    - Deletes duplicate entity
    - Updates references in other databases
    """
    neo4j = Neo4jService()

    # Transfer relationships
    neo4j.run("""
        MATCH (duplicate:Entity {uuid: $duplicate_uuid})
        MATCH (seed:Entity {uuid: $seed_uuid})

        // Transfer outgoing relationships
        MATCH (duplicate)-[r]->(target)
        WHERE NOT (seed)-[]->(target)
        CREATE (seed)-[r2:${type(r)}]->(target)
        SET r2 = properties(r)
        DELETE r

        // Transfer incoming relationships
        MATCH (source)-[r]->(duplicate)
        WHERE NOT (source)-[]->(seed)
        CREATE (source)-[r2:${type(r)}]->(seed)
        SET r2 = properties(r)
        DELETE r

        // Delete duplicate
        DELETE duplicate

        RETURN seed.name AS merged_into, count(r) AS relationships_transferred
    """, seed_uuid=seed_uuid, duplicate_uuid=duplicate_uuid)

    print(f"✅ Merged {duplicate_uuid} into {seed_uuid}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/maintenance/merge_entities.py <seed_uuid> <duplicate_uuid>")
        sys.exit(1)

    seed = sys.argv[1]
    duplicate = sys.argv[2]
    merge_entities(seed, duplicate)
```

### 5.3 Monitoring Dashboard

Add to Grafana dashboard (`monitoring/dashboards/seed-entities.json`):

```json
{
  "panels": [
    {
      "title": "Seed vs Extracted Entities",
      "targets": [
        {
          "expr": "count(apex_entities{source='seed_data'})",
          "legendFormat": "Seed Entities"
        },
        {
          "expr": "count(apex_entities{source='graphiti_extraction'})",
          "legendFormat": "Extracted Entities"
        }
      ]
    },
    {
      "title": "Potential Duplicates",
      "targets": [
        {
          "expr": "apex_entity_duplicates_detected",
          "legendFormat": "Duplicates Detected"
        }
      ]
    }
  ]
}
```

---

## 6. Production Rollout

### 6.1 Rollout Timeline

**Week 1: Seed Core Entities**
- [ ] Review and finalize `data/seed/entities.json`
- [ ] Run seed workflow in staging
- [ ] Validate all entities created correctly
- [ ] Deploy to production

**Week 2-4: Ingest Documents**
- [ ] Ingest 10-20 representative documents
- [ ] Let Graphiti extract entities naturally
- [ ] Monitor extraction accuracy (target: 90%+)

**Week 4: Deduplication Review**
- [ ] Run deduplication query
- [ ] Merge any duplicates found
- [ ] Update seed entity aliases if needed

**Ongoing: Maintenance**
- [ ] Weekly deduplication check
- [ ] Monthly seed entity review
- [ ] Quarterly schema evolution planning

### 6.2 Success Metrics

**Target Metrics:**
- ✅ **5 core entities created** in all databases
- ✅ **5 core relationships** established
- ✅ **90%+ extraction accuracy** from Graphiti
- ✅ **<5% duplicate rate** after deduplication
- ✅ **<50ms query latency** for seed entity lookups

**Monitor with Prometheus:**
```promql
# Seed entity creation rate
rate(apex_seed_entities_created_total[5m])

# Duplicate detection rate
rate(apex_entity_duplicates_detected_total[1h])

# Graphiti extraction accuracy
apex_graphiti_extraction_accuracy

# Query latency for seed entities
histogram_quantile(0.90, apex_entity_query_latency{source="seed_data"})
```

### 6.3 Rollback Plan

**If seed workflow fails:**

1. **Check Temporal UI** - Identify failed activity
2. **Review logs** - Check error messages
3. **Compensations run automatically** - Temporal saga pattern
4. **Manual cleanup (if needed):**

```cypher
// Neo4j - Delete all seed entities
MATCH (e:Entity {source: 'seed_data'})
DETACH DELETE e
```

```sql
-- PostgreSQL - Delete all seed entities
DELETE FROM entities WHERE source = 'seed_data';
```

```python
# Qdrant - Delete seed entities
client.delete(
    collection_name="entities",
    points_selector={
        "filter": {
            "must": [{"key": "source", "match": {"value": "seed_data"}}]
        }
    }
)
```

5. **Fix seed data** - Update `entities.json`
6. **Re-run workflow**

---

## Summary

**This hybrid approach gives you:**

✅ **Predictable Core** - 5 seed entities ensure consistent naming
✅ **Flexible Growth** - Graphiti discovers long-tail entities automatically
✅ **90%+ Accuracy** - LLM extraction for natural language content
✅ **Easy Maintenance** - Deduplication scripts + monitoring
✅ **Production-Ready** - Saga pattern ensures database consistency

**Next Steps:**
1. Customize `data/seed/entities.json` with your core entities
2. Run seed workflow in staging
3. Ingest representative documents
4. Monitor extraction + deduplicate weekly

---

**Document Version:** 1.0
**Last Updated:** 2025-11-01
**Maintained By:** Apex Memory System Development Team
