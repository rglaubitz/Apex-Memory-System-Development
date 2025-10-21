# Phase 2: Complete Data Pipeline (API → Temporal → All Databases)

**Status:** UNVERIFIED
**Created:** 2025-10-20
**Researcher:** TBD
**Priority:** CRITICAL

---

## Hypothesis

The document ingestion data pipeline is incomplete. While components exist (API, Temporal workflows, database writers), the end-to-end pipeline from API request to all 4 databases may not be fully implemented or functional.

**Specific Gaps Suspected:**
1. API `/api/v1/ingest` may not trigger Temporal workflows correctly
2. `DocumentIngestionWorkflow` may not execute all activities end-to-end
3. Not all 4 databases (Neo4j, PostgreSQL, Qdrant, Redis) may be written to in parallel
4. Staging infrastructure may be missing (`/tmp/apex-staging/`)
5. Cleanup activities may not execute
6. Error handling and rollback may be incomplete

**What This Means:**
Users can upload documents via the UI/API, but the documents may not be fully processed through the entire pipeline, resulting in incomplete data storage across the multi-database system.

---

## Expected Behavior

### Complete End-to-End Pipeline:

```
User Upload
    ↓
POST /api/v1/ingest (file + source)
    ↓
API creates staging area → /tmp/apex-staging/[source]/[doc-uuid]/
    ↓
API triggers DocumentIngestionWorkflow via Temporal
    ↓
Temporal Worker picks up workflow
    ↓
Execute 6 Activities in Sequence:
    1. pull_and_stage_document_activity()
       → Copy file to staging
    2. parse_document_activity()
       → Extract text from PDF/DOCX/etc
    3. extract_entities_activity()
       → Graphiti LLM extraction
    4. generate_embeddings_activity()
       → OpenAI embeddings
    5. write_to_databases_activity()
       → Enhanced Saga writes to all 4 DBs in parallel
    6. cleanup_staging_activity()
       → Remove staged file
    ↓
Response to User:
{
  "success": true,
  "uuid": "doc-uuid",
  "workflow_id": "ingest-doc-uuid",
  "databases_written": ["neo4j", "postgres", "qdrant", "redis"]
}
```

### Where it should exist:

**1. API Endpoint:**
- Location: `apex-memory-system/src/apex_memory/api/routes/ingestion.py`
- Endpoint: `POST /api/v1/ingest`
- Functionality:
  - Accept file upload
  - Create staging directory
  - Trigger `DocumentIngestionWorkflow`
  - Return workflow ID

**2. Temporal Workflow:**
- Location: `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`
- Workflow: `DocumentIngestionWorkflow`
- All 6 activities orchestrated
- Saga pattern for rollback

**3. All 6 Activities:**
- Location: `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`
- Activities:
  - `pull_and_stage_document_activity()`
  - `parse_document_activity()`
  - `extract_entities_activity()`
  - `generate_embeddings_activity()`
  - `write_to_databases_activity()`
  - `cleanup_staging_activity()`

**4. Database Writers:**
- All 4 database writers functional:
  - `PostgresWriter.write_document()`
  - `Neo4jWriter.write_document()`
  - `QdrantWriter.write_embedding()`
  - `RedisWriter.set()` (cache)

**5. Staging Infrastructure:**
- Directory: `/tmp/apex-staging/`
- Subdirectories: `api/`, `local_upload/`, `webhook/`
- TTL-based cleanup (24h default)

### How it should work:

**User Flow:**
```
1. User uploads document via API
   POST /api/v1/ingest
   -F "file=@document.pdf"
   -F "source=api"

2. API creates staging:
   /tmp/apex-staging/api/[doc-uuid]/document.pdf

3. API triggers DocumentIngestionWorkflow

4. Workflow executes 6 activities

5. Document stored in all 4 databases:
   - PostgreSQL: Full text + metadata + embedding
   - Neo4j: Document node + entities + relationships
   - Qdrant: 1536-dim embedding vector
   - Redis: Cached metadata

6. Staging cleaned up:
   /tmp/apex-staging/api/[doc-uuid]/ deleted

7. API responds:
   {
     "success": true,
     "uuid": "doc-uuid-123",
     "workflow_id": "ingest-doc-uuid-123",
     "databases_written": ["neo4j", "postgres", "qdrant", "redis"],
     "staging_cleaned": true
   }
```

---

## Why Important

**Deployment Impact:** CRITICAL

**This is CRITICAL because:**

1. **Core Functionality:** Document ingestion is the primary feature of the system. If the pipeline is incomplete, the system cannot fulfill basic requirements.

2. **Data Integrity:** Incomplete pipeline → partial writes → data inconsistency across databases → unreliable retrieval.

3. **User Experience:** Users expect uploaded documents to be searchable. Incomplete pipeline means documents may not appear in search results.

4. **Resource Leaks:** If staging cleanup doesn't work, disk space fills up with orphaned files.

5. **Testing Validation:** The testing-kit assumes this pipeline works. If it doesn't, all tests validating it are invalid.

**Without a complete pipeline, deployment would result in data loss and system unreliability.**

---

## Research Plan

### Files to Check:

**API Layer:**
```bash
# Check ingestion API endpoint
grep -r "def ingest" apex-memory-system/src/apex_memory/api/routes/

# Check if API triggers Temporal
grep -r "execute_workflow" apex-memory-system/src/apex_memory/api/routes/ingestion.py

# Check API response structure
grep -r "workflow_id" apex-memory-system/src/apex_memory/api/routes/ingestion.py
```

**Temporal Workflow:**
```bash
# Check DocumentIngestionWorkflow definition
grep -r "class DocumentIngestionWorkflow" apex-memory-system/src/apex_memory/temporal/workflows/

# Check if all 6 activities are called
grep -r "pull_and_stage_document_activity" apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py
grep -r "cleanup_staging_activity" apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py

# Check saga pattern implementation
grep -r "rollback" apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py
```

**Activities:**
```bash
# Check all activities exist
ls apex-memory-system/src/apex_memory/temporal/activities/ingestion.py

# Verify all 6 activities defined
grep -r "@activity.defn" apex-memory-system/src/apex_memory/temporal/activities/ingestion.py | wc -l
# Should return: 6 or more
```

**Database Writers:**
```bash
# Check parallel write implementation
grep -r "write_document_parallel" apex-memory-system/src/apex_memory/database/

# Check Enhanced Saga
grep -r "class EnhancedSaga" apex-memory-system/src/apex_memory/services/

# Verify all 4 DB writers called
grep -r "PostgresWriter" apex-memory-system/src/apex_memory/database/database_writer.py
grep -r "Neo4jWriter" apex-memory-system/src/apex_memory/database/database_writer.py
grep -r "QdrantWriter" apex-memory-system/src/apex_memory/database/database_writer.py
grep -r "RedisWriter" apex-memory-system/src/apex_memory/database/database_writer.py
```

**Staging Infrastructure:**
```bash
# Check staging directory exists
ls -la /tmp/apex-staging/

# Check staging manager
grep -r "class StagingManager" apex-memory-system/src/apex_memory/services/

# Check cleanup logic
grep -r "cleanup_staging" apex-memory-system/src/apex_memory/temporal/activities/
```

### Tests to Run:

**Integration Tests:**
```bash
# Run document ingestion E2E test
pytest apex-memory-system/tests/integration/test_document_workflow_staging.py -v -m integration

# Check if all 4 databases written
# Should verify: PostgreSQL, Neo4j, Qdrant, Redis all have data

# Run staging cleanup test
pytest apex-memory-system/tests/integration/ -v -k "staging"
```

**API Tests:**
```bash
# Test document upload
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@/tmp/test.pdf" \
  -F "source=api"

# Expected response:
# {
#   "success": true,
#   "uuid": "...",
#   "workflow_id": "...",
#   "databases_written": ["neo4j", "postgres", "qdrant", "redis"]
# }
```

**Temporal Workflow Test:**
```bash
# Check workflow in Temporal UI
open http://localhost:8088
# Search for: ingest-*
# Verify: All 6 activities completed successfully

# Check staging cleaned
ls /tmp/apex-staging/api/
# Should be empty or only recent files
```

**Database Verification:**
```bash
# PostgreSQL
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory \
  -c "SELECT COUNT(*) FROM documents;"

# Neo4j
# Open http://localhost:7474
# Run: MATCH (d:Document) RETURN count(d)

# Qdrant
curl http://localhost:6333/collections/documents

# Redis
redis-cli KEYS "doc:*"
```

### Evidence Needed:

**To prove IMPLEMENTED:**
- [ ] API endpoint responds 200 with workflow_id
- [ ] Temporal workflow executes all 6 activities
- [ ] All 4 databases contain document data
- [ ] Staging directory created and cleaned
- [ ] Tests passing (integration + E2E)

**To prove MISSING:**
- [ ] API returns errors
- [ ] Workflow doesn't execute all activities
- [ ] Databases missing data (less than 4 DBs written)
- [ ] Staging not cleaned up
- [ ] Tests failing

### Success Criteria:

**Feature is IMPLEMENTED if:**
1. API successfully triggers workflow
2. All 6 activities execute
3. All 4 databases written
4. Staging cleaned up
5. Integration tests passing

**Feature is MISSING if:**
1. API doesn't trigger workflow, OR
2. Some activities don't execute, OR
3. Less than 4 databases written, OR
4. Staging not cleaned, OR
5. Tests failing

---

## Research Log

**Link:** `research-logs/phase-2-complete-data-pipeline-research.md`

---

## Verification Decision

**Status:** PENDING

**Decision Date:** TBD
**Verified By:** TBD

**Evidence:**
[To be filled after research]

**Next Steps:**
- If IMPLEMENTED: Move to `verified/implemented/` and document architecture
- If MISSING: Move to `verified/missing/` and create completion plan

---

**Expected Outcome:** PARTIAL (likely some components exist, but incomplete pipeline)

**Reason:** Testing-kit shows recent work on Temporal workflows and activities, but full E2E pipeline may have gaps (especially staging and cleanup).

**If MISSING, Auto-Trigger:**
- Create `upgrades/active/complete-document-pipeline/`
- Priority: CRITICAL
- Timeline: 1 week to complete missing pieces
