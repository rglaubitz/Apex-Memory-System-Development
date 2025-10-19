# Graphiti + JSON Integration - Implementation Guide

**Project:** Apex Memory System - Temporal Implementation
**Document Type:** Step-by-Step Implementation Guide
**Based On:** Tier 1 Official Documentation
**Status:** Ready for Execution
**Created:** 2025-10-19

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Graphiti Integration](#phase-1-graphiti-integration)
3. [Phase 2: JSON Support](#phase-2-json-support)
4. [Phase 3: Staging Lifecycle](#phase-3-staging-lifecycle)
5. [Phase 4: Two Workflows](#phase-4-two-workflows)
6. [Validation & Testing](#validation--testing)

---

## Prerequisites

### Verification Checklist

**Before starting implementation, verify:**

```bash
# 1. Graphiti is installed
python3 -c "import graphiti_core; print(f'Graphiti version: {graphiti_core.__version__}')"
# Expected output: Graphiti version: 0.20.4

# 2. GraphitiService exists
ls -la apex-memory-system/src/apex_memory/services/graphiti_service.py
# Expected: File exists

# 3. Neo4j is running (for Graphiti knowledge graph)
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT 1"
# Expected: Connection successful

# 4. Temporal worker is running
temporal workflow list
# Expected: Shows running workflows (if any)

# 5. All 121 Enhanced Saga tests pass
cd apex-memory-system && pytest tests/ --ignore=tests/load/ -v
# Expected: 121/121 tests pass
```

### Environment Setup

**Required environment variables:**

```bash
# .env file in apex-memory-system/
OPENAI_API_KEY=sk-...                    # For Graphiti LLM extraction
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=apexmemory2024
POSTGRES_URI=postgresql://apex:apexmemory2024@localhost:5432/apex_memory
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379

# Graphiti feature flag (add this)
ENABLE_GRAPHITI_EXTRACTION=true          # Toggle Graphiti on/off
```

### Documentation References

**Official Documentation (Tier 1) to have open:**

- **Temporal Python SDK:** https://docs.temporal.io/develop/python
- **Temporal Activity Best Practices:** https://docs.temporal.io/develop/python/core-application#develop-activities
- **Graphiti Getting Started:** https://help.getzep.com/graphiti/getting-started/overview
- **Graphiti API Reference:** https://github.com/getzep/graphiti
- **Pydantic Models:** https://docs.pydantic.dev/latest/
- **PostgreSQL JSONB:** https://www.postgresql.org/docs/16/datatype-json.html
- **Qdrant Collections:** https://qdrant.tech/documentation/concepts/collections/

---

## Phase 1: Graphiti Integration

**Goal:** Replace EntityExtractor with Graphiti in `extract_entities_activity`

### Step 1.1: Update extract_entities_activity

**File:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**Reference:** [Temporal Activity Defn](https://docs.temporal.io/develop/python/core-application#activity-definition) | [Graphiti add_document_episode](https://github.com/getzep/graphiti)

#### Current Implementation (BEFORE):

```python
@activity.defn
async def extract_entities_activity(parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract entities using EntityExtractor (regex patterns)."""
    from apex_memory.services.entity_extractor import EntityExtractor

    record_temporal_activity_started('extract_entities_activity')

    extractor = EntityExtractor()
    entities = extractor.extract_entities(parsed_doc['content'])

    record_temporal_activity_completed('extract_entities_activity', success=True)

    return [entity.to_dict() for entity in entities]
```

#### New Implementation (AFTER):

```python
@activity.defn
async def extract_entities_activity(parsed_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Extract entities using Graphiti (LLM-powered).

    Uses Graphiti's add_document_episode() for:
    - LLM-based entity extraction (GPT-4.1-mini)
    - Automatic relationship inference
    - Temporal knowledge graph tracking

    References:
        Graphiti API: https://help.getzep.com/graphiti/getting-started/overview
        Temporal Activities: https://docs.temporal.io/develop/python/core-application#activity-definition

    Returns:
        Dict with:
            - entities: List[Dict] of extracted entities
            - graphiti_episode_uuid: str for rollback
            - edges_created: int count of relationships

    Raises:
        ApplicationError: If Graphiti extraction fails (non-retryable)
    """
    from apex_memory.services.graphiti_service import GraphitiService
    from apex_memory.config.settings import Settings
    from temporalio.exceptions import ApplicationError

    # Record activity start
    record_temporal_activity_started('extract_entities_activity')

    try:
        # Initialize Graphiti service
        settings = Settings()
        graphiti = GraphitiService(
            neo4j_uri=settings.neo4j_uri,
            neo4j_user=settings.neo4j_user,
            neo4j_password=settings.neo4j_password,
            openai_api_key=settings.openai_api_key,
        )

        # Add document episode to Graphiti
        # Graphiti will automatically:
        # 1. Extract entities using LLM
        # 2. Infer relationships between entities
        # 3. Create temporal edges with validity periods
        result = await graphiti.add_document_episode(
            document_uuid=parsed_doc['uuid'],
            document_title=parsed_doc.get('metadata', {}).get('title', 'Untitled'),
            document_content=parsed_doc['content'],
            document_type=parsed_doc.get('metadata', {}).get('file_type', 'unknown'),
            reference_time=parsed_doc.get('parse_timestamp'),
        )

        if not result.success:
            raise ApplicationError(
                f"Graphiti extraction failed: {result.error}",
                non_retryable=True
            )

        # Convert Graphiti entities to dict format
        # Note: Graphiti doesn't pre-classify entity types (it extracts any entities)
        entities = [
            {
                'name': entity_name,
                'entity_type': 'graphiti_extracted',  # Generic type
                'confidence': 0.9,  # High confidence (LLM-powered)
                'source': 'graphiti',
            }
            for entity_name in result.entities_extracted
        ]

        # Record data quality metrics
        record_temporal_data_quality(
            metric_type='entities_per_document',
            value=len(entities),
            source='graphiti'
        )

        # Record activity completion
        record_temporal_activity_completed('extract_entities_activity', success=True)

        return {
            'entities': entities,
            'graphiti_episode_uuid': parsed_doc['uuid'],  # For rollback
            'edges_created': len(result.edges_created),
        }

    except ApplicationError:
        # Re-raise ApplicationError (non-retryable)
        record_temporal_activity_completed('extract_entities_activity', success=False)
        raise
    except Exception as e:
        # Log error and raise as retryable
        activity.logger.error(
            f"Graphiti extraction error: {e}",
            exc_info=True,
            extra={'document_uuid': parsed_doc.get('uuid')}
        )
        record_temporal_activity_completed('extract_entities_activity', success=False)
        raise
```

**Key Changes:**
1. ✅ Return type changed from `List[Dict]` to `Dict[str, Any]`
2. ✅ Uses `GraphitiService.add_document_episode()`
3. ✅ Returns `graphiti_episode_uuid` for rollback tracking
4. ✅ Includes `edges_created` count for monitoring

**Testing:** Run unit test to verify Graphiti extraction works:

```bash
cd apex-memory-system
pytest tests/unit/test_graphiti_extraction_activity.py -v
```

---

### Step 1.2: Add Graphiti Rollback Logic

**File:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**Reference:** [Saga Pattern](https://microservices.io/patterns/data/saga.html) | [Graphiti Episode Management](https://github.com/getzep/graphiti)

#### Add rollback_graphiti_episode Helper Function:

```python
async def rollback_graphiti_episode(episode_uuid: str) -> None:
    """Rollback Graphiti episode on saga failure.

    Ensures no orphaned knowledge graph data when Saga fails.

    References:
        Saga Pattern: https://microservices.io/patterns/data/saga.html
        Graphiti remove_episode: https://github.com/getzep/graphiti

    Args:
        episode_uuid: Episode UUID to remove

    Note:
        If rollback fails, sends to DLQ for manual cleanup.
    """
    from apex_memory.services.graphiti_service import GraphitiService
    from apex_memory.config.settings import Settings

    settings = Settings()
    graphiti = GraphitiService(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
    )

    try:
        success = await graphiti.remove_episode(episode_uuid)

        if success:
            activity.logger.info(f"✅ Rolled back Graphiti episode: {episode_uuid}")
            record_temporal_saga_rollback('graphiti', success=True)
        else:
            activity.logger.error(f"❌ Failed to rollback Graphiti episode: {episode_uuid}")
            record_temporal_saga_rollback('graphiti', success=False)
            # TODO: Send to Dead Letter Queue for manual cleanup

    except Exception as e:
        activity.logger.error(
            f"Error rolling back Graphiti episode {episode_uuid}: {e}",
            exc_info=True
        )
        record_temporal_saga_rollback('graphiti', success=False)
        # TODO: Send to DLQ
```

#### Update write_to_databases_activity:

```python
@activity.defn
async def write_to_databases_activity(
    parsed_doc: Dict[str, Any],
    entities: Dict[str, Any],  # ← Changed from List[Dict[str, Any]]
    embeddings: Dict[str, Any],
) -> Dict[str, Any]:
    """Write to databases with Graphiti-aware rollback.

    Flow:
    1. Extract Graphiti episode UUID from entities dict
    2. Execute Saga parallel writes
    3. If Saga fails, rollback Graphiti episode

    References:
        Enhanced Saga Pattern: Internal documentation
        Graphiti Rollback: https://github.com/getzep/graphiti

    Args:
        parsed_doc: Parsed document data
        entities: Dict with 'entities' list and 'graphiti_episode_uuid'
        embeddings: Document and chunk embeddings

    Returns:
        Dict with write confirmations from all databases
    """
    from apex_memory.services.database_writer import DatabaseWriteOrchestrator

    record_temporal_activity_started('write_to_databases_activity')

    # Extract Graphiti episode UUID
    graphiti_episode_uuid = entities.get('graphiti_episode_uuid')
    entity_list = entities.get('entities', [])

    # Delegate to Saga orchestrator
    orchestrator = DatabaseWriteOrchestrator()

    try:
        result = await orchestrator.write_document_parallel(
            parsed_doc=parsed_doc,
            embedding=embeddings['document_embedding'],
            chunks=parsed_doc.get('chunks', []),
            chunk_embeddings=embeddings.get('chunk_embeddings'),
            entities=entity_list,  # Pass entity list (not dict)
        )

        # If saga failed, rollback Graphiti episode
        if not result.all_success and graphiti_episode_uuid:
            activity.logger.warning(
                f"Saga failed, rolling back Graphiti episode: {graphiti_episode_uuid}"
            )
            await rollback_graphiti_episode(graphiti_episode_uuid)

        record_temporal_activity_completed('write_to_databases_activity', success=result.all_success)

        return result.model_dump()

    except Exception as e:
        # On any error, rollback Graphiti
        if graphiti_episode_uuid:
            activity.logger.error(f"Exception occurred, rolling back Graphiti: {graphiti_episode_uuid}")
            await rollback_graphiti_episode(graphiti_episode_uuid)

        record_temporal_activity_completed('write_to_databases_activity', success=False)
        raise
```

**Key Changes:**
1. ✅ `entities` parameter changed from `List` to `Dict`
2. ✅ Extracts `graphiti_episode_uuid` from entities dict
3. ✅ Calls `rollback_graphiti_episode()` on Saga failure
4. ✅ Rollback also called in exception handler

**Testing:** Run rollback test:

```bash
pytest tests/unit/test_graphiti_rollback.py -v
```

---

### Step 1.3: Update Workflow Signature

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`

**No breaking changes needed!** The workflow passes data transparently between activities. The signature change from `List[Dict]` to `Dict[str, Any]` is handled automatically.

**Verification:** Run workflow test:

```bash
pytest tests/integration/test_document_ingestion_with_graphiti.py -v
```

---

### Step 1.4: Add Feature Flag

**File:** `apex-memory-system/src/apex_memory/config/settings.py`

**Reference:** [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

```python
class Settings(BaseSettings):
    # Graphiti feature flag
    enable_graphiti_extraction: bool = Field(
        default=True,
        env="ENABLE_GRAPHITI_EXTRACTION",
        description="Enable Graphiti LLM-powered entity extraction (fallback to EntityExtractor if False)"
    )
```

**Update extract_entities_activity to use flag:**

```python
@activity.defn
async def extract_entities_activity(parsed_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Extract entities using Graphiti or EntityExtractor (based on feature flag)."""
    from apex_memory.config.settings import Settings

    settings = Settings()

    if settings.enable_graphiti_extraction:
        # Use Graphiti (new implementation)
        return await _extract_entities_graphiti(parsed_doc)
    else:
        # Fallback to EntityExtractor (old implementation)
        return await _extract_entities_legacy(parsed_doc)
```

---

### Phase 1 Validation

**Run all tests:**

```bash
cd apex-memory-system

# 1. Unit tests for Graphiti integration (10 tests)
pytest tests/unit/test_graphiti_extraction_activity.py -v
pytest tests/unit/test_graphiti_rollback.py -v

# 2. Integration test (end-to-end with Graphiti)
pytest tests/integration/test_document_ingestion_with_graphiti.py -v

# 3. Baseline validation (121 Enhanced Saga tests)
pytest tests/ --ignore=tests/load/ -v
# Expected: 131/131 tests pass (121 + 10 new)

# 4. Verify knowledge graph in Neo4j
# Open Neo4j Browser: http://localhost:7474
# Run Cypher query:
# MATCH (e:Entity) RETURN e LIMIT 10
# Expected: See entities extracted by Graphiti
```

**Phase 1 Complete:** ✅ Graphiti integration operational

---

## Phase 2: JSON Support

**Goal:** Add structured data ingestion with Graphiti JSON extraction

### Step 2.1: Create Pydantic Models

**File:** `apex-memory-system/src/apex_memory/models/structured_data.py` (NEW)

**Reference:** [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)

```python
"""Structured data models for JSON ingestion.

Supports:
- Samsara GPS telemetry
- Turvo TMS shipments
- FrontApp webhook messages
- Generic JSON data

References:
    Pydantic Models: https://docs.pydantic.dev/latest/concepts/models/
    Pydantic Fields: https://docs.pydantic.dev/latest/concepts/fields/
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class StructuredDataType(str, Enum):
    """Types of structured data.

    Based on external data sources:
    - GPS_EVENT: Samsara vehicle telemetry
    - SHIPMENT: Turvo TMS shipment updates
    - MESSAGE: FrontApp webhook messages
    - GENERIC_JSON: Fallback for other JSON
    """
    GPS_EVENT = "gps_event"
    SHIPMENT = "shipment"
    MESSAGE = "message"
    GENERIC_JSON = "generic_json"


class StructuredDataMetadata(BaseModel):
    """Metadata for structured JSON data.

    Tracks:
    - External ID (from source system)
    - Source system name
    - Data type classification
    - Ingestion timestamp
    - Custom metadata (flexible)
    """
    data_id: str = Field(..., description="External ID or UUID from source system")
    source: str = Field(..., description="Data source (samsara, turvo, frontapp)")
    data_type: StructuredDataType = Field(..., description="Type of structured data")
    ingestion_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When data was ingested into Apex Memory"
    )
    custom_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional source-specific metadata"
    )


class StructuredData(BaseModel):
    """Structured JSON data model (parallel to ParsedDocument).

    Used for:
    - API responses (Samsara, Turvo)
    - Webhook payloads (FrontApp)
    - Event streams
    - Logs and telemetry

    Flow:
    1. Fetch JSON from source
    2. Create StructuredData instance
    3. Extract entities via Graphiti
    4. Generate embeddings
    5. Write to databases via Saga

    References:
        Pydantic Validation: https://docs.pydantic.dev/latest/concepts/validators/
    """
    uuid: str = Field(..., description="Internal UUID (generated by Apex)")
    metadata: StructuredDataMetadata = Field(..., description="Metadata about the data")
    raw_json: Dict[str, Any] = Field(..., description="Original JSON payload")
    text_representation: str = Field(
        ...,
        description="Text representation for embeddings (generated from JSON)"
    )
    entities: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Entities extracted by Graphiti (populated after extraction)"
    )
    graphiti_episode_uuid: Optional[str] = Field(
        None,
        description="Graphiti episode UUID (for rollback)"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "metadata": {
                    "data_id": "SHIP-12345",
                    "source": "turvo",
                    "data_type": "shipment",
                    "ingestion_timestamp": "2025-10-19T10:30:00Z",
                    "custom_metadata": {"carrier": "ACME Trucking"}
                },
                "raw_json": {
                    "shipment_id": "SHIP-12345",
                    "status": "in_transit",
                    "pickup": {"location": "Chicago, IL"}
                },
                "text_representation": "Shipment SHIP-12345 from Chicago, IL, status: in_transit"
            }
        }
```

**Testing:**

```bash
pytest tests/unit/test_structured_data_models.py -v
```

---

### Step 2.2: Add Database Write Methods

#### PostgreSQL Writer

**File:** `apex-memory-system/src/apex_memory/database/postgres_writer.py`

**Reference:** [PostgreSQL JSONB](https://www.postgresql.org/docs/16/datatype-json.html) | [asyncpg](https://magicstack.github.io/asyncpg/current/)

**Add method:**

```python
async def write_json_record(
    self,
    structured_data: "StructuredData",
    entities: List[Dict[str, Any]],
) -> WriteResult:
    """Write structured JSON to PostgreSQL.

    Stores in `structured_data` table with JSONB column.

    References:
        PostgreSQL JSONB: https://www.postgresql.org/docs/16/datatype-json.html
        asyncpg: https://magicstack.github.io/asyncpg/current/

    Args:
        structured_data: StructuredData instance
        entities: Entities extracted by Graphiti

    Returns:
        WriteResult with success status
    """
    try:
        query = """
        INSERT INTO structured_data (
            uuid, data_id, source, data_type,
            raw_json, text_representation,
            entities, ingestion_timestamp, custom_metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (uuid) DO NOTHING
        """

        await self.pool.execute(
            query,
            structured_data.uuid,
            structured_data.metadata.data_id,
            structured_data.metadata.source,
            structured_data.metadata.data_type.value,
            structured_data.raw_json,  # JSONB column
            structured_data.text_representation,
            entities,  # JSONB array
            structured_data.metadata.ingestion_timestamp,
            structured_data.metadata.custom_metadata,  # JSONB object
        )

        return WriteResult(success=True, database="postgres")

    except Exception as e:
        logger.error(f"PostgreSQL write_json_record failed: {e}")
        return WriteResult(success=False, database="postgres", error=str(e))
```

**Create migration:**

```sql
-- File: schemas/postgres_structured_data.sql
CREATE TABLE IF NOT EXISTS structured_data (
    uuid UUID PRIMARY KEY,
    data_id TEXT NOT NULL,
    source TEXT NOT NULL,
    data_type TEXT NOT NULL,
    raw_json JSONB NOT NULL,
    text_representation TEXT,
    entities JSONB,
    ingestion_timestamp TIMESTAMPTZ DEFAULT NOW(),
    custom_metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_structured_data_source ON structured_data(source);
CREATE INDEX idx_structured_data_type ON structured_data(data_type);
CREATE INDEX idx_structured_data_timestamp ON structured_data(ingestion_timestamp);
CREATE INDEX idx_structured_data_raw_json ON structured_data USING gin(raw_json);
```

**Run migration:**

```bash
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -f schemas/postgres_structured_data.sql
```

#### Qdrant Writer

**File:** `apex-memory-system/src/apex_memory/database/qdrant_writer.py`

**Reference:** [Qdrant Collections](https://qdrant.tech/documentation/concepts/collections/) | [Qdrant Python Client](https://github.com/qdrant/qdrant-client)

```python
async def write_json_record(
    self,
    structured_data: "StructuredData",
    embedding: List[float],
) -> WriteResult:
    """Write structured JSON embedding to Qdrant.

    Stores in `apex_structured_data` collection.

    References:
        Qdrant Collections: https://qdrant.tech/documentation/concepts/collections/
        Qdrant Python Client: https://github.com/qdrant/qdrant-client

    Args:
        structured_data: StructuredData instance
        embedding: Vector embedding (1536 dimensions)

    Returns:
        WriteResult with success status
    """
    from qdrant_client.models import PointStruct

    try:
        # Ensure collection exists
        self._ensure_json_collection_exists()

        # Create point
        point = PointStruct(
            id=structured_data.uuid,
            vector=embedding,
            payload={
                "data_id": structured_data.metadata.data_id,
                "source": structured_data.metadata.source,
                "data_type": structured_data.metadata.data_type.value,
                "text": structured_data.text_representation[:500],  # Truncate for payload
                "ingestion_timestamp": structured_data.metadata.ingestion_timestamp.isoformat(),
                "custom_metadata": structured_data.metadata.custom_metadata,
            }
        )

        # Upsert to collection
        self.client.upsert(
            collection_name="apex_structured_data",
            points=[point]
        )

        return WriteResult(success=True, database="qdrant")

    except Exception as e:
        logger.error(f"Qdrant write_json_record failed: {e}")
        return WriteResult(success=False, database="qdrant", error=str(e))


def _ensure_json_collection_exists(self) -> None:
    """Ensure apex_structured_data collection exists."""
    from qdrant_client.models import VectorParams, Distance

    collections = self.client.get_collections().collections
    collection_names = [c.name for c in collections]

    if "apex_structured_data" not in collection_names:
        self.client.create_collection(
            collection_name="apex_structured_data",
            vectors_config=VectorParams(
                size=1536,  # OpenAI text-embedding-3-small
                distance=Distance.COSINE
            )
        )
        logger.info("Created Qdrant collection: apex_structured_data")
```

#### Neo4j Writer

**File:** `apex-memory-system/src/apex_memory/database/neo4j_writer.py`

**Reference:** [Neo4j Cypher](https://neo4j.com/docs/cypher-manual/current/) | [Neo4j Python Driver](https://neo4j.com/docs/api/python-driver/current/)

```python
async def write_json_record(
    self,
    structured_data: "StructuredData",
    entities: List[Dict[str, Any]],
) -> WriteResult:
    """Write structured JSON metadata to Neo4j.

    Creates :StructuredData node and links to entities.

    References:
        Neo4j Cypher: https://neo4j.com/docs/cypher-manual/current/
        Neo4j Python Driver: https://neo4j.com/docs/api/python-driver/current/

    Args:
        structured_data: StructuredData instance
        entities: Entities extracted by Graphiti

    Returns:
        WriteResult with success status
    """
    try:
        # Create StructuredData node
        query = """
        MERGE (d:StructuredData {uuid: $uuid})
        SET d.data_id = $data_id,
            d.source = $source,
            d.data_type = $data_type,
            d.ingestion_timestamp = datetime($ingestion_timestamp)
        """

        await self.driver.execute_query(
            query,
            uuid=structured_data.uuid,
            data_id=structured_data.metadata.data_id,
            source=structured_data.metadata.source,
            data_type=structured_data.metadata.data_type.value,
            ingestion_timestamp=structured_data.metadata.ingestion_timestamp.isoformat(),
        )

        # Link entities (extracted by Graphiti)
        for entity in entities:
            entity_query = """
            MATCH (d:StructuredData {uuid: $uuid})
            MERGE (e:Entity {name: $entity_name})
            MERGE (d)-[:CONTAINS_ENTITY]->(e)
            """
            await self.driver.execute_query(
                entity_query,
                uuid=structured_data.uuid,
                entity_name=entity['name']
            )

        return WriteResult(success=True, database="neo4j")

    except Exception as e:
        logger.error(f"Neo4j write_json_record failed: {e}")
        return WriteResult(success=False, database="neo4j", error=str(e))
```

#### Redis Writer

**File:** `apex-memory-system/src/apex_memory/database/redis_writer.py`

**Reference:** [Redis JSON](https://redis.io/docs/latest/develop/data-types/json/)

```python
async def write_json_record(
    self,
    structured_data: "StructuredData",
) -> WriteResult:
    """Write structured JSON to Redis for fast lookup.

    References:
        Redis JSON: https://redis.io/docs/latest/develop/data-types/json/

    Args:
        structured_data: StructuredData instance

    Returns:
        WriteResult with success status
    """
    try:
        import json

        key = f"structured_data:{structured_data.uuid}"
        value = {
            "data_id": structured_data.metadata.data_id,
            "source": structured_data.metadata.source,
            "data_type": structured_data.metadata.data_type.value,
            "text": structured_data.text_representation,
            "raw_json": structured_data.raw_json,
        }

        # Set with 24hr TTL
        await self.redis.set(key, json.dumps(value), ex=86400)

        return WriteResult(success=True, database="redis")

    except Exception as e:
        logger.error(f"Redis write_json_record failed: {e}")
        return WriteResult(success=False, database="redis", error=str(e))
```

**Testing:**

```bash
pytest tests/unit/test_json_writer_postgres.py -v
pytest tests/unit/test_json_writer_qdrant.py -v
pytest tests/unit/test_json_writer_neo4j.py -v
pytest tests/unit/test_json_writer_redis.py -v
```

---

### Step 2.3: Add Saga Orchestrator Method

**File:** `apex-memory-system/src/apex_memory/services/database_writer.py`

**Reference:** [asyncio.gather](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) | [Saga Pattern](https://microservices.io/patterns/data/saga.html)

```python
async def write_structured_data_parallel(
    self,
    structured_data: "StructuredData",
    embedding: List[float],
    entities: List[Dict[str, Any]],
) -> SagaResult:
    """Write structured JSON to all 4 databases with parallel saga pattern.

    Same infrastructure as write_document_parallel(), but for JSON.

    References:
        Saga Pattern: https://microservices.io/patterns/data/saga.html
        asyncio.gather: https://docs.python.org/3/library/asyncio-task.html

    Args:
        structured_data: StructuredData instance
        embedding: Vector embedding
        entities: Extracted entities

    Returns:
        SagaResult with write confirmations
    """
    uuid = structured_data.uuid

    # Step 1: Idempotency check (reuse existing infrastructure)
    idempotency_key = None
    if self.enable_idempotency:
        idempotency_key = self.idempotency.generate_key(
            "write_structured_data_parallel",
            uuid=uuid,
            content_hash=hash(str(structured_data.raw_json)),
        )

        cached = await self.idempotency.get_cached_result(idempotency_key)
        if cached:
            logger.info(f"Idempotent request for structured data {uuid}")
            return SagaResult(**cached.result)

    # Step 2: Acquire distributed lock (reuse existing infrastructure)
    lock_token = None
    if self.enable_locking:
        lock_token = await self.distributed_lock.acquire(uuid)
        if not lock_token:
            raise LockAcquisitionError(uuid, 5.0)

    try:
        # Step 3: Execute parallel writes
        logger.info(f"Starting parallel write for structured data: {uuid}")

        write_operations = [
            ("postgres", self.postgres_writer.write_json_record(structured_data, entities)),
            ("qdrant", self.qdrant_writer.write_json_record(structured_data, embedding)),
            ("neo4j", self.neo4j_writer.write_json_record(structured_data, entities)),
            ("redis", self.redis_writer.write_json_record(structured_data)),
        ]

        # Execute in parallel
        results = await asyncio.gather(
            *[op[1] for op in write_operations],
            return_exceptions=True
        )

        # Process results (same logic as write_document_parallel)
        neo4j_success = not isinstance(results[2], Exception) and results[2].success
        postgres_success = not isinstance(results[0], Exception) and results[0].success
        qdrant_success = not isinstance(results[1], Exception) and results[1].success
        redis_success = not isinstance(results[3], Exception) and results[3].success

        all_success = neo4j_success and postgres_success and qdrant_success and redis_success

        # Step 4: Rollback if needed (reuse existing infrastructure)
        rollback_performed = False
        if not all_success:
            rollback_performed = await self._rollback_writes(
                uuid, neo4j_success, postgres_success, qdrant_success, redis_success
            )

        # Step 5: Cache result (reuse existing infrastructure)
        result = SagaResult(
            status=WriteStatus.SUCCESS if all_success else WriteStatus.ROLLED_BACK,
            uuid=uuid,
            neo4j_success=neo4j_success,
            postgres_success=postgres_success,
            qdrant_success=qdrant_success,
            redis_success=redis_success,
        )

        if self.enable_idempotency and idempotency_key:
            await self.idempotency.cache_result(
                idempotency_key, "write_structured_data_parallel",
                all_success, result.model_dump()
            )

        return result

    finally:
        # Release lock
        if self.enable_locking and lock_token:
            await self.distributed_lock.release(uuid, lock_token)
```

**Testing:**

```bash
pytest tests/integration/test_structured_data_saga.py -v
```

---

### Step 2.4: Add Temporal Activities for JSON

**File:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**Reference:** [Temporal Activities](https://docs.temporal.io/develop/python/core-application#activity-definition)

#### Add extract_entities_from_json_activity:

```python
@activity.defn
async def extract_entities_from_json_activity(
    structured_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Extract entities from JSON using Graphiti.

    Uses Graphiti's add_json_episode() for:
    - LLM-based entity extraction from JSON
    - Automatic relationship inference
    - Temporal tracking

    References:
        Graphiti JSON API: https://github.com/getzep/graphiti
        Temporal Activities: https://docs.temporal.io/develop/python/core-application

    Args:
        structured_data: StructuredData as dict

    Returns:
        Dict with:
            - entities: List of extracted entities
            - graphiti_episode_uuid: Episode UUID for rollback
            - text_representation: Text for embeddings
    """
    from apex_memory.services.graphiti_service import GraphitiService
    from apex_memory.config.settings import Settings
    from apex_memory.models.structured_data import StructuredData

    record_temporal_activity_started('extract_entities_from_json_activity')

    try:
        # Reconstruct StructuredData
        data = StructuredData(**structured_data)

        # Initialize Graphiti
        settings = Settings()
        graphiti = GraphitiService(
            neo4j_uri=settings.neo4j_uri,
            neo4j_user=settings.neo4j_user,
            neo4j_password=settings.neo4j_password,
            openai_api_key=settings.openai_api_key,
        )

        # Add JSON episode to Graphiti
        result = await graphiti.add_json_episode(
            json_id=data.uuid,
            json_data=data.raw_json,
            metadata={
                'source': data.metadata.source,
                'data_type': data.metadata.data_type.value,
            }
        )

        if not result.success:
            raise ApplicationError(
                f"Graphiti JSON extraction failed: {result.error}",
                non_retryable=True
            )

        # Convert Graphiti entities
        entities = [
            {
                'name': entity_name,
                'entity_type': 'graphiti_json_extracted',
                'confidence': 0.9,
                'source': 'graphiti_json',
            }
            for entity_name in result.entities_extracted
        ]

        record_temporal_activity_completed('extract_entities_from_json_activity', success=True)

        return {
            'entities': entities,
            'graphiti_episode_uuid': data.uuid,
            'edges_created': len(result.edges_created),
            'text_representation': data.text_representation,  # For embeddings
        }

    except ApplicationError:
        record_temporal_activity_completed('extract_entities_from_json_activity', success=False)
        raise
    except Exception as e:
        activity.logger.error(f"JSON extraction error: {e}", exc_info=True)
        record_temporal_activity_completed('extract_entities_from_json_activity', success=False)
        raise
```

#### Add write_structured_data_activity:

```python
@activity.defn
async def write_structured_data_activity(
    structured_data: Dict[str, Any],
    entities: Dict[str, Any],
    embeddings: Dict[str, Any],
) -> Dict[str, Any]:
    """Write structured JSON data to databases with Graphiti rollback.

    Flow:
    1. Call Saga write_structured_data_parallel()
    2. If Saga fails, rollback Graphiti episode

    References:
        Enhanced Saga: Internal documentation
        Graphiti Rollback: https://github.com/getzep/graphiti

    Args:
        structured_data: StructuredData as dict
        entities: Dict with entities and graphiti_episode_uuid
        embeddings: Dict with embedding vector

    Returns:
        Dict with write confirmations
    """
    from apex_memory.models.structured_data import StructuredData
    from apex_memory.services.database_writer import DatabaseWriteOrchestrator

    record_temporal_activity_started('write_structured_data_activity')

    # Reconstruct StructuredData model
    data = StructuredData(**structured_data)

    # Extract Graphiti episode UUID
    graphiti_episode_uuid = entities.get('graphiti_episode_uuid')

    orchestrator = DatabaseWriteOrchestrator()

    try:
        result = await orchestrator.write_structured_data_parallel(
            structured_data=data,
            embedding=embeddings['embedding'],
            entities=entities.get('entities', []),
        )

        # Rollback Graphiti on failure
        if not result.all_success and graphiti_episode_uuid:
            await rollback_graphiti_episode(graphiti_episode_uuid)

        record_temporal_activity_completed('write_structured_data_activity', success=result.all_success)

        return result.model_dump()

    except Exception as e:
        # Rollback Graphiti
        if graphiti_episode_uuid:
            await rollback_graphiti_episode(graphiti_episode_uuid)

        record_temporal_activity_completed('write_structured_data_activity', success=False)
        raise
```

**Testing:**

```bash
pytest tests/unit/test_graphiti_json_extraction.py -v
pytest tests/integration/test_json_graphiti_rollback.py -v
```

---

### Phase 2 Validation

**Run all tests:**

```bash
# 1. Unit tests for JSON support (15 tests)
pytest tests/unit/test_structured_data_models.py -v
pytest tests/unit/test_json_writer_*.py -v
pytest tests/unit/test_graphiti_json_extraction.py -v

# 2. Integration tests
pytest tests/integration/test_structured_data_saga.py -v
pytest tests/integration/test_json_graphiti_rollback.py -v

# 3. End-to-end test with sample JSON
pytest tests/integration/test_samsara_json_ingestion.py -v

# 4. Baseline validation (121 + 10 + 15 = 146 tests)
pytest tests/ --ignore=tests/load/ -v
# Expected: 146/146 tests pass

# 5. Verify databases
# PostgreSQL:
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT * FROM structured_data LIMIT 1"
# Qdrant:
curl http://localhost:6333/collections/apex_structured_data
# Neo4j:
# Browser: http://localhost:7474
# Query: MATCH (d:StructuredData) RETURN d LIMIT 1
```

**Phase 2 Complete:** ✅ JSON support operational

---

## Phase 3: Staging Lifecycle

**Goal:** Replace S3 with local staging, add source pulling, add cleanup

### Step 3.1: Add pull_and_stage_document_activity

**File:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**Reference:** [Temporal File Handling](https://docs.temporal.io/develop/python/data-converters) | [Python pathlib](https://docs.python.org/3/library/pathlib.html)

```python
@activity.defn
async def pull_and_stage_document_activity(
    document_id: str,
    source: str,
    source_location: str,
) -> str:
    """Pull document from source and write to local staging folder.

    Handles:
    - FrontApp API downloads (via OAuth)
    - Local file system moves
    - HTTP/HTTPS URL downloads

    References:
        Temporal File Handling: https://docs.temporal.io/develop/python/data-converters
        Python pathlib: https://docs.python.org/3/library/pathlib.html

    Args:
        document_id: Unique document identifier (UUID)
        source: Data source name (frontapp, local_upload, http)
        source_location: Where to fetch from (URL, file path, API endpoint)

    Returns:
        Local staging path: "/tmp/apex-staging/{source}/{document_id}/filename.ext"

    Raises:
        ApplicationError: If download fails
    """
    import os
    import shutil
    from pathlib import Path
    from apex_memory.config.settings import Settings

    record_temporal_activity_started('pull_and_stage_document_activity')

    try:
        settings = Settings()
        staging_dir = Path(settings.staging_base_dir) / source / document_id
        staging_dir.mkdir(parents=True, exist_ok=True)

        if source == "frontapp":
            # Pull via FrontApp API
            from apex_memory.integrations.frontapp import FrontAppClient

            client = FrontAppClient(api_token=settings.frontapp_api_token)
            attachment = await client.get_attachment(source_location)

            file_path = staging_dir / attachment.filename
            file_path.write_bytes(attachment.content)

        elif source == "local_upload":
            # Move from temporary upload location
            source_path = Path(source_location)
            file_path = staging_dir / source_path.name
            shutil.copy(source_location, file_path)

        elif source.startswith("http"):
            # Download via HTTP
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(source_location)
                response.raise_for_status()

                # Extract filename from Content-Disposition or URL
                filename = response.headers.get("Content-Disposition", "document.pdf")
                file_path = staging_dir / filename
                file_path.write_bytes(response.content)

        else:
            raise ApplicationError(f"Unknown source: {source}", non_retryable=True)

        # Emit metric
        file_size = file_path.stat().st_size
        record_temporal_data_quality(
            metric_type='staging_bytes_written',
            value=file_size,
            source=source
        )

        activity.logger.info(f"Staged document: {file_path} ({file_size} bytes)")

        record_temporal_activity_completed('pull_and_stage_document_activity', success=True)

        return str(file_path)

    except ApplicationError:
        record_temporal_activity_completed('pull_and_stage_document_activity', success=False)
        raise
    except Exception as e:
        activity.logger.error(f"Staging failed: {e}", exc_info=True)
        record_temporal_activity_completed('pull_and_stage_document_activity', success=False)
        raise
```

**Testing:**

```bash
pytest tests/unit/test_pull_and_stage_activity.py -v
```

---

### Step 3.2: Add fetch_structured_data_activity

**File:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

```python
@activity.defn
async def fetch_structured_data_activity(
    data_id: str,
    source: str,
    source_endpoint: str,
    data_type: str,
) -> dict:
    """Fetch structured JSON data from external API.

    Handles:
    - Samsara GPS telemetry (via REST API)
    - Turvo shipment data (via REST API)
    - FrontApp webhook payloads (already in memory)

    References:
        Samsara API: https://developers.samsara.com/reference
        Turvo API: https://api.turvo.com/docs

    Args:
        data_id: Unique data identifier
        source: Data source (samsara, turvo, frontapp_webhook)
        source_endpoint: API endpoint or JSON string
        data_type: Type of data (gps_event, shipment, message)

    Returns:
        Raw JSON dictionary from source
    """
    import json
    import httpx
    from apex_memory.config.settings import Settings

    record_temporal_activity_started('fetch_structured_data_activity')

    try:
        if source == "samsara":
            # Fetch via Samsara API
            settings = Settings()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    source_endpoint,
                    headers={"Authorization": f"Bearer {settings.samsara_api_token}"}
                )
                response.raise_for_status()
                data = response.json()

        elif source == "turvo":
            # Fetch via Turvo API
            settings = Settings()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    source_endpoint,
                    headers={"Authorization": f"Bearer {settings.turvo_api_token}"}
                )
                response.raise_for_status()
                data = response.json()

        elif source == "frontapp_webhook":
            # Webhook payload already provided (JSON string)
            data = json.loads(source_endpoint)

        else:
            raise ApplicationError(f"Unknown source: {source}", non_retryable=True)

        # Emit metric
        record_temporal_data_quality(
            metric_type='structured_data_fetched',
            value=1,
            source=source
        )

        activity.logger.info(f"Fetched {data_type} from {source}: {data_id}")

        record_temporal_activity_completed('fetch_structured_data_activity', success=True)

        return data

    except ApplicationError:
        record_temporal_activity_completed('fetch_structured_data_activity', success=False)
        raise
    except Exception as e:
        activity.logger.error(f"Fetch failed: {e}", exc_info=True)
        record_temporal_activity_completed('fetch_structured_data_activity', success=False)
        raise
```

**Testing:**

```bash
pytest tests/unit/test_fetch_structured_data_activity.py -v
```

---

### Step 3.3: Create StagingManager Service

**File:** `apex-memory-system/src/apex_memory/services/staging_manager.py` (NEW)

**Reference:** [Python pathlib](https://docs.python.org/3/library/pathlib.html)

```python
"""Staging Manager Service.

Manages local folder lifecycle for document staging:
- Create staging directories
- Track metadata
- Cleanup failed ingestions (after retention period)
- Monitor disk usage

References:
    Python pathlib: https://docs.python.org/3/library/pathlib.html
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from apex_memory.config.settings import Settings

logger = logging.getLogger(__name__)


class StagingManager:
    """Manage local staging folder lifecycle."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize staging manager.

        Args:
            settings: Settings instance (defaults to Settings())
        """
        self.settings = settings or Settings()
        self.base_dir = Path(self.settings.staging_base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_staging_dir(self, source: str, document_id: str) -> Path:
        """Create staging directory for document.

        Args:
            source: Data source name
            document_id: Document UUID

        Returns:
            Path to staging directory
        """
        staging_dir = self.base_dir / source / document_id
        staging_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Created staging directory: {staging_dir}")
        return staging_dir

    def cleanup_staging_dir(self, staging_path: str) -> bool:
        """Remove staging directory after successful ingestion.

        Args:
            staging_path: Path to staging file or directory

        Returns:
            True if cleanup successful, False otherwise
        """
        staging_dir = Path(staging_path).parent

        try:
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
                logger.info(f"Cleaned up staging directory: {staging_dir}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cleanup {staging_dir}: {e}")
            return False

    def cleanup_old_failed_ingestions(self) -> int:
        """Cleanup failed ingestion folders older than retention period.

        Returns:
            Number of directories cleaned up
        """
        retention_hours = self.settings.staging_failed_retention_hours
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)

        cleaned = 0

        for source_dir in self.base_dir.iterdir():
            if not source_dir.is_dir():
                continue

            for document_dir in source_dir.iterdir():
                if not document_dir.is_dir():
                    continue

                # Check modification time
                mod_time = datetime.fromtimestamp(document_dir.stat().st_mtime)

                if mod_time < cutoff_time:
                    try:
                        shutil.rmtree(document_dir)
                        logger.info(f"Cleaned up old staging: {document_dir}")
                        cleaned += 1
                    except Exception as e:
                        logger.error(f"Failed to cleanup {document_dir}: {e}")

        return cleaned

    def get_disk_usage(self) -> int:
        """Get current disk usage of staging directory.

        Returns:
            Disk usage in bytes
        """
        total_size = 0

        for dirpath, dirnames, filenames in os.walk(self.base_dir):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                total_size += file_path.stat().st_size

        return total_size

    def is_disk_full(self) -> bool:
        """Check if staging disk usage exceeds maximum.

        Returns:
            True if disk usage > max_size_gb
        """
        max_bytes = self.settings.staging_max_size_gb * 1024 * 1024 * 1024
        current_bytes = self.get_disk_usage()

        return current_bytes > max_bytes
```

**Testing:**

```bash
pytest tests/unit/test_staging_manager.py -v
```

---

### Step 3.4: Add cleanup_staging_activity

**File:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

```python
@activity.defn
async def cleanup_staging_activity(staging_path: str) -> None:
    """Remove staging directory after successful ingestion.

    References:
        Python pathlib: https://docs.python.org/3/library/pathlib.html

    Args:
        staging_path: Path to staging file or directory
    """
    from apex_memory.services.staging_manager import StagingManager

    record_temporal_activity_started('cleanup_staging_activity')

    try:
        manager = StagingManager()
        success = manager.cleanup_staging_dir(staging_path)

        if success:
            # Emit metric
            record_temporal_data_quality(
                metric_type='staging_cleanups',
                value=1,
                source='cleanup_activity'
            )

            activity.logger.info(f"Cleaned up staging: {staging_path}")
            record_temporal_activity_completed('cleanup_staging_activity', success=True)
        else:
            activity.logger.warning(f"Staging already removed: {staging_path}")
            record_temporal_activity_completed('cleanup_staging_activity', success=True)

    except Exception as e:
        activity.logger.error(f"Cleanup failed: {e}", exc_info=True)
        record_temporal_activity_completed('cleanup_staging_activity', success=False)
        # Don't raise - cleanup failure shouldn't fail the workflow
```

**Testing:**

```bash
pytest tests/unit/test_cleanup_staging_activity.py -v
```

---

### Step 3.5: Add Staging Metrics

**File:** `apex-memory-system/src/apex_memory/monitoring/metrics.py`

**Reference:** [Prometheus Python Client](https://github.com/prometheus/client_python)

```python
# Staging metrics
apex_temporal_staging_bytes_written = Histogram(
    "apex_temporal_staging_bytes_written",
    "Bytes written to local staging",
    ["source"],
    buckets=[1024, 10240, 102400, 1048576, 10485760],  # 1KB to 10MB
)

apex_temporal_staging_cleanups_total = Counter(
    "apex_temporal_staging_cleanups_total",
    "Total staging directory cleanups",
    ["status"],  # success, failed
)

apex_temporal_staging_disk_usage_bytes = Gauge(
    "apex_temporal_staging_disk_usage_bytes",
    "Current disk usage of staging directory",
)

# Structured data metrics
apex_temporal_structured_data_fetched_total = Counter(
    "apex_temporal_structured_data_fetched_total",
    "Total structured data records fetched",
    ["source", "data_type"],
)

apex_temporal_entities_per_json_bucket = Histogram(
    "apex_temporal_entities_per_json_bucket",
    "Entities extracted per JSON record",
    ["source", "data_type"],
    buckets=[0, 1, 5, 10, 20, 50],
)
```

**Testing:**

```bash
pytest tests/unit/test_staging_metrics.py -v
```

---

### Phase 3 Validation

**Run all tests:**

```bash
# 1. Unit tests for staging (10 tests)
pytest tests/unit/test_pull_and_stage_activity.py -v
pytest tests/unit/test_fetch_structured_data_activity.py -v
pytest tests/unit/test_staging_manager.py -v
pytest tests/unit/test_cleanup_staging_activity.py -v
pytest tests/unit/test_staging_metrics.py -v

# 2. Integration test
pytest tests/integration/test_local_staging_workflow.py -v

# 3. Baseline validation (121 + 10 + 15 + 10 = 156 tests)
pytest tests/ --ignore=tests/load/ -v
# Expected: 156/156 tests pass

# 4. Verify staging cleanup
ls -la /tmp/apex-staging/
# Expected: Should be empty or contain only recent folders
```

**Phase 3 Complete:** ✅ Local staging operational

---

## Phase 4: Two Workflows

**Goal:** Create separate workflows for documents vs. structured data

### Step 4.1: Update DocumentIngestionWorkflow

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`

**Reference:** [Temporal Workflows](https://docs.temporal.io/develop/python/core-application#develop-workflows)

```python
@workflow.defn(name="DocumentIngestionWorkflow")
class DocumentIngestionWorkflow:
    """Document ingestion workflow with local staging.

    6 Activities:
    1. pull_and_stage_document_activity (NEW - replaces S3 download)
    2. parse_document_activity (Docling)
    3. extract_entities_activity (Graphiti)
    4. generate_embeddings_activity (OpenAI)
    5. write_to_databases_activity (Saga)
    6. cleanup_staging_activity (NEW)

    References:
        Temporal Workflows: https://docs.temporal.io/develop/python/core-application
    """

    def __init__(self):
        """Initialize workflow instance variables."""
        self.document_id: Optional[str] = None
        self.source: Optional[str] = None
        self.status: str = "pending"
        self.staging_path: Optional[str] = None
        self.error_message: Optional[str] = None

    @workflow.run
    async def run(
        self,
        document_id: str,
        source: str,
        source_location: str,  # ← Changed from s3_bucket
    ) -> dict:
        """Run document ingestion workflow.

        Args:
            document_id: Document UUID
            source: Data source (frontapp, local_upload, http)
            source_location: Where to fetch from (URL, file path, API endpoint)

        Returns:
            Ingestion result with database write confirmations
        """
        self.document_id = document_id
        self.source = source
        self.status = "pulling"

        # ============================================================
        # ACTIVITY 1: Pull from source → Local staging (NEW)
        # ============================================================
        self.staging_path = await workflow.execute_activity(
            pull_and_stage_document_activity,
            args=[document_id, source, source_location],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3,
            ),
        )

        self.status = "staged"

        # ============================================================
        # ACTIVITY 2: Parse document
        # ============================================================
        self.status = "parsing"
        parsed_doc = await workflow.execute_activity(
            parse_document_activity,
            args=[self.staging_path],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=20),
                maximum_attempts=3,
            ),
        )

        self.status = "parsed"

        # ============================================================
        # ACTIVITY 3: Extract entities (Graphiti)
        # ============================================================
        self.status = "extracting_entities"
        entities = await workflow.execute_activity(
            extract_entities_activity,
            args=[parsed_doc],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
            ),
        )

        self.status = "entities_extracted"

        # ============================================================
        # ACTIVITY 4: Generate embeddings
        # ============================================================
        self.status = "generating_embeddings"
        embeddings = await workflow.execute_activity(
            generate_embeddings_activity,
            args=[parsed_doc],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=5,
            ),
        )

        self.status = "embeddings_generated"

        # ============================================================
        # ACTIVITY 5: Write to databases (Saga)
        # ============================================================
        self.status = "writing_to_databases"
        saga_result = await workflow.execute_activity(
            write_to_databases_activity,
            args=[parsed_doc, entities, embeddings],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
            ),
        )

        # ============================================================
        # ACTIVITY 6: Cleanup staging (NEW)
        # ============================================================
        await workflow.execute_activity(
            cleanup_staging_activity,
            args=[self.staging_path],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=5),
                maximum_attempts=3,
            ),
        )

        self.status = "completed"

        return {
            "status": "success",
            "document_id": document_id,
            "source": source,
            "databases_written": saga_result,
            "entities_extracted": len(entities.get('entities', [])),
            "chunks_created": len(parsed_doc.get('chunks', [])),
        }

    @workflow.query
    def get_status(self) -> dict:
        """Query workflow status."""
        return {
            "document_id": self.document_id,
            "source": self.source,
            "status": self.status,
            "staging_path": self.staging_path,
            "error_message": self.error_message,
        }
```

**Testing:**

```bash
pytest tests/integration/test_document_workflow_local_staging.py -v
```

---

### Step 4.2: Create StructuredDataIngestionWorkflow

**File:** `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`

**Reference:** [Temporal Workflows](https://docs.temporal.io/develop/python/core-application#develop-workflows)

```python
@workflow.defn(name="StructuredDataIngestionWorkflow")
class StructuredDataIngestionWorkflow:
    """Structured data ingestion workflow (for JSON).

    4 Activities:
    1. fetch_structured_data_activity
    2. extract_entities_from_json_activity (Graphiti)
    3. generate_embeddings_from_json_activity (OpenAI)
    4. write_structured_data_activity (Saga)

    No staging needed (JSON < 2MB fits in Temporal payload limit).

    References:
        Temporal Workflows: https://docs.temporal.io/develop/python/core-application
        Temporal Payload Limits: https://docs.temporal.io/develop/python/data-converters
    """

    def __init__(self):
        """Initialize workflow instance variables."""
        self.data_id: Optional[str] = None
        self.source: Optional[str] = None
        self.data_type: Optional[str] = None
        self.status: str = "pending"
        self.error_message: Optional[str] = None

    @workflow.run
    async def run(
        self,
        data_id: str,
        source: str,
        source_endpoint: str,
        data_type: str,
    ) -> dict:
        """Run structured data ingestion workflow.

        Args:
            data_id: Unique data identifier
            source: Data source (samsara, turvo, frontapp_webhook)
            source_endpoint: API endpoint or JSON payload
            data_type: Type of data (gps_event, shipment, message)

        Returns:
            Ingestion result with database write confirmations
        """
        self.data_id = data_id
        self.source = source
        self.data_type = data_type
        self.status = "fetching"

        # ============================================================
        # ACTIVITY 1: Fetch structured data from source
        # ============================================================
        raw_json = await workflow.execute_activity(
            fetch_structured_data_activity,
            args=[data_id, source, source_endpoint, data_type],
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=5,
            ),
        )

        self.status = "fetched"

        # ============================================================
        # ACTIVITY 2: Extract entities with Graphiti
        # ============================================================
        self.status = "extracting_entities"

        # Create StructuredData instance
        from apex_memory.models.structured_data import StructuredData, StructuredDataMetadata, StructuredDataType
        import uuid

        structured_data = StructuredData(
            uuid=str(uuid.uuid4()),
            metadata=StructuredDataMetadata(
                data_id=data_id,
                source=source,
                data_type=StructuredDataType(data_type),
            ),
            raw_json=raw_json,
            text_representation=f"{data_type} from {source}: {data_id}",  # TODO: Better text conversion
        )

        entities = await workflow.execute_activity(
            extract_entities_from_json_activity,
            args=[structured_data.model_dump()],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
            ),
        )

        # Update text representation from Graphiti result
        structured_data.text_representation = entities.get('text_representation', structured_data.text_representation)

        self.status = "entities_extracted"

        # ============================================================
        # ACTIVITY 3: Generate embeddings
        # ============================================================
        self.status = "generating_embeddings"
        embeddings = await workflow.execute_activity(
            generate_embeddings_from_json_activity,
            args=[structured_data.text_representation],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=5,
            ),
        )

        self.status = "embeddings_generated"

        # ============================================================
        # ACTIVITY 4: Write to databases (Saga)
        # ============================================================
        self.status = "writing_to_databases"
        saga_result = await workflow.execute_activity(
            write_structured_data_activity,
            args=[structured_data.model_dump(), entities, embeddings],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
            ),
        )

        self.status = "completed"

        return {
            "status": "success",
            "data_id": data_id,
            "source": source,
            "data_type": data_type,
            "databases_written": saga_result,
            "entities_extracted": len(entities.get('entities', [])),
        }

    @workflow.query
    def get_status(self) -> dict:
        """Query workflow status."""
        return {
            "data_id": self.data_id,
            "source": self.source,
            "data_type": self.data_type,
            "status": self.status,
            "error_message": self.error_message,
        }
```

**Testing:**

```bash
pytest tests/integration/test_structured_data_workflow.py -v
```

---

### Step 4.3: Update API Routes

**File:** `apex-memory-system/src/apex_memory/api/ingestion.py`

**Reference:** [FastAPI](https://fastapi.tiangolo.com/) | [Temporal Client](https://docs.temporal.io/develop/python/core-application#connect-to-temporal)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from temporalio.client import Client

router = APIRouter(prefix="/ingest", tags=["ingestion"])


class IngestDocumentRequest(BaseModel):
    """Request to ingest a document."""
    document_id: str
    source: str  # frontapp, local_upload, http
    source_location: str  # URL, file path, or API endpoint


class IngestStructuredDataRequest(BaseModel):
    """Request to ingest structured JSON data."""
    data_id: str
    source: str  # samsara, turvo, frontapp_webhook
    source_endpoint: str  # API endpoint or JSON payload
    data_type: str  # gps_event, shipment, message


@router.post("/document")
async def ingest_document(request: IngestDocumentRequest):
    """Ingest a document via DocumentIngestionWorkflow.

    Routes to local staging workflow (6 activities).

    References:
        FastAPI: https://fastapi.tiangolo.com/
        Temporal Client: https://docs.temporal.io/develop/python/core-application
    """
    client = await Client.connect("localhost:7233")

    try:
        result = await client.execute_workflow(
            DocumentIngestionWorkflow.run,
            args=[request.document_id, request.source, request.source_location],
            id=f"ingest-doc-{request.document_id}",
            task_queue="apex-ingestion-queue",
        )

        return {"status": "success", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/structured")
async def ingest_structured_data(request: IngestStructuredDataRequest):
    """Ingest structured JSON via StructuredDataIngestionWorkflow.

    Routes to JSON workflow (4 activities, no staging).

    References:
        FastAPI: https://fastapi.tiangolo.com/
        Temporal Client: https://docs.temporal.io/develop/python/core-application
    """
    client = await Client.connect("localhost:7233")

    try:
        result = await client.execute_workflow(
            StructuredDataIngestionWorkflow.run,
            args=[request.data_id, request.source, request.source_endpoint, request.data_type],
            id=f"ingest-json-{request.data_id}",
            task_queue="apex-ingestion-queue",
        )

        return {"status": "success", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/frontapp")
async def frontapp_webhook(payload: dict):
    """FrontApp webhook receiver.

    References:
        FrontApp Webhooks: https://dev.frontapp.com/docs/webhooks
    """
    import json

    # Extract message data
    message_id = payload.get("payload", {}).get("id")

    # Route to StructuredDataIngestionWorkflow
    client = await Client.connect("localhost:7233")

    await client.start_workflow(
        StructuredDataIngestionWorkflow.run,
        args=[message_id, "frontapp_webhook", json.dumps(payload), "message"],
        id=f"frontapp-{message_id}",
        task_queue="apex-ingestion-queue",
    )

    return {"status": "accepted"}


@router.post("/webhook/turvo")
async def turvo_webhook(payload: dict):
    """Turvo webhook receiver.

    References:
        Turvo API: https://api.turvo.com/docs
    """
    import json

    shipment_id = payload.get("shipment_id")

    client = await Client.connect("localhost:7233")

    await client.start_workflow(
        StructuredDataIngestionWorkflow.run,
        args=[shipment_id, "turvo_webhook", json.dumps(payload), "shipment"],
        id=f"turvo-{shipment_id}",
        task_queue="apex-ingestion-queue",
    )

    return {"status": "accepted"}
```

**Testing:**

```bash
pytest tests/integration/test_api_routing.py -v
```

---

### Step 4.4: Update Worker Configuration

**File:** `apex-memory-system/src/apex_memory/temporal/workers/dev_worker.py`

**Reference:** [Temporal Workers](https://docs.temporal.io/develop/python/core-application#run-a-dev-worker)

```python
from temporalio.client import Client
from temporalio.worker import Worker
from apex_memory.temporal.workflows.ingestion import (
    DocumentIngestionWorkflow,
    StructuredDataIngestionWorkflow,  # NEW
)
from apex_memory.temporal.activities.ingestion import (
    # Document activities
    pull_and_stage_document_activity,  # NEW - replaces download_from_s3_activity
    parse_document_activity,
    extract_entities_activity,
    generate_embeddings_activity,
    write_to_databases_activity,
    cleanup_staging_activity,  # NEW

    # Structured data activities (NEW)
    fetch_structured_data_activity,
    extract_entities_from_json_activity,
    generate_embeddings_from_json_activity,
    write_structured_data_activity,
)


async def main():
    """Run Temporal worker with both workflows."""
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="apex-ingestion-queue",
        workflows=[
            DocumentIngestionWorkflow,
            StructuredDataIngestionWorkflow,  # NEW
        ],
        activities=[
            # Document activities
            pull_and_stage_document_activity,
            parse_document_activity,
            extract_entities_activity,
            generate_embeddings_activity,
            write_to_databases_activity,
            cleanup_staging_activity,

            # Structured data activities
            fetch_structured_data_activity,
            extract_entities_from_json_activity,
            generate_embeddings_from_json_activity,
            write_structured_data_activity,
        ],
    )

    print("✅ Worker started - listening on apex-ingestion-queue")
    print("✅ Workflows: DocumentIngestionWorkflow, StructuredDataIngestionWorkflow")
    print("✅ Activities: 10 total (6 document + 4 structured)")

    await worker.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Start worker:**

```bash
cd apex-memory-system
python -m apex_memory.temporal.workers.dev_worker
```

---

### Phase 4 Validation

**Run all tests:**

```bash
# 1. Integration tests for both workflows
pytest tests/integration/test_document_workflow_local_staging.py -v
pytest tests/integration/test_structured_data_workflow.py -v
pytest tests/integration/test_api_routing.py -v

# 2. Load test (100+ parallel workflows)
pytest tests/load/test_concurrent_workflows.py -v

# 3. Final baseline validation (121 + 10 + 15 + 10 = 156 tests)
pytest tests/ --ignore=tests/load/ -v
# Expected: 156/156 tests pass

# 4. Verify both workflows in Temporal UI
# Open: http://localhost:8088
# Expected: See both DocumentIngestionWorkflow and StructuredDataIngestionWorkflow

# 5. Test document ingestion end-to-end
curl -X POST http://localhost:8000/ingest/document \
  -H "Content-Type: application/json" \
  -d '{"document_id": "test-123", "source": "http", "source_location": "https://example.com/sample.pdf"}'

# 6. Test JSON ingestion end-to-end
curl -X POST http://localhost:8000/ingest/structured \
  -H "Content-Type: application/json" \
  -d '{"data_id": "ship-456", "source": "turvo", "source_endpoint": "https://api.turvo.com/shipments/456", "data_type": "shipment"}'
```

**Phase 4 Complete:** ✅ Two-workflow architecture operational

---

## Validation & Testing

### Final Validation Checklist

**Run all tests in sequence:**

```bash
cd apex-memory-system

# 1. Unit tests (35 tests)
pytest tests/unit/test_graphiti_*.py -v                    # 10 tests
pytest tests/unit/test_json_*.py -v                        # 15 tests
pytest tests/unit/test_staging_*.py -v                     # 10 tests

# 2. Integration tests
pytest tests/integration/test_*_graphiti.py -v             # 2 tests
pytest tests/integration/test_*_saga.py -v                 # 2 tests
pytest tests/integration/test_*_workflow.py -v             # 3 tests
pytest tests/integration/test_api_routing.py -v            # 1 test

# 3. Baseline validation (121 Enhanced Saga tests)
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v
# Expected: 121/121 tests pass

# 4. Load tests
pytest tests/load/test_concurrent_workflows.py -v

# 5. Total test count
pytest tests/ --ignore=tests/load/ -v
# Expected: 156/156 tests pass (121 + 35)
```

### Database Verification

```bash
# 1. PostgreSQL - Verify structured_data table
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "\d structured_data"
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT COUNT(*) FROM structured_data"

# 2. Qdrant - Verify collection
curl http://localhost:6333/collections/apex_structured_data

# 3. Neo4j - Verify Graphiti knowledge graph
# Browser: http://localhost:7474
# Cypher: MATCH (e:Entity) RETURN count(e)
# Cypher: MATCH (d:StructuredData) RETURN count(d)

# 4. Redis - Verify structured data keys
redis-cli KEYS "structured_data:*"
```

### Monitoring Verification

```bash
# 1. Verify staging metrics
curl http://localhost:9090/api/v1/query?query=apex_temporal_staging_bytes_written_bucket

# 2. Verify Graphiti metrics
curl http://localhost:9090/api/v1/query?query=apex_temporal_entities_per_document_bucket

# 3. Verify structured data metrics
curl http://localhost:9090/api/v1/query?query=apex_temporal_structured_data_fetched_total

# 4. Open Grafana dashboard
# URL: http://localhost:3001/d/temporal-ingestion
# Expected: See panels for both workflows
```

### Performance Benchmarks

```bash
# Document workflow (with Graphiti)
time curl -X POST http://localhost:8000/ingest/document \
  -H "Content-Type: application/json" \
  -d '{"document_id": "perf-test-1", "source": "http", "source_location": "https://example.com/5mb.pdf"}'
# Expected: <30s end-to-end

# Structured data workflow
time curl -X POST http://localhost:8000/ingest/structured \
  -H "Content-Type: application/json" \
  -d '{"data_id": "perf-test-2", "source": "turvo", "source_endpoint": "https://api.turvo.com/shipments/123", "data_type": "shipment"}'
# Expected: <10s end-to-end
```

---

## Success Criteria

✅ **Phase 1: Graphiti Integration**
- extract_entities_activity uses Graphiti
- Graphiti episodes rolled back on saga failure
- Knowledge graph visible in Neo4j
- 10 new tests pass

✅ **Phase 2: JSON Support**
- All 4 database writers have write_json_record()
- Saga supports structured data
- 15 new tests pass

✅ **Phase 3: Staging Lifecycle**
- Local staging operational
- S3 deprecated (read-only)
- 10 new tests pass

✅ **Phase 4: Two Workflows**
- DocumentIngestionWorkflow (6 activities)
- StructuredDataIngestionWorkflow (4 activities)
- API routes correctly
- Worker registers both workflows

✅ **Overall**
- All 156 tests pass (121 + 35)
- Load test: 100+ concurrent workflows
- Performance: Document <30s, JSON <10s
- Monitoring: All metrics collected

---

**Implementation Complete!** 🎉

**Next Steps:**
1. Deploy to staging environment
2. Run production readiness checklist
3. Gradual rollout (10% → 50% → 100%)
4. Monitor for 1 week
5. Deprecate S3 staging completely

---

**Document Version:** 1.0
**Last Updated:** 2025-10-19
**Author:** Claude Code
**Based On:** Tier 1 Official Documentation
