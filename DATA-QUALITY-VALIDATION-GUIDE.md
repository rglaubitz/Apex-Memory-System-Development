# Data Quality Validation Guide

**Question:** "How will I know the data going into the database is structured and connected well?"

**Answer:** You've already built comprehensive monitoring. Here's how to use it.

---

## 🎯 What You've Already Built

### **27 Temporal Metrics** (Section 9 Complete)

Your system tracks:
- ✅ Chunks per document
- ✅ Entities per document
- ✅ Entities by type (customer, invoice, equipment, person, project)
- ✅ Embeddings per document
- ✅ Database write success/failure
- ✅ Workflow success rate
- ✅ Activity-level failures

**Location:** `src/apex_memory/monitoring/metrics.py`

---

## 📊 How to Validate Data Quality (Live)

### **Method 1: Grafana Dashboard (Best for Real-Time)**

**Access:** http://localhost:3001/d/temporal-ingestion

**Credentials:** admin / apexmemory2024

**What to Check:**

#### Panel: "Chunks Per Document (P50/P90/P99)"
```
Good: P50 = 10-30 chunks (means documents are being split properly)
Warning: P50 < 5 chunks (documents might be too small or parser failing)
Alert: P50 = 0 (parser completely broken)
```

#### Panel: "Entities Per Document (P50/P90/P99)"
```
Good: P50 = 5-20 entities (Graphiti extracting properly)
Warning: P50 < 3 entities (extraction not finding much)
Alert: P50 = 0 (extraction completely broken - check Graphiti)
```

#### Panel: "Entity Types Distribution"
```
Good: Mix of Customer, Invoice, Equipment, Person, Project
Warning: Only 1-2 types showing (extraction too narrow)
Alert: No types at all (entity classification broken)
```

#### Panel: "Workflow Success Rate"
```
Good: > 95% success rate
Warning: 90-95% (some failures happening)
Alert: < 90% (systemic issues)
```

#### Panel: "Database Write Success"
```
Good: 100% success for all 4 databases
Warning: 1 database failing (check logs for which)
Alert: Multiple databases failing (saga rollback working but check root cause)
```

---

### **Method 2: Temporal UI (Best for Debugging)**

**Access:** http://localhost:8088

**What to Check:**

1. **Click on a completed workflow**
2. **View workflow history** - See each activity:
   ```
   ✅ pull_and_stage_document_activity
   ✅ parse_document_activity → Check: Did it extract text?
   ✅ extract_entities_activity → Check: How many entities?
   ✅ generate_embeddings_activity → Check: How many embeddings?
   ✅ write_to_databases_activity → Check: All 4 databases succeed?
   ```

3. **Click on each activity** - See input/output:
   ```json
   // extract_entities_activity output
   {
     "entities": [...],  // Check: Are there entities?
     "graphiti_episode_uuid": "doc-123",
     "edges_created": 5  // Check: Are relationships created?
   }
   ```

4. **Check for failed workflows** - Red X icon
   - Click to see which activity failed
   - View error message
   - See retry attempts

---

### **Method 3: Direct Database Queries (Best for Deep Inspection)**

#### PostgreSQL - Check Document Quality
```bash
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory

-- How many documents ingested?
SELECT COUNT(*) FROM documents;

-- Recent documents with chunk/entity counts
SELECT
  title,
  doc_type,
  chunk_count,
  LENGTH(content) as content_length,
  created_at
FROM documents
ORDER BY created_at DESC
LIMIT 10;

-- Documents with NO chunks (BAD - parsing failed)
SELECT uuid, title, doc_type
FROM documents
WHERE chunk_count = 0;

-- Documents with NO content (BAD - extraction failed)
SELECT uuid, title, doc_type
FROM documents
WHERE content IS NULL OR LENGTH(content) < 100;

-- Entities extracted per document
SELECT
  d.title,
  COUNT(de.entity_uuid) as entity_count
FROM documents d
LEFT JOIN document_entities de ON d.uuid = de.document_uuid
GROUP BY d.uuid, d.title
ORDER BY entity_count DESC;

-- Entity type distribution (should see variety)
SELECT
  entity_type,
  COUNT(*) as count,
  ROUND(AVG(confidence), 2) as avg_confidence
FROM entities
GROUP BY entity_type
ORDER BY count DESC;
```

#### Neo4j - Check Relationship Quality
**Access:** http://localhost:7474

**Credentials:** neo4j / apexmemory2024

```cypher
// How many entities in graph?
MATCH (e:Entity) RETURN COUNT(e);

// How many relationships?
MATCH ()-[r]->() RETURN COUNT(r);

// Relationship type distribution
MATCH ()-[r]->()
RETURN type(r) as rel_type, COUNT(*) as count
ORDER BY count DESC;

// Entities with NO relationships (might be isolated - investigate)
MATCH (e:Entity)
WHERE NOT (e)-[]-()
RETURN e.name, e.entity_type
LIMIT 10;

// Entities with LOTS of relationships (central nodes - good!)
MATCH (e:Entity)-[r]-()
RETURN e.name, e.entity_type, COUNT(r) as connections
ORDER BY connections DESC
LIMIT 10;

// Check temporal properties on edges
MATCH ()-[r]->()
WHERE r.valid_from IS NOT NULL
RETURN
  type(r) as relationship,
  r.valid_from,
  r.valid_to,
  r.confidence
LIMIT 10;
```

#### Qdrant - Check Embedding Quality
```python
# In Python shell
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6335)

# How many vectors stored?
collection_info = client.get_collection("apex_documents")
print(f"Total vectors: {collection_info.points_count}")

# Search test (should return relevant results)
from openai import OpenAI
openai_client = OpenAI()

query = "invoices from ACME Corporation"
embedding = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=query
).data[0].embedding

results = client.search(
    collection_name="apex_documents",
    query_vector=embedding,
    limit=5,
    score_threshold=0.7
)

for result in results:
    print(f"Score: {result.score}")
    print(f"Title: {result.payload['title']}")
    print(f"Content preview: {result.payload['content'][:200]}")
    print("---")
```

#### Graphiti - Check LLM Extraction Quality
```python
from apex_memory.services.graphiti_service import GraphitiService
from apex_memory.config import Settings

settings = Settings()
graphiti = GraphitiService(
    neo4j_uri=settings.neo4j_uri,
    neo4j_user=settings.neo4j_user,
    neo4j_password=settings.neo4j_password,
)

# Get Graphiti stats
stats = await graphiti.get_graph_stats()
print(f"Nodes: {stats['node_count']}")
print(f"Edges: {stats['edge_count']}")
print(f"Node types: {stats['node_labels']}")
print(f"Edge types: {stats['relationship_types']}")

# Search by entity
results = await graphiti.search(
    query="ACME Corporation",
    limit=10
)

for node in results.nodes:
    print(f"Entity: {node.name}")
    print(f"Type: {node.entity_type}")
    print(f"Relationships: {len(node.edges)}")
```

---

## ✅ What "Good" Data Quality Looks Like

### **Good Metrics Baseline**

| Metric | Good Range | Warning | Critical |
|--------|-----------|---------|----------|
| **Chunks per doc** | 10-50 | < 5 or > 100 | 0 |
| **Entities per doc** | 5-30 | < 3 or > 100 | 0 |
| **Entity types** | 3-5 types | 1-2 types | 0 types |
| **Embeddings per doc** | = chunks + 1 | < chunks | 0 |
| **Workflow success** | > 95% | 90-95% | < 90% |
| **DB write success** | 100% | 99% | < 99% |
| **Graph relationships** | 2-10 per entity | < 1 | 0 |

### **Good Data Examples**

#### Example 1: Well-Structured Invoice Document
```json
{
  "document": {
    "title": "Invoice INV-2025-001.pdf",
    "chunk_count": 12,
    "entities_extracted": 8,
    "content_length": 4500
  },
  "entities": [
    {"type": "invoice", "name": "INV-2025-001", "confidence": 0.95},
    {"type": "customer", "name": "ACME Corp", "confidence": 0.92},
    {"type": "person", "name": "John Smith", "confidence": 0.88},
    ...
  ],
  "relationships": [
    {"from": "INV-2025-001", "to": "ACME Corp", "type": "ISSUED_TO"},
    {"from": "John Smith", "to": "ACME Corp", "type": "WORKS_WITH"},
    ...
  ]
}
```

**Why it's good:**
- ✅ Reasonable chunk count (12 chunks for 4500 chars ≈ 375 chars/chunk)
- ✅ Multiple entities extracted (8)
- ✅ High confidence (> 0.85)
- ✅ Relationships created between entities
- ✅ Entity types are specific (invoice, customer, person)

#### Example 2: Well-Structured Equipment Manual
```json
{
  "document": {
    "title": "CAT-950-Manual.pdf",
    "chunk_count": 45,
    "entities_extracted": 15,
    "content_length": 18000
  },
  "entities": [
    {"type": "equipment", "name": "CAT 950 Loader", "confidence": 0.96},
    {"type": "person", "name": "Operator: Mike Davis", "confidence": 0.89},
    {"type": "customer", "name": "ABC Construction", "confidence": 0.91},
    ...
  ],
  "relationships": [
    {"from": "Mike Davis", "to": "CAT 950 Loader", "type": "OPERATES"},
    {"from": "ABC Construction", "to": "CAT 950 Loader", "type": "OWNS"},
    ...
  ]
}
```

**Why it's good:**
- ✅ Chunk count scales with content (45 chunks for 18K chars)
- ✅ Many entities (15) from technical manual
- ✅ Domain-specific extraction (equipment, operators)
- ✅ Temporal relationships (who operates what)

---

## 🚨 What "Bad" Data Quality Looks Like

### **Bad Example 1: Parser Failure**
```json
{
  "document": {
    "title": "corrupted.pdf",
    "chunk_count": 0,  // ❌ NO CHUNKS
    "entities_extracted": 0,  // ❌ NO ENTITIES
    "content_length": 45  // ❌ ALMOST NO CONTENT
  }
}
```

**Diagnosis:** PDF parsing failed
**Fix:** Check Docling parser, try different PDF

### **Bad Example 2: Poor Entity Extraction**
```json
{
  "document": {
    "title": "invoice-123.pdf",
    "chunk_count": 15,  // ✅ Chunks OK
    "entities_extracted": 1,  // ❌ VERY FEW ENTITIES
    "content_length": 5000  // ✅ Content OK
  },
  "entities": [
    {"type": "invoice", "name": "123", "confidence": 0.45}  // ❌ LOW CONFIDENCE
  ]
}
```

**Diagnosis:** Graphiti extraction underperforming
**Fix:**
- Check if GPT-5 API key is valid
- Check if custom entity types are loaded
- Verify document has extractable entities

### **Bad Example 3: No Relationships**
```json
{
  "document": {
    "title": "customer-notes.pdf",
    "chunk_count": 20,  // ✅ Chunks OK
    "entities_extracted": 10,  // ✅ Entities OK
    "relationships_created": 0  // ❌ NO CONNECTIONS
  }
}
```

**Diagnosis:** Entities extracted but not connected
**Fix:**
- Check Graphiti edge extraction
- Verify edge types are defined
- Check if relationships exist in source text

---

## 🔍 Data Quality Debugging Workflow

### **Step 1: Upload Test Document**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@test-invoice.pdf" \
  -F "source=test"
```

### **Step 2: Check Temporal UI**
1. Go to http://localhost:8088
2. Find your workflow (search by document name)
3. Click to view execution
4. Check each activity output:
   - **parse_document_activity** - Did it extract text?
   - **extract_entities_activity** - How many entities? Which types?
   - **generate_embeddings_activity** - Embeddings count match chunks?
   - **write_to_databases_activity** - All 4 DBs succeed?

### **Step 3: Check Grafana Metrics**
1. Go to http://localhost:3001/d/temporal-ingestion
2. Look at last 5 minutes
3. Check:
   - Chunks per document histogram (should show your doc)
   - Entities per document histogram
   - Entity types distribution

### **Step 4: Validate in Databases**
```sql
-- PostgreSQL: Find your document
SELECT uuid, title, chunk_count, created_at
FROM documents
WHERE title LIKE '%test-invoice%';

-- Get document UUID from above, then check entities
SELECT e.name, e.entity_type, e.confidence
FROM entities e
JOIN document_entities de ON e.uuid = de.entity_uuid
WHERE de.document_uuid = '<YOUR_UUID>';
```

```cypher
-- Neo4j: Check relationships
MATCH (e:Entity)-[r]->(e2:Entity)
WHERE e.name CONTAINS 'test'
RETURN e.name, type(r), e2.name
LIMIT 10;
```

### **Step 5: Test Search Quality**
```bash
# Query via API
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "find invoices from test", "limit": 5}'
```

**Good response:** Returns your test document in top 3 results
**Bad response:** Doesn't return your document or returns with low score

---

## 📊 Data Quality Dashboards

### **Dashboard 1: Grafana - Temporal Ingestion**
**URL:** http://localhost:3001/d/temporal-ingestion
**What it shows:**
- Workflow success rate
- Activity failures
- Chunks/entities per document
- Database write success
- Performance metrics

### **Dashboard 2: Temporal UI**
**URL:** http://localhost:8088
**What it shows:**
- Individual workflow executions
- Activity inputs/outputs
- Error messages
- Retry history
- Execution timeline

### **Dashboard 3: Prometheus (Raw Metrics)**
**URL:** http://localhost:9090
**Example Queries:**
```promql
# Average entities per document (last hour)
avg(apex_temporal_entities_per_document)

# Documents with zero entities (bad!)
count(apex_temporal_entities_per_document == 0)

# Entity extraction success rate
rate(apex_temporal_activity_completed_total{activity_name="extract_entities_activity", status="success"}[5m])

# Workflow failure rate
rate(apex_temporal_workflow_completed_total{status="failed"}[5m])
```

---

## 🎯 Automated Quality Alerts (Already Built!)

**Location:** `monitoring/alerts/rules.yml`

**12 Alert Rules Including:**

1. **High Workflow Failure Rate** - > 10% failures in 5 minutes
2. **Zero Entities Extracted** - Documents with no entities
3. **Zero Chunks Created** - Parsing failures
4. **Database Write Failures** - Saga rollback happening
5. **High Activity Retry Rate** - Activities struggling
6. **Workflow Duration** - Taking too long (> 5 min)

**How to Check Alerts:**
1. Go to Prometheus: http://localhost:9090/alerts
2. See active alerts (if any are firing)
3. Get alert notifications (configure in alerts/rules.yml)

---

## ✅ Quality Validation Checklist

Before deploying to production, validate:

### **Data Completeness**
- [ ] Every document has content (no empty docs)
- [ ] Every document has chunks (chunk_count > 0)
- [ ] Most documents have entities (> 80% with entities > 0)
- [ ] Embeddings generated (embeddings_count = chunks + 1)

### **Data Accuracy**
- [ ] Entity types are correct (customer, invoice, equipment, etc.)
- [ ] Entity confidence is high (avg > 0.75)
- [ ] Relationships exist (edges_created > 0 for most)
- [ ] Temporal properties set (valid_from, confidence)

### **Data Connectivity**
- [ ] Entities connected in Neo4j graph
- [ ] Relationships make sense (invoice → customer, operator → equipment)
- [ ] Communities detected (related entities clustered)
- [ ] Search returns connected results

### **Data Performance**
- [ ] Vector search returns relevant results (score > 0.7)
- [ ] Graph queries return in < 1 second
- [ ] Cache hit rate > 70% for repeat queries
- [ ] Workflow success rate > 95%

---

## 🔧 Common Data Quality Issues

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| **No chunks** | chunk_count = 0 | Parser failed | Check Docling config, try different PDF |
| **No entities** | entities = 0 | Graphiti extraction failed | Check GPT-5 API key, verify entity types loaded |
| **Low confidence** | confidence < 0.5 | Poor LLM extraction | Use better prompts, check document quality |
| **No relationships** | edges = 0 | Edge extraction failed | Verify edge types defined, check source text |
| **Duplicate entities** | Same entity twice | Deduplication failed | Check entity_name normalization |
| **Wrong entity type** | Invoice labeled as Customer | Classification error | Improve entity type descriptions |
| **Slow ingestion** | Workflow > 5 min | LLM or DB slow | Check API rate limits, DB connections |
| **Workflow failures** | Status = failed | Activity error | Check Temporal UI for error message |

---

## 🎯 Next Steps

### **Immediate (5 minutes)**
1. Open Grafana: http://localhost:3001/d/temporal-ingestion
2. Ingest a test document
3. Watch metrics update in real-time

### **Short-term (1 hour)**
1. Run queries in PostgreSQL to check data
2. Explore Neo4j graph relationships
3. Test search quality with sample queries

### **Before Production**
1. Define your quality thresholds
2. Set up alert notifications
3. Create data quality report script
4. Add automated quality tests

---

## 📚 Further Reading

- **Monitoring Documentation:** `Apex System Pieces/10-Monitoring-Observability/README.md`
- **Temporal Metrics:** `src/apex_memory/monitoring/metrics.py`
- **Grafana Dashboard:** `monitoring/dashboards/temporal-ingestion.json`
- **Alert Rules:** `monitoring/alerts/rules.yml`

---

**Bottom Line:** You have COMPREHENSIVE data quality monitoring already built. Just open Grafana and start watching your data flow! 🎉
