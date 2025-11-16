# Structured Data Ingestion - Deployment Guide

**Feature:** JSON/Structured Data Workflows
**Status:** ✅ Production Ready (Implemented Nov 6, 2025)
**Impact:** Critical - Enables ingestion from Samsara, Turvo, FrontApp APIs
**Deployment Week:** Week 2 (Dockerization & Configuration)

---

## Overview

Structured Data Ingestion provides two Temporal workflows for ingesting JSON data from external APIs (Samsara GPS events, Turvo shipments, FrontApp messages, generic JSON).

**What It Does:**
- Single JSON ingestion (`StructuredDataIngestionWorkflow`)
- Bulk batch ingestion (`BatchStructuredDataIngestionWorkflow`)
- PostgreSQL JSONB storage for flexible schema
- Entity extraction from JSON fields
- Integration with existing 4-database architecture

**Key Benefits:**
- No schema migrations needed for new JSON formats
- Automatic entity extraction using Graphiti
- Separate workflow from document ingestion (optimized for JSON)
- Support for 4 data types: GPS_EVENT, SHIPMENT, MESSAGE, GENERIC_JSON

**Dependencies:**
- PostgreSQL (already deployed)
- Temporal Cloud (already deployed)
- Graphiti (for entity extraction)

**References:**
- Workflows: `src/apex_memory/temporal/workflows/structured_data_ingestion.py`
- Activities: `src/apex_memory/temporal/activities/structured_data_ingestion.py`
- Models: `src/apex_memory/models/structured_data.py`
- Tests: `tests/integration/test_json_integration_e2e.py` (15,808 bytes)

---

## Prerequisites

- PostgreSQL database deployed (Phase 2)
- Temporal Cloud configured (Phase 3)
- Graphiti Integration enabled (see `deployment/components/graphiti-integration/`)

---

## Setup Instructions

### Step 1: Run Database Migration

```bash
cd apex-memory-system

# Run migration to create structured_data table
alembic upgrade head

# Verify table created
export PGPASSWORD=apexmemory2024
psql -h localhost -U apex -d apex_memory -c "\d structured_data"

# Expected columns: uuid, source, data_type, data (JSONB), external_id, created_at, updated_at
```

**Migration File:** `alembic/versions/00765e428bf3_add_structured_data_table_with_jsonb_.py`

### Step 2: Enable Feature Flag

**Cloud Run Update:**
```bash
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="ENABLE_STRUCTURED_DATA_INGESTION=true"
```

### Step 3: Register Workflows with Temporal Worker

Workflows are automatically registered by the Temporal worker. Verify registration:

```bash
# Check Temporal UI
# http://localhost:8088 (or Temporal Cloud URL)
# Navigate to: Workflows → Search for "StructuredDataIngestionWorkflow"
```

**Worker File:** `src/apex_memory/temporal/workers/dev_worker.py`

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENABLE_STRUCTURED_DATA_INGESTION` | Yes | `false` | Enable structured data workflows |

### API Endpoint

```
POST /api/v1/ingest/structured
```

**Payload Example (Turvo Shipment):**
```json
{
  "source": "turvo",
  "data_id": "SHIP-12345",
  "data_type": "shipment",
  "data": {
    "shipment_id": "SHIP-12345",
    "status": "in_transit",
    "origin": "Dallas, TX",
    "destination": "Chicago, IL",
    "carrier": "FreightCo",
    "estimated_delivery": "2025-11-20"
  }
}
```

**Payload Example (Samsara GPS):**
```json
{
  "source": "samsara",
  "data_id": "GPS-789",
  "data_type": "gps_event",
  "data": {
    "vehicle_id": "TRUCK-042",
    "latitude": 32.7767,
    "longitude": -96.7970,
    "timestamp": "2025-11-15T14:30:00Z",
    "speed_mph": 65
  }
}
```

---

## Deployment

### Production Checklist

- [ ] Database migration completed (`structured_data` table exists)
- [ ] Feature flag enabled (`ENABLE_STRUCTURED_DATA_INGESTION=true`)
- [ ] Temporal worker running with workflows registered
- [ ] API endpoint accessible (`/api/v1/ingest/structured`)
- [ ] Verification tests passing

### Deployment Commands

```bash
# 1. Run migration
cd apex-memory-system && alembic upgrade head

# 2. Enable feature
gcloud run services update apex-api \
  --region=us-central1 \
  --update-env-vars="ENABLE_STRUCTURED_DATA_INGESTION=true"

# 3. Restart worker (if needed)
# Cloud Run auto-restarts on config change
```

---

## Verification

### Test 1: Single JSON Ingestion

```bash
export API_URL=$(gcloud run services describe apex-api --region=us-central1 --format="value(status.url)")

curl -X POST "$API_URL/api/v1/ingest/structured" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "turvo",
    "data_id": "TEST-001",
    "data_type": "shipment",
    "data": {
      "shipment_id": "TEST-001",
      "status": "delivered",
      "carrier": "TestCo"
    }
  }'

# Expected: {"success": true, "uuid": "...", "workflow_id": "..."}
```

### Test 2: Verify PostgreSQL Storage

```bash
export PGPASSWORD=apexmemory2024
psql -h POSTGRES_IP -U apex -d apex_memory -c "
  SELECT uuid, source, data_type, data->>'shipment_id', created_at
  FROM structured_data
  WHERE source = 'turvo'
  ORDER BY created_at DESC
  LIMIT 5;
"

# Should show TEST-001 shipment
```

### Test 3: Verify Entity Extraction

```bash
# Check Neo4j for extracted entities
curl -u neo4j:PASSWORD http://NEO4J_IP:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{
    "statements": [{
      "statement": "MATCH (n) WHERE n.source_data_id = '\''TEST-001'\'' RETURN n.name, labels(n)"
    }]
  }'

# Should show entities: TestCo (Organization), etc.
```

### Test 4: Batch Ingestion

```bash
curl -X POST "$API_URL/api/v1/ingest/structured/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"source": "samsara", "data_id": "GPS-001", "data_type": "gps_event", "data": {"vehicle_id": "TRUCK-01", "lat": 32.77, "lon": -96.79}},
      {"source": "samsara", "data_id": "GPS-002", "data_type": "gps_event", "data": {"vehicle_id": "TRUCK-02", "lat": 33.45, "lon": -97.12}}
    ]
  }'

# Expected: {"success": true, "ingested": 2, "workflow_ids": [...]}
```

---

## Troubleshooting

### Issue 1: Migration Fails

**Symptom:** `alembic upgrade head` returns error about existing table

**Solution:**
```bash
# Check current revision
alembic current

# If behind, force upgrade
alembic upgrade head

# If table already exists (manual creation), stamp migration
alembic stamp 00765e428bf3
```

### Issue 2: Workflow Not Found in Temporal

**Symptom:** API returns "Workflow not registered"

**Solution:**
```bash
# 1. Restart Temporal worker
gcloud run services update apex-api --region=us-central1

# 2. Check worker logs
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~\"StructuredDataIngestionWorkflow\"" \
  --limit=20

# 3. Verify worker file includes workflow
grep -n "StructuredDataIngestionWorkflow" src/apex_memory/temporal/workers/dev_worker.py
```

### Issue 3: JSONB Query Performance Slow

**Symptom:** Queries on `structured_data.data` field are slow

**Solution:**
```sql
-- Create GIN index on JSONB column
CREATE INDEX idx_structured_data_jsonb ON structured_data USING gin(data);

-- Create indexes on common query fields
CREATE INDEX idx_structured_data_source ON structured_data(source);
CREATE INDEX idx_structured_data_type ON structured_data(data_type);
CREATE INDEX idx_structured_data_external_id ON structured_data(external_id);
```

---

## Rollback

```bash
# 1. Disable feature flag
gcloud run services update apex-api \
  --region=us-central1 \
  --remove-env-vars="ENABLE_STRUCTURED_DATA_INGESTION"

# 2. (Optional) Revert migration
cd apex-memory-system
alembic downgrade -1

# 3. Verify
curl -X POST "$API_URL/api/v1/ingest/structured" \
  -H "Content-Type: application/json" \
  -d '{"source": "test"}'

# Should return 404 or feature disabled error
```

---

## Cost Breakdown

**$0/month** - Uses existing infrastructure
- PostgreSQL: Already deployed
- Temporal Cloud: Already included in subscription
- No additional GCP resources required

---

## References

- **Completion Summary:** `upgrades/completed/graphiti-json-integration/COMPLETION-SUMMARY.md`
- **Implementation Guide:** `upgrades/completed/graphiti-json-integration/IMPLEMENTATION.md`
- **Tests:** `tests/integration/test_json_integration_e2e.py`

---

**Deployment Status:** ✅ Ready for Production
**Last Updated:** 2025-11-15
**Next Step:** Proceed to Conversation Processing deployment
