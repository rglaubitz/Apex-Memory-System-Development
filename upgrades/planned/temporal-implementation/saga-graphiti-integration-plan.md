# Saga JSON Support + Staging Lifecycle + Graphiti Integration Plan

## Executive Summary

**Goal:** Add structured data (JSON) ingestion with Graphiti as the primary entity extractor, then implement staging lifecycle management.

**Key Architectural Decision:** ✅ Option A with Enhancement
- Graphiti replaces EntityExtractor for LLM-powered entity extraction
- Graphiti manages its own Neo4j knowledge graph (separate from Saga)
- Saga handles rollback of Graphiti episodes on failure
- Graphiti.add_json_episode() used for all structured data

**Impact Level:** 🟡 Medium - Replaces EntityExtractor, adds JSON support, zero risk to Saga baseline

---

## 📊 Updated Architecture Flow

### Document Ingestion (Current → New)

**BEFORE (Current):**
```
parse_document
    ↓
extract_entities (EntityExtractor - regex patterns) ❌
    ↓
generate_embeddings (OpenAI)
    ↓
Saga → 4 Databases (Neo4j basic node, Postgres, Qdrant, Redis)
```

**AFTER (New with Graphiti):**
```
parse_document
    ↓
Graphiti.add_document_episode()  ✅ (LLM entity extraction + knowledge graph)
    ↓ (returns extracted entities)
generate_embeddings (OpenAI)
    ↓
Saga → 4 Databases (Postgres, Qdrant, Redis, Neo4j metadata)
    ↓ (on failure)
Rollback: Graphiti.remove_episode()  ✅
```

### Structured Data Ingestion (NEW)

```
Fetch JSON from API (Samsara, Turvo, FrontApp)
    ↓
Graphiti.add_json_episode()  ✅ (LLM entity extraction from JSON)
    ↓ (returns extracted entities + text representation)
generate_embeddings (OpenAI - embed text representation)
    ↓
Saga → 4 Databases (Postgres, Qdrant, Redis, Neo4j metadata)
    ↓ (on failure)
Rollback: Graphiti.remove_episode()  ✅
```

---

## Phase 1: Graphiti Integration into Document Pipeline

### 1.1 Update extract_entities_activity to Use Graphiti

**File:** `src/apex_memory/temporal/activities/ingestion.py`

**BEFORE:**
```python
@activity.defn
async def extract_entities_activity(parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract entities using EntityExtractor (regex patterns)."""
    extractor = EntityExtractor()
    entities = extractor.extract_entities(parsed_doc['content'])
    return [entity.to_dict() for entity in entities]
```

**AFTER:**
```python
@activity.defn
async def extract_entities_activity(parsed_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Extract entities using Graphiti (LLM-powered).
    
    Returns:
        Dict with:
            - entities: List of extracted entities
            - graphiti_episode_uuid: Episode UUID for rollback
    """
    from apex_memory.services.graphiti_service import GraphitiService
    from apex_memory.config.settings import Settings
    
    settings = Settings()
    graphiti = GraphitiService(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
    )
    
    # Add document episode to Graphiti
    result = await graphiti.add_document_episode(
        document_uuid=parsed_doc['uuid'],
        document_title=parsed_doc['metadata']['title'],
        document_content=parsed_doc['content'],
        document_type=parsed_doc['metadata']['file_type'],
        reference_time=parsed_doc.get('parse_timestamp'),
    )
    
    if not result.success:
        raise ApplicationError(f"Graphiti extraction failed: {result.error}")
    
    # Convert Graphiti entities to dict format
    entities = [
        {
            'name': entity_name,
            'entity_type': 'graphiti_extracted',  # Graphiti doesn't pre-classify types
            'confidence': 0.9,  # Graphiti uses LLMs (high confidence)
            'source': 'graphiti',
        }
        for entity_name in result.entities_extracted
    ]
    
    return {
        'entities': entities,
        'graphiti_episode_uuid': parsed_doc['uuid'],  # For rollback
        'edges_created': len(result.edges_created),
    }
```

**Why:** Graphiti provides LLM-powered extraction (way better than regex), automatic relationship inference, and temporal tracking.

---

### 1.2 Update write_to_databases_activity to Handle Graphiti Rollback

**File:** `src/apex_memory/temporal/activities/ingestion.py`

**Enhanced signature:**
```python
@activity.defn
async def write_to_databases_activity(
    parsed_doc: Dict[str, Any],
    entities: Dict[str, Any],  # Now includes graphiti_episode_uuid
    embeddings: Dict[str, Any],
) -> Dict[str, Any]:
    """Write to databases with Graphiti-aware rollback."""
    
    # Extract Graphiti episode UUID
    graphiti_episode_uuid = entities.get('graphiti_episode_uuid')
    entity_list = entities.get('entities', [])
    
    # Delegate to Saga orchestrator
    orchestrator = DatabaseWriteOrchestrator()
    
    try:
        result = await orchestrator.write_document_parallel(
            parsed_doc=parsed_doc,
            embedding=embeddings['document_embedding'],
            chunks=parsed_doc['chunks'],
            chunk_embeddings=embeddings.get('chunk_embeddings'),
            entities=entity_list,
        )
        
        # If saga failed, rollback Graphiti episode
        if not result.all_success and graphiti_episode_uuid:
            await rollback_graphiti_episode(graphiti_episode_uuid)
        
        return result.model_dump()
        
    except Exception as e:
        # On any error, rollback Graphiti
        if graphiti_episode_uuid:
            await rollback_graphiti_episode(graphiti_episode_uuid)
        raise


async def rollback_graphiti_episode(episode_uuid: str) -> None:
    """Rollback Graphiti episode on saga failure."""
    from apex_memory.services.graphiti_service import GraphitiService
    from apex_memory.config.settings import Settings
    
    settings = Settings()
    graphiti = GraphitiService(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
    )
    
    success = await graphiti.remove_episode(episode_uuid)
    if success:
        logger.info(f"Rolled back Graphiti episode: {episode_uuid}")
    else:
        logger.error(f"Failed to rollback Graphiti episode: {episode_uuid}")
        # Send to DLQ for manual cleanup
```

**Why:** Ensures Graphiti episodes are cleaned up if Saga fails (prevents orphaned knowledge graph data).

---

### 1.3 Update Workflow to Handle New Entity Format

**File:** `src/apex_memory/temporal/workflows/ingestion.py`

No breaking changes needed! The workflow just passes data between activities. The signature change from `List[Dict]` to `Dict[str, Any]` is handled transparently.

---

## Phase 2: Add Structured Data (JSON) Support

### 2.1 Create Pydantic Models

**File:** `src/apex_memory/models/structured_data.py` (NEW)

```python
from enum import Enum
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class StructuredDataType(str, Enum):
    """Types of structured data."""
    GPS_EVENT = "gps_event"          # Samsara GPS telemetry
    SHIPMENT = "shipment"            # Turvo TMS shipments  
    MESSAGE = "message"              # FrontApp webhook messages
    GENERIC_JSON = "generic_json"    # Fallback for other JSON


class StructuredDataMetadata(BaseModel):
    """Metadata for structured JSON data."""
    data_id: str = Field(..., description="External ID or UUID")
    source: str = Field(..., description="Data source (samsara, turvo, frontapp)")
    data_type: StructuredDataType
    ingestion_timestamp: datetime = Field(default_factory=datetime.utcnow)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class StructuredData(BaseModel):
    """Structured JSON data (parallel to ParsedDocument)."""
    uuid: str = Field(..., description="Internal UUID")
    metadata: StructuredDataMetadata
    raw_json: Dict[str, Any] = Field(..., description="Original JSON payload")
    text_representation: str = Field(..., description="Text for embeddings")
```

---

### 2.2 Add Database Write Methods

#### PostgreSQL Writer
**File:** `src/apex_memory/database/postgres_writer.py`

```python
async def write_json_record(self, structured_data: StructuredData, entities: List[Dict[str, Any]]) -> WriteResult:
    """Write structured JSON to Postgres."""
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
            structured_data.raw_json,
            structured_data.text_representation,
            entities,
            structured_data.metadata.ingestion_timestamp,
            structured_data.metadata.custom_metadata,
        )
        
        return WriteResult(success=True, database="postgres")
        
    except Exception as e:
        return WriteResult(success=False, database="postgres", error=str(e))
```

#### Qdrant Writer
**File:** `src/apex_memory/database/qdrant_writer.py`

```python
async def write_json_record(self, structured_data: StructuredData, embedding: List[float]) -> WriteResult:
    """Write structured JSON to Qdrant."""
    try:
        point = PointStruct(
            id=structured_data.uuid,
            vector=embedding,
            payload={
                "data_id": structured_data.metadata.data_id,
                "source": structured_data.metadata.source,
                "data_type": structured_data.metadata.data_type.value,
                "text": structured_data.text_representation,
                "ingestion_timestamp": structured_data.metadata.ingestion_timestamp.isoformat(),
                "custom_metadata": structured_data.metadata.custom_metadata,
            }
        )
        
        self.client.upsert(
            collection_name="apex_structured_data",
            points=[point]
        )
        
        return WriteResult(success=True, database="qdrant")
        
    except Exception as e:
        return WriteResult(success=False, database="qdrant", error=str(e))
```

#### Neo4j Writer
**File:** `src/apex_memory/database/neo4j_writer.py`

```python
async def write_json_record(self, structured_data: StructuredData, entities: List[Dict[str, Any]]) -> WriteResult:
    """Write structured JSON metadata to Neo4j."""
    try:
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
        
        # Link entities (from Graphiti extraction)
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
        return WriteResult(success=False, database="neo4j", error=str(e))
```

#### Redis Writer
**File:** `src/apex_memory/database/redis_writer.py`

```python
async def write_json_record(self, structured_data: StructuredData) -> WriteResult:
    """Write structured JSON to Redis for fast lookup."""
    try:
        key = f"structured_data:{structured_data.uuid}"
        value = {
            "data_id": structured_data.metadata.data_id,
            "source": structured_data.metadata.source,
            "data_type": structured_data.metadata.data_type.value,
            "text": structured_data.text_representation,
            "raw_json": structured_data.raw_json,
        }
        
        await self.redis.set(key, json.dumps(value), ex=86400)  # 24hr TTL
        
        return WriteResult(success=True, database="redis")
        
    except Exception as e:
        return WriteResult(success=False, database="redis", error=str(e))
```

---

### 2.3 Add Saga Orchestrator Method

**File:** `src/apex_memory/orchestration/saga.py`

```python
async def write_structured_data_parallel(
    self,
    structured_data: StructuredData,
    embedding: List[float],
    entities: List[Dict[str, Any]],
) -> SagaResult:
    """Write structured JSON to all 4 databases with parallel saga pattern."""
    
    write_operations = [
        ("postgres", self.postgres_writer.write_json_record(structured_data, entities)),
        ("qdrant", self.qdrant_writer.write_json_record(structured_data, embedding)),
        ("neo4j", self.neo4j_writer.write_json_record(structured_data, entities)),
        ("redis", self.redis_writer.write_json_record(structured_data)),
    ]
    
    return await self._execute_parallel_saga(write_operations)
```

---

### 2.4 Add Temporal Activity for Entity Extraction from JSON

**File:** `src/apex_memory/temporal/activities/ingestion.py`

```python
@activity.defn
async def extract_entities_from_json_activity(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract entities from JSON using Graphiti.
    
    Returns:
        Dict with:
            - entities: List of extracted entities
            - graphiti_episode_uuid: Episode UUID for rollback
    """
    from apex_memory.services.graphiti_service import GraphitiService
    from apex_memory.config.settings import Settings
    from apex_memory.models.structured_data import StructuredData
    
    settings = Settings()
    graphiti = GraphitiService(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
    )
    
    # Reconstruct StructuredData
    data = StructuredData(**structured_data)
    
    # Add JSON episode to Graphiti
    result = await graphiti.add_json_episode(
        episode_uuid=data.uuid,
        json_data=data.raw_json,
        data_type=data.metadata.data_type.value,
        source=data.metadata.source,
        reference_time=data.metadata.ingestion_timestamp,
    )
    
    if not result.success:
        raise ApplicationError(f"Graphiti JSON extraction failed: {result.error}")
    
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
    
    return {
        'entities': entities,
        'graphiti_episode_uuid': data.uuid,
        'edges_created': len(result.edges_created),
        'text_representation': result.text_representation,  # For embeddings
    }
```

---

### 2.5 Add Temporal Activity for JSON Database Writes

**File:** `src/apex_memory/temporal/activities/ingestion.py`

```python
@activity.defn
async def write_structured_data_activity(
    structured_data: Dict[str, Any],
    entities: Dict[str, Any],
    embeddings: Dict[str, Any],
) -> Dict[str, Any]:
    """Write structured JSON data to databases with Graphiti rollback."""
    from apex_memory.models.structured_data import StructuredData
    
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
        
        return result.model_dump()
        
    except Exception as e:
        # Rollback Graphiti
        if graphiti_episode_uuid:
            await rollback_graphiti_episode(graphiti_episode_uuid)
        raise
```

---

## Phase 3: Staging Lifecycle Management

*(Same as original plan - unchanged)*

### 3.1 Add Staging Configuration

**File:** `src/apex_memory/config/settings.py`

```python
class Settings(BaseSettings):
    # Staging lifecycle
    staging_base_dir: str = "/tmp/apex-staging"
    staging_failed_retention_hours: int = 24
    staging_cleanup_interval_minutes: int = 60
    staging_max_size_gb: int = 10
```

### 3.2 Create Staging Manager Service

**File:** `src/apex_memory/services/staging_manager.py` (NEW)

*(Full implementation from original plan)*

### 3.3 Add Staging Cleanup Worker

**File:** `src/apex_memory/workers/staging_cleanup_worker.py` (NEW)

*(Full implementation from original plan)*

### 3.4 Add Staging Metrics

**File:** `src/apex_memory/monitoring/metrics.py`

*(Metrics from original plan)*

---

## Testing Strategy

### Phase 1: Graphiti Integration

**Unit Tests:**
- `tests/unit/test_graphiti_extraction_activity.py` - Graphiti entity extraction
- `tests/unit/test_graphiti_rollback.py` - Rollback on saga failure

**Integration Tests:**
- `tests/integration/test_document_ingestion_with_graphiti.py` - End-to-end with Graphiti
- `tests/integration/test_graphiti_rollback_on_saga_failure.py` - Verify Graphiti cleanup

**Baseline Validation:**
- ✅ Run all 121 Enhanced Saga tests (ensure no regression)

**Target:** 10 new tests

---

### Phase 2: JSON Support

**Unit Tests:**
- `tests/unit/test_structured_data_models.py` - Pydantic validation
- `tests/unit/test_json_writer_*.py` - 4 database writers (4 tests)
- `tests/unit/test_graphiti_json_extraction.py` - Graphiti.add_json_episode

**Integration Tests:**
- `tests/integration/test_structured_data_saga.py` - Full saga with JSON
- `tests/integration/test_json_graphiti_rollback.py` - Graphiti rollback for JSON

**Target:** 15 new tests

---

### Phase 3: Staging Lifecycle

*(Same as original plan)*

**Target:** 10 new tests

---

## Rollout Plan

### Week 1: Graphiti Integration

**Day 1-2:** Update extract_entities_activity
- ✅ Replace EntityExtractor with Graphiti
- ✅ Update activity signatures
- ✅ Add Graphiti rollback logic
- ✅ Run unit tests (5 tests)

**Day 3-4:** Integration Testing
- ✅ Run end-to-end document ingestion
- ✅ Test Graphiti rollback on saga failure
- ✅ Validate knowledge graph quality
- ✅ Run integration tests (5 tests)

**Day 5:** Baseline Validation
- ✅ Run all 121 Enhanced Saga tests
- ✅ Verify no regression in saga pattern
- ✅ Deploy to dev environment

---

### Week 2: JSON Support

**Day 1-2:** Database Writers
- ✅ Add write_json_record() to all 4 writers
- ✅ Create Postgres migration (CREATE TABLE structured_data)
- ✅ Create Qdrant collection (apex_structured_data)
- ✅ Run unit tests (10 tests)

**Day 3-4:** Saga + Activities
- ✅ Add write_structured_data_parallel()
- ✅ Add write_structured_data_activity
- ✅ Add extract_entities_from_json_activity
- ✅ Run integration tests (5 tests)

**Day 5:** End-to-End Testing
- ✅ Test with sample Samsara JSON
- ✅ Test with sample Turvo JSON
- ✅ Verify Graphiti extracts entities from JSON
- ✅ Verify all 4 databases written

---

### Week 3: Staging Lifecycle

*(Same as original plan - 5 days)*

---

## Success Criteria

### Phase 1: Graphiti Integration ✅

- extract_entities_activity uses Graphiti.add_document_episode()
- Graphiti episodes rolled back on saga failure
- Knowledge graph visible in Neo4j (entities + relationships)
- All 121 Enhanced Saga tests still pass
- 10 new Graphiti tests pass

### Phase 2: JSON Support ✅

- All 4 database writers have write_json_record()
- write_structured_data_parallel() passes idempotency tests
- write_structured_data_parallel() passes rollback tests
- Graphiti.add_json_episode() extracts entities from JSON
- Sample Samsara/Turvo JSON writes to all 4 databases
- 15 new JSON tests pass

### Phase 3: Staging Lifecycle ✅

*(Same as original plan)*

- 10 new staging tests pass

---

## Risk Assessment

### 🟢 LOW RISK

**Why:**
- ✅ Graphiti integration is additive (EntityExtractor deprecated but not removed yet)
- ✅ All existing 121 Enhanced Saga tests continue passing
- ✅ JSON support is completely new code path (zero impact on documents)
- ✅ Staging lifecycle is standalone service
- ✅ Graphiti rollback ensures no orphaned knowledge graph data

**Mitigation:**
- Feature flag: ENABLE_GRAPHITI_EXTRACTION (can disable and fall back to EntityExtractor)
- Run full Enhanced Saga test suite after every change
- Keep EntityExtractor as fallback for 1 release cycle

---

## Post-Implementation: Unlocks TD-003

**What this enables:**

1. ✅ Graphiti is THE entity extractor - LLM-powered, relationship inference, temporal tracking
2. ✅ JSON natively supported - Graphiti.add_json_episode() + Saga writes
3. ✅ Staging lifecycle ready - Local folders managed properly
4. ✅ Rollback guarantees - Graphiti episodes cleaned up on saga failure

**Next: TD-003 Implementation**
- Replace S3 staging with local folders (use StagingManager)
- Create pull-from-source activities (Samsara API, FrontApp API)
- Route JSON → StructuredDataIngestionWorkflow → write_structured_data_activity
- Route documents → DocumentIngestionWorkflow (now with Graphiti!)

---

## Summary

**Timeline:** 3 weeks (1 week per phase)  
**Tests Added:** 35 tests (10 Graphiti + 15 JSON + 10 staging)  
**Files Created:** 8 new files  
**Files Modified:** 10 files  
**Breaking Changes:** 0 ❌ None (EntityExtractor deprecated, not removed)
