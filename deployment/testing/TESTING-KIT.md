# Apex Memory System - Comprehensive Testing Kit

**Purpose:** Pre-deployment validation to identify internal failures and integration issues
**Author:** Claude Code (System Analysis)
**Date:** 2025-10-20
**Status:** Active Testing Reference

---

## Table of Contents

1. [Testing Strategy Overview](#testing-strategy-overview)
2. [Pre-Flight Validation](#pre-flight-validation)
3. [Layer 1: Database Writers](#layer-1-database-writers)
4. [Layer 2: Services](#layer-2-services)
5. [Layer 3: Temporal Activities](#layer-3-temporal-activities)
6. [Layer 4: Temporal Workflows](#layer-4-temporal-workflows)
7. [Layer 5: API Endpoints](#layer-5-api-endpoints)
8. [Layer 6: Query Router](#layer-6-query-router)
9. [Critical Integration Points](#critical-integration-points)
10. [Known Issues & Gotchas](#known-issues--gotchas)
11. [Debugging Procedures](#debugging-procedures)
12. [Load & Chaos Testing](#load--chaos-testing)
13. [Deployment Readiness Checklist](#deployment-readiness-checklist)
14. [Quick Reference Commands](#quick-reference-commands)

---

## Testing Strategy Overview

### Philosophy

**Test from Bottom-Up:**
- Start with foundations (database connections)
- Build up to services (business logic)
- Validate orchestration (Temporal workflows)
- Verify interfaces (API endpoints)
- Stress test integration (E2E scenarios)

**Test Categories:**

1. **Unit Tests** - Individual functions/classes (mocked dependencies)
2. **Integration Tests** - Component interactions (real dependencies)
3. **E2E Tests** - Full workflows (API → Temporal → Databases)
4. **Load Tests** - Concurrent operations (10+ docs/sec)
5. **Chaos Tests** - Failure scenarios (DB down, network partitions)

### Success Criteria for Deployment

✅ **ALL baseline tests passing** (121 Enhanced Saga + section tests)
✅ **Zero critical errors** in logs during test runs
✅ **Metrics recording** correctly (27 Temporal metrics)
✅ **Grafana dashboard** functional and accurate
✅ **Alerts firing** when triggered
✅ **No orphaned resources** (staging files, Graphiti episodes)
✅ **Performance targets met** (10+ docs/sec, <1s queries)
✅ **Cache hit rate** >60% for repeat queries

### Known Limitations (Acceptable)

⚠️ **Staging TTL cleanup** - Manual cleanup may be needed for failed tests
⚠️ **Graphiti episode orphans** - Documented in DLQ for manual review
⚠️ **Circuit breaker state** - May need manual reset between test runs
⚠️ **Redis cache pollution** - Flush Redis between major test suites

---

## Pre-Flight Validation

**Run these checks BEFORE starting comprehensive testing.**

### 1. Database Health Check

```bash
# Check all 4 databases are running
docker ps | grep -E "postgres|neo4j|qdrant|redis"

# Expected: 4 containers RUNNING
```

**Validation:**
- PostgreSQL container: `apex_memory_postgres` (port 5432)
- Neo4j container: `apex_memory_neo4j` (ports 7474, 7687)
- Qdrant container: `apex_memory_qdrant` (port 6333)
- Redis container: `apex_memory_redis` (port 6379)

### 2. Database Connectivity

```bash
# PostgreSQL
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT 1"

# Redis
redis-cli ping
# Expected: PONG

# Neo4j (via browser)
# Open: http://localhost:7474
# Login: neo4j / apexmemory2024

# Qdrant (via API)
curl http://localhost:6333/collections
```

**Expected Results:**
- PostgreSQL: Returns `1`
- Redis: Returns `PONG`
- Neo4j: Login successful
- Qdrant: Returns JSON list of collections

**If Failing:**
```bash
# Restart all services
cd apex-memory-system/docker
docker-compose down
docker-compose up -d

# Wait 30 seconds for initialization
sleep 30

# Retry connectivity checks
```

### 3. Temporal Server Health

```bash
# Check Temporal server running
temporal server health

# Expected: "temporal server is healthy"
```

**If Failing:**
```bash
# Start Temporal dev server
temporal server start-dev

# In separate terminal, verify:
temporal server health
```

### 4. Worker Process Check

```bash
# Check if worker is running
ps aux | grep "dev_worker"

# Or start worker manually
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python src/apex_memory/temporal/workers/dev_worker.py
```

**Expected Output:**
```
Worker started successfully
Polling task queue: apex-ingestion-queue
```

### 5. Environment Variables

```bash
# Check critical env vars are set
cd apex-memory-system

# Check .env file exists
ls -la .env

# Verify key variables
cat .env | grep -E "OPENAI_API_KEY|NEO4J_PASSWORD|POSTGRES_PASSWORD"
```

**Required Variables:**
- `OPENAI_API_KEY` - For embeddings and Graphiti
- `NEO4J_PASSWORD` - Neo4j authentication
- `POSTGRES_PASSWORD` - PostgreSQL authentication
- `TEMPORAL_HOST` - Temporal server address (default: localhost:7233)

### 6. Staging Directory

```bash
# Check staging directory exists and is writable
ls -ld /tmp/apex-staging

# If missing, create it
mkdir -p /tmp/apex-staging
chmod 755 /tmp/apex-staging

# Clean old staging files (optional)
find /tmp/apex-staging -type f -mtime +1 -delete
```

### 7. API Server Health

```bash
# Check API server is running
curl http://localhost:8000/api/v1/health

# Expected: {"status": "healthy", "databases": {...}}
```

**If API Not Running:**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH uvicorn apex_memory.main:app --reload --port 8000
```

### Pre-Flight Checklist

- [ ] PostgreSQL: ✓ Running, ✓ Connectable
- [ ] Neo4j: ✓ Running, ✓ Connectable
- [ ] Qdrant: ✓ Running, ✓ Connectable
- [ ] Redis: ✓ Running, ✓ Connectable
- [ ] Temporal Server: ✓ Healthy
- [ ] Temporal Worker: ✓ Running
- [ ] Environment: ✓ All vars set
- [ ] Staging: ✓ Directory exists, writable
- [ ] API: ✓ Responds to /health

**If ANY check fails, STOP and fix before proceeding.**

---

## Layer 1: Database Writers

**Goal:** Validate each database writer works independently.

### PostgresWriter Tests

**Location:** `apex-memory-system/src/apex_memory/database/postgres_writer.py`

**Test 1: Connection Pool**
```bash
cd apex-memory-system
python3 -c "
from apex_memory.database.postgres_writer import PostgresWriter
writer = PostgresWriter()
print('✅ PostgresWriter initialized')
writer.close()
print('✅ Connection pool closed')
"
```

**Expected:** Both ✅ messages, no errors

**Test 2: Write Document**
```bash
cd apex-memory-system
python3 << 'EOF'
from apex_memory.database.postgres_writer import PostgresWriter
from apex_memory.models.document import ParsedDocument, DocumentMetadata
from datetime import datetime
import uuid

writer = PostgresWriter()

# Create test document
metadata = DocumentMetadata(
    title="Test Document",
    author="Test User",
    file_type="txt",
    file_size=1024,
    source_path="/tmp/test.txt",
    created_date=datetime.utcnow()
)

doc = ParsedDocument(
    uuid=str(uuid.uuid4()),
    metadata=metadata,
    content="Test content for PostgreSQL write",
    chunks=["Chunk 1", "Chunk 2"]
)

# Test write
embedding = [0.1] * 1536  # Mock embedding
success = writer.write_document(doc, embedding)

if success:
    print("✅ Document written to PostgreSQL")
else:
    print("❌ PostgreSQL write failed")

writer.close()
EOF
```

**Expected:** `✅ Document written to PostgreSQL`

**Test 3: Write Chunks**
```bash
cd apex-memory-system
python3 << 'EOF'
from apex_memory.database.postgres_writer import PostgresWriter
import uuid

writer = PostgresWriter()

doc_uuid = str(uuid.uuid4())
chunks = ["Test chunk 1", "Test chunk 2", "Test chunk 3"]
embeddings = [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]

success = writer.write_chunks(doc_uuid, chunks, embeddings)

if success:
    print("✅ Chunks written to PostgreSQL")
else:
    print("❌ Chunk write failed")

writer.close()
EOF
```

**Expected:** `✅ Chunks written to PostgreSQL`

**Common Failures:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `psycopg2.OperationalError` | PostgreSQL not running | `docker-compose up -d postgres` |
| `FATAL: password authentication failed` | Wrong password in .env | Update `POSTGRES_PASSWORD` |
| `pgvector extension not found` | Missing extension | Run `CREATE EXTENSION vector;` in psql |
| `relation "documents" does not exist` | Schema not initialized | Run migrations (see setup docs) |

---

### Neo4jWriter Tests

**Location:** `apex-memory-system/src/apex_memory/database/neo4j_writer.py`

**Test 1: Connection**
```bash
cd apex-memory-system
python3 -c "
from apex_memory.database.neo4j_writer import Neo4jWriter
writer = Neo4jWriter()
print('✅ Neo4jWriter initialized')
writer.close()
print('✅ Neo4j connection closed')
"
```

**Test 2: Write Document Node**
```bash
cd apex-memory-system
python3 << 'EOF'
from apex_memory.database.neo4j_writer import Neo4jWriter
from apex_memory.models.document import ParsedDocument, DocumentMetadata
from datetime import datetime
import uuid

writer = Neo4jWriter()

metadata = DocumentMetadata(
    title="Test Graph Document",
    author="Test User",
    file_type="txt",
    file_size=2048,
    source_path="/tmp/graph_test.txt"
)

doc = ParsedDocument(
    uuid=str(uuid.uuid4()),
    metadata=metadata,
    content="Graph test content",
    chunks=["Graph chunk 1"]
)

success = writer.write_document(doc)

if success:
    print("✅ Document node created in Neo4j")
else:
    print("❌ Neo4j write failed")

writer.close()
EOF
```

**Test 3: Write Entity Relationships**
```bash
cd apex-memory-system
python3 << 'EOF'
from apex_memory.database.neo4j_writer import Neo4jWriter
import uuid

writer = Neo4jWriter()

doc_uuid = str(uuid.uuid4())
entities = [
    {"name": "ACME Corporation", "entity_type": "Customer"},
    {"name": "Invoice INV-001", "entity_type": "Invoice"}
]

success = writer.write_entities(doc_uuid, entities)

if success:
    print("✅ Entities and relationships created in Neo4j")
else:
    print("❌ Entity write failed")

writer.close()
EOF
```

**Common Failures:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ServiceUnavailable` | Neo4j not running | `docker-compose up -d neo4j` |
| `AuthError` | Wrong credentials | Update `NEO4J_PASSWORD` in .env |
| `ClientError: [Constraint]` | Duplicate entities | Expected (ON MERGE behavior) |

---

### QdrantWriter Tests

**Location:** `apex-memory-system/src/apex_memory/database/qdrant_writer.py`

**Test 1: Collection Exists**
```bash
cd apex-memory-system
python3 -c "
from apex_memory.database.qdrant_writer import QdrantWriter
writer = QdrantWriter()
print('✅ QdrantWriter initialized')
writer.close()
print('✅ Qdrant connection closed')
"
```

**Test 2: Write Embedding**
```bash
cd apex-memory-system
python3 << 'EOF'
from apex_memory.database.qdrant_writer import QdrantWriter
import uuid

writer = QdrantWriter()

doc_uuid = str(uuid.uuid4())
embedding = [0.5] * 1536
metadata = {"title": "Qdrant Test", "doc_type": "test"}

success = writer.write_embedding(
    collection_name="documents",
    point_id=doc_uuid,
    embedding=embedding,
    metadata=metadata
)

if success:
    print("✅ Embedding written to Qdrant")
else:
    print("❌ Qdrant write failed")

writer.close()
EOF
```

**Common Failures:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `UnexpectedResponse: 404` | Collection doesn't exist | Create collection (see setup) |
| `Connection refused` | Qdrant not running | `docker-compose up -d qdrant` |
| `Dimension mismatch` | Wrong embedding size | Use 1536 dims (text-embedding-3-small) |

---

### RedisWriter Tests

**Location:** `apex-memory-system/src/apex_memory/database/redis_writer.py`

**Test 1: Connection**
```bash
cd apex-memory-system
python3 -c "
from apex_memory.database.redis_writer import RedisWriter
writer = RedisWriter()
print('✅ RedisWriter initialized')
writer.close()
print('✅ Redis connection closed')
"
```

**Test 2: Cache Operations**
```bash
cd apex-memory-system
python3 << 'EOF'
from apex_memory.database.redis_writer import RedisWriter

writer = RedisWriter()

# Test set
writer.set("test_key", "test_value", ttl=60)
print("✅ Redis SET successful")

# Test get
value = writer.get("test_key")
if value == "test_value":
    print("✅ Redis GET successful")
else:
    print("❌ Redis GET failed")

# Test delete
writer.delete("test_key")
print("✅ Redis DELETE successful")

writer.close()
EOF
```

**Common Failures:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ConnectionError` | Redis not running | `docker-compose up -d redis` |
| `WRONGTYPE` | Key type mismatch | Flush Redis: `redis-cli FLUSHDB` |

---

### Layer 1 Summary

**Pass Criteria:**
- [ ] PostgresWriter: ✓ Connection, ✓ Write document, ✓ Write chunks
- [ ] Neo4jWriter: ✓ Connection, ✓ Write document, ✓ Write entities
- [ ] QdrantWriter: ✓ Connection, ✓ Write embedding
- [ ] RedisWriter: ✓ Connection, ✓ Cache ops (set/get/delete)

**If ALL pass:** Proceed to Layer 2
**If ANY fail:** Fix before continuing (database issues will cascade)

---

## Layer 2: Services

**Goal:** Validate business logic services with mocked external dependencies.

### Enhanced Saga Pattern (DatabaseWriteOrchestrator)

**Location:** `apex-memory-system/src/apex_memory/services/database_writer.py`

**Baseline Tests (121 tests):**
```bash
cd apex-memory-system
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v --tb=short

# Expected: 121 tests passing
```

**Test Coverage:**
- Distributed locking (prevents concurrent writes)
- Idempotency (safe retries without duplicates)
- Circuit breakers (failure isolation)
- Exponential backoff retries
- Atomic saga (all succeed or all rollback)
- Graphiti episode rollback (orphan cleanup)

**Key Test Files:**
```bash
# Distributed locking
pytest tests/unit/test_distributed_lock.py -v

# Idempotency
pytest tests/unit/test_idempotency.py -v

# Circuit breakers
pytest tests/unit/test_circuit_breaker.py -v

# Saga orchestration
pytest tests/unit/test_database_writer.py -v

# Graphiti rollback
pytest tests/unit/test_graphiti_rollback.py -v
```

**Critical Test: Graphiti Rollback on Saga Failure**
```bash
cd apex-memory-system
pytest tests/unit/test_graphiti_rollback.py::test_rollback_on_saga_failure -v --no-cov
```

**Expected Output:**
```
test_graphiti_rollback.py::test_rollback_on_saga_failure PASSED
```

**If Failing:**
- Check Graphiti episode UUID is passed correctly
- Verify rollback_graphiti_episode() is called in write_to_databases_activity
- Check Neo4j connection (rollback uses Neo4j)

---

### Graphiti Service

**Location:** `apex-memory-system/src/apex_memory/services/graphiti_service.py`

**Test 1: Add Document Episode**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.services.graphiti_service import GraphitiService
from apex_memory.config.settings import Settings

async def test_graphiti():
    settings = Settings()
    graphiti = GraphitiService(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
        openai_api_key=settings.openai_api_key
    )

    result = await graphiti.add_document_episode(
        document_uuid="test-doc-123",
        document_title="Test Document",
        document_content="ACME Corporation ordered 50 brake parts from Supplier Inc.",
        document_type="txt"
    )

    if result.success:
        print(f"✅ Graphiti extraction successful")
        print(f"   Entities: {len(result.entities_extracted)}")
        print(f"   Edges: {len(result.edges_created)}")
    else:
        print(f"❌ Graphiti extraction failed: {result.error}")

asyncio.run(test_graphiti())
EOF
```

**Expected:**
```
✅ Graphiti extraction successful
   Entities: 2-4 (ACME Corporation, Supplier Inc, brake parts)
   Edges: 1-3 (relationships)
```

**Test 2: JSON Episode**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.services.graphiti_service import GraphitiService
from apex_memory.config.settings import Settings
from datetime import datetime

async def test_json():
    settings = Settings()
    graphiti = GraphitiService(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
        openai_api_key=settings.openai_api_key
    )

    json_data = {
        "shipment_id": "SHIP-12345",
        "status": "in_transit",
        "origin": "Chicago, IL",
        "destination": "Indianapolis, IN"
    }

    result = await graphiti.add_json_episode(
        json_id="test-json-123",
        json_data=json_data,
        metadata={"source": "turvo", "data_type": "shipment"}
    )

    if result.success:
        print(f"✅ Graphiti JSON extraction successful")
        print(f"   Entities: {len(result.entities_extracted)}")
    else:
        print(f"❌ Graphiti JSON extraction failed: {result.error}")

asyncio.run(test_json())
EOF
```

**Common Failures:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `OpenAI API key not found` | Missing OPENAI_API_KEY | Add to .env |
| `Neo4j connection failed` | Neo4j not running | Start Neo4j container |
| `Rate limit exceeded` | Too many API calls | Wait 60s, retry |
| `graphiti-core import error` | Wrong version | `pip install graphiti-core==0.22.0` |

---

### Document Parser

**Location:** `apex-memory-system/src/apex_memory/services/document_parser.py`

**Test: Parse PDF**
```bash
cd apex-memory-system

# Create test PDF (if you have one)
# Or use existing test file
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
from apex_memory.services.document_parser import DocumentParser
from pathlib import Path

parser = DocumentParser()

# Replace with actual test file path
test_file = Path("tests/fixtures/sample.pdf")

if test_file.exists():
    parsed = parser.parse_document(test_file)
    print(f"✅ PDF parsed successfully")
    print(f"   Title: {parsed.metadata.title}")
    print(f"   Chunks: {len(parsed.chunks)}")
    print(f"   Content length: {len(parsed.content)} chars")
else:
    print("⚠️  Test file not found, skipping")
EOF
```

**Test Formats:**
- PDF (Docling + OCR fallback)
- DOCX (python-docx)
- PPTX (python-pptx)
- HTML (BeautifulSoup)
- Markdown (markdown-it-py)
- TXT (direct read)

---

### Embedding Service

**Location:** `apex-memory-system/src/apex_memory/services/embedding_service.py`

**Test: Generate Embedding**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
from apex_memory.services.embedding_service import EmbeddingService

service = EmbeddingService()

text = "This is a test document for embedding generation"
embedding = service.generate_embedding(text)

if len(embedding) == 1536:
    print("✅ Embedding generated (1536 dimensions)")
else:
    print(f"❌ Wrong embedding dimension: {len(embedding)}")
EOF
```

**Test: Batch Embeddings**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
from apex_memory.services.embedding_service import EmbeddingService

service = EmbeddingService()

texts = ["Chunk 1", "Chunk 2", "Chunk 3"]
result = service.generate_embeddings(texts)

embeddings = result.embeddings if hasattr(result, 'embeddings') else result

if len(embeddings) == 3 and len(embeddings[0]) == 1536:
    print("✅ Batch embeddings generated")
else:
    print(f"❌ Batch embeddings failed")
EOF
```

**Common Failures:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `OpenAI API key not found` | Missing OPENAI_API_KEY | Add to .env |
| `Rate limit exceeded` | Too many requests | Wait 60s, retry |
| `Invalid API key` | Wrong key | Update OPENAI_API_KEY |

---

### Staging Manager

**Location:** `apex-memory-system/src/apex_memory/services/staging_manager.py`

**Test: Create Staging Directory**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
from apex_memory.services.staging_manager import StagingManager, StagingStatus
import shutil

manager = StagingManager()

# Create staging
doc_id = "TEST-DOC-001"
source = "api"

staging_path = manager.create_staging(doc_id, source)
print(f"✅ Staging created: {staging_path}")

# Check metadata
metadata = manager.get_metadata(doc_id, source)
if metadata:
    print(f"✅ Metadata retrieved: status={metadata.status.value}")
else:
    print("❌ Metadata not found")

# Update status
manager.update_status(doc_id, source, StagingStatus.SUCCESS)
print("✅ Status updated to SUCCESS")

# Cleanup
shutil.rmtree(staging_path)
print("✅ Staging cleaned up")
EOF
```

**Test: TTL Cleanup**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
from apex_memory.services.staging_manager import StagingManager

manager = StagingManager()

# Run TTL cleanup (removes expired staging)
removed = manager.cleanup_expired()

print(f"✅ TTL cleanup complete: {removed} items removed")
EOF
```

---

### Layer 2 Summary

**Pass Criteria:**
- [ ] Enhanced Saga: ✓ 121 tests passing
- [ ] Graphiti: ✓ Document extraction, ✓ JSON extraction
- [ ] Document Parser: ✓ Parse test file
- [ ] Embedding Service: ✓ Single embedding, ✓ Batch embeddings
- [ ] Staging Manager: ✓ Create, ✓ Metadata, ✓ TTL cleanup

**If ALL pass:** Proceed to Layer 3
**If ANY fail:** Services are critical - must fix before workflows

---

## Layer 3: Temporal Activities

**Goal:** Test each of the 9 activities in isolation.

### Activity Testing Strategy

Each activity should:
1. Execute without errors
2. Record metrics correctly
3. Handle retries properly
4. Return expected output format

### Test 1: pull_and_stage_document_activity

**Location:** `src/apex_memory/temporal/activities/ingestion.py:1522`

```bash
cd apex-memory-system

# Create test file
echo "Test document content" > /tmp/test_doc.txt

PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.temporal.activities.ingestion import pull_and_stage_document_activity

async def test():
    result = await pull_and_stage_document_activity(
        document_id="TEST-001",
        source="local_upload",
        source_location="/tmp/test_doc.txt"
    )

    print(f"✅ Document staged: {result}")

asyncio.run(test())
EOF
```

**Expected:** File path in `/tmp/apex-staging/local_upload/TEST-001/`

---

### Test 2: parse_document_activity

**Location:** `src/apex_memory/temporal/activities/ingestion.py:64`

```bash
cd apex-memory-system

# Create test file
echo "This is a test document for parsing validation." > /tmp/parse_test.txt

PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.temporal.activities.ingestion import parse_document_activity

async def test():
    result = await parse_document_activity("/tmp/parse_test.txt")

    print(f"✅ Document parsed")
    print(f"   UUID: {result['uuid']}")
    print(f"   Chunks: {len(result['chunks'])}")
    print(f"   Content length: {len(result['content'])}")

asyncio.run(test())
EOF
```

**Expected:** Dict with uuid, content, metadata, chunks

---

### Test 3: extract_entities_activity

**Location:** `src/apex_memory/temporal/activities/ingestion.py:274`

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.temporal.activities.ingestion import extract_entities_activity
import uuid

async def test():
    parsed_doc = {
        "uuid": str(uuid.uuid4()),
        "content": "ACME Corporation ordered 50 brake parts. Invoice INV-2025-001 was issued.",
        "metadata": {"title": "Test", "file_type": "txt"},
        "chunks": ["ACME Corporation ordered 50 brake parts."]
    }

    result = await extract_entities_activity(parsed_doc)

    print(f"✅ Entities extracted")
    print(f"   Entities: {len(result['entities'])}")
    print(f"   Graphiti episode: {result['graphiti_episode_uuid']}")
    print(f"   Edges: {result['edges_created']}")

asyncio.run(test())
EOF
```

**Expected:** Dict with entities, graphiti_episode_uuid, edges_created

---

### Test 4: generate_embeddings_activity

**Location:** `src/apex_memory/temporal/activities/ingestion.py:528`

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.temporal.activities.ingestion import generate_embeddings_activity
import uuid

async def test():
    parsed_doc = {
        "uuid": str(uuid.uuid4()),
        "content": "Test content for embedding generation",
        "chunks": ["Test chunk 1", "Test chunk 2"]
    }

    result = await generate_embeddings_activity(parsed_doc)

    print(f"✅ Embeddings generated")
    print(f"   Document embedding dims: {len(result['document_embedding'])}")
    print(f"   Chunk embeddings: {len(result['chunk_embeddings'])}")

asyncio.run(test())
EOF
```

**Expected:** 1536-dim document embedding + 2 chunk embeddings

---

### Test 5: write_to_databases_activity

**Location:** `src/apex_memory/temporal/activities/ingestion.py:811`

**Note:** This is the most critical activity (uses Enhanced Saga)

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.temporal.activities.ingestion import write_to_databases_activity
from datetime import datetime
import uuid

async def test():
    doc_uuid = str(uuid.uuid4())

    parsed_doc = {
        "uuid": doc_uuid,
        "content": "Test document for database write",
        "metadata": {
            "title": "DB Write Test",
            "author": "Test User",
            "file_type": "txt",
            "file_size": 1024,
            "source_path": "/tmp/test.txt",
            "created_date": datetime.utcnow().isoformat(),
            "modified_date": None
        },
        "chunks": ["Test chunk"]
    }

    entities = {
        "entities": [{"name": "Test Entity", "entity_type": "test"}],
        "graphiti_episode_uuid": doc_uuid,
        "edges_created": 0
    }

    embeddings = {
        "document_embedding": [0.1] * 1536,
        "chunk_embeddings": [[0.2] * 1536]
    }

    result = await write_to_databases_activity(parsed_doc, entities, embeddings)

    print(f"✅ Database write completed")
    print(f"   Status: {result['status']}")
    print(f"   Databases: {result['databases_written']}")

asyncio.run(test())
EOF
```

**Expected:** Status "success", all 4 databases written

---

### Test 6: cleanup_staging_activity

**Location:** `src/apex_memory/temporal/activities/ingestion.py:1849`

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.temporal.activities.ingestion import cleanup_staging_activity
from pathlib import Path

async def test():
    # Create test staging
    doc_id = "CLEANUP-TEST-001"
    source = "api"
    staging_path = Path(f"/tmp/apex-staging/{source}/{doc_id}")
    staging_path.mkdir(parents=True, exist_ok=True)
    (staging_path / "test.txt").write_text("test")

    print(f"Created staging: {staging_path}")

    # Cleanup (success)
    await cleanup_staging_activity(doc_id, source, "success")

    if not staging_path.exists():
        print("✅ Staging cleaned up successfully")
    else:
        print("❌ Staging still exists")

asyncio.run(test())
EOF
```

**Expected:** Staging directory removed

---

### Test 7-9: JSON Activities

**fetch_structured_data_activity:**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.temporal.activities.ingestion import fetch_structured_data_activity
import json

async def test():
    # FrontApp webhook (JSON string)
    json_string = json.dumps({
        "event": "message_created",
        "message_id": "MSG-123",
        "content": "Test message"
    })

    result = await fetch_structured_data_activity(
        data_id="MSG-123",
        source="frontapp",
        source_location=json_string,
        auth_token=None
    )

    print(f"✅ JSON fetched: {list(result.keys())}")

asyncio.run(test())
EOF
```

**extract_entities_from_json_activity + write_structured_data_activity:**
Similar pattern to document activities (omitted for brevity, but same validation approach)

---

### Layer 3 Summary

**Pass Criteria:**
- [ ] pull_and_stage: ✓ Staging created
- [ ] parse_document: ✓ Returns parsed dict
- [ ] extract_entities: ✓ Graphiti extraction works
- [ ] generate_embeddings: ✓ 1536-dim embeddings
- [ ] write_to_databases: ✓ All 4 DBs written
- [ ] cleanup_staging: ✓ Directory removed
- [ ] fetch_structured_data: ✓ JSON fetched
- [ ] extract_entities_from_json: ✓ JSON extraction
- [ ] write_structured_data: ✓ Saga write

**If ALL pass:** Activities work independently, proceed to workflows
**If ANY fail:** Fix activity before testing workflows (workflows depend on activities)

---

## Layer 4: Temporal Workflows

**Goal:** Test complete workflows end-to-end via Temporal.

### DocumentIngestionWorkflow E2E

**Location:** `src/apex_memory/temporal/workflows/ingestion.py:45`

**Prerequisites:**
1. Temporal server running
2. Worker running (listening on `apex-ingestion-queue`)
3. All 4 databases healthy

**Test: Complete Document Ingestion**

```bash
cd apex-memory-system

# Create test document
echo "ACME Corporation ordered 50 brake parts from Supplier Inc. Invoice INV-2025-100 was issued on 2025-01-15." > /tmp/workflow_test.txt

# Copy to staging
mkdir -p /tmp/apex-staging/local_upload/WORKFLOW-TEST-001
cp /tmp/workflow_test.txt /tmp/apex-staging/local_upload/WORKFLOW-TEST-001/test.txt

# Run workflow via Python client
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from temporalio.client import Client
from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow

async def run_workflow():
    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Execute workflow
    result = await client.execute_workflow(
        DocumentIngestionWorkflow.run,
        args=["WORKFLOW-TEST-001", "local_upload", "/tmp/apex-staging/local_upload/WORKFLOW-TEST-001/test.txt"],
        id="test-workflow-001",
        task_queue="apex-ingestion-queue",
    )

    print(f"✅ Workflow completed")
    print(f"   Status: {result['status']}")
    print(f"   UUID: {result.get('uuid')}")
    print(f"   Databases: {result.get('databases_written')}")
    print(f"   Staging cleaned: {result.get('staging_cleaned')}")

asyncio.run(run_workflow())
EOF
```

**Expected Output:**
```
✅ Workflow completed
   Status: success
   UUID: <generated-uuid>
   Databases: ['neo4j', 'postgres', 'qdrant', 'redis']
   Staging cleaned: True
```

**Validation:**
```bash
# Check Temporal UI
# Open: http://localhost:8088
# Search for workflow ID: test-workflow-001
# Verify: All 6 activities completed successfully

# Check staging cleaned
ls /tmp/apex-staging/local_upload/WORKFLOW-TEST-001
# Expected: Directory not found (cleaned up)
```

**Query Workflow Status:**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from temporalio.client import Client
from apex_memory.temporal.workflows.ingestion import DocumentIngestionWorkflow

async def query_status():
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle("test-workflow-001")

    status = await handle.query(DocumentIngestionWorkflow.get_status)

    print(f"Workflow Status:")
    print(f"   Document ID: {status['document_id']}")
    print(f"   Source: {status['source']}")
    print(f"   Status: {status['status']}")

asyncio.run(query_status())
EOF
```

---

### StructuredDataIngestionWorkflow E2E

**Location:** `src/apex_memory/temporal/workflows/ingestion.py:336`

**Test: JSON Ingestion**

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
import json
from temporalio.client import Client
from apex_memory.temporal.workflows.ingestion import StructuredDataIngestionWorkflow

async def run_json_workflow():
    client = await Client.connect("localhost:7233")

    # Create JSON payload
    json_payload = json.dumps({
        "shipment_id": "SHIP-12345",
        "status": "in_transit",
        "origin": "Chicago, IL",
        "destination": "Indianapolis, IN",
        "carrier": "ACME Transport"
    })

    # Execute workflow
    result = await client.execute_workflow(
        StructuredDataIngestionWorkflow.run,
        args=["SHIP-12345", "frontapp", json_payload, "shipment"],
        id="test-json-workflow-001",
        task_queue="apex-ingestion-queue",
    )

    print(f"✅ JSON Workflow completed")
    print(f"   Status: {result['status']}")
    print(f"   Data ID: {result.get('data_id')}")
    print(f"   Databases: {result.get('databases_written')}")
    print(f"   Entities: {result.get('entities_extracted')}")

asyncio.run(run_json_workflow())
EOF
```

**Expected:** Status "success", all 4 databases written, entities extracted

---

### Integration Test Suite

**Run comprehensive integration tests:**

```bash
cd apex-memory-system

# Document ingestion E2E
pytest tests/integration/test_temporal_ingestion_workflow.py -v -m integration

# JSON ingestion E2E
pytest tests/integration/test_json_integration_e2e.py -v -m integration

# Staging lifecycle
pytest tests/integration/test_document_workflow_staging.py -v -m integration
```

**Expected:** All integration tests passing

---

### Layer 4 Summary

**Pass Criteria:**
- [ ] DocumentIngestionWorkflow: ✓ E2E success
- [ ] StructuredDataIngestionWorkflow: ✓ E2E success
- [ ] Integration tests: ✓ All passing
- [ ] Temporal UI: ✓ Workflows visible, activities completed
- [ ] Staging: ✓ Cleaned up after success

**If ALL pass:** Workflows orchestrate correctly, proceed to API
**If ANY fail:** Check Temporal logs, worker logs, activity failures

---

## Layer 5: API Endpoints

**Goal:** Validate FastAPI endpoints work correctly.

### Health Check

```bash
curl http://localhost:8000/api/v1/health | jq

# Expected:
# {
#   "status": "healthy",
#   "databases": {
#     "neo4j": true,
#     "postgres": true,
#     "qdrant": true,
#     "redis": true
#   }
# }
```

---

### Document Ingestion

```bash
# Create test file
echo "Test document for API ingestion" > /tmp/api_test.txt

# Upload document
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/api_test.txt" \
  -F "source=api" | jq

# Expected:
# {
#   "success": true,
#   "uuid": "<uuid>",
#   "workflow_id": "ingest-<uuid>",
#   "filename": "api_test.txt",
#   "source": "api",
#   "status": "processing",
#   "staging_path": "/tmp/apex-staging/api/<uuid>/api_test.txt"
# }
```

**Save workflow_id for status query**

---

### Workflow Status Query

```bash
# Replace with actual workflow_id from above
WORKFLOW_ID="ingest-<uuid>"

curl http://localhost:8000/api/v1/workflow/${WORKFLOW_ID}/status | jq

# Expected:
# {
#   "uuid": "<uuid>",
#   "workflow_id": "ingest-<uuid>",
#   "status": "completed",  # or "parsing", "entities_extracted", etc.
#   "document_id": "<doc_id>",
#   "source": "api"
# }
```

---

### JSON Ingestion

```bash
curl -X POST http://localhost:8000/api/v1/ingest-structured \
  -H "Content-Type: application/json" \
  -d '{
    "data_id": "API-TEST-001",
    "source": "frontapp",
    "source_endpoint": "{\"message_id\": \"MSG-001\", \"content\": \"Test message\"}",
    "data_type": "message"
  }' | jq

# Expected:
# {
#   "success": true,
#   "data_id": "API-TEST-001",
#   "workflow_id": "ingest-json-API-TEST-001",
#   "source": "frontapp",
#   "data_type": "message",
#   "status": "processing"
# }
```

---

### Error Handling

**Test 1: Invalid file type**
```bash
echo "test" > /tmp/test.xyz

curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/test.xyz" \
  -F "source=api"

# Expected: 400 Bad Request (unsupported format)
```

**Test 2: Missing file**
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "source=api"

# Expected: 422 Unprocessable Entity (missing file)
```

---

### Layer 5 Summary

**Pass Criteria:**
- [ ] /health: ✓ Returns database status
- [ ] /ingest: ✓ Accepts document, starts workflow
- [ ] /ingest-structured: ✓ Accepts JSON, starts workflow
- [ ] /workflow/{id}/status: ✓ Returns workflow status
- [ ] Error handling: ✓ Returns correct HTTP codes

**If ALL pass:** API layer functional, proceed to query router
**If ANY fail:** Check FastAPI logs, Temporal connection

---

## Layer 6: Query Router

**Goal:** Validate intent classification and database routing.

### LLM Intent Classifier

**Location:** `src/apex_memory/query_router/llm_classifier.py`

**Test: Intent Classification**

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.query_router.llm_classifier import LLMIntentClassifier

async def test():
    classifier = LLMIntentClassifier()

    # Test graph intent
    intent, conf = await classifier.verify("which vendors supply brake parts")
    print(f"Graph query: {intent} (confidence: {conf:.2f})")

    # Test temporal intent
    intent, conf = await classifier.verify("track SOP revisions over the past year")
    print(f"Temporal query: {intent} (confidence: {conf:.2f})")

    # Test semantic intent
    intent, conf = await classifier.verify("find safety procedures")
    print(f"Semantic query: {intent} (confidence: {conf:.2f})")

    # Test metadata intent
    intent, conf = await classifier.verify("list all active drivers")
    print(f"Metadata query: {intent} (confidence: {conf:.2f})")

asyncio.run(test())
EOF
```

**Expected:**
```
Graph query: graph (confidence: 0.90+)
Temporal query: temporal (confidence: 0.85+)
Semantic query: semantic (confidence: 0.90+)
Metadata query: metadata (confidence: 0.95+)
```

**If confidence < 0.80 for obvious queries:** Check Claude API key, prompt engineering

---

### Database Routing

**Test: Routing Logic**

```bash
cd apex-memory-system
pytest tests/unit/test_query_router.py -v

# Validates:
# - graph intent → Neo4j
# - temporal intent → Graphiti
# - semantic intent → Qdrant
# - metadata intent → PostgreSQL
```

---

### Cache Performance

**Test: Cache Hit Rate**

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
from apex_memory.query_router.cache import QueryCache
import time

cache = QueryCache()

# Test cache write
query = "list all active drivers"
result = {"data": ["Driver 1", "Driver 2"]}

cache.set(query, result, ttl=60)
print("✅ Cache write successful")

# Test cache read
cached = cache.get(query)
if cached == result:
    print("✅ Cache hit successful")
else:
    print("❌ Cache miss (unexpected)")

# Test TTL expiration
time.sleep(2)
cached = cache.get(query)
if cached:
    print("✅ Cache still valid (within TTL)")
else:
    print("❌ Cache expired prematurely")

cache.close()
EOF
```

---

### Layer 6 Summary

**Pass Criteria:**
- [ ] LLM Classifier: ✓ All 4 intents >0.80 confidence
- [ ] Database Routing: ✓ Correct DB for each intent
- [ ] Cache: ✓ Write/read/TTL working

**If ALL pass:** Query router functional
**If ANY fail:** Check Claude API, routing logic

---

## Critical Integration Points

**Goal:** Test cross-layer integrations.

### 1. API → Temporal

**Test: Workflow Triggering**

```bash
# Upload document via API
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/test.txt" \
  -F "source=api" | jq -r '.workflow_id'

# Check Temporal UI for workflow
# http://localhost:8088
# Search for workflow_id
# Verify: Workflow running or completed
```

**Validation:** Workflow appears in Temporal UI within 5 seconds

---

### 2. Temporal → Services

**Test: Activity Delegation**

```bash
# Run integration test
cd apex-memory-system
pytest tests/integration/test_temporal_ingestion_workflow.py::test_parse_activity -v

# Validates: parse_document_activity calls DocumentParser service
```

---

### 3. Enhanced Saga → 4 Databases

**Test: Parallel Writes**

```bash
cd apex-memory-system

# Run Saga baseline tests
pytest tests/unit/test_database_writer.py -v -k "test_parallel_write"

# Expected: All 4 databases written simultaneously
```

---

### 4. Graphiti → Neo4j

**Test: Entity Storage**

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.services.graphiti_service import GraphitiService
from apex_memory.config.settings import Settings
from neo4j import GraphDatabase

async def test():
    settings = Settings()

    # Extract entities
    graphiti = GraphitiService(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
        openai_api_key=settings.openai_api_key
    )

    result = await graphiti.add_document_episode(
        document_uuid="integration-test-123",
        document_title="Integration Test",
        document_content="ACME Corporation ordered parts.",
        document_type="txt"
    )

    print(f"✅ Graphiti extracted {len(result.entities_extracted)} entities")

    # Verify in Neo4j
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password)
    )

    with driver.session() as session:
        entities = session.run("MATCH (n) WHERE n.uuid = 'integration-test-123' RETURN count(n) as count")
        count = entities.single()["count"]

        if count > 0:
            print(f"✅ Entities found in Neo4j: {count}")
        else:
            print("❌ Entities not found in Neo4j")

    driver.close()

asyncio.run(test())
EOF
```

---

### 5. Redis → All Components

**Test: Distributed Locking**

```bash
cd apex-memory-system
pytest tests/unit/test_distributed_lock.py -v

# Validates: Redis locks prevent concurrent writes
```

**Test: Cache Layer**

```bash
cd apex-memory-system
pytest tests/unit/test_cache.py -v

# Validates: Query results cached in Redis
```

---

### Integration Summary

**Pass Criteria:**
- [ ] API → Temporal: ✓ Workflows triggered
- [ ] Temporal → Services: ✓ Activities call services
- [ ] Saga → Databases: ✓ Parallel writes work
- [ ] Graphiti → Neo4j: ✓ Entities stored
- [ ] Redis → Components: ✓ Locks + cache work

**If ALL pass:** System integrated correctly
**If ANY fail:** Check connection between layers

---

## Known Issues & Gotchas

### 1. Graphiti 0.22.0 Migration

**Issue:** `graphiti-core` updated from 0.21.x to 0.22.0, API changes

**Symptoms:**
- `TypeError: __init__() got an unexpected keyword argument`
- Import errors for Graphiti classes

**Fix:**
```bash
pip install graphiti-core==0.22.0 --force-reinstall
```

**Validation:**
```bash
python3 -c "import graphiti; print(graphiti.__version__)"
# Expected: 0.22.0
```

---

### 2. Temporal SDK API Changes

**Issue:** Temporal Python SDK updated, workflow syntax changed

**Symptoms:**
- `DeprecationWarning: Workflow.run is deprecated`
- `AttributeError: 'WorkflowHandle' object has no attribute 'result'`

**Fix:** Already migrated in codebase (using `@workflow.run` decorator)

**Validation:**
```bash
grep -r "@workflow.run" apex-memory-system/src/apex_memory/temporal/workflows/
# Expected: Found in both workflows
```

---

### 3. Staging Directory Cleanup Edge Cases

**Issue:** Failed workflows may leave orphaned staging files

**Symptoms:**
- `/tmp/apex-staging/` grows over time
- Disk space usage increases

**Fix:**
```bash
# Manual cleanup (run weekly)
find /tmp/apex-staging -type f -mtime +7 -delete

# Or full cleanup
rm -rf /tmp/apex-staging/*
```

**Prevention:** TTL cleanup runs automatically (see StagingManager)

---

### 4. Circuit Breaker Stuck Open

**Issue:** After 5 failures, circuit breaker opens and stays open

**Symptoms:**
- `CircuitBreakerOpenError` even after database recovers
- All writes failing

**Fix:**
```bash
# Restart worker (resets circuit breaker state)
# Kill worker process
pkill -f dev_worker

# Restart
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python src/apex_memory/temporal/workers/dev_worker.py
```

**Prevention:** Circuit breakers auto-reset after 60s timeout

---

### 5. Orphaned Graphiti Episodes

**Issue:** Saga rollback fails, Graphiti episode not removed

**Symptoms:**
- Neo4j has orphaned nodes
- Episode exists but no corresponding data in other DBs

**Detection:**
```bash
# List orphaned episodes (manual query)
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
from neo4j import GraphDatabase
from apex_memory.config.settings import Settings

settings = Settings()
driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password)
)

with driver.session() as session:
    # Find episode nodes with no document in PostgreSQL
    query = """
    MATCH (e:Episode)
    WHERE NOT EXISTS {
        MATCH (d:Document {uuid: e.uuid})
    }
    RETURN e.uuid as orphan_episode
    LIMIT 10
    """

    result = session.run(query)
    orphans = [record["orphan_episode"] for record in result]

    if orphans:
        print(f"⚠️  Found {len(orphans)} orphaned episodes:")
        for ep in orphans:
            print(f"   - {ep}")
    else:
        print("✅ No orphaned episodes found")

driver.close()
EOF
```

**Fix:**
```bash
# Manual cleanup (use with caution)
# Remove orphaned episode
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.services.graphiti_service import GraphitiService
from apex_memory.config.settings import Settings

async def cleanup():
    settings = Settings()
    graphiti = GraphitiService(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
        openai_api_key=settings.openai_api_key
    )

    # Replace with actual orphan episode UUID
    episode_uuid = "ORPHAN-EPISODE-UUID"

    success = await graphiti.remove_episode(episode_uuid)

    if success:
        print(f"✅ Removed orphaned episode: {episode_uuid}")
    else:
        print(f"❌ Failed to remove episode: {episode_uuid}")

asyncio.run(cleanup())
EOF
```

---

### 6. OpenAI Rate Limits

**Issue:** Embedding generation hits rate limit (3 RPM on free tier)

**Symptoms:**
- `RateLimitError: Rate limit exceeded`
- Workflows retry repeatedly

**Fix:**
```bash
# Wait 60 seconds
sleep 60

# Retry workflow
```

**Prevention:** Upgrade OpenAI tier or add rate limiting to embedding service

---

### 7. Redis Memory Pressure

**Issue:** Redis cache fills up, evicts old entries

**Symptoms:**
- Cache hit rate drops
- `OOM command not allowed` errors

**Fix:**
```bash
# Flush Redis (loses cache)
redis-cli FLUSHDB

# Or increase maxmemory
redis-cli CONFIG SET maxmemory 2gb
```

**Prevention:** Monitor Redis memory usage, set appropriate eviction policy

---

## Debugging Procedures

### Workflow Failed in Temporal

**Symptoms:**
- Workflow shows "Failed" status in Temporal UI
- Activities not completing

**Debug Steps:**

1. **Check Temporal UI**
   ```
   Open: http://localhost:8088
   Search: workflow_id
   View: Activity errors, retry attempts
   ```

2. **Check Worker Logs**
   ```bash
   # If worker running in terminal, check output
   # Or check log file (if configured)
   ```

3. **Check Activity Failure**
   ```bash
   # In Temporal UI, click failed activity
   # View: Error message, stack trace
   ```

4. **Retry Workflow**
   ```bash
   cd apex-memory-system
   PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
   import asyncio
   from temporalio.client import Client

   async def retry():
       client = await Client.connect("localhost:7233")
       handle = client.get_workflow_handle("FAILED-WORKFLOW-ID")

       # Terminate failed workflow
       await handle.terminate()

       # Re-trigger workflow (via API or client)
       print("Workflow terminated. Re-trigger via API.")

   asyncio.run(retry())
   EOF
   ```

---

### Database Write Failed

**Symptoms:**
- Saga status: `ROLLED_BACK` or `FAILED`
- Error: `Database write failed`

**Debug Steps:**

1. **Check Database Connectivity**
   ```bash
   # Run pre-flight checks (see above)
   PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT 1"
   redis-cli ping
   curl http://localhost:6333/collections
   ```

2. **Check Saga Logs**
   ```bash
   cd apex-memory-system
   # View write_to_databases_activity logs
   # Look for failed database name
   ```

3. **Check Individual Writer**
   ```bash
   # Test failing writer in isolation (see Layer 1 tests)
   # Example: PostgresWriter
   python3 -c "from apex_memory.database.postgres_writer import PostgresWriter; w = PostgresWriter(); print('✅ OK')"
   ```

4. **Rollback Verification**
   ```bash
   # Verify data was rolled back from all databases
   # Check PostgreSQL
   PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT uuid FROM documents WHERE uuid = 'FAILED-DOC-UUID'"
   # Expected: No results (rolled back)
   ```

---

### Graphiti Extraction Failed

**Symptoms:**
- Error: `Graphiti extraction failed`
- Zero entities extracted

**Debug Steps:**

1. **Check OpenAI API Key**
   ```bash
   cd apex-memory-system
   cat .env | grep OPENAI_API_KEY
   # Verify key is set and valid
   ```

2. **Test Graphiti Directly**
   ```bash
   # Run manual extraction (see Layer 2 tests)
   PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
   import asyncio
   from apex_memory.services.graphiti_service import GraphitiService
   from apex_memory.config.settings import Settings

   async def test():
       settings = Settings()
       graphiti = GraphitiService(
           neo4j_uri=settings.neo4j_uri,
           neo4j_user=settings.neo4j_user,
           neo4j_password=settings.neo4j_password,
           openai_api_key=settings.openai_api_key
       )

       result = await graphiti.add_document_episode(
           document_uuid="debug-test",
           document_title="Debug",
           document_content="Test content with entities.",
           document_type="txt"
       )

       print(f"Success: {result.success}")
       print(f"Error: {result.error}")

   asyncio.run(test())
   EOF
   ```

3. **Check Neo4j Connection**
   ```bash
   # Verify Neo4j accessible
   curl http://localhost:7474
   # Expected: Neo4j browser page
   ```

---

### High Latency / Slow Performance

**Symptoms:**
- Workflows taking >5min to complete
- Query latency >2s

**Debug Steps:**

1. **Check Database Load**
   ```bash
   # PostgreSQL
   PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT count(*) FROM pg_stat_activity"

   # Neo4j
   # Open http://localhost:7474
   # Run: :queries (to see running queries)

   # Qdrant
   curl http://localhost:6333/metrics
   ```

2. **Check Metrics**
   ```bash
   # Open Grafana
   # http://localhost:3001/d/temporal-ingestion
   # Check: Activity duration, database write latency
   ```

3. **Check Worker Concurrency**
   ```bash
   # Count active workflow executions
   ps aux | grep dev_worker

   # If too many, increase worker pool size
   # (see dev_worker.py configuration)
   ```

---

## Load & Chaos Testing

### Concurrent Workflow Execution

**Goal:** Validate 10+ documents/second throughput

**Test:**
```bash
cd apex-memory-system
pytest tests/load/test_concurrent_workflows.py -v -m load

# Validates:
# - 10+ concurrent workflows
# - No resource exhaustion
# - All workflows complete successfully
# - Metrics accurate under load
```

**Expected:** All workflows complete within 5min, zero errors

---

### Database Failure Scenarios

**Test 1: PostgreSQL Down**
```bash
# Stop PostgreSQL
docker-compose stop postgres

# Trigger workflow
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/test.txt" \
  -F "source=api"

# Expected: Workflow fails, saga rollback triggered

# Restart PostgreSQL
docker-compose start postgres

# Retry workflow (should succeed)
```

**Test 2: Neo4j Down**
```bash
# Same pattern as PostgreSQL
docker-compose stop neo4j
# Trigger workflow → Expected: Rollback
docker-compose start neo4j
# Retry → Expected: Success
```

---

### Network Partition Simulation

**Test: Simulate slow network**
```bash
# Add latency to Redis (requires tc utility)
# sudo tc qdisc add dev lo root netem delay 500ms

# Run workflow
# Expected: Timeouts, retries, eventual success or failure

# Remove latency
# sudo tc qdisc del dev lo root
```

---

### Resource Exhaustion

**Test: Disk Space Exhaustion**
```bash
# Fill /tmp (staging directory)
dd if=/dev/zero of=/tmp/fill_disk bs=1M count=1000

# Trigger workflow
# Expected: Staging activity fails with disk space error

# Cleanup
rm /tmp/fill_disk
```

---

## Deployment Readiness Checklist

**Run this checklist before deploying to production.**

### 1. Baseline Tests

- [ ] Enhanced Saga: 121/121 tests passing
- [ ] Integration tests: All passing
- [ ] Unit tests: All passing (excluding known failures)

```bash
cd apex-memory-system
pytest tests/ --ignore=tests/load/ -v
# Expected: 121+ tests passing
```

---

### 2. Critical Services

- [ ] All 4 databases: Running and connectable
- [ ] Temporal server: Healthy
- [ ] Worker: Running and polling
- [ ] API: Responding to /health

```bash
# Run pre-flight validation
# See "Pre-Flight Validation" section
```

---

### 3. Metrics & Observability

- [ ] Prometheus: Scraping metrics
- [ ] Grafana: Dashboard accessible
- [ ] Alerts: Configured and firing (test)
- [ ] Logs: Structured and queryable

```bash
# Check Prometheus
curl http://localhost:9090/-/healthy
# Expected: Prometheus is Healthy.

# Check Grafana
curl http://localhost:3001/api/health
# Expected: {"commit": "...", "database": "ok", "version": "..."}

# Trigger test alert
# (Manually cause failure, verify alert fires)
```

---

### 4. No Orphaned Resources

- [ ] Staging: No files older than 7 days
- [ ] Graphiti: No orphaned episodes
- [ ] Redis: No stale locks

```bash
# Check staging
find /tmp/apex-staging -type f -mtime +7
# Expected: No output

# Check orphaned episodes (see Known Issues section)
# Run Neo4j query

# Check Redis locks
redis-cli KEYS "lock:*"
# Expected: Empty or only active locks
```

---

### 5. Performance Targets

- [ ] Query latency: <1s (P90)
- [ ] Cache hit rate: >60%
- [ ] Throughput: 10+ docs/sec
- [ ] Database write: <2s (P90)

```bash
# Check Grafana dashboard
# http://localhost:3001/d/temporal-ingestion

# Metrics to verify:
# - temporal_workflow_duration_seconds (P90 < 60s)
# - Redis cache hit rate (>60%)
# - temporal_database_writes_total (>10/sec)
```

---

### 6. Error Handling

- [ ] Failed workflows: Rollback correctly
- [ ] API errors: Return correct HTTP codes
- [ ] Retries: Exponential backoff working
- [ ] Circuit breakers: Open after 5 failures

```bash
# Test failure scenario
# Stop PostgreSQL, trigger workflow
docker-compose stop postgres
curl -X POST http://localhost:8000/api/v1/ingest -F "file=@/tmp/test.txt" -F "source=api"

# Check Temporal UI: Workflow failed, rollback triggered
# Expected: Saga status ROLLED_BACK

# Restart PostgreSQL
docker-compose start postgres
```

---

### 7. Security

- [ ] Environment variables: Not committed to git
- [ ] API keys: Rotated and secured
- [ ] Database passwords: Strong and unique
- [ ] Network: Databases not exposed publicly

```bash
# Check .env not in git
git ls-files | grep .env
# Expected: No output

# Check .gitignore
cat .gitignore | grep .env
# Expected: .env listed
```

---

### 8. Documentation

- [ ] README: Up to date
- [ ] API docs: Generated and accurate
- [ ] Runbook: Operational procedures documented
- [ ] Architecture: Diagrams current

```bash
# Check API docs
curl http://localhost:8000/docs
# Expected: FastAPI Swagger UI
```

---

### Final Go/No-Go Decision

**GO if:**
✅ ALL baseline tests passing
✅ ALL critical services healthy
✅ Metrics recording correctly
✅ Performance targets met
✅ Zero orphaned resources
✅ Error handling validated

**NO-GO if:**
❌ ANY baseline test failing
❌ Database connectivity issues
❌ Metrics not recording
❌ Performance <50% of target
❌ Orphaned resources accumulating
❌ Error handling broken

---

## Quick Reference Commands

### Start All Services

```bash
cd apex-memory-system/docker
docker-compose up -d

# Wait for initialization
sleep 30

# Verify all healthy
docker ps
```

---

### Start Temporal

```bash
# Dev server
temporal server start-dev

# Or use existing Temporal Cloud/cluster
```

---

### Start Worker

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python src/apex_memory/temporal/workers/dev_worker.py
```

---

### Start API

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH uvicorn apex_memory.main:app --reload --port 8000
```

---

### Run All Tests

```bash
cd apex-memory-system

# Baseline (121 tests)
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v

# Integration
pytest tests/integration/ -v -m integration

# Load
pytest tests/load/ -v -m load
```

---

### Check Metrics

```bash
# Prometheus
curl http://localhost:9090/api/v1/query?query=temporal_workflow_completed_total

# Grafana
open http://localhost:3001/d/temporal-ingestion
```

---

### Debug Workflow

```bash
# List recent workflows
cd apex-memory-system
python scripts/temporal/list-failed-workflows.py --last 24h

# Check workflow status
python scripts/temporal/check-workflow-status.py --workflow-id WORKFLOW-ID

# Compare metrics
python scripts/temporal/compare-metrics.py

# Worker health
bash scripts/temporal/worker-health-check.sh
```

---

### Cleanup

```bash
# Flush Redis
redis-cli FLUSHDB

# Clean staging
rm -rf /tmp/apex-staging/*

# Reset circuit breakers (restart worker)
pkill -f dev_worker
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python src/apex_memory/temporal/workers/dev_worker.py
```

---

## End of Testing Kit

**Last Updated:** 2025-10-20
**Version:** 1.0
**Status:** Active

**For questions or issues, refer to:**
- System Manual: `SYSTEM-MANUAL.html`
- Project Documentation: `apex-memory-system/README.md`
- Temporal Docs: `https://docs.temporal.io/`
- Graphiti Docs: `https://github.com/getzep/graphiti`

**Good luck with deployment! 🚀**
