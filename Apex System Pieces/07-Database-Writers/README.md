# 07 - Database Writers

## 🎯 Purpose

Specialized write operations for each of the 4 databases with saga pattern orchestration for atomic multi-DB writes. Ensures data consistency across all databases or rollback on any failure.

## 🛠 Technical Stack

- **Neo4j Driver:** Graph writes (nodes, relationships)
- **psycopg2:** PostgreSQL writes (metadata, vectors)
- **Qdrant Client:** Vector collection writes
- **Redis Client:** Cache writes with TTL

## 📂 Key Files (4 Writers + Orchestrator)

### Database-Specific Writers

**1. neo4j_writer.py** (16,943 bytes)
```python
class Neo4jWriter:
    """Write documents, entities, relationships to Neo4j."""
    def write_document_graph(doc, entities, relationships):
        # Creates Document node + Entity nodes + relationships
```

**2. postgres_writer.py** (30,214 bytes)
```python
class PostgresWriter:
    """Write metadata + vectors to PostgreSQL."""
    def write_document(doc, chunks, embeddings):
        # INSERT INTO documents, chunks (with pgvector)
```

**3. qdrant_writer.py** (15,660 bytes)
```python
class QdrantWriter:
    """Write vectors to Qdrant collection."""
    def write_vectors(doc_id, chunk_vectors, payloads):
        # Upsert to 'documents' collection
```

**4. redis_writer.py** (13,509 bytes)
```python
class RedisWriter:
    """Write cached results with TTL."""
    def write_cache(key, value, ttl=3600):
        # SET with expiration
```

### Saga Orchestrator

**5. database_writer.py** (47,604 bytes)
```python
class DatabaseWriteOrchestrator:
    """Atomic multi-DB writes with rollback."""
    
    def write_document(doc, chunks, entities, embeddings):
        # Phase 1: Write to all 4 databases in parallel
        results = await asyncio.gather(
            neo4j_writer.write_document_graph(...),
            postgres_writer.write_document(...),
            qdrant_writer.write_vectors(...),
            redis_writer.write_cache(...)
        )
        
        # Phase 2: Check all succeeded
        if any(r.failed for r in results):
            # Rollback all
            await self.rollback_all(doc_id)
            raise IngestionError("Partial write detected")
        
        return Success(document_id=doc_id)
```

## Saga Pattern Flow

```
┌─────────────────────────────────────┐
│ Orchestrator.write_document()      │
└─────────────────────────────────────┘
              ↓
    ┌─────────────────────┐
    │ Parallel Writes     │
    ├─────────────────────┤
    │ Neo4j    → Success  │
    │ PostgreSQL → Success│
    │ Qdrant   → Success  │
    │ Redis    → FAILURE  │
    └─────────────────────┘
              ↓
    ┌─────────────────────┐
    │ Rollback Detected   │
    ├─────────────────────┤
    │ Delete from Neo4j   │
    │ Delete from PostgreSQL│
    │ Delete from Qdrant  │
    └─────────────────────┘
              ↓
    Return IngestionError
```

## Example Usage

```python
from apex_memory.services.database_writer import DatabaseWriteOrchestrator

orchestrator = DatabaseWriteOrchestrator(
    neo4j_driver=neo4j_driver,
    postgres_pool=postgres_pool,
    qdrant_client=qdrant_client,
    redis_client=redis_client
)

result = orchestrator.write_document(
    document=doc,
    chunks=chunks,
    entities=entities,
    embeddings=embeddings
)

if result.success:
    print(f"✅ Document {result.document_id} written to all databases")
else:
    print(f"❌ Rollback performed: {result.error}")
```

---

**Previous Component:** [06-Data-Models](../06-Data-Models/README.md)
**Next Component:** [08-Frontend-Application](../08-Frontend-Application/README.md)
