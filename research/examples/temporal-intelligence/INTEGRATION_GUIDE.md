# Temporal Intelligence Integration Guide

**Purpose:** Practical implementation patterns for integrating bi-temporal intelligence into Apex Memory System
**Reference:** README.md (main research document)
**Status:** Implementation Blueprint

---

## Quick Reference

### Bi-Temporal Schema for Apex Memory System

```python
# Entity temporal metadata (PostgreSQL + Neo4j)
class TemporalEntity:
    # Core identity
    id: str
    type: str

    # Transaction time (database timeline)
    created_at: datetime  # When entity was created in system
    updated_at: datetime  # When entity was last modified
    deleted_at: datetime | None  # Soft delete timestamp

    # Valid time (real-world timeline)
    valid_from: datetime | None  # When entity became valid in reality
    valid_to: datetime | None  # When entity ceased being valid

    # Metadata
    source: str  # Where information came from
    confidence: float  # Confidence score (0-1)
    version: int  # Version number for optimistic locking


# Relationship temporal metadata (Neo4j)
class TemporalRelationship:
    # Core identity
    source_id: str
    target_id: str
    type: str

    # Transaction time (database timeline)
    created_at: datetime  # When relationship was created
    expired_at: datetime | None  # When relationship was invalidated

    # Valid time (real-world timeline)
    valid_at: datetime | None  # When relationship became true
    invalid_at: datetime | None  # When relationship ceased being true

    # Metadata
    fact: str  # Natural language description
    source: str  # Source of information
    confidence: float  # Confidence score (0-1)
```

---

## Integration Pattern 1: Graphiti as Temporal Layer

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐      ┌──────────────────┐                │
│  │  Ingestion    │      │  Query Router    │                │
│  │  Pipeline     │      │                  │                │
│  └───────┬───────┘      └────────┬─────────┘                │
│          │                       │                           │
│          ▼                       ▼                           │
│  ┌───────────────────────────────────────────┐              │
│  │        Graphiti Temporal Layer            │              │
│  │  ┌─────────────────────────────────────┐  │              │
│  │  │  Bi-Temporal Knowledge Graph        │  │              │
│  │  │  - created_at / expired_at          │  │              │
│  │  │  - valid_at / invalid_at            │  │              │
│  │  │  - Conflict resolution              │  │              │
│  │  │  - LLM entity extraction            │  │              │
│  │  └─────────────────────────────────────┘  │              │
│  └───────────────────┬───────────────────────┘              │
│                      │                                       │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Neo4j Graph Database                     │  │
│  │  - Temporal relationships                             │  │
│  │  - Entity connections                                 │  │
│  │  - Historical snapshots                               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Parallel Databases:                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PostgreSQL   │  │   Qdrant     │  │    Redis     │      │
│  │ + pgvector   │  │   Vector     │  │    Cache     │      │
│  │ Temporal idx │  │   Search     │  │   Temporal   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Code Example: Graphiti Integration

```python
# apex_memory/services/temporal_service.py

from datetime import datetime, timezone
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TemporalIntelligenceService:
    """
    Manages temporal intelligence layer using Graphiti.

    Provides bi-temporal tracking for entities and relationships
    with automatic conflict resolution and time-travel queries.
    """

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        llm_api_key: str
    ):
        self.graphiti = Graphiti(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            llm_api_key=llm_api_key
        )
        logger.info("Temporal Intelligence Service initialized")


    async def ingest_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any],
        reference_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Ingest document into temporal knowledge graph.

        Args:
            document_id: Unique document identifier
            content: Document text content
            metadata: Document metadata (source, type, etc.)
            reference_time: When events in document occurred (defaults to now)

        Returns:
            Ingestion result with extracted entities and relationships
        """
        if reference_time is None:
            reference_time = datetime.now(timezone.utc)

        try:
            # Add episode to Graphiti
            result = await self.graphiti.add_episode(
                name=f"document_{document_id}",
                episode_body=content,
                source=EpisodeType.text,
                source_description=metadata.get("source", "unknown"),
                reference_time=reference_time,
                metadata=metadata
            )

            logger.info(
                f"Ingested document {document_id} with "
                f"{len(result.get('entities', []))} entities, "
                f"{len(result.get('edges', []))} relationships"
            )

            return {
                "document_id": document_id,
                "ingested_at": datetime.now(timezone.utc),
                "reference_time": reference_time,
                "entities_extracted": len(result.get("entities", [])),
                "relationships_extracted": len(result.get("edges", [])),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error ingesting document {document_id}: {e}")
            raise


    async def query_temporal_knowledge(
        self,
        query: str,
        valid_time: Optional[datetime] = None,
        transaction_time: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query knowledge graph with temporal filtering.

        Args:
            query: Natural language query
            valid_time: Filter by when facts were true (real-world time)
            transaction_time: Filter by when facts were known (database time)
            limit: Maximum results to return

        Returns:
            List of relevant facts with temporal metadata
        """
        try:
            # Search Graphiti with temporal context
            results = await self.graphiti.search(
                query=query,
                limit=limit
            )

            # Apply temporal filtering
            filtered_results = []
            for result in results:
                # Check if result was valid at specified time
                if valid_time and not self._is_valid_at(result, valid_time):
                    continue

                # Check if result was known at specified transaction time
                if transaction_time and not self._was_known_at(result, transaction_time):
                    continue

                filtered_results.append({
                    "fact": result.get("fact"),
                    "entities": result.get("entities", []),
                    "valid_from": result.get("valid_at"),
                    "valid_to": result.get("invalid_at"),
                    "created_at": result.get("created_at"),
                    "confidence": result.get("confidence", 0.0),
                    "source": result.get("source")
                })

            logger.info(
                f"Query '{query}' returned {len(filtered_results)} results "
                f"(filtered from {len(results)})"
            )

            return filtered_results

        except Exception as e:
            logger.error(f"Error querying temporal knowledge: {e}")
            raise


    def _is_valid_at(self, result: Dict[str, Any], valid_time: datetime) -> bool:
        """Check if result was valid at specified time."""
        valid_at = result.get("valid_at")
        invalid_at = result.get("invalid_at")

        # If no temporal bounds, assume always valid
        if valid_at is None:
            return True

        # Check if valid_time falls within validity range
        if valid_time < valid_at:
            return False

        if invalid_at and valid_time >= invalid_at:
            return False

        return True


    def _was_known_at(self, result: Dict[str, Any], transaction_time: datetime) -> bool:
        """Check if result was known in database at specified time."""
        created_at = result.get("created_at")
        expired_at = result.get("expired_at")

        # Must have been created before transaction_time
        if created_at and transaction_time < created_at:
            return False

        # Must not have been expired before transaction_time
        if expired_at and transaction_time >= expired_at:
            return False

        return True


    async def get_entity_history(
        self,
        entity_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get complete history of an entity's property changes.

        Args:
            entity_id: Entity identifier
            start_time: Start of time range (optional)
            end_time: End of time range (optional)

        Returns:
            List of property states with temporal bounds
        """
        # Query Neo4j directly for entity history
        query = """
        MATCH (e:Entity {id: $entity_id})
        OPTIONAL MATCH (e)-[r]->(v)
        WHERE ($start_time IS NULL OR r.valid_at >= $start_time)
          AND ($end_time IS NULL OR r.valid_at <= $end_time)
        RETURN e, r, v
        ORDER BY r.valid_at ASC
        """

        # Execute via Graphiti's Neo4j connection
        # (Implementation depends on Graphiti's query interface)

        return []  # Placeholder


    async def resolve_temporal_conflict(
        self,
        entity_id: str,
        conflicting_facts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Resolve conflicts between multiple facts about same entity.

        Graphiti handles this automatically during ingestion,
        but this method allows manual conflict resolution.

        Args:
            entity_id: Entity with conflicting information
            conflicting_facts: List of facts that contradict each other

        Returns:
            Resolution result with temporal boundaries updated
        """
        # Graphiti's built-in conflict resolution:
        # 1. Semantic similarity search detects conflicts
        # 2. LLM evaluates which fact is correct
        # 3. Old edges get expired_at and invalid_at set
        # 4. New edge created with current information

        logger.info(f"Resolving conflict for entity {entity_id}")

        # For manual resolution, we would:
        # 1. Sort facts by valid_time
        # 2. Set temporal boundaries appropriately
        # 3. Update database

        return {
            "entity_id": entity_id,
            "conflicts_resolved": len(conflicting_facts),
            "resolution_strategy": "temporal_ordering"
        }
```

### Usage Example

```python
# In ingestion pipeline
temporal_service = TemporalIntelligenceService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="apexmemory2024",
    llm_api_key=os.getenv("OPENAI_API_KEY")
)

# Ingest document with temporal context
result = await temporal_service.ingest_document(
    document_id="employee_record_2024",
    content="""
    John Smith was promoted to VP of Engineering on January 15, 2024.
    He previously served as Senior Engineering Manager from July 2022.
    His new salary is $180,000 effective from the promotion date.
    """,
    metadata={
        "source": "HR System",
        "document_type": "promotion_notice",
        "department": "Engineering"
    },
    reference_time=datetime(2024, 1, 15, tzinfo=timezone.utc)
)

# Query with temporal filtering
results = await temporal_service.query_temporal_knowledge(
    query="What was John Smith's role in December 2023?",
    valid_time=datetime(2023, 12, 1, tzinfo=timezone.utc)
)
# Returns: "Senior Engineering Manager" (not VP, which was future)

results = await temporal_service.query_temporal_knowledge(
    query="What was John Smith's role in February 2024?",
    valid_time=datetime(2024, 2, 1, tzinfo=timezone.utc)
)
# Returns: "VP of Engineering" (promotion effective Jan 15)
```

---

## Integration Pattern 2: PostgreSQL Temporal Tables

### Schema Design

```sql
-- PostgreSQL temporal table implementation
-- Combines bi-temporal tracking with pgvector for semantic search

CREATE TABLE temporal_entities (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Entity data
    entity_id VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    properties JSONB NOT NULL,

    -- Embeddings for semantic search
    embedding vector(1536),  -- OpenAI ada-002 dimensions

    -- Transaction time (database timeline)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,  -- Soft delete

    -- Valid time (real-world timeline)
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,

    -- Metadata
    source VARCHAR(255),
    confidence REAL CHECK (confidence >= 0 AND confidence <= 1),
    version INTEGER NOT NULL DEFAULT 1,

    -- Temporal constraints
    CONSTRAINT valid_time_range CHECK (
        valid_to IS NULL OR valid_from IS NULL OR valid_to > valid_from
    ),
    CONSTRAINT deleted_after_created CHECK (
        deleted_at IS NULL OR deleted_at >= created_at
    )
);

-- Indexes for temporal queries
CREATE INDEX idx_temporal_entities_entity_id ON temporal_entities(entity_id);
CREATE INDEX idx_temporal_entities_type ON temporal_entities(entity_type);
CREATE INDEX idx_temporal_entities_created_at ON temporal_entities(created_at);
CREATE INDEX idx_temporal_entities_valid_from ON temporal_entities(valid_from);
CREATE INDEX idx_temporal_entities_valid_to ON temporal_entities(valid_to);

-- Bitemporal composite index for point-in-time queries
CREATE INDEX idx_temporal_entities_bitemporal ON temporal_entities(
    entity_id,
    valid_from,
    valid_to,
    created_at,
    deleted_at
);

-- Vector similarity search index
CREATE INDEX idx_temporal_entities_embedding ON temporal_entities
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Temporal relationships table
CREATE TABLE temporal_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationship data
    source_entity_id VARCHAR(255) NOT NULL,
    target_entity_id VARCHAR(255) NOT NULL,
    relationship_type VARCHAR(100) NOT NULL,
    properties JSONB,

    -- Transaction time (database timeline)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expired_at TIMESTAMPTZ,  -- When relationship was invalidated

    -- Valid time (real-world timeline)
    valid_at TIMESTAMPTZ,
    invalid_at TIMESTAMPTZ,

    -- Metadata
    fact TEXT,  -- Natural language description
    source VARCHAR(255),
    confidence REAL CHECK (confidence >= 0 AND confidence <= 1),

    -- Temporal constraints
    CONSTRAINT relationship_valid_time CHECK (
        invalid_at IS NULL OR valid_at IS NULL OR invalid_at > valid_at
    ),
    CONSTRAINT relationship_transaction_time CHECK (
        expired_at IS NULL OR expired_at >= created_at
    )
);

-- Indexes for relationship queries
CREATE INDEX idx_temporal_rels_source ON temporal_relationships(source_entity_id);
CREATE INDEX idx_temporal_rels_target ON temporal_relationships(target_entity_id);
CREATE INDEX idx_temporal_rels_type ON temporal_relationships(relationship_type);
CREATE INDEX idx_temporal_rels_bitemporal ON temporal_relationships(
    source_entity_id,
    target_entity_id,
    valid_at,
    invalid_at,
    created_at,
    expired_at
);
```

### Temporal Query Functions

```sql
-- Function: Get entity state at specific point in time
CREATE OR REPLACE FUNCTION get_entity_at_time(
    p_entity_id VARCHAR,
    p_valid_time TIMESTAMPTZ,
    p_transaction_time TIMESTAMPTZ DEFAULT NOW()
)
RETURNS TABLE (
    id UUID,
    entity_type VARCHAR,
    properties JSONB,
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.entity_type,
        e.properties,
        e.valid_from,
        e.valid_to
    FROM temporal_entities e
    WHERE e.entity_id = p_entity_id
      -- Valid time check
      AND (e.valid_from IS NULL OR e.valid_from <= p_valid_time)
      AND (e.valid_to IS NULL OR e.valid_to > p_valid_time)
      -- Transaction time check
      AND e.created_at <= p_transaction_time
      AND (e.deleted_at IS NULL OR e.deleted_at > p_transaction_time)
    ORDER BY e.version DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function: Get entity history over time range
CREATE OR REPLACE FUNCTION get_entity_history(
    p_entity_id VARCHAR,
    p_start_time TIMESTAMPTZ DEFAULT '-infinity',
    p_end_time TIMESTAMPTZ DEFAULT 'infinity'
)
RETURNS TABLE (
    version INTEGER,
    properties JSONB,
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    source VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.version,
        e.properties,
        e.valid_from,
        e.valid_to,
        e.created_at,
        e.source
    FROM temporal_entities e
    WHERE e.entity_id = p_entity_id
      AND (e.valid_from IS NULL OR e.valid_from < p_end_time)
      AND (e.valid_to IS NULL OR e.valid_to > p_start_time)
    ORDER BY e.valid_from ASC, e.created_at ASC;
END;
$$ LANGUAGE plpgsql;

-- Function: Temporal join (entities and relationships at same time)
CREATE OR REPLACE FUNCTION get_relationships_at_time(
    p_entity_id VARCHAR,
    p_valid_time TIMESTAMPTZ,
    p_transaction_time TIMESTAMPTZ DEFAULT NOW()
)
RETURNS TABLE (
    source_id VARCHAR,
    target_id VARCHAR,
    relationship_type VARCHAR,
    fact TEXT,
    valid_at TIMESTAMPTZ,
    invalid_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.source_entity_id,
        r.target_entity_id,
        r.relationship_type,
        r.fact,
        r.valid_at,
        r.invalid_at
    FROM temporal_relationships r
    WHERE (r.source_entity_id = p_entity_id OR r.target_entity_id = p_entity_id)
      -- Valid time check
      AND (r.valid_at IS NULL OR r.valid_at <= p_valid_time)
      AND (r.invalid_at IS NULL OR r.invalid_at > p_valid_time)
      -- Transaction time check
      AND r.created_at <= p_transaction_time
      AND (r.expired_at IS NULL OR r.expired_at > p_transaction_time)
    ORDER BY r.created_at ASC;
END;
$$ LANGUAGE plpgsql;
```

### Python Integration

```python
# apex_memory/database/temporal_postgres.py

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import asyncpg
from pydantic import BaseModel


class TemporalEntity(BaseModel):
    """Temporal entity model."""
    entity_id: str
    entity_type: str
    properties: Dict[str, Any]
    embedding: List[float]
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    source: str
    confidence: float = 1.0


class TemporalPostgresService:
    """Service for temporal operations on PostgreSQL."""

    def __init__(self, connection_pool: asyncpg.Pool):
        self.pool = connection_pool

    async def insert_entity(
        self,
        entity: TemporalEntity,
        reference_time: Optional[datetime] = None
    ) -> str:
        """Insert temporal entity with bi-temporal tracking."""
        if reference_time is None:
            reference_time = datetime.now(timezone.utc)

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO temporal_entities (
                    entity_id,
                    entity_type,
                    properties,
                    embedding,
                    valid_from,
                    valid_to,
                    source,
                    confidence,
                    created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
                """,
                entity.entity_id,
                entity.entity_type,
                entity.properties,
                entity.embedding,
                entity.valid_from or reference_time,
                entity.valid_to,
                entity.source,
                entity.confidence,
                datetime.now(timezone.utc)
            )
            return str(row['id'])

    async def query_at_time(
        self,
        entity_id: str,
        valid_time: datetime,
        transaction_time: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Query entity state at specific point in time."""
        if transaction_time is None:
            transaction_time = datetime.now(timezone.utc)

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM get_entity_at_time($1, $2, $3)",
                entity_id,
                valid_time,
                transaction_time
            )

            if row:
                return dict(row)
            return None

    async def get_history(
        self,
        entity_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get complete entity history over time range."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM get_entity_history($1, $2, $3)",
                entity_id,
                start_time or datetime.min,
                end_time or datetime.max
            )
            return [dict(row) for row in rows]
```

---

## Integration Pattern 3: Neo4j Temporal Cypher Queries

### Temporal Relationship Modeling

```cypher
// Create temporal entity with lifecycle metadata
CREATE (e:Entity:Person {
    id: 'john_smith_001',
    name: 'John Smith',
    created_at: datetime('2020-01-01T00:00:00Z')
})

// Create temporal relationship with bi-temporal metadata
MATCH (p:Person {id: 'john_smith_001'})
MATCH (r:Role {name: 'VP Engineering'})
CREATE (p)-[rel:HAS_ROLE {
    // Transaction time (database timeline)
    created_at: datetime('2024-01-15T10:00:00Z'),
    expired_at: null,

    // Valid time (real-world timeline)
    valid_at: datetime('2024-01-15T00:00:00Z'),
    invalid_at: null,

    // Metadata
    fact: 'John Smith holds position of VP of Engineering',
    source: 'HR System',
    confidence: 1.0,

    // Additional context
    salary: 180000,
    department: 'Engineering',
    start_date: date('2024-01-15')
}]->(r)
```

### Point-in-Time Queries

```cypher
// Query: What was John's role on specific date?
MATCH (p:Person {id: 'john_smith_001'})-[r:HAS_ROLE]->(role:Role)
WHERE (r.valid_at IS NULL OR r.valid_at <= datetime('2024-02-01'))
  AND (r.invalid_at IS NULL OR r.invalid_at > datetime('2024-02-01'))
  AND (r.created_at <= datetime('2024-02-01'))
  AND (r.expired_at IS NULL OR r.expired_at > datetime('2024-02-01'))
RETURN p.name, role.name, r.valid_at, r.invalid_at
```

### Temporal Range Queries

```cypher
// Query: All role changes for John in 2024
MATCH (p:Person {id: 'john_smith_001'})-[r:HAS_ROLE]->(role:Role)
WHERE r.valid_at >= datetime('2024-01-01')
  AND r.valid_at < datetime('2025-01-01')
RETURN role.name, r.valid_at, r.invalid_at, r.fact
ORDER BY r.valid_at ASC
```

### Temporal Conflict Resolution

```cypher
// Scenario: New information contradicts existing relationship
// Step 1: Find existing relationship
MATCH (p:Person {id: 'john_smith_001'})-[old_rel:HAS_ROLE]->(old_role:Role)
WHERE old_rel.invalid_at IS NULL  // Still current

// Step 2: Set expiration timestamps (invalidate old relationship)
SET old_rel.expired_at = datetime(),
    old_rel.invalid_at = datetime('2024-01-14T23:59:59Z')

// Step 3: Create new relationship with corrected information
WITH p
MATCH (new_role:Role {name: 'Director of Engineering'})
CREATE (p)-[new_rel:HAS_ROLE {
    created_at: datetime(),
    expired_at: null,
    valid_at: datetime('2022-07-01T00:00:00Z'),  // Backdated correction
    invalid_at: datetime('2024-01-14T23:59:59Z'),  // Valid until promotion
    fact: 'John Smith was Director of Engineering before VP promotion',
    source: 'Corrected HR Records',
    confidence: 1.0
}]->(new_role)

// Result: Both relationships preserved with correct temporal bounds
```

### Entity History Traversal

```cypher
// Query: Complete job history for John
MATCH (p:Person {id: 'john_smith_001'})-[r:HAS_ROLE]->(role:Role)
RETURN
    role.name AS position,
    r.valid_at AS start_date,
    r.invalid_at AS end_date,
    duration.between(r.valid_at, coalesce(r.invalid_at, datetime())).months AS months_in_role,
    r.source AS information_source
ORDER BY r.valid_at ASC
```

---

## Integration Pattern 4: Redis Temporal Caching

### Caching Strategy

```python
# apex_memory/cache/temporal_cache.py

import redis.asyncio as redis
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


class TemporalCacheService:
    """
    Cache temporal query results with TTL.

    Key format: temporal:{query_type}:{entity_id}:{timestamp}
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour

    def _make_cache_key(
        self,
        query_type: str,
        entity_id: str,
        valid_time: datetime,
        transaction_time: Optional[datetime] = None
    ) -> str:
        """Generate cache key for temporal query."""
        time_str = valid_time.isoformat()
        if transaction_time:
            time_str += f":{transaction_time.isoformat()}"
        return f"temporal:{query_type}:{entity_id}:{time_str}"

    async def cache_point_in_time_query(
        self,
        entity_id: str,
        valid_time: datetime,
        result: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """Cache point-in-time query result."""
        key = self._make_cache_key("point_in_time", entity_id, valid_time)
        await self.redis.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(result, default=str)
        )

    async def get_cached_point_in_time(
        self,
        entity_id: str,
        valid_time: datetime
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached point-in-time query."""
        key = self._make_cache_key("point_in_time", entity_id, valid_time)
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def cache_entity_history(
        self,
        entity_id: str,
        history: List[Dict[str, Any]],
        ttl: Optional[int] = None
    ) -> None:
        """Cache entity history."""
        key = f"temporal:history:{entity_id}"
        await self.redis.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(history, default=str)
        )

    async def invalidate_entity_cache(self, entity_id: str) -> None:
        """Invalidate all cached queries for an entity."""
        pattern = f"temporal:*:{entity_id}:*"
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break
```

---

## Testing Strategy

### Unit Tests for Temporal Logic

```python
# tests/unit/test_temporal_service.py

import pytest
from datetime import datetime, timezone, timedelta
from apex_memory.services.temporal_service import TemporalIntelligenceService


@pytest.fixture
def temporal_service():
    return TemporalIntelligenceService(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="test",
        llm_api_key="test_key"
    )


class TestTemporalValidation:
    """Test temporal validation logic."""

    def test_is_valid_at_no_bounds(self, temporal_service):
        """Entity with no temporal bounds is always valid."""
        result = {"fact": "Test fact"}
        assert temporal_service._is_valid_at(
            result,
            datetime(2024, 1, 1, tzinfo=timezone.utc)
        )

    def test_is_valid_at_within_range(self, temporal_service):
        """Entity is valid when query time is within range."""
        result = {
            "valid_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "invalid_at": datetime(2024, 12, 31, tzinfo=timezone.utc)
        }
        assert temporal_service._is_valid_at(
            result,
            datetime(2024, 6, 1, tzinfo=timezone.utc)
        )

    def test_is_valid_at_before_range(self, temporal_service):
        """Entity is not valid before valid_at."""
        result = {
            "valid_at": datetime(2024, 1, 1, tzinfo=timezone.utc)
        }
        assert not temporal_service._is_valid_at(
            result,
            datetime(2023, 12, 31, tzinfo=timezone.utc)
        )

    def test_is_valid_at_after_range(self, temporal_service):
        """Entity is not valid after invalid_at."""
        result = {
            "valid_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "invalid_at": datetime(2024, 12, 31, tzinfo=timezone.utc)
        }
        assert not temporal_service._is_valid_at(
            result,
            datetime(2025, 1, 1, tzinfo=timezone.utc)
        )


class TestTransactionTime:
    """Test transaction time validation."""

    def test_was_known_at_before_creation(self, temporal_service):
        """Result was not known before created_at."""
        result = {
            "created_at": datetime(2024, 1, 15, tzinfo=timezone.utc)
        }
        assert not temporal_service._was_known_at(
            result,
            datetime(2024, 1, 1, tzinfo=timezone.utc)
        )

    def test_was_known_at_after_expiration(self, temporal_service):
        """Result was not known after expired_at."""
        result = {
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "expired_at": datetime(2024, 12, 31, tzinfo=timezone.utc)
        }
        assert not temporal_service._was_known_at(
            result,
            datetime(2025, 1, 1, tzinfo=timezone.utc)
        )

    def test_was_known_at_within_range(self, temporal_service):
        """Result was known between created_at and expired_at."""
        result = {
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "expired_at": datetime(2024, 12, 31, tzinfo=timezone.utc)
        }
        assert temporal_service._was_known_at(
            result,
            datetime(2024, 6, 1, tzinfo=timezone.utc)
        )
```

### Integration Tests

```python
# tests/integration/test_temporal_integration.py

import pytest
from datetime import datetime, timezone
from apex_memory.services.temporal_service import TemporalIntelligenceService


@pytest.mark.asyncio
class TestTemporalIngestion:
    """Test temporal ingestion and querying."""

    async def test_ingest_and_query_current(self, temporal_service):
        """Ingest document and query current state."""
        # Ingest
        await temporal_service.ingest_document(
            document_id="test_001",
            content="Alice is a Software Engineer at Acme Corp.",
            metadata={"source": "test"},
            reference_time=datetime(2024, 1, 1, tzinfo=timezone.utc)
        )

        # Query current state
        results = await temporal_service.query_temporal_knowledge(
            query="What is Alice's role?",
            valid_time=datetime(2024, 6, 1, tzinfo=timezone.utc)
        )

        assert len(results) > 0
        assert "Software Engineer" in str(results[0])

    async def test_temporal_conflict_resolution(self, temporal_service):
        """Test that conflicting information is handled temporally."""
        # First ingestion: Alice is Engineer
        await temporal_service.ingest_document(
            document_id="test_002a",
            content="Alice is a Software Engineer.",
            metadata={"source": "test"},
            reference_time=datetime(2024, 1, 1, tzinfo=timezone.utc)
        )

        # Second ingestion: Alice is Manager (promotion)
        await temporal_service.ingest_document(
            document_id="test_002b",
            content="Alice was promoted to Engineering Manager on June 1, 2024.",
            metadata={"source": "test"},
            reference_time=datetime(2024, 6, 1, tzinfo=timezone.utc)
        )

        # Query before promotion
        results_before = await temporal_service.query_temporal_knowledge(
            query="What is Alice's role?",
            valid_time=datetime(2024, 3, 1, tzinfo=timezone.utc)
        )

        # Query after promotion
        results_after = await temporal_service.query_temporal_knowledge(
            query="What is Alice's role?",
            valid_time=datetime(2024, 8, 1, tzinfo=timezone.utc)
        )

        # Verify temporal boundaries
        assert "Engineer" in str(results_before[0])
        assert "Manager" in str(results_after[0])
```

---

## Performance Considerations

### Temporal Query Optimization

1. **Index Strategy:**
   - Composite indexes on (entity_id, valid_from, valid_to, created_at)
   - Separate indexes for each temporal dimension
   - Cover indexes for common query patterns

2. **Caching:**
   - Cache point-in-time snapshots for common dates (end of month, year)
   - TTL based on query frequency and data volatility
   - Invalidate cache on entity updates

3. **Query Patterns:**
   - Use covering indexes to avoid table lookups
   - Batch queries for multiple entities at same time
   - Materialize historical snapshots for reporting

4. **Storage:**
   - Partition tables by time ranges (yearly, monthly)
   - Archive expired relationships to separate storage
   - Compress historical data

---

## Monitoring and Observability

### Metrics to Track

```python
# apex_memory/monitoring/temporal_metrics.py

from prometheus_client import Counter, Histogram, Gauge


# Temporal query metrics
temporal_queries_total = Counter(
    'temporal_queries_total',
    'Total temporal queries',
    ['query_type', 'status']
)

temporal_query_duration = Histogram(
    'temporal_query_duration_seconds',
    'Temporal query duration',
    ['query_type']
)

temporal_cache_hits = Counter(
    'temporal_cache_hits_total',
    'Temporal cache hits',
    ['query_type']
)

temporal_conflicts_resolved = Counter(
    'temporal_conflicts_resolved_total',
    'Temporal conflicts resolved',
    ['resolution_strategy']
)

temporal_entities_count = Gauge(
    'temporal_entities_total',
    'Total temporal entities'
)

temporal_relationships_count = Gauge(
    'temporal_relationships_total',
    'Total temporal relationships'
)
```

---

## Next Steps

1. **Implement Graphiti Integration** (Phase 4)
   - Set up Graphiti client in temporal service
   - Configure Neo4j connection
   - Test bi-temporal ingestion and queries

2. **Extend PostgreSQL Schema** (Phase 4)
   - Add temporal columns to entity tables
   - Create temporal query functions
   - Build indexes for performance

3. **Build Temporal Query API** (Phase 4)
   - Add temporal filtering to query router
   - Implement point-in-time endpoints
   - Create history retrieval endpoints

4. **Configure Redis Caching** (Phase 4)
   - Implement temporal cache service
   - Set up cache invalidation logic
   - Monitor cache hit rates

5. **Testing and Validation** (Phase 5)
   - Unit tests for temporal logic
   - Integration tests for bi-temporal queries
   - Performance benchmarks

---

**Document Version:** 1.0
**Companion to:** README.md (Temporal Intelligence Research)
**Status:** Implementation Ready
**Next Review:** Phase 3.5 (Review Board)
