# Phase 3: Structured Data Ingestion (JSON/API Integration)

**Status:** ⏸️ ON HOLD (Code Complete, Pending Domain Configuration)
**Created:** 2025-10-20
**Researcher:** Claude Code
**Priority:** IMPORTANT

---

## UPDATE (2025-10-20)

**Verification Status:** Code infrastructure is **FULLY IMPLEMENTED** ✅, but marking as **ON HOLD** pending domain configuration.

**What Exists:**
- ✅ StructuredDataIngestionWorkflow (4 activities)
- ✅ Pydantic models (StructuredData, StructuredDataType)
- ✅ PostgreSQL JSONB schema (structured_data table)
- ✅ API endpoint for structured data ingestion
- ✅ Comprehensive tests (6 test files, 50+ tests)

**Why On Hold:**
The current implementation uses **generic Graphiti extraction** (no domain knowledge). This leads to:
- Random entity types (e.g., "Document" instead of "PartsInvoice")
- Missing semantic relationships (e.g., no "BELONGS_TO" connections)
- Poor knowledge graph quality (hard to query, limited insights)

**Required Before IMPLEMENTED:**
Complete **Graphiti Domain Configuration** upgrade:
- Location: `upgrades/active/graphiti-domain-configuration/`
- Timeline: 2-3 days
- Goal: 90%+ entity extraction accuracy with domain-specific types
- Blocks: Phase 3 verification (this phase)

**After domain configuration completes:**
- This phase will be marked **FULLY IMPLEMENTED**
- No code changes needed (just configuration)

**See:** `upgrades/active/graphiti-domain-configuration/README.md` for complete plan

---

## Hypothesis

Structured data ingestion from external APIs (Samsara GPS, Turvo shipments, FrontApp messages) is not implemented. The system can ingest documents, but cannot pull JSON data from APIs and process it through the multi-database pipeline.

**Specific Gaps Suspected:**
1. No `StructuredDataIngestionWorkflow` exists
2. No API integrations for Samsara/Turvo/FrontApp
3. No JSONB storage schema in PostgreSQL
4. No Pydantic models for structured data validation
5. No entity extraction from JSON data
6. No tests for structured data ingestion

**What This Means:**
The system is limited to manual document uploads and cannot automatically ingest operational data from APIs, reducing its value as an operational memory system.

---

## Expected Behavior

### Complete Structured Data Pipeline:

```
Scheduled Job (or Webhook)
    ↓
Fetch JSON from API:
  - Samsara: GET https://api.samsara.com/v1/fleet/locations
  - Turvo: GET https://api.turvo.com/v1/shipments
  - FrontApp: GET https://api2.frontapp.com/conversations
    ↓
POST /api/v1/ingest-structured
{
  "data_id": "SHIP-12345",
  "source": "turvo",
  "source_endpoint": "{...json...}",
  "data_type": "shipment"
}
    ↓
API triggers StructuredDataIngestionWorkflow
    ↓
Execute 4 Activities:
    1. fetch_structured_data_activity()
       → Validate JSON with Pydantic
    2. extract_entities_from_json_activity()
       → Graphiti extracts entities from JSON
    3. generate_embeddings_from_json_activity()
       → Create embeddings from JSON text
    4. write_structured_data_activity()
       → Write to all 4 DBs (JSONB in PostgreSQL)
    ↓
Response:
{
  "success": true,
  "data_id": "SHIP-12345",
  "workflow_id": "ingest-json-SHIP-12345",
  "databases_written": ["neo4j", "postgres", "qdrant", "redis"],
  "entities_extracted": 4
}
```

### Where it should exist:

**1. API Endpoint:**
- Location: `apex-memory-system/src/apex_memory/api/routes/ingestion.py`
- Endpoint: `POST /api/v1/ingest-structured`
- Accepts: `{data_id, source, source_endpoint, data_type}`

**2. Temporal Workflow:**
- Location: `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`
- Workflow: `StructuredDataIngestionWorkflow`
- Activities:
  - `fetch_structured_data_activity()`
  - `extract_entities_from_json_activity()`
  - `generate_embeddings_from_json_activity()`
  - `write_structured_data_activity()`

**3. Pydantic Models:**
- Location: `apex-memory-system/src/apex_memory/models/structured_data.py`
- Models:
  ```python
  class StructuredDataType(str, Enum):
      GPS = "gps"
      SHIPMENT = "shipment"
      MESSAGE = "message"

  class StructuredData(BaseModel):
      data_id: str
      source: str
      data_type: StructuredDataType
      data: Dict[str, Any]
      timestamp: datetime
  ```

**4. Database Schema (PostgreSQL):**
```sql
CREATE TABLE structured_data (
    id UUID PRIMARY KEY,
    data_id TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    data_type TEXT NOT NULL,
    data JSONB NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**5. API Integrations:**
- Location: `apex-memory-system/src/apex_memory/integrations/`
- Clients:
  - `samsara_client.py`
  - `turvo_client.py`
  - `frontapp_client.py`

---

## Why Important

**Deployment Impact:** IMPORTANT

**This is IMPORTANT because:**

1. **Operational Data:** Real-time operational data (GPS, shipments, messages) is critical for operational memory, not just documents.

2. **Automation:** Without API integrations, users must manually input operational data, reducing system value.

3. **Completeness:** The system was designed for multi-source ingestion. Document-only ingestion is incomplete.

4. **Differentiation:** Structured data ingestion differentiates Apex from simple document stores.

5. **Use Case Validation:** Key use cases (fleet management, logistics tracking) require structured data ingestion.

**Note:** Not a blocker for deployment, but significantly reduces system value and usability.

---

## Research Plan

### Files to Check:

**API Endpoint:**
```bash
# Search for structured data endpoint
grep -r "ingest-structured" apex-memory-system/src/apex_memory/api/routes/

# Search for structured data API classes
grep -r "class StructuredData" apex-memory-system/src/apex_memory/api/
```

**Temporal Workflow:**
```bash
# Search for StructuredDataIngestionWorkflow
grep -r "StructuredDataIngestionWorkflow" apex-memory-system/src/apex_memory/temporal/workflows/

# Search for JSON activities
grep -r "fetch_structured_data_activity" apex-memory-system/src/apex_memory/temporal/activities/
grep -r "extract_entities_from_json" apex-memory-system/src/apex_memory/temporal/activities/
```

**Pydantic Models:**
```bash
# Search for StructuredData models
grep -r "class StructuredData" apex-memory-system/src/apex_memory/models/

# Search for StructuredDataType enum
grep -r "StructuredDataType" apex-memory-system/src/apex_memory/models/
```

**Database Schema:**
```bash
# Check for structured_data table
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory -c "\dt" | grep structured_data

# Check JSONB columns
PGPASSWORD=apexmemory2024 psql -h localhost -U apex -d apex_memory \
  -c "\d structured_data"
```

**API Integrations:**
```bash
# Search for integration clients
ls apex-memory-system/src/apex_memory/integrations/

# Search for API client classes
grep -r "SamsaraClient" apex-memory-system/src/apex_memory/
grep -r "TurvoClient" apex-memory-system/src/apex_memory/
grep -r "FrontAppClient" apex-memory-system/src/apex_memory/
```

### Tests to Run:

**Unit Tests:**
```bash
# Search for JSON tests
find apex-memory-system/tests/unit/ -name "*json*"
find apex-memory-system/tests/unit/ -name "*structured*"

# Run JSON activity tests
pytest apex-memory-system/tests/unit/test_json_temporal_activities.py -v
```

**Integration Tests:**
```bash
# Search for structured data integration tests
find apex-memory-system/tests/integration/ -name "*structured*"
find apex-memory-system/tests/integration/ -name "*json*"

# Run structured data E2E test
pytest apex-memory-system/tests/integration/test_json_integration_e2e.py -v -m integration
```

**API Tests:**
```bash
# Test structured data endpoint
curl -X POST http://localhost:8000/api/v1/ingest-structured \
  -H "Content-Type: application/json" \
  -d '{
    "data_id": "TEST-001",
    "source": "samsara",
    "source_endpoint": "{\"vehicle_id\": \"V123\", \"location\": \"Chicago\"}",
    "data_type": "gps"
  }'
```

### Evidence Needed:

**To prove IMPLEMENTED:**
- [ ] API endpoint `/api/v1/ingest-structured` exists
- [ ] `StructuredDataIngestionWorkflow` defined
- [ ] All 4 activities implemented
- [ ] PostgreSQL `structured_data` table with JSONB column
- [ ] Pydantic models defined
- [ ] Tests passing

**To prove MISSING:**
- [ ] No API endpoint
- [ ] No workflow
- [ ] No activities
- [ ] No database schema
- [ ] No models
- [ ] No tests

### Success Criteria:

**Feature is IMPLEMENTED if:**
1. API endpoint responds correctly
2. Workflow executes all 4 activities
3. JSONB data stored in PostgreSQL
4. Entities extracted from JSON
5. Tests passing

**Feature is MISSING if:**
1. No API endpoint, OR
2. No workflow, OR
3. No JSONB storage, OR
4. No entity extraction, OR
5. Tests missing/failing

---

## Research Log

**Link:** `research-logs/phase-3-structured-data-ingestion-research.md`

---

## Verification Decision

**Status:** PENDING

**Decision Date:** TBD
**Verified By:** TBD

**Evidence:**
[To be filled after research]

**Next Steps:**
- If IMPLEMENTED: Move to `verified/implemented/`
- If MISSING: Move to `verified/missing/` and create upgrade plan

---

**Expected Outcome:** PARTIAL (Graphiti + JSON Integration plan exists, but may not be fully implemented)

**Reason:** The Graphiti + JSON Integration upgrade plan exists in `upgrades/active/`, but Week 2-4 work may not be complete. Need to verify what's actually implemented vs. planned.

**If MISSING, Auto-Trigger:**
- Create `upgrades/active/structured-data-completion/` OR complete existing `graphiti-json-integration/` plan
- Priority: IMPORTANT
- Timeline: 2-3 weeks (Weeks 2-4 from existing plan)
