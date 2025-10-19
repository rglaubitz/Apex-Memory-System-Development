# Graphiti + JSON Integration - Complete Planning Document

**Project:** Apex Memory System - Temporal Implementation
**Phase:** Graphiti Entity Extraction + JSON Support + Staging Lifecycle
**Timeline:** 4 weeks
**Status:** Ready for Implementation
**Created:** 2025-10-19

---

## Executive Summary

### Goal

Add LLM-powered entity extraction using Graphiti, native JSON ingestion support, local staging lifecycle management, and two-workflow architecture to the Apex Memory System.

### Key Deliverables

1. **Graphiti Integration** - Replace regex-based EntityExtractor with Graphiti's LLM-powered extraction
2. **JSON Support** - Native structured data ingestion with Graphiti entity extraction
3. **Staging Lifecycle** - Local folder staging with automatic cleanup
4. **Two Workflows** - Separate optimized workflows for documents vs. structured data

### Impact Level

🟡 **Medium** - Additive changes, zero breaking changes, preserves Enhanced Saga baseline (121 tests)

### Timeline

**4 weeks total:**
- Week 1: Graphiti Integration (10 tests)
- Week 2: JSON Support (15 tests)
- Week 3: Staging Lifecycle (10 tests)
- Week 4: Two Workflows (integration testing)

---

## Current vs. Target Architecture

### BEFORE (Current - Section 9 Complete)

```
┌─────────────┐
│  S3 Bucket  │ ← External systems push (not orchestrated by Temporal)
└─────────────┘
       ↓
┌──────────────────────────────────────────────────────────┐
│  DocumentIngestionWorkflow (5 activities)                │
├──────────────────────────────────────────────────────────┤
│  1. download_from_s3_activity (interim TD-001)           │
│  2. parse_document_activity (Docling)                    │
│  3. extract_entities_activity (EntityExtractor - regex)  │ ❌ Regex patterns only
│  4. generate_embeddings_activity (OpenAI)                │
│  5. write_to_databases_activity (Enhanced Saga)          │
└──────────────────────────────────────────────────────────┘
       ↓
┌────────────────────────────────────────────────────┐
│  Enhanced Saga → 4 Databases (parallel writes)     │
├────────────────────────────────────────────────────┤
│  • PostgreSQL + pgvector                          │
│  • Qdrant                                          │
│  • Neo4j (basic document nodes)                    │
│  • Redis                                           │
└────────────────────────────────────────────────────┘
```

**Problems:**
- ❌ Entity extraction uses regex (low quality)
- ❌ No JSON/structured data support
- ❌ S3 staging not orchestrated by Temporal
- ❌ Single workflow for all data types (not optimized)
- ❌ No relationship inference between entities

### AFTER (Target Architecture)

```
┌──────────────────────────────────────────────────────────┐
│  DATA SOURCE ROUTER (API endpoint)                       │
│  Determines data type → Routes to appropriate workflow   │
└──────────────────────────────────────────────────────────┘
       │
       ├────────────────────────┬────────────────────────────┐
       ▼                        ▼                            ▼
┌─────────────┐        ┌──────────────┐          ┌──────────────┐
│  PDF/DOCX   │        │ Samsara GPS  │          │ Turvo JSON   │
│  FrontApp   │        │ FrontApp     │          │ Bank Export  │
└─────────────┘        └──────────────┘          └──────────────┘
       │                        │                            │
       ▼                        ▼                            ▼
┌──────────────────────┐    ┌──────────────────────────────────┐
│  Document            │    │  Structured Data                 │
│  Ingestion           │    │  Ingestion                       │
│  Workflow            │    │  Workflow                        │
│  (6 activities)      │    │  (4 activities)                  │
└──────────────────────┘    └──────────────────────────────────┘

BOTH WORKFLOWS CONVERGE:
       │                                  │
       └──────────────┬───────────────────┘
                      ▼
       ┌──────────────────────────────┐
       │  GRAPHITI                    │ ✅ LLM-powered extraction
       │  Entity Extraction           │ ✅ Relationship inference
       │  + Knowledge Graph           │ ✅ Temporal tracking
       └──────────────────────────────┘
                      ↓
       ┌──────────────────────────────┐
       │  EMBEDDINGS                  │
       │  (OpenAI)                    │
       └──────────────────────────────┘
                      ↓
       ┌──────────────────────────────┐
       │  ENHANCED SAGA               │ ✅ Graphiti rollback
       │  (4-DB parallel writes)      │ ✅ Atomic guarantees
       └──────────────────────────────┘
                      ↓
       ┌─────────┬──────────┬──────────┬──────────┐
       ▼         ▼          ▼          ▼          ▼
  ┌──────┐ ┌──────┐ ┌──────────┐ ┌────────┐ ┌───────┐
  │Neo4j │ │Qdrant│ │PostgreSQL│ │Graphiti│ │ Redis │
  │(meta)│ │      │ │          │ │ (KG)   │ │       │
  └──────┘ └──────┘ └──────────┘ └────────┘ └───────┘
```

**Improvements:**
- ✅ Temporal orchestrates entire flow (source → staging → processing → databases)
- ✅ Local staging `/tmp/apex-staging/` (fast, free, ephemeral)
- ✅ Graphiti LLM extraction (vastly superior to regex)
- ✅ Two optimized workflows (document vs. structured data)
- ✅ JSON natively supported via `add_json_episode()`
- ✅ Knowledge graph with entity relationships
- ✅ Graphiti episodes rolled back on Saga failure

---

## 4-Week Implementation Plan

### Week 1: Graphiti Integration

**Goal:** Replace EntityExtractor with Graphiti in existing DocumentIngestionWorkflow

#### Day 1-2: Update extract_entities_activity

**Changes:**
- Replace EntityExtractor (regex) with GraphitiService
- Call `graphiti.add_document_episode()`
- Return format: `{entities: [...], graphiti_episode_uuid: ...}`

**Files Modified:**
- `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**Testing:**
- 5 unit tests (graphiti extraction, error handling, format conversion)

**Success Criteria:**
- Activity uses Graphiti successfully
- Returns entities in correct format
- Episode UUID tracked for rollback

#### Day 3-4: Add Graphiti Rollback Logic

**Changes:**
- Update `write_to_databases_activity` to accept Graphiti episode UUID
- Add `rollback_graphiti_episode()` helper function
- Call rollback on Saga failure

**Files Modified:**
- `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**Testing:**
- 5 unit tests (rollback on failure, partial success, orphaned cleanup)

**Success Criteria:**
- Graphiti episodes cleaned up on Saga failure
- No orphaned knowledge graph data
- Logging includes rollback events

#### Day 5: Integration Testing & Baseline Validation

**Testing:**
- Run end-to-end document ingestion
- Verify knowledge graph in Neo4j (entities + relationships)
- Run all 121 Enhanced Saga tests (ensure no regression)

**Success Criteria:**
- ✅ Graphiti integration works end-to-end
- ✅ Knowledge graph visible in Neo4j
- ✅ All 121 Enhanced Saga tests still pass
- ✅ 10 new Graphiti tests pass

**Deliverables:**
- Week 1 complete: Graphiti replaces EntityExtractor
- Feature flag: `ENABLE_GRAPHITI_EXTRACTION=true/false`

---

### Week 2: JSON Support

**Goal:** Add structured data ingestion capability with Graphiti JSON extraction

#### Day 1: Create Pydantic Models

**New Files:**
- `apex-memory-system/src/apex_memory/models/structured_data.py`

**Models:**
- `StructuredDataType` (enum: gps_event, shipment, message)
- `StructuredDataMetadata` (data_id, source, type, timestamp)
- `StructuredData` (uuid, metadata, raw_json, text_representation)

**Testing:**
- 3 unit tests (model validation, enum types, serialization)

**Success Criteria:**
- Pydantic models validate correctly
- Serialization/deserialization works

#### Day 2: Add Database Write Methods

**Files Modified:**
- `apex-memory-system/src/apex_memory/database/postgres_writer.py`
- `apex-memory-system/src/apex_memory/database/qdrant_writer.py`
- `apex-memory-system/src/apex_memory/database/neo4j_writer.py`
- `apex-memory-system/src/apex_memory/database/redis_writer.py`

**New Methods:**
- `write_json_record()` in all 4 database writers

**Database Changes:**
- PostgreSQL: CREATE TABLE `structured_data` with JSONB column
- Qdrant: CREATE COLLECTION `apex_structured_data`
- Neo4j: CREATE node label `:StructuredData`
- Redis: JSON keys with 24hr TTL

**Testing:**
- 12 unit tests (3 tests per database writer)

**Success Criteria:**
- All 4 writers handle JSON records
- Database schemas created
- Write operations idempotent

#### Day 3: Add Saga Orchestrator Method

**Files Modified:**
- `apex-memory-system/src/apex_memory/services/database_writer.py`

**New Method:**
- `write_structured_data_parallel()` - Saga pattern for JSON

**Testing:**
- 5 integration tests (parallel writes, rollback, idempotency)

**Success Criteria:**
- Saga pattern works for JSON (no chunks)
- Rollback works correctly
- Idempotency preserved

#### Day 4: Add Temporal Activities

**Files Modified:**
- `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**New Activities:**
- `extract_entities_from_json_activity` - Uses `graphiti.add_json_episode()`
- `write_structured_data_activity` - Calls Saga + Graphiti rollback

**Testing:**
- 5 unit tests (JSON extraction, Graphiti rollback, activity errors)

**Success Criteria:**
- JSON extraction works via Graphiti
- Graphiti rollback on failure
- Activities properly instrumented

#### Day 5: End-to-End JSON Testing

**Testing:**
- Test with sample Samsara GPS JSON
- Test with sample Turvo shipment JSON
- Test with sample FrontApp message JSON
- Verify all 4 databases written
- Verify Graphiti knowledge graph

**Success Criteria:**
- ✅ JSON ingestion works end-to-end
- ✅ Graphiti extracts entities from JSON
- ✅ All 4 databases receive JSON records
- ✅ 15 new JSON tests pass
- ✅ 121 Enhanced Saga tests still pass

**Deliverables:**
- Week 2 complete: JSON support fully functional
- Database schemas deployed
- Saga supports structured data

---

### Week 3: Staging Lifecycle

**Goal:** Replace S3 with local staging, add source pulling, add cleanup

#### Day 1: Add pull_and_stage_document_activity

**Files Modified:**
- `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**New Activity:**
- `pull_and_stage_document_activity` - Pulls from source to `/tmp/apex-staging/`

**Handles:**
- FrontApp API downloads (OAuth)
- Local file system moves
- HTTP/HTTPS downloads

**Testing:**
- 3 unit tests (FrontApp mock, local file, HTTP download)

**Success Criteria:**
- Activity pulls from various sources
- Writes to local staging folder
- Returns staging path

#### Day 2: Add fetch_structured_data_activity

**Files Modified:**
- `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**New Activity:**
- `fetch_structured_data_activity` - Fetches JSON from APIs

**Handles:**
- Samsara REST API
- Turvo REST API
- FrontApp webhook payloads

**Testing:**
- 3 unit tests (mock API responses)

**Success Criteria:**
- Fetches JSON from external APIs
- Handles authentication
- Returns JSON dict

#### Day 3: Create StagingManager Service

**New Files:**
- `apex-memory-system/src/apex_memory/services/staging_manager.py`

**Features:**
- Create staging directories
- Track staging metadata
- Cleanup failed ingestions (after 24hr)
- Monitor disk usage

**Configuration:**
- `staging_base_dir: /tmp/apex-staging`
- `staging_failed_retention_hours: 24`
- `staging_cleanup_interval_minutes: 60`
- `staging_max_size_gb: 10`

**Testing:**
- 5 tests (create, cleanup, monitor, retention, disk usage)

**Success Criteria:**
- Staging manager creates folders
- Cleanup works correctly
- Disk usage monitored

#### Day 4: Add cleanup_staging_activity

**Files Modified:**
- `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`

**New Activity:**
- `cleanup_staging_activity` - Removes staging directory after success

**Testing:**
- 2 tests (successful cleanup, cleanup failure handling)

**Success Criteria:**
- Cleanup activity removes folders
- Logs cleanup events
- Handles cleanup failures gracefully

#### Day 5: Add Staging Metrics

**Files Modified:**
- `apex-memory-system/src/apex_memory/monitoring/metrics.py`

**New Metrics:**
- `apex_temporal_staging_bytes_written` (histogram)
- `apex_temporal_staging_cleanups_total` (counter)
- `apex_temporal_staging_disk_usage_bytes` (gauge)

**Dashboard Updates:**
- Add "Staging Operations" panel to Grafana
- Track staging cleanup rate
- Alert on staging cleanup failures

**Testing:**
- 2 tests (metrics recording, dashboard queries)

**Success Criteria:**
- ✅ Staging metrics collected
- ✅ Dashboard shows staging operations
- ✅ Alerts configured
- ✅ 10 new staging tests pass

**Deliverables:**
- Week 3 complete: Local staging fully functional
- S3 dependency removed (deprecated)
- StagingManager service operational

---

### Week 4: Two Workflows

**Goal:** Create separate workflows for documents vs. structured data

#### Day 1-2: Update DocumentIngestionWorkflow

**Files Modified:**
- `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`

**Changes:**
- Replace `download_from_s3_activity` → `pull_and_stage_document_activity`
- Add `cleanup_staging_activity` at end
- Update workflow signature (accept `source_location` instead of `s3_bucket`)

**Activities (6 total):**
1. pull_and_stage_document_activity
2. parse_document_activity (Docling)
3. extract_entities_activity (Graphiti)
4. generate_embeddings_activity (OpenAI)
5. write_to_databases_activity (Saga)
6. cleanup_staging_activity

**Testing:**
- 3 integration tests (end-to-end, rollback, cleanup)

**Success Criteria:**
- Workflow uses local staging
- Cleanup happens after success
- All activities instrumented

#### Day 3: Create StructuredDataIngestionWorkflow

**Files Modified:**
- `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`

**New Workflow:**
- `StructuredDataIngestionWorkflow`

**Activities (4 total):**
1. fetch_structured_data_activity
2. extract_entities_from_json_activity (Graphiti)
3. generate_embeddings_from_json_activity (OpenAI)
4. write_structured_data_activity (Saga)

**Testing:**
- 3 integration tests (JSON end-to-end, rollback, multiple sources)

**Success Criteria:**
- Workflow handles JSON natively
- No staging needed (JSON < 2MB)
- Graphiti + Saga integrated

#### Day 4: Update API Routes

**Files Modified:**
- `apex-memory-system/src/apex_memory/api/ingestion.py`

**Changes:**
- Update `/ingest` endpoint to detect data type
- Route to `DocumentIngestionWorkflow` or `StructuredDataIngestionWorkflow`
- Remove S3 upload logic

**New Endpoints:**
- `POST /ingest/webhook/frontapp` - FrontApp webhook receiver
- `POST /ingest/webhook/turvo` - Turvo webhook receiver
- `POST /ingest/scheduled/samsara` - Samsara polling trigger

**Testing:**
- 5 API tests (routing, webhooks, error handling)

**Success Criteria:**
- API routes to correct workflow
- Webhooks work correctly
- Error responses formatted

#### Day 5: Update Worker & Integration Testing

**Files Modified:**
- `apex-memory-system/src/apex_memory/temporal/workers/dev_worker.py`

**Changes:**
- Register both workflows
- Register all activities (document + structured)

**Integration Testing:**
- Run 100+ parallel workflows (load test)
- Test concurrent document + JSON ingestion
- Verify Enhanced Saga baseline (121 tests)

**Success Criteria:**
- ✅ Worker registers both workflows
- ✅ Load test passes (100+ workflows)
- ✅ Both workflows work concurrently
- ✅ 121 Enhanced Saga tests still pass
- ✅ Total 35 new tests pass (10 + 15 + 10)

**Deliverables:**
- Week 4 complete: Two-workflow architecture operational
- API routing functional
- Worker handling both workflows

---

## Success Criteria (Final)

### Functional Requirements

- ✅ Graphiti LLM-powered entity extraction operational
- ✅ Graphiti episodes rolled back on Saga failure
- ✅ JSON ingestion works for Samsara, Turvo, FrontApp
- ✅ All 4 databases support JSON records
- ✅ Local staging replaces S3 (S3 deprecated)
- ✅ Two workflows operational (Document + Structured)
- ✅ API routes to correct workflow based on data type

### Quality Requirements

- ✅ All 121 Enhanced Saga tests still pass
- ✅ 35 new tests pass (10 Graphiti + 15 JSON + 10 staging)
- ✅ Unit test coverage >80% for new code
- ✅ Integration tests pass for both workflows
- ✅ Load test: 100+ concurrent workflows

### Performance Requirements

- ✅ Document workflow: <30s end-to-end (matches current)
- ✅ Structured data workflow: <10s end-to-end (no parsing)
- ✅ Staging I/O: <500ms for typical 5MB PDF
- ✅ Graphiti extraction: <5s for typical document
- ✅ Staging cleanup: <1GB disk footprint

### Observability Requirements

- ✅ All new activities emit metrics (start, complete, retry, fail)
- ✅ Grafana dashboard shows both workflows
- ✅ Staging metrics tracked (bytes, cleanup rate)
- ✅ Alerts cover Graphiti failures, staging failures, API failures
- ✅ Temporal UI differentiates workflow types

---

## Risk Assessment

### 🟢 LOW RISK

**Why:**
1. ✅ **Additive changes only** - EntityExtractor deprecated but kept as fallback
2. ✅ **Feature flag** - `ENABLE_GRAPHITI_EXTRACTION` can toggle Graphiti on/off
3. ✅ **Enhanced Saga baseline preserved** - 121 tests run after every change
4. ✅ **JSON is new code path** - Zero impact on existing document ingestion
5. ✅ **Staging is parallel** - S3 kept as read-only backup during migration
6. ✅ **Graphiti rollback** - No orphaned knowledge graph data

### Mitigation Strategies

**If Graphiti fails:**
- Fallback to EntityExtractor via feature flag
- Keep EntityExtractor code for 1 release cycle
- Monitor Graphiti extraction quality metrics

**If Saga rollback fails:**
- Dead Letter Queue (DLQ) for manual cleanup
- Alerts on rollback failures
- Graphiti episode cleanup script

**If staging fills disk:**
- Automatic cleanup after 24 hours
- Disk usage monitoring with alerts
- Maximum staging size limit (10GB)

**If API migration breaks:**
- Keep S3 staging as fallback
- Gradual rollout (10% → 50% → 100%)
- Rollback plan documented

---

## Timeline Summary

| Week | Phase | Deliverables | Tests |
|------|-------|-------------|-------|
| **Week 1** | Graphiti Integration | `extract_entities_activity` with Graphiti, rollback logic | 10 tests |
| **Week 2** | JSON Support | Database writers, Saga method, Temporal activities | 15 tests |
| **Week 3** | Staging Lifecycle | Local staging, StagingManager, cleanup worker | 10 tests |
| **Week 4** | Two Workflows | DocumentIngestion + StructuredDataIngestion workflows | Integration tests |

**Total Duration:** 4 weeks
**Total Tests:** 35 new tests (all 121 Enhanced Saga tests preserved)
**Files Created:** 8 new files
**Files Modified:** 15 files
**Breaking Changes:** 0 ❌ None

---

## Post-Implementation Benefits

### Immediate Benefits (Week 1-2)

- ✅ **Superior entity extraction** - LLM-powered vs. regex (5-10x better)
- ✅ **Knowledge graph** - Entity relationships automatically inferred
- ✅ **Temporal tracking** - Bi-temporal versioning built-in
- ✅ **JSON support** - Native structured data ingestion

### Medium-Term Benefits (Week 3-4)

- ✅ **Cost savings** - No S3 storage costs for staging
- ✅ **Performance** - Local I/O faster than S3 downloads
- ✅ **Orchestration** - Temporal controls entire flow (source → DBs)
- ✅ **Scalability** - Two optimized workflows (not one-size-fits-all)

### Long-Term Benefits

- ✅ **Unlocks TD-003 full implementation** - Foundation for complete redesign
- ✅ **API integrations ready** - Samsara, Turvo, FrontApp webhook support
- ✅ **Knowledge graph queries** - Graphiti hybrid search available
- ✅ **Pattern detection** - Graphiti communities and relationships

---

## Dependencies

### External Dependencies

- Graphiti Core 0.20.4 (already installed ✅)
- OpenAI API (GPT-4.1-mini for extraction)
- Neo4j 5.x (Graphiti knowledge graph)
- PostgreSQL 16 + JSONB (structured data)
- Qdrant 1.12+ (vector collections)
- Redis 7.2+ (caching)

### Internal Dependencies

- Enhanced Saga pattern (121 tests must pass)
- Temporal infrastructure (Sections 1-9 complete)
- Monitoring system (27 metrics operational)
- Database schemas (need JSONB support in Postgres)

---

## Approval & Sign-off

**Status:** ⏳ **Awaiting Approval**

**Approval Required From:**
- [ ] Product Owner - Strategic alignment
- [ ] Tech Lead - Technical architecture
- [ ] DevOps - Infrastructure readiness

**Next Step After Approval:**
- Begin Week 1: Graphiti Integration
- Follow IMPLEMENTATION.md step-by-step guide

---

**Document Version:** 1.0
**Last Updated:** 2025-10-19
**Author:** Claude Code
**Based On:** saga-graphiti-integration-plan.md + TD-003-ARCHITECTURE-REDESIGN.md
