# Testing Kit Implementation Guide

**Purpose:** Step-by-step guide to validate the Apex Memory System before deployment
**Time Required:** 3-4 hours (comprehensive) | 1 hour (quick validation)
**Last Updated:** 2025-10-20
**Status:** Active

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Experienced Users)](#quick-start-experienced-users)
3. [Pre-Flight Validation (15 min)](#pre-flight-validation-15-min)
4. [Layer 1: Database Writers (30 min)](#layer-1-database-writers-30-min)
5. [Layer 2: Services (30 min)](#layer-2-services-30-min)
6. [Layer 3: Temporal Activities (30 min)](#layer-3-temporal-activities-30-min)
7. [Layer 4: Workflows (30 min)](#layer-4-workflows-30-min)
8. [Layer 5: API Endpoints (15 min)](#layer-5-api-endpoints-15-min)
9. [Layer 6: Query Router (15 min)](#layer-6-query-router-15-min)
10. [Integration Testing (30 min)](#integration-testing-30-min)
11. [Load & Chaos Testing (1 hour, optional)](#load--chaos-testing-1-hour-optional)
12. [Results Interpretation](#results-interpretation)
13. [Troubleshooting Common Failures](#troubleshooting-common-failures)
14. [Deployment Decision (GO/NO-GO)](#deployment-decision-gono-go)
15. [Quick Reference Commands](#quick-reference-commands)

---

## Prerequisites

Before starting, ensure you have:

### Required Software

- [ ] **Docker** - Running containers for databases
- [ ] **Python 3.11+** - Runtime environment
- [ ] **Temporal CLI** - `temporal` command available
- [ ] **PostgreSQL client** - `psql` command (for manual queries)
- [ ] **Redis CLI** - `redis-cli` command
- [ ] **curl** - For API testing
- [ ] **jq** - JSON parsing (optional but recommended)

### Required Services Running

- [ ] **PostgreSQL** - Port 5432
- [ ] **Neo4j** - Ports 7474 (HTTP), 7687 (Bolt)
- [ ] **Qdrant** - Port 6333
- [ ] **Redis** - Port 6379
- [ ] **Temporal Server** - Port 7233
- [ ] **Temporal Worker** - Running and polling `apex-ingestion-queue`
- [ ] **API Server** - Port 8000

### Environment Setup

- [ ] `.env` file configured in `apex-memory-system/`
- [ ] `OPENAI_API_KEY` set (for embeddings and Graphiti)
- [ ] Database credentials correct
- [ ] `/tmp/apex-staging/` directory exists and writable

### Test Recording

- [ ] Have `testing-kit/results/RESULTS-TEMPLATE.md` ready
- [ ] Pen/paper or text editor for notes
- [ ] Access to Temporal UI (http://localhost:8088)
- [ ] Access to Grafana (http://localhost:3001)

---

## Quick Start (Experienced Users)

**For those familiar with the system, run tests in this order:**

```bash
# 1. Pre-flight checks
cd apex-memory-system
docker ps | grep -E "postgres|neo4j|qdrant|redis"
temporal server health
curl http://localhost:8000/api/v1/health

# 2. Baseline tests (121 Enhanced Saga)
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v

# 3. Integration tests
pytest tests/integration/ -v -m integration

# 4. API smoke test
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/test.txt" \
  -F "source=api"

# 5. Check metrics
open http://localhost:3001/d/temporal-ingestion

# 6. Deployment decision
# See "Deployment Decision" section for GO/NO-GO criteria
```

**If all pass:** System ready for deployment
**If any fail:** Continue to detailed layer-by-layer testing below

---

## Pre-Flight Validation (15 min)

**Goal:** Ensure all infrastructure is healthy before testing begins.

### Step 1: Check All Databases Running

**What this validates:** Infrastructure is up

```bash
docker ps | grep -E "postgres|neo4j|qdrant|redis"
```

**Expected Output:**
```
<container_id>  postgres:15     ... Up ... apex_memory_postgres
<container_id>  neo4j:5.x      ... Up ... apex_memory_neo4j
<container_id>  qdrant/qdrant  ... Up ... apex_memory_qdrant
<container_id>  redis:7        ... Up ... apex_memory_redis
```

**What You'll Know:** All 4 databases are running

**If Failed:**
```bash
cd apex-memory-system/docker
docker-compose up -d
sleep 30  # Wait for initialization
```

---

### Step 2: Test Database Connectivity

**What this validates:** Databases accept connections

**PostgreSQL:**
```bash
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "SELECT 1"
```
**Expected:** `1` (single row)
**What You'll Know:** PostgreSQL connectable with correct credentials

**Redis:**
```bash
redis-cli ping
```
**Expected:** `PONG`
**What You'll Know:** Redis responding

**Neo4j:**
```bash
# Open browser
open http://localhost:7474
# Login: neo4j / apexmemory2024
```
**Expected:** Neo4j browser loads
**What You'll Know:** Neo4j web interface accessible

**Qdrant:**
```bash
curl http://localhost:6333/collections
```
**Expected:** JSON response with collections list
**What You'll Know:** Qdrant API responding

---

### Step 3: Temporal Server Health

**What this validates:** Temporal orchestration layer ready

```bash
temporal server health
```

**Expected Output:**
```
temporal server is healthy
```

**What You'll Know:** Temporal can accept workflow executions

**If Failed:**
```bash
# Start Temporal dev server
temporal server start-dev

# Or check if already running
ps aux | grep temporal
```

---

### Step 4: Worker Process Running

**What this validates:** Activities can be executed

```bash
ps aux | grep dev_worker
```

**Expected:** Process running with `apex_memory/temporal/workers/dev_worker.py`

**What You'll Know:** Worker polling for workflow tasks

**If Failed:**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python src/apex_memory/temporal/workers/dev_worker.py &
```

---

### Step 5: API Server Health

**What this validates:** REST API layer functional

```bash
curl http://localhost:8000/api/v1/health | jq
```

**Expected Output:**
```json
{
  "status": "healthy",
  "databases": {
    "neo4j": true,
    "postgres": true,
    "qdrant": true,
    "redis": true
  }
}
```

**What You'll Know:** API can communicate with all databases

**If Failed:**
```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH uvicorn apex_memory.main:app --reload --port 8000 &
```

---

### Step 6: Staging Directory Ready

**What this validates:** Local file staging operational

```bash
ls -ld /tmp/apex-staging
```

**Expected:** Directory exists with write permissions

**What You'll Know:** Workflows can stage documents

**If Failed:**
```bash
mkdir -p /tmp/apex-staging
chmod 755 /tmp/apex-staging
```

---

### Pre-Flight Checklist

Record results in `results/RESULTS-TEMPLATE.md`:

- [ ] ✅ PostgreSQL: Running, Connectable
- [ ] ✅ Neo4j: Running, Connectable
- [ ] ✅ Qdrant: Running, Connectable
- [ ] ✅ Redis: Running, Connectable
- [ ] ✅ Temporal Server: Healthy
- [ ] ✅ Temporal Worker: Running
- [ ] ✅ API: /health responding
- [ ] ✅ Staging: Directory writable

**If ALL checked:** ✅ Proceed to Layer 1
**If ANY unchecked:** ❌ STOP - Fix infrastructure first

---

## Layer 1: Database Writers (30 min)

**Goal:** Validate each database writer works independently (no dependencies).

### Why This Matters

Database writers are the **foundation**. If these fail, everything else will fail. Test in isolation to identify exact failure points.

---

### Test 1.1: PostgresWriter - Basic Connection

**What this validates:** PostgreSQL client can initialize connection pool

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

**Expected Output:**
```
✅ PostgresWriter initialized
✅ Connection pool closed
```

**What You'll Know:** Connection pooling works, credentials valid

**If Failed:**
- **Error:** `ModuleNotFoundError` → `cd apex-memory-system && pip install -e .`
- **Error:** `OperationalError` → PostgreSQL not running
- **Error:** `password authentication failed` → Check `POSTGRES_PASSWORD` in .env

---

### Test 1.2: PostgresWriter - Write Document

**What this validates:** Can insert document + embedding into PostgreSQL

```bash
cd apex-memory-system
python3 << 'EOF'
from apex_memory.database.postgres_writer import PostgresWriter
from apex_memory.models.document import ParsedDocument, DocumentMetadata
from datetime import datetime
import uuid

writer = PostgresWriter()

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

embedding = [0.1] * 1536  # Mock embedding
success = writer.write_document(doc, embedding)

if success:
    print("✅ Document written to PostgreSQL")
else:
    print("❌ PostgreSQL write failed")

writer.close()
EOF
```

**Expected Output:**
```
✅ Document written to PostgreSQL
```

**What You'll Know:**
- Documents table accessible
- pgvector extension working
- Embedding writes functional

**If Failed:**
- **Error:** `relation "documents" does not exist` → Run schema migrations
- **Error:** `extension "vector" does not exist` → Install pgvector extension

---

### Test 1.3: Neo4jWriter - Basic Connection

**What this validates:** Neo4j driver can establish connection

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

**Expected Output:**
```
✅ Neo4jWriter initialized
✅ Neo4j connection closed
```

**What You'll Know:** Neo4j credentials correct, driver working

---

### Test 1.4: Neo4jWriter - Write Document Node

**What this validates:** Can create nodes in Neo4j graph

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

**Expected Output:**
```
✅ Document node created in Neo4j
```

**What You'll Know:**
- Neo4j graph is writable
- Node creation working
- Cypher queries executing

---

### Test 1.5: QdrantWriter - Basic Connection

**What this validates:** Qdrant client can connect to vector DB

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

**Expected Output:**
```
✅ QdrantWriter initialized
✅ Qdrant connection closed
```

**What You'll Know:** Qdrant accessible, collections exist

---

### Test 1.6: QdrantWriter - Write Embedding

**What this validates:** Can store vectors in Qdrant

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

**Expected Output:**
```
✅ Embedding written to Qdrant
```

**What You'll Know:**
- Vector storage working
- 1536-dim embeddings accepted
- Metadata attached to vectors

---

### Test 1.7: RedisWriter - Cache Operations

**What this validates:** Redis cache layer functional

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

**Expected Output:**
```
✅ Redis SET successful
✅ Redis GET successful
✅ Redis DELETE successful
```

**What You'll Know:**
- Cache writes working
- TTL configuration correct
- Key-value storage functional

---

### Layer 1 Checkpoint

**Record in results template:**

- [ ] PostgresWriter: ✅ Connection, ✅ Write document
- [ ] Neo4jWriter: ✅ Connection, ✅ Write node
- [ ] QdrantWriter: ✅ Connection, ✅ Write embedding
- [ ] RedisWriter: ✅ Cache operations

**What You Now Know:**
- ✅ All 4 databases are **independently writable**
- ✅ Database clients configured correctly
- ✅ Foundation is solid for higher layers

**If ALL passed:** ✅ Proceed to Layer 2
**If ANY failed:** ❌ STOP - Database issues will cascade up

---

## Layer 2: Services (30 min)

**Goal:** Validate business logic services with mocked external dependencies.

### Why This Matters

Services orchestrate database writers and implement core logic. The **Enhanced Saga pattern** (121 tests) is the most critical component.

---

### Test 2.1: Enhanced Saga Baseline (CRITICAL)

**What this validates:** All saga patterns still work after recent changes

```bash
cd apex-memory-system
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v --tb=short
```

**Expected Output:**
```
====================== 121 passed in 45.23s ======================
```

**What You'll Know:**
- ✅ Distributed locking prevents concurrent writes
- ✅ Idempotency enables safe retries
- ✅ Circuit breakers isolate failures
- ✅ Atomic saga (all succeed or all rollback)
- ✅ Graphiti episode rollback working

**This is the MOST IMPORTANT test. If this fails, deployment is a NO-GO.**

**If Failed:**
```bash
# See which tests failed
pytest tests/ --ignore=tests/load/ --ignore=tests/integration/ -v --tb=short | grep FAILED

# Run specific failed test with full output
pytest tests/unit/test_database_writer.py::test_specific_test -v --tb=long
```

---

### Test 2.2: Graphiti Service - Document Extraction

**What this validates:** LLM-powered entity extraction working (90%+ accuracy)

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

**Expected Output:**
```
✅ Graphiti extraction successful
   Entities: 2-4
   Edges: 1-3
```

**What You'll Know:**
- ✅ OpenAI API key working
- ✅ Graphiti LLM extraction functional
- ✅ Entities being created in Neo4j

**If Failed:**
- **Error:** `OpenAI API key not found` → Add to .env
- **Error:** `Rate limit exceeded` → Wait 60s, retry
- **Error:** `graphiti-core import error` → `pip install graphiti-core==0.22.0`

---

### Test 2.3: Embedding Service

**What this validates:** OpenAI embeddings generating correctly

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

**Expected Output:**
```
✅ Embedding generated (1536 dimensions)
```

**What You'll Know:**
- ✅ text-embedding-3-small model accessible
- ✅ Correct dimensionality for pgvector + Qdrant
- ✅ API calls succeeding

---

### Test 2.4: Staging Manager

**What this validates:** Local file staging + TTL cleanup working

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
from apex_memory.services.staging_manager import StagingManager, StagingStatus
import shutil

manager = StagingManager()

doc_id = "TEST-DOC-001"
source = "api"

# Create staging
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

**Expected Output:**
```
✅ Staging created: /tmp/apex-staging/api/TEST-DOC-001
✅ Metadata retrieved: status=pending
✅ Status updated to SUCCESS
✅ Staging cleaned up
```

**What You'll Know:**
- ✅ Staging directory creation working
- ✅ Metadata tracking functional
- ✅ Cleanup logic correct

---

### Layer 2 Checkpoint

**Record in results template:**

- [ ] Enhanced Saga: ✅ 121/121 tests passing
- [ ] Graphiti: ✅ Document extraction (2-4 entities)
- [ ] Embedding: ✅ 1536-dim vectors
- [ ] Staging: ✅ Create, metadata, cleanup

**What You Now Know:**
- ✅ Business logic layer is **sound**
- ✅ Saga pattern protecting data integrity
- ✅ LLM extraction achieving high accuracy
- ✅ Services ready for workflow integration

**If ALL passed:** ✅ Proceed to Layer 3
**If ANY failed:** ❌ Fix before workflows (activities depend on services)

---

## Layer 3: Temporal Activities (30 min)

**Goal:** Test each of the 9 activities in isolation.

### Why This Matters

Activities are the **unit of work** in Temporal. Each must execute correctly, record metrics, and handle retries.

---

### Test 3.1: parse_document_activity

**What this validates:** Document parsing works in Temporal context

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

**Expected Output:**
```
✅ Document parsed
   UUID: <generated-uuid>
   Chunks: 1
   Content length: 47
```

**What You'll Know:**
- ✅ Activity executes without errors
- ✅ Returns expected dict structure
- ✅ Parsing logic functional

---

### Test 3.2: extract_entities_activity

**What this validates:** Graphiti extraction as Temporal activity

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

**Expected Output:**
```
✅ Entities extracted
   Entities: 2-4
   Graphiti episode: <episode-uuid>
   Edges: 1-3
```

**What You'll Know:**
- ✅ Activity calls Graphiti service correctly
- ✅ Episode UUID returned for saga tracking
- ✅ Entity count reasonable for content

---

### Test 3.3: generate_embeddings_activity

**What this validates:** Embedding generation as activity

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

**Expected Output:**
```
✅ Embeddings generated
   Document embedding dims: 1536
   Chunk embeddings: 2
```

**What You'll Know:**
- ✅ Batch embedding generation working
- ✅ Correct dimensionality
- ✅ Multiple embeddings in single API call

---

### Test 3.4: write_to_databases_activity (CRITICAL)

**What this validates:** Enhanced Saga executes in Temporal activity

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

**Expected Output:**
```
✅ Database write completed
   Status: success
   Databases: ['neo4j', 'postgres', 'qdrant', 'redis']
```

**What You'll Know:**
- ✅ All 4 databases written in parallel
- ✅ Saga pattern executed successfully
- ✅ No rollback triggered (success case)

---

### Test 3.5: cleanup_staging_activity

**What this validates:** Staging cleanup in Temporal context

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
from apex_memory.temporal.activities.ingestion import cleanup_staging_activity
from pathlib import Path

async def test():
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

**Expected Output:**
```
Created staging: /tmp/apex-staging/api/CLEANUP-TEST-001
✅ Staging cleaned up successfully
```

**What You'll Know:**
- ✅ Cleanup activity removes staging
- ✅ Success case handled correctly

---

### Layer 3 Checkpoint

**Record in results template:**

- [ ] parse_document: ✅ Returns parsed dict
- [ ] extract_entities: ✅ Graphiti extraction works
- [ ] generate_embeddings: ✅ 1536-dim embeddings
- [ ] write_to_databases: ✅ All 4 DBs written
- [ ] cleanup_staging: ✅ Directory removed

**What You Now Know:**
- ✅ All 9 activities execute **independently**
- ✅ Activities ready for workflow orchestration
- ✅ Metrics being recorded (check Prometheus)

**If ALL passed:** ✅ Proceed to Layer 4
**If ANY failed:** ❌ Fix activity before testing workflows

---

## Layer 4: Workflows (30 min)

**Goal:** Test complete workflows end-to-end via Temporal.

### Why This Matters

Workflows **orchestrate activities** into a complete business process. This validates the entire ingestion pipeline.

---

### Test 4.1: DocumentIngestionWorkflow E2E

**What this validates:** Complete 6-step document ingestion workflow

**Prerequisites Check:**
```bash
# Temporal server running
temporal server health

# Worker running
ps aux | grep dev_worker

# All databases healthy
curl http://localhost:8000/api/v1/health | jq
```

**Run Workflow:**

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
    client = await Client.connect("localhost:7233")

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

**What You'll Know:**
- ✅ All 6 activities executed in sequence
- ✅ Document parsed, entities extracted, embeddings generated
- ✅ All 4 databases written atomically
- ✅ Staging cleaned up
- ✅ Complete E2E pipeline functional

**Validation:**
```bash
# Check Temporal UI
open http://localhost:8088
# Search: test-workflow-001
# Verify: All 6 activities completed successfully

# Check staging cleaned
ls /tmp/apex-staging/local_upload/WORKFLOW-TEST-001
# Expected: Directory not found (cleaned up)
```

---

### Test 4.2: StructuredDataIngestionWorkflow E2E

**What this validates:** JSON ingestion workflow (4 steps)

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
import asyncio
import json
from temporalio.client import Client
from apex_memory.temporal.workflows.ingestion import StructuredDataIngestionWorkflow

async def run_json_workflow():
    client = await Client.connect("localhost:7233")

    json_payload = json.dumps({
        "shipment_id": "SHIP-12345",
        "status": "in_transit",
        "origin": "Chicago, IL",
        "destination": "Indianapolis, IN",
        "carrier": "ACME Transport"
    })

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

**Expected Output:**
```
✅ JSON Workflow completed
   Status: success
   Data ID: SHIP-12345
   Databases: ['neo4j', 'postgres', 'qdrant', 'redis']
   Entities: 2-4
```

**What You'll Know:**
- ✅ JSON workflow functional
- ✅ Structured data extraction working
- ✅ No staging needed (JSON fits in payload)

---

### Test 4.3: Integration Test Suite

**What this validates:** Comprehensive integration tests pass

```bash
cd apex-memory-system

# Document ingestion E2E
pytest tests/integration/test_temporal_ingestion_workflow.py -v -m integration

# JSON ingestion E2E
pytest tests/integration/test_json_integration_e2e.py -v -m integration

# Staging lifecycle
pytest tests/integration/test_document_workflow_staging.py -v -m integration
```

**Expected Output:**
```
====================== X passed in Y.YYs ======================
```

**What You'll Know:**
- ✅ Integration tests validate E2E scenarios
- ✅ Multiple workflows can run concurrently
- ✅ Staging lifecycle managed correctly

---

### Layer 4 Checkpoint

**Record in results template:**

- [ ] DocumentIngestionWorkflow: ✅ E2E success
- [ ] StructuredDataIngestionWorkflow: ✅ E2E success
- [ ] Integration tests: ✅ All passing
- [ ] Temporal UI: ✅ Workflows visible
- [ ] Staging: ✅ Cleaned after success

**What You Now Know:**
- ✅ Workflows **orchestrate correctly**
- ✅ Complete ingestion pipeline functional
- ✅ Both document and JSON workflows working

**If ALL passed:** ✅ Proceed to Layer 5
**If ANY failed:** ❌ Check Temporal logs, worker logs, activity failures

---

## Layer 5: API Endpoints (15 min)

**Goal:** Validate FastAPI endpoints work correctly.

### Why This Matters

The API is the **user-facing interface**. It must trigger workflows, return status, and handle errors gracefully.

---

### Test 5.1: Health Check

**What this validates:** API responding, database connectivity

```bash
curl http://localhost:8000/api/v1/health | jq
```

**Expected Output:**
```json
{
  "status": "healthy",
  "databases": {
    "neo4j": true,
    "postgres": true,
    "qdrant": true,
    "redis": true
  }
}
```

**What You'll Know:**
- ✅ API server running
- ✅ Can connect to all 4 databases
- ✅ Health endpoint functional

---

### Test 5.2: Document Ingestion

**What this validates:** File upload triggers workflow

```bash
# Create test file
echo "Test document for API ingestion" > /tmp/api_test.txt

# Upload document
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/api_test.txt" \
  -F "source=api" | jq
```

**Expected Output:**
```json
{
  "success": true,
  "uuid": "<uuid>",
  "workflow_id": "ingest-<uuid>",
  "filename": "api_test.txt",
  "source": "api",
  "status": "processing",
  "staging_path": "/tmp/apex-staging/api/<uuid>/api_test.txt"
}
```

**What You'll Know:**
- ✅ File upload accepted
- ✅ Workflow triggered
- ✅ Staging path created
- ✅ Workflow ID returned for tracking

**Save the workflow_id for next test**

---

### Test 5.3: Workflow Status Query

**What this validates:** Status endpoint tracks workflow progress

```bash
# Replace with actual workflow_id from above
WORKFLOW_ID="ingest-<uuid>"

curl http://localhost:8000/api/v1/workflow/${WORKFLOW_ID}/status | jq
```

**Expected Output:**
```json
{
  "uuid": "<uuid>",
  "workflow_id": "ingest-<uuid>",
  "status": "completed",
  "document_id": "<doc_id>",
  "source": "api"
}
```

**What You'll Know:**
- ✅ Status endpoint working
- ✅ Workflow completed successfully
- ✅ API can query Temporal

---

### Test 5.4: JSON Ingestion

**What this validates:** Structured data endpoint works

```bash
curl -X POST http://localhost:8000/api/v1/ingest-structured \
  -H "Content-Type: application/json" \
  -d '{
    "data_id": "API-TEST-001",
    "source": "frontapp",
    "source_endpoint": "{\"message_id\": \"MSG-001\", \"content\": \"Test message\"}",
    "data_type": "message"
  }' | jq
```

**Expected Output:**
```json
{
  "success": true,
  "data_id": "API-TEST-001",
  "workflow_id": "ingest-json-API-TEST-001",
  "source": "frontapp",
  "data_type": "message",
  "status": "processing"
}
```

**What You'll Know:**
- ✅ JSON endpoint accepting structured data
- ✅ JSON workflow triggered
- ✅ No staging needed

---

### Test 5.5: Error Handling

**What this validates:** API returns correct error codes

**Test Invalid File Type:**
```bash
echo "test" > /tmp/test.xyz

curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/test.xyz" \
  -F "source=api"
```

**Expected:** `400 Bad Request` (unsupported format)

**What You'll Know:**
- ✅ File type validation working
- ✅ Correct HTTP error codes

---

### Layer 5 Checkpoint

**Record in results template:**

- [ ] /health: ✅ Returns database status
- [ ] /ingest: ✅ Accepts document, starts workflow
- [ ] /ingest-structured: ✅ Accepts JSON, starts workflow
- [ ] /workflow/{id}/status: ✅ Returns workflow status
- [ ] Error handling: ✅ Returns correct HTTP codes

**What You Now Know:**
- ✅ API layer **fully functional**
- ✅ Workflows triggered via REST endpoints
- ✅ Status tracking working

**If ALL passed:** ✅ Proceed to Layer 6
**If ANY failed:** ❌ Check FastAPI logs, Temporal connection

---

## Layer 6: Query Router (15 min)

**Goal:** Validate intent classification and database routing.

### Why This Matters

The query router determines **which database handles each query**. Incorrect routing means poor results.

---

### Test 6.1: LLM Intent Classifier

**What this validates:** Claude 3.5 Sonnet classifying intents correctly

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

**Expected Output:**
```
Graph query: graph (confidence: 0.90+)
Temporal query: temporal (confidence: 0.85+)
Semantic query: semantic (confidence: 0.90+)
Metadata query: metadata (confidence: 0.95+)
```

**What You'll Know:**
- ✅ LLM classifier achieving >80% confidence
- ✅ Intent categories correct
- ✅ Claude API accessible

**If confidence <0.80:** Review prompt engineering, check API key

---

### Test 6.2: Cache Performance

**What this validates:** Redis cache improving query latency

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python3 << 'EOF'
from apex_memory.query_router.cache import QueryCache
import time

cache = QueryCache()

query = "list all active drivers"
result = {"data": ["Driver 1", "Driver 2"]}

# Test cache write
cache.set(query, result, ttl=60)
print("✅ Cache write successful")

# Test cache read
cached = cache.get(query)
if cached == result:
    print("✅ Cache hit successful")
else:
    print("❌ Cache miss (unexpected)")

# Test TTL
time.sleep(2)
cached = cache.get(query)
if cached:
    print("✅ Cache still valid (within TTL)")
else:
    print("❌ Cache expired prematurely")

cache.close()
EOF
```

**Expected Output:**
```
✅ Cache write successful
✅ Cache hit successful
✅ Cache still valid (within TTL)
```

**What You'll Know:**
- ✅ Query cache functional
- ✅ TTL working correctly
- ✅ Cache can reduce latency for repeat queries

---

### Layer 6 Checkpoint

**Record in results template:**

- [ ] LLM Classifier: ✅ All 4 intents >0.80 confidence
- [ ] Database Routing: ✅ Correct DB for each intent
- [ ] Cache: ✅ Write/read/TTL working

**What You Now Know:**
- ✅ Query router **correctly classifying** queries
- ✅ Cache layer reducing latency
- ✅ Intent-based routing functional

**If ALL passed:** ✅ Proceed to Integration Testing
**If ANY failed:** ❌ Check Claude API, routing logic

---

## Integration Testing (30 min)

**Goal:** Test cross-layer integrations and critical integration points.

### Why This Matters

Individual layers may work, but **integration points** can fail. This validates data flows correctly between layers.

---

### Test 7.1: API → Temporal Integration

**What this validates:** API triggers workflows in Temporal

```bash
# Upload document via API
WORKFLOW_ID=$(curl -s -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/test.txt" \
  -F "source=api" | jq -r '.workflow_id')

echo "Workflow ID: $WORKFLOW_ID"

# Wait 5 seconds
sleep 5

# Check Temporal UI
open http://localhost:8088
# Search for $WORKFLOW_ID
# Verify: Workflow running or completed
```

**Expected:** Workflow appears in Temporal UI within 5 seconds

**What You'll Know:**
- ✅ API successfully triggers Temporal workflows
- ✅ Workflow ID returned matches Temporal execution

---

### Test 7.2: Enhanced Saga → 4 Databases

**What this validates:** Parallel writes to all databases work

```bash
cd apex-memory-system
pytest tests/unit/test_database_writer.py -v -k "test_parallel_write"
```

**Expected:** Test passes, all 4 databases written

**What You'll Know:**
- ✅ Saga coordinates parallel writes
- ✅ All databases written simultaneously
- ✅ Atomic commit working

---

### Test 7.3: Graphiti → Neo4j Storage

**What this validates:** Extracted entities stored in Neo4j

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

**Expected:**
```
✅ Graphiti extracted 1-2 entities
✅ Entities found in Neo4j: 1-2
```

**What You'll Know:**
- ✅ Graphiti → Neo4j integration working
- ✅ Entities persisted correctly

---

### Integration Checkpoint

**Record in results template:**

- [ ] API → Temporal: ✅ Workflows triggered
- [ ] Saga → Databases: ✅ Parallel writes work
- [ ] Graphiti → Neo4j: ✅ Entities stored

**What You Now Know:**
- ✅ All layers **integrate correctly**
- ✅ Data flows end-to-end
- ✅ No integration failures

**If ALL passed:** ✅ System integrated correctly
**If ANY failed:** ❌ Check connection between layers

---

## Load & Chaos Testing (1 hour, optional)

**Goal:** Validate system resilience under stress and failures.

### Why This Matters

Production systems face **concurrent load** and **infrastructure failures**. This validates graceful degradation.

---

### Test 8.1: Concurrent Workflow Execution

**What this validates:** System handles 10+ docs/second

```bash
cd apex-memory-system
pytest tests/load/test_concurrent_workflows.py -v -m load
```

**Expected:** All workflows complete, zero errors

**What You'll Know:**
- ✅ System achieves target throughput
- ✅ No resource exhaustion under load
- ✅ Metrics accurate during high load

---

### Test 8.2: Database Failure Scenario

**What this validates:** Saga rollback on database failure

```bash
# Stop PostgreSQL
docker-compose stop postgres

# Trigger workflow
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/test.txt" \
  -F "source=api"

# Check Temporal UI: Workflow failed, rollback triggered
# Expected: Saga status ROLLED_BACK

# Restart PostgreSQL
docker-compose start postgres

# Retry workflow (should succeed)
```

**What You'll Know:**
- ✅ Saga detects failures
- ✅ Rollback prevents partial writes
- ✅ System recovers after DB restart

---

### Load Testing Checkpoint

**Record in results template:**

- [ ] Concurrent Load: ✅ 10+ workflows succeed
- [ ] Database Failure: ✅ Rollback triggered
- [ ] Recovery: ✅ System recovers after restart

**What You Now Know:**
- ✅ System **resilient under stress**
- ✅ Failure handling working correctly

---

## Results Interpretation

### How to Read Test Outputs

**✅ Success Indicators:**
- Tests pass with `PASSED` or `OK`
- Expected outputs match actual outputs
- No error messages in logs
- Metrics recording correctly

**❌ Failure Indicators:**
- Tests fail with `FAILED` or `ERROR`
- Unexpected error messages
- Metrics not recording
- Rollback triggered unexpectedly

### Key Metrics to Monitor

**During Testing:**
- Open Grafana: http://localhost:3001/d/temporal-ingestion
- Check Prometheus: http://localhost:9090

**Metrics to Validate:**
- `temporal_workflow_completed_total` - Workflows completing
- `temporal_activity_duration_seconds` - Activity latency
- `redis_cache_hit_rate` - Cache effectiveness
- `temporal_database_writes_total` - Write throughput

**Target Values:**
- Query latency (P90): <1s
- Cache hit rate: >60%
- Throughput: 10+ docs/sec
- Workflow duration: <60s

---

## Troubleshooting Common Failures

### Enhanced Saga Tests Failing

**Symptom:** `pytest tests/` shows failures
**Likely Cause:** Recent code changes broke baseline

**Fix:**
1. Identify which test failed: `pytest tests/ -v | grep FAILED`
2. Run specific test with full output: `pytest tests/unit/test_database_writer.py::test_name -v --tb=long`
3. Check error message for root cause
4. Fix code or revert breaking change
5. Re-run baseline tests

---

### Graphiti Extraction Failing

**Symptom:** `❌ Graphiti extraction failed`
**Likely Causes:**
- OpenAI API key missing/invalid
- Rate limit exceeded
- Neo4j connection failed

**Fix:**
1. Check API key: `cat apex-memory-system/.env | grep OPENAI_API_KEY`
2. Test Neo4j: `curl http://localhost:7474`
3. Wait 60s if rate limited
4. Verify graphiti-core version: `pip show graphiti-core`

---

### Workflow Not Appearing in Temporal UI

**Symptom:** Workflow not visible after API call
**Likely Causes:**
- Worker not running
- Wrong task queue
- Temporal server down

**Fix:**
1. Check worker: `ps aux | grep dev_worker`
2. Check Temporal: `temporal server health`
3. Restart worker if needed
4. Check API logs for errors

---

### Database Write Failed

**Symptom:** `Saga status: ROLLED_BACK`
**Likely Causes:**
- Database not running
- Connection refused
- Schema/collection missing

**Fix:**
1. Check all DBs: `docker ps | grep -E "postgres|neo4j|qdrant|redis"`
2. Test connectivity (see Pre-Flight section)
3. Check individual writer (see Layer 1 tests)
4. Verify rollback completed successfully

---

## Deployment Decision (GO/NO-GO)

### Critical GO Criteria

**You MUST have ALL of these to deploy:**

✅ **Enhanced Saga: 121/121 tests passing**
✅ **All databases: Healthy and connectable**
✅ **Workflows: Both DocumentIngestion + StructuredDataIngestion E2E success**
✅ **API: All endpoints responding correctly**
✅ **Metrics: Recording correctly in Prometheus**
✅ **Zero critical errors** in logs during test runs

### Optional GO Criteria

**Nice to have, but not deployment blockers:**

⚠️ Load testing: 10+ docs/sec achieved
⚠️ Cache hit rate: >60%
⚠️ Query latency: <1s P90
⚠️ Chaos testing: Graceful degradation validated

### Definite NO-GO Criteria

**If ANY of these are true, DO NOT deploy:**

❌ **Enhanced Saga tests failing** (data integrity risk)
❌ **Any database unreachable** (system won't function)
❌ **Workflows not completing E2E** (ingestion broken)
❌ **Graphiti extraction failing** (accuracy <90%)
❌ **Metrics not recording** (no observability)
❌ **Orphaned resources accumulating** (resource leak)

---

### Final Checklist

**Before deployment, verify:**

- [ ] All Layer 1-6 tests: ✅ PASSED
- [ ] Integration tests: ✅ PASSED
- [ ] Baseline 121 tests: ✅ PASSED
- [ ] Grafana dashboard: ✅ Functional
- [ ] Prometheus metrics: ✅ Recording
- [ ] No orphaned staging files
- [ ] No orphaned Graphiti episodes
- [ ] Environment variables: ✅ Set correctly
- [ ] Documentation: ✅ Up to date

---

## GO / NO-GO Decision

**Based on test results, make your decision:**

### ✅ GO FOR DEPLOYMENT

**If you checked ALL critical criteria:**
- Enhanced Saga: 121/121 ✅
- All databases: Healthy ✅
- Workflows: E2E success ✅
- API: Functional ✅
- Metrics: Recording ✅
- Zero critical errors ✅

**Confidence Level:** HIGH
**Risk Level:** LOW
**Deployment Recommendation:** PROCEED

---

### ❌ NO-GO - DO NOT DEPLOY

**If ANY critical criteria failed:**
- Enhanced Saga: X/121 ❌
- Database issues ❌
- Workflow failures ❌
- Metrics not recording ❌

**Confidence Level:** LOW
**Risk Level:** HIGH
**Deployment Recommendation:** FIX ISSUES FIRST

---

### ⚠️ CONDITIONAL GO

**If critical criteria pass, but optional criteria fail:**
- Critical tests: ✅ All passing
- Load testing: ❌ Only 8 docs/sec
- Cache hit rate: ❌ 45%

**Confidence Level:** MEDIUM
**Risk Level:** MEDIUM
**Deployment Recommendation:** DEPLOY with monitoring, optimize later

---

## Quick Reference Commands

### Start All Services

```bash
cd apex-memory-system/docker
docker-compose up -d
sleep 30
docker ps
```

### Start Temporal & Worker

```bash
# Temporal server
temporal server start-dev &

# Worker
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python src/apex_memory/temporal/workers/dev_worker.py &
```

### Start API

```bash
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH uvicorn apex_memory.main:app --reload --port 8000 &
```

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

### Check Metrics

```bash
# Prometheus
curl http://localhost:9090/api/v1/query?query=temporal_workflow_completed_total

# Grafana
open http://localhost:3001/d/temporal-ingestion
```

### Cleanup

```bash
# Flush Redis
redis-cli FLUSHDB

# Clean staging
rm -rf /tmp/apex-staging/*

# Reset circuit breakers
pkill -f dev_worker
cd apex-memory-system
PYTHONPATH=src:$PYTHONPATH python src/apex_memory/temporal/workers/dev_worker.py &
```

---

## Summary

**You've completed the Testing Kit Implementation Guide!**

**Time Spent:** ~3-4 hours (comprehensive) or ~1 hour (quick validation)

**What You Now Know:**
- ✅/❌ System health at all 6 layers
- ✅/❌ Integration points working correctly
- ✅/❌ Performance metrics vs. targets
- ✅/❌ Production readiness (GO/NO-GO)

**Next Steps:**
1. Record all results in `results/RESULTS-TEMPLATE.md`
2. Make GO/NO-GO decision based on criteria
3. If GO: Proceed to deployment
4. If NO-GO: Fix issues, re-run tests

**For Detailed Reference:**
- See `TESTING-KIT.md` for comprehensive testing documentation
- See `../SYSTEM-MANUAL.html` for system architecture

---

**Good luck with deployment! 🚀**

**Last Updated:** 2025-10-20
**Version:** 1.0
