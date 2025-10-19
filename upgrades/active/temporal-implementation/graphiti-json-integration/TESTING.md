# Graphiti + JSON Integration - Testing Guide

**Project:** Apex Memory System - Temporal Implementation
**Document Type:** Test Specifications & Execution Guide
**Total Tests:** 35 new tests (10 + 15 + 10)
**Status:** Ready for Execution
**Created:** 2025-10-19

---

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Phase 1 Tests: Graphiti Integration (10 tests)](#phase-1-tests-graphiti-integration)
3. [Phase 2 Tests: JSON Support (15 tests)](#phase-2-tests-json-support)
4. [Phase 3 Tests: Staging Lifecycle (10 tests)](#phase-3-tests-staging-lifecycle)
5. [Baseline Validation](#baseline-validation)
6. [Test Execution Guide](#test-execution-guide)

---

## Testing Strategy

### Test Pyramid

```
                    ┌─────────────┐
                    │  Load Tests │ (Optional)
                    │   (5 tests) │
                    └─────────────┘
                  ┌───────────────────┐
                  │ Integration Tests │ (8 tests)
                  │ End-to-End Flows  │
                  └───────────────────┘
            ┌─────────────────────────────────┐
            │        Unit Tests               │
            │   (27 tests - isolated units)   │
            └─────────────────────────────────┘
      ┌──────────────────────────────────────────────┐
      │     Baseline Validation (121 tests)         │
      │   Enhanced Saga Pattern (Must Always Pass)  │
      └──────────────────────────────────────────────┘
```

### Test Categories

**Unit Tests (27 tests)**
- Test individual functions/methods in isolation
- Mock external dependencies
- Fast execution (<5 seconds total)

**Integration Tests (8 tests)**
- Test complete workflows end-to-end
- Use real databases (local development)
- Moderate execution time (30-60 seconds total)

**Baseline Validation (121 tests)**
- Enhanced Saga pattern tests (existing)
- MUST pass after every phase
- Regression prevention

**Load Tests (5 tests - optional)**
- Test concurrent workflow execution
- Verify system handles 100+ parallel workflows
- Execution time: 2-5 minutes

---

## Phase 1 Tests: Graphiti Integration

**Goal:** Validate Graphiti LLM entity extraction and rollback functionality

**Total Tests:** 10 (5 unit + 5 unit)

### Test File 1: test_graphiti_extraction_activity.py

**Location:** `apex-memory-system/tests/unit/test_graphiti_extraction_activity.py`

**Tests:** 5

#### TEST 1.1: test_extract_entities_with_graphiti_success

**Purpose:** Verify Graphiti extraction works with valid document

**Setup:**
```python
from apex_memory.temporal.activities.ingestion import extract_entities_activity
from unittest.mock import AsyncMock, patch

parsed_doc = {
    'uuid': 'doc-123',
    'content': 'John Smith works at Acme Corp in Chicago.',
    'metadata': {
        'title': 'Sample Doc',
        'file_type': 'pdf'
    }
}
```

**Execution:**
```python
@pytest.mark.asyncio
async def test_extract_entities_with_graphiti_success():
    # Mock GraphitiService
    with patch('apex_memory.temporal.activities.ingestion.GraphitiService') as mock_graphiti_cls:
        mock_graphiti = AsyncMock()
        mock_graphiti.add_document_episode.return_value = AsyncMock(
            success=True,
            entities_extracted=['John Smith', 'Acme Corp', 'Chicago'],
            edges_created=['edge1', 'edge2']
        )
        mock_graphiti_cls.return_value = mock_graphiti

        result = await extract_entities_activity(parsed_doc)

        assert result['entities'].__len__() == 3
        assert result['graphiti_episode_uuid'] == 'doc-123'
        assert result['edges_created'] == 2
```

**Expected Output:**
```python
{
    'entities': [
        {'name': 'John Smith', 'entity_type': 'graphiti_extracted', 'confidence': 0.9, 'source': 'graphiti'},
        {'name': 'Acme Corp', 'entity_type': 'graphiti_extracted', 'confidence': 0.9, 'source': 'graphiti'},
        {'name': 'Chicago', 'entity_type': 'graphiti_extracted', 'confidence': 0.9, 'source': 'graphiti'}
    ],
    'graphiti_episode_uuid': 'doc-123',
    'edges_created': 2
}
```

**Assertion Checks:**
- ✅ Returns dict (not list)
- ✅ Contains 'entities' key with list
- ✅ Contains 'graphiti_episode_uuid'
- ✅ Entities have correct format
- ✅ Graphiti service called once

---

#### TEST 1.2: test_extract_entities_graphiti_failure

**Purpose:** Verify error handling when Graphiti extraction fails

**Setup:**
```python
parsed_doc = {
    'uuid': 'doc-456',
    'content': 'Test content',
    'metadata': {'title': 'Test', 'file_type': 'pdf'}
}
```

**Execution:**
```python
@pytest.mark.asyncio
async def test_extract_entities_graphiti_failure():
    with patch('apex_memory.temporal.activities.ingestion.GraphitiService') as mock_graphiti_cls:
        mock_graphiti = AsyncMock()
        mock_graphiti.add_document_episode.return_value = AsyncMock(
            success=False,
            error='LLM timeout'
        )
        mock_graphiti_cls.return_value = mock_graphiti

        with pytest.raises(ApplicationError) as exc_info:
            await extract_entities_activity(parsed_doc)

        assert 'Graphiti extraction failed' in str(exc_info.value)
        assert exc_info.value.non_retryable is True
```

**Expected Behavior:**
- ✅ Raises ApplicationError
- ✅ Error message includes 'Graphiti extraction failed'
- ✅ Error is non-retryable
- ✅ Metrics record failure

---

#### TEST 1.3: test_extract_entities_format_conversion

**Purpose:** Verify Graphiti entities converted to correct dict format

**Setup:**
```python
parsed_doc = {
    'uuid': 'doc-789',
    'content': 'Alice and Bob met in Paris.',
    'metadata': {'title': 'Meeting Notes', 'file_type': 'docx'}
}
```

**Execution:**
```python
@pytest.mark.asyncio
async def test_extract_entities_format_conversion():
    with patch('apex_memory.temporal.activities.ingestion.GraphitiService') as mock_graphiti_cls:
        mock_graphiti = AsyncMock()
        mock_graphiti.add_document_episode.return_value = AsyncMock(
            success=True,
            entities_extracted=['Alice', 'Bob', 'Paris'],
            edges_created=[]
        )
        mock_graphiti_cls.return_value = mock_graphiti

        result = await extract_entities_activity(parsed_doc)

        # Verify format
        for entity in result['entities']:
            assert 'name' in entity
            assert 'entity_type' in entity
            assert 'confidence' in entity
            assert 'source' in entity
            assert entity['entity_type'] == 'graphiti_extracted'
            assert entity['confidence'] == 0.9
            assert entity['source'] == 'graphiti'
```

**Expected Output:**
- ✅ Each entity has required fields
- ✅ entity_type is 'graphiti_extracted'
- ✅ confidence is 0.9
- ✅ source is 'graphiti'

---

#### TEST 1.4: test_extract_entities_episode_uuid_tracking

**Purpose:** Verify graphiti_episode_uuid is correctly tracked for rollback

**Setup:**
```python
parsed_doc = {
    'uuid': 'doc-unique-123',
    'content': 'Test',
    'metadata': {'title': 'Test', 'file_type': 'pdf'}
}
```

**Execution:**
```python
@pytest.mark.asyncio
async def test_extract_entities_episode_uuid_tracking():
    with patch('apex_memory.temporal.activities.ingestion.GraphitiService') as mock_graphiti_cls:
        mock_graphiti = AsyncMock()
        mock_graphiti.add_document_episode.return_value = AsyncMock(
            success=True,
            entities_extracted=['Entity1'],
            edges_created=[]
        )
        mock_graphiti_cls.return_value = mock_graphiti

        result = await extract_entities_activity(parsed_doc)

        # Verify UUID tracking
        assert result['graphiti_episode_uuid'] == 'doc-unique-123'

        # Verify add_document_episode was called with correct UUID
        mock_graphiti.add_document_episode.assert_called_once()
        call_args = mock_graphiti.add_document_episode.call_args
        assert call_args.kwargs['document_uuid'] == 'doc-unique-123'
```

**Expected Behavior:**
- ✅ graphiti_episode_uuid matches document UUID
- ✅ Graphiti called with correct UUID
- ✅ UUID available for rollback

---

#### TEST 1.5: test_graphiti_client_initialization

**Purpose:** Verify GraphitiService initialized with correct credentials

**Setup:**
```python
from apex_memory.config.settings import Settings

parsed_doc = {
    'uuid': 'doc-init-test',
    'content': 'Test',
    'metadata': {'title': 'Test', 'file_type': 'pdf'}
}
```

**Execution:**
```python
@pytest.mark.asyncio
async def test_graphiti_client_initialization():
    with patch('apex_memory.temporal.activities.ingestion.GraphitiService') as mock_graphiti_cls:
        mock_graphiti = AsyncMock()
        mock_graphiti.add_document_episode.return_value = AsyncMock(
            success=True,
            entities_extracted=[],
            edges_created=[]
        )
        mock_graphiti_cls.return_value = mock_graphiti

        await extract_entities_activity(parsed_doc)

        # Verify GraphitiService was initialized with correct parameters
        mock_graphiti_cls.assert_called_once()
        call_args = mock_graphiti_cls.call_args

        assert 'neo4j_uri' in call_args.kwargs
        assert 'neo4j_user' in call_args.kwargs
        assert 'neo4j_password' in call_args.kwargs
        assert 'openai_api_key' in call_args.kwargs
```

**Expected Behavior:**
- ✅ GraphitiService initialized once
- ✅ All required credentials passed
- ✅ Settings loaded correctly

---

### Test File 2: test_graphiti_rollback.py

**Location:** `apex-memory-system/tests/unit/test_graphiti_rollback.py`

**Tests:** 5

#### TEST 1.6: test_rollback_on_saga_failure

**Purpose:** Verify Graphiti episode rolled back when Saga fails

**Setup:**
```python
from apex_memory.temporal.activities.ingestion import write_to_databases_activity

entities = {
    'entities': [{'name': 'Entity1'}],
    'graphiti_episode_uuid': 'doc-rollback-test'
}
```

**Execution:**
```python
@pytest.mark.asyncio
async def test_rollback_on_saga_failure():
    with patch('apex_memory.temporal.activities.ingestion.DatabaseWriteOrchestrator') as mock_orchestrator_cls:
        with patch('apex_memory.temporal.activities.ingestion.rollback_graphiti_episode') as mock_rollback:
            # Mock Saga failure
            mock_orchestrator = AsyncMock()
            mock_orchestrator.write_document_parallel.return_value = AsyncMock(
                all_success=False,
                neo4j_success=False,
                model_dump=lambda: {'status': 'failed'}
            )
            mock_orchestrator_cls.return_value = mock_orchestrator

            parsed_doc = {'uuid': 'doc-test', 'chunks': []}
            embeddings = {'document_embedding': [0.1] * 1536}

            result = await write_to_databases_activity(parsed_doc, entities, embeddings)

            # Verify rollback was called
            mock_rollback.assert_called_once_with('doc-rollback-test')
```

**Expected Behavior:**
- ✅ rollback_graphiti_episode called once
- ✅ Called with correct episode UUID
- ✅ Activity completes (doesn't raise)
- ✅ Metrics record rollback

---

#### TEST 1.7: test_no_rollback_on_saga_success

**Purpose:** Verify Graphiti episode NOT rolled back when Saga succeeds

**Setup:** Same as above

**Execution:**
```python
@pytest.mark.asyncio
async def test_no_rollback_on_saga_success():
    with patch('apex_memory.temporal.activities.ingestion.DatabaseWriteOrchestrator') as mock_orchestrator_cls:
        with patch('apex_memory.temporal.activities.ingestion.rollback_graphiti_episode') as mock_rollback:
            # Mock Saga success
            mock_orchestrator = AsyncMock()
            mock_orchestrator.write_document_parallel.return_value = AsyncMock(
                all_success=True,
                model_dump=lambda: {'status': 'success'}
            )
            mock_orchestrator_cls.return_value = mock_orchestrator

            entities = {
                'entities': [{'name': 'Entity1'}],
                'graphiti_episode_uuid': 'doc-no-rollback'
            }

            await write_to_databases_activity({'uuid': 'doc', 'chunks': []}, entities, {'document_embedding': [0.1] * 1536})

            # Verify rollback NOT called
            mock_rollback.assert_not_called()
```

**Expected Behavior:**
- ✅ rollback_graphiti_episode NOT called
- ✅ Saga completes successfully
- ✅ Metrics record success

---

#### TEST 1.8: test_rollback_graphiti_episode_success

**Purpose:** Verify rollback_graphiti_episode helper function works

**Setup:**
```python
from apex_memory.temporal.activities.ingestion import rollback_graphiti_episode

episode_uuid = 'test-episode-123'
```

**Execution:**
```python
@pytest.mark.asyncio
async def test_rollback_graphiti_episode_success():
    with patch('apex_memory.temporal.activities.ingestion.GraphitiService') as mock_graphiti_cls:
        mock_graphiti = AsyncMock()
        mock_graphiti.remove_episode.return_value = True  # Success
        mock_graphiti_cls.return_value = mock_graphiti

        await rollback_graphiti_episode(episode_uuid)

        # Verify remove_episode called
        mock_graphiti.remove_episode.assert_called_once_with(episode_uuid)
```

**Expected Behavior:**
- ✅ GraphitiService.remove_episode called
- ✅ Called with correct UUID
- ✅ Logs success message
- ✅ Metrics record rollback success

---

#### TEST 1.9: test_rollback_graphiti_episode_failure

**Purpose:** Verify rollback failure logged but doesn't raise

**Setup:** Same as above

**Execution:**
```python
@pytest.mark.asyncio
async def test_rollback_graphiti_episode_failure():
    with patch('apex_memory.temporal.activities.ingestion.GraphitiService') as mock_graphiti_cls:
        mock_graphiti = AsyncMock()
        mock_graphiti.remove_episode.return_value = False  # Failure
        mock_graphiti_cls.return_value = mock_graphiti

        # Should not raise, just log error
        await rollback_graphiti_episode('test-uuid')

        # Verify error logged
        # TODO: Verify DLQ sending (if implemented)
```

**Expected Behavior:**
- ✅ Does not raise exception
- ✅ Logs error message
- ✅ Metrics record rollback failure
- ✅ Sends to DLQ for manual cleanup (TODO)

---

#### TEST 1.10: test_orphaned_episode_cleanup

**Purpose:** Verify orphaned episodes don't remain in Neo4j

**Setup:**
```python
# Integration test - requires real Neo4j
```

**Execution:**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_orphaned_episode_cleanup():
    from neo4j import GraphDatabase
    from apex_memory.config.settings import Settings

    settings = Settings()

    # Create a Graphiti episode
    graphiti = GraphitiService(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
    )

    result = await graphiti.add_document_episode(
        document_uuid='orphan-test',
        document_title='Test',
        document_content='Test content',
        document_type='test'
    )

    assert result.success

    # Rollback the episode
    await rollback_graphiti_episode('orphan-test')

    # Verify episode removed from Neo4j
    driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
    with driver.session() as session:
        result = session.run("MATCH (e:Episode {uuid: $uuid}) RETURN count(e)", uuid='orphan-test')
        count = result.single()[0]
        assert count == 0, "Episode should be removed from Neo4j"

    driver.close()
```

**Expected Behavior:**
- ✅ Episode created in Neo4j
- ✅ Rollback removes episode
- ✅ Neo4j query confirms deletion
- ✅ No orphaned data

---

**Phase 1 Test Summary:**
- Total: 10 tests (5 + 5)
- Unit: 9 tests
- Integration: 1 test
- Execution time: ~10 seconds
- Dependencies: GraphitiService, Neo4j (for integration test)

**Run Phase 1 Tests:**
```bash
pytest tests/unit/test_graphiti_extraction_activity.py -v
pytest tests/unit/test_graphiti_rollback.py -v
```

---

## Phase 2 Tests: JSON Support

**Goal:** Validate JSON ingestion, database writers, and Saga orchestration

**Total Tests:** 15 (3 + 12)

### Test File 3: test_structured_data_models.py

**Location:** `apex-memory-system/tests/unit/test_structured_data_models.py`

**Tests:** 3

#### TEST 2.1: test_structured_data_model_validation

**Purpose:** Verify StructuredData Pydantic model validation

**Execution:**
```python
from apex_memory.models.structured_data import StructuredData, StructuredDataMetadata, StructuredDataType

def test_structured_data_model_validation():
    data = StructuredData(
        uuid='550e8400-e29b-41d4-a716-446655440000',
        metadata=StructuredDataMetadata(
            data_id='SHIP-12345',
            source='turvo',
            data_type=StructuredDataType.SHIPMENT
        ),
        raw_json={'shipment_id': 'SHIP-12345', 'status': 'in_transit'},
        text_representation='Shipment SHIP-12345, status: in_transit'
    )

    assert data.uuid == '550e8400-e29b-41d4-a716-446655440000'
    assert data.metadata.data_id == 'SHIP-12345'
    assert data.metadata.source == 'turvo'
    assert data.metadata.data_type == StructuredDataType.SHIPMENT
    assert data.raw_json['status'] == 'in_transit'
```

**Expected Behavior:**
- ✅ Model validates correctly
- ✅ All fields accessible
- ✅ Enum type works

---

#### TEST 2.2: test_structured_data_serialization

**Purpose:** Verify StructuredData serializes to/from JSON

**Execution:**
```python
def test_structured_data_serialization():
    data = StructuredData(...)  # Same as above

    # Serialize to dict
    data_dict = data.model_dump()
    assert 'uuid' in data_dict
    assert 'metadata' in data_dict
    assert 'raw_json' in data_dict

    # Serialize to JSON string
    json_str = data.model_dump_json()
    assert isinstance(json_str, str)

    # Deserialize from dict
    data2 = StructuredData(**data_dict)
    assert data2.uuid == data.uuid

    # Deserialize from JSON
    data3 = StructuredData.model_validate_json(json_str)
    assert data3.uuid == data.uuid
```

**Expected Behavior:**
- ✅ model_dump() works
- ✅ model_dump_json() works
- ✅ Round-trip serialization preserves data

---

#### TEST 2.3: test_structured_data_enum_validation

**Purpose:** Verify StructuredDataType enum validation

**Execution:**
```python
def test_structured_data_enum_validation():
    # Valid enum value
    data = StructuredData(
        uuid='test',
        metadata=StructuredDataMetadata(
            data_id='test',
            source='test',
            data_type=StructuredDataType.GPS_EVENT
        ),
        raw_json={},
        text_representation='test'
    )
    assert data.metadata.data_type == StructuredDataType.GPS_EVENT

    # Invalid enum value
    with pytest.raises(ValidationError):
        StructuredData(
            uuid='test',
            metadata=StructuredDataMetadata(
                data_id='test',
                source='test',
                data_type='invalid_type'  # Invalid
            ),
            raw_json={},
            text_representation='test'
        )
```

**Expected Behavior:**
- ✅ Valid enum values accepted
- ✅ Invalid enum values raise ValidationError

---

### Test Files 4-7: Database Writer Tests (12 tests)

**Locations:**
- `tests/unit/test_json_writer_postgres.py` (3 tests)
- `tests/unit/test_json_writer_qdrant.py` (3 tests)
- `tests/unit/test_json_writer_neo4j.py` (3 tests)
- `tests/unit/test_json_writer_redis.py` (3 tests)

**Pattern (same for all 4 writers):**

#### TEST 2.4-2.6: PostgreSQL Writer Tests

**File:** `tests/unit/test_json_writer_postgres.py`

```python
@pytest.mark.asyncio
async def test_postgres_write_json_record_success():
    """Test successful JSON write to PostgreSQL."""
    # Mock asyncpg pool
    # Call write_json_record()
    # Verify query executed with correct parameters
    # Assert WriteResult.success is True

@pytest.mark.asyncio
async def test_postgres_write_json_record_failure():
    """Test JSON write failure handling."""
    # Mock asyncpg raising exception
    # Call write_json_record()
    # Verify error logged
    # Assert WriteResult.success is False

@pytest.mark.asyncio
async def test_postgres_write_json_record_idempotency():
    """Test ON CONFLICT DO NOTHING for duplicate UUIDs."""
    # Call write_json_record() twice with same UUID
    # Verify only one row inserted
```

#### TEST 2.7-2.9: Qdrant Writer Tests

**File:** `tests/unit/test_json_writer_qdrant.py`

```python
@pytest.mark.asyncio
async def test_qdrant_write_json_record_success():
    """Test successful JSON write to Qdrant."""
    # Mock qdrant_client
    # Call write_json_record()
    # Verify upsert called with correct collection
    # Assert WriteResult.success is True

@pytest.mark.asyncio
async def test_qdrant_write_json_record_collection_creation():
    """Test automatic collection creation."""
    # Mock collection doesn't exist
    # Call write_json_record()
    # Verify create_collection called
    # Verify apex_structured_data collection created

@pytest.mark.asyncio
async def test_qdrant_write_json_record_payload_truncation():
    """Test text_representation truncated to 500 chars."""
    # Create StructuredData with long text (1000 chars)
    # Call write_json_record()
    # Verify payload text is 500 chars max
```

#### TEST 2.10-2.12: Neo4j Writer Tests

**File:** `tests/unit/test_json_writer_neo4j.py`

```python
@pytest.mark.asyncio
async def test_neo4j_write_json_record_success():
    """Test successful JSON write to Neo4j."""
    # Mock neo4j driver
    # Call write_json_record()
    # Verify MERGE query executed
    # Assert WriteResult.success is True

@pytest.mark.asyncio
async def test_neo4j_write_json_record_entity_linking():
    """Test entities linked to StructuredData node."""
    # Call write_json_record() with 3 entities
    # Verify 3 CONTAINS_ENTITY relationships created
    # Verify entity queries executed

@pytest.mark.asyncio
async def test_neo4j_write_json_record_idempotency():
    """Test MERGE ensures idempotency."""
    # Call write_json_record() twice
    # Verify only one node created (MERGE behavior)
```

#### TEST 2.13-2.15: Redis Writer Tests

**File:** `tests/unit/test_json_writer_redis.py`

```python
@pytest.mark.asyncio
async def test_redis_write_json_record_success():
    """Test successful JSON write to Redis."""
    # Mock redis client
    # Call write_json_record()
    # Verify set() called with correct key
    # Assert WriteResult.success is True

@pytest.mark.asyncio
async def test_redis_write_json_record_ttl():
    """Test 24hr TTL set correctly."""
    # Call write_json_record()
    # Verify setex() called with ex=86400
    # Verify TTL is 24 hours

@pytest.mark.asyncio
async def test_redis_write_json_record_key_format():
    """Test key format is structured_data:{uuid}."""
    # Call write_json_record()
    # Verify key is 'structured_data:{uuid}'
```

---

**Phase 2 Test Summary:**
- Total: 15 tests (3 models + 12 writers)
- All unit tests
- Execution time: ~15 seconds
- Dependencies: Pydantic, asyncpg, qdrant-client, neo4j, redis

**Run Phase 2 Tests:**
```bash
pytest tests/unit/test_structured_data_models.py -v
pytest tests/unit/test_json_writer_*.py -v
```

---

## Phase 3 Tests: Staging Lifecycle

**Goal:** Validate local staging, cleanup, and disk management

**Total Tests:** 10 (7 unit + 3 integration)

### Test File 8: test_pull_and_stage_activity.py

**Location:** `apex-memory-system/tests/unit/test_pull_and_stage_activity.py`

**Tests:** 3

#### TEST 3.1: test_pull_and_stage_frontapp

**Purpose:** Test FrontApp API document staging

**Execution:**
```python
@pytest.mark.asyncio
async def test_pull_and_stage_frontapp():
    # Mock FrontApp API client
    # Call pull_and_stage_document_activity()
    # Verify file written to /tmp/apex-staging/frontapp/{doc_id}/
    # Assert staging path returned
```

#### TEST 3.2: test_pull_and_stage_local_file

**Purpose:** Test local file move to staging

**Execution:**
```python
@pytest.mark.asyncio
async def test_pull_and_stage_local_file():
    # Create temp file
    # Call pull_and_stage_document_activity(source='local_upload')
    # Verify file copied to staging
    # Assert original file still exists
```

#### TEST 3.3: test_pull_and_stage_http_download

**Purpose:** Test HTTP download to staging

**Execution:**
```python
@pytest.mark.asyncio
async def test_pull_and_stage_http_download():
    # Mock httpx client
    # Call pull_and_stage_document_activity(source='http')
    # Verify file downloaded to staging
    # Verify metrics emitted
```

---

### Test File 9: test_staging_manager.py

**Location:** `apex-memory-system/tests/unit/test_staging_manager.py`

**Tests:** 5

#### TEST 3.4: test_create_staging_dir

**Purpose:** Test staging directory creation

**Execution:**
```python
def test_create_staging_dir():
    manager = StagingManager()
    staging_dir = manager.create_staging_dir('frontapp', 'doc-123')

    assert staging_dir.exists()
    assert str(staging_dir).endswith('frontapp/doc-123')
```

#### TEST 3.5: test_cleanup_staging_dir

**Purpose:** Test staging directory removal

**Execution:**
```python
def test_cleanup_staging_dir():
    manager = StagingManager()
    staging_dir = manager.create_staging_dir('test', 'doc-456')

    # Create dummy file
    (staging_dir / 'test.pdf').write_text('test')

    # Cleanup
    success = manager.cleanup_staging_dir(str(staging_dir / 'test.pdf'))

    assert success
    assert not staging_dir.exists()
```

#### TEST 3.6: test_cleanup_old_failed_ingestions

**Purpose:** Test old folder cleanup (24hr retention)

**Execution:**
```python
def test_cleanup_old_failed_ingestions():
    manager = StagingManager()

    # Create old staging dir (modify timestamp to 25 hours ago)
    old_dir = manager.create_staging_dir('test', 'old-doc')
    os.utime(old_dir, (time.time() - 90000, time.time() - 90000))  # 25 hours

    # Cleanup
    cleaned = manager.cleanup_old_failed_ingestions()

    assert cleaned == 1
    assert not old_dir.exists()
```

#### TEST 3.7: test_get_disk_usage

**Purpose:** Test disk usage calculation

**Execution:**
```python
def test_get_disk_usage():
    manager = StagingManager()

    # Create staging with known size
    staging_dir = manager.create_staging_dir('test', 'size-test')
    (staging_dir / 'file.txt').write_bytes(b'x' * 1000)  # 1000 bytes

    usage = manager.get_disk_usage()
    assert usage >= 1000
```

#### TEST 3.8: test_is_disk_full

**Purpose:** Test disk full detection

**Execution:**
```python
def test_is_disk_full():
    # Set max size to 1 byte
    settings = Settings(staging_max_size_gb=0.000000001)  # ~1 byte
    manager = StagingManager(settings)

    # Create file larger than limit
    staging_dir = manager.create_staging_dir('test', 'full-test')
    (staging_dir / 'big.txt').write_bytes(b'x' * 1000)

    assert manager.is_disk_full()
```

---

### Test File 10: test_cleanup_staging_activity.py

**Location:** `apex-memory-system/tests/unit/test_cleanup_staging_activity.py`

**Tests:** 2

#### TEST 3.9: test_cleanup_staging_activity_success

**Purpose:** Test cleanup activity execution

**Execution:**
```python
@pytest.mark.asyncio
async def test_cleanup_staging_activity_success():
    from apex_memory.temporal.activities.ingestion import cleanup_staging_activity

    # Create staging dir
    staging_dir = Path('/tmp/apex-staging/test/cleanup-test')
    staging_dir.mkdir(parents=True)
    staging_file = staging_dir / 'test.pdf'
    staging_file.write_text('test')

    # Cleanup
    await cleanup_staging_activity(str(staging_file))

    # Verify removed
    assert not staging_dir.exists()
```

#### TEST 3.10: test_cleanup_staging_activity_already_removed

**Purpose:** Test cleanup when folder already removed

**Execution:**
```python
@pytest.mark.asyncio
async def test_cleanup_staging_activity_already_removed():
    # Call cleanup on non-existent path
    await cleanup_staging_activity('/tmp/nonexistent/path')

    # Should complete without error
    # (Activity logs warning but doesn't raise)
```

---

**Phase 3 Test Summary:**
- Total: 10 tests (7 unit + 3 integration)
- Execution time: ~10 seconds
- Dependencies: pathlib, StagingManager

**Run Phase 3 Tests:**
```bash
pytest tests/unit/test_pull_and_stage_activity.py -v
pytest tests/unit/test_staging_manager.py -v
pytest tests/unit/test_cleanup_staging_activity.py -v
```

---

## Baseline Validation

**Purpose:** Ensure Enhanced Saga pattern (121 tests) still passes after every phase

### Enhanced Saga Test Suite

**Location:** `apex-memory-system/tests/`

**Tests:** 121 existing tests

**Categories:**
- Unit tests for database writers (40 tests)
- Saga orchestrator tests (30 tests)
- Idempotency tests (20 tests)
- Distributed lock tests (15 tests)
- Rollback tests (16 tests)

**Run Baseline:**
```bash
cd apex-memory-system
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v
# Expected: 121/121 tests pass
```

**Critical Checkpoints:**
- ✅ After Phase 1: 131 tests pass (121 + 10)
- ✅ After Phase 2: 146 tests pass (121 + 10 + 15)
- ✅ After Phase 3: 156 tests pass (121 + 10 + 15 + 10)

---

## Test Execution Guide

### Quick Reference

```bash
# Phase 1 tests (10 tests)
pytest tests/unit/test_graphiti_extraction_activity.py -v
pytest tests/unit/test_graphiti_rollback.py -v

# Phase 2 tests (15 tests)
pytest tests/unit/test_structured_data_models.py -v
pytest tests/unit/test_json_writer_*.py -v

# Phase 3 tests (10 tests)
pytest tests/unit/test_pull_and_stage_activity.py -v
pytest tests/unit/test_staging_manager.py -v
pytest tests/unit/test_cleanup_staging_activity.py -v

# Baseline validation (121 tests)
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v

# All tests (156 tests)
pytest tests/ --ignore=tests/load/ -v
```

### Test Execution Workflow

**After implementing each phase:**

```bash
# 1. Run new phase tests
pytest tests/unit/test_[phase]_*.py -v

# 2. Run baseline validation
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v

# 3. If baseline passes, run integration tests
pytest tests/integration/ -v

# 4. If all pass, proceed to next phase
```

### Continuous Testing

**During development:**

```bash
# Watch mode (re-run on file changes)
pytest-watch tests/unit/test_graphiti_*.py -v

# Run specific test
pytest tests/unit/test_graphiti_extraction_activity.py::test_extract_entities_with_graphiti_success -v

# Run with coverage
pytest tests/unit/ --cov=apex_memory --cov-report=html
```

### Test Markers

```python
# Mark integration tests
@pytest.mark.integration

# Mark slow tests
@pytest.mark.slow

# Mark load tests
@pytest.mark.load

# Run only unit tests
pytest -m "not integration and not slow and not load" -v
```

---

## Success Criteria

### Phase 1 Success
- ✅ 10/10 Graphiti tests pass
- ✅ 121/121 baseline tests still pass
- ✅ Total: 131 tests pass

### Phase 2 Success
- ✅ 15/15 JSON tests pass
- ✅ 131/131 previous tests still pass
- ✅ Total: 146 tests pass

### Phase 3 Success
- ✅ 10/10 Staging tests pass
- ✅ 146/146 previous tests still pass
- ✅ Total: 156 tests pass

### Final Success
- ✅ All 156 tests pass (121 + 35)
- ✅ Test coverage >80% for new code
- ✅ No flaky tests
- ✅ All tests pass in CI/CD pipeline

---

**Document Version:** 1.0
**Last Updated:** 2025-10-19
**Author:** Claude Code
