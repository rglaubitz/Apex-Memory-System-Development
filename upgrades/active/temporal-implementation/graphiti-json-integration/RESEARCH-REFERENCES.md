# Research References - Graphiti + JSON Integration

**Complete bibliography and research foundation for the Graphiti + JSON integration upgrade.**

This document provides comprehensive references to all Tier 1 documentation, research sources, project dependencies, and internal architecture decisions that inform this implementation.

---

## Table of Contents

1. [Tier 1 Official Documentation](#tier-1-official-documentation)
2. [GitHub Repositories & SDKs](#github-repositories--sdks)
3. [Internal Architecture Decisions](#internal-architecture-decisions)
4. [Project Dependencies](#project-dependencies)
5. [Development Context](#development-context)
6. [Related Planning Documents](#related-planning-documents)

---

## Tier 1 Official Documentation

### Temporal.io

**Primary Source:** Official Temporal Python SDK Documentation

- **Overview:** https://docs.temporal.io/
- **Python SDK:** https://docs.temporal.io/dev-guide/python
- **Workflows:** https://docs.temporal.io/dev-guide/python/foundations#develop-workflows
- **Activities:** https://docs.temporal.io/dev-guide/python/foundations#develop-activities
- **Saga Pattern:** https://docs.temporal.io/encyclopedia/saga-pattern
- **Testing:** https://docs.temporal.io/dev-guide/python/testing
- **Retries & Timeouts:** https://docs.temporal.io/dev-guide/python/features#activity-timeouts

**Key Concepts Used:**
- Durable execution with automatic retries
- Activity heartbeats for long-running tasks
- Compensating transactions (Saga rollback)
- Workflow versioning and determinism

**Research Location:** `research/documentation/temporal/`

---

### Graphiti

**Primary Source:** Official Graphiti Documentation & GitHub

- **GitHub Repository:** https://github.com/getzep/graphiti
- **Documentation:** https://help.getzep.com/graphiti
- **API Reference:** https://help.getzep.com/graphiti/api-reference
- **Episodic Memory:** https://help.getzep.com/graphiti/concepts/episodes
- **Entity Extraction:** https://help.getzep.com/graphiti/concepts/entities
- **Temporal Reasoning:** https://help.getzep.com/graphiti/concepts/temporal

**Version:** 0.20.4 (verified in `requirements.txt`)

**Key Methods Used:**
```python
GraphitiClient.add_episode(
    name: str,
    episode_body: str,
    source_description: str,
    reference_time: datetime,
    source: EpisodeType = EpisodeType.text
)

GraphitiClient.delete_episode(episode_uuid: UUID)
```

**Critical Implementation Notes:**
- Do NOT pass custom UUIDs to `add_episode()` - Graphiti auto-generates
- Use document UUID for tracking, Graphiti episode UUID for rollback
- Episodes support both `EpisodeType.text` (documents) and `EpisodeType.json` (structured data)
- `reference_time` is optional, defaults to current time

**Research Location:** `research/documentation/graphiti/`

---

### Neo4j

**Primary Source:** Official Neo4j Documentation

- **Overview:** https://neo4j.com/docs/
- **Python Driver:** https://neo4j.com/docs/python-manual/current/
- **Cypher Query Language:** https://neo4j.com/docs/cypher-manual/current/
- **Graph Data Modeling:** https://neo4j.com/docs/getting-started/data-modeling/
- **Best Practices:** https://neo4j.com/docs/cypher-manual/current/query-tuning/

**Version:** 5.15.0 (Docker image)

**Key Usage:**
- Primary graph database for Graphiti episodes
- Entity and relationship storage
- Bi-temporal versioning (event time vs. transaction time)

**Research Location:** `research/documentation/neo4j/`

---

### PostgreSQL + pgvector

**Primary Source:** Official PostgreSQL & pgvector Documentation

- **PostgreSQL Docs:** https://www.postgresql.org/docs/16/
- **JSONB Type:** https://www.postgresql.org/docs/16/datatype-json.html
- **JSONB Operations:** https://www.postgresql.org/docs/16/functions-json.html
- **pgvector GitHub:** https://github.com/pgvector/pgvector
- **pgvector Docs:** https://github.com/pgvector/pgvector#pgvector

**Versions:**
- PostgreSQL: 16.1 (Docker image)
- pgvector: 0.5.1

**Key Usage:**
- Metadata storage with JSONB columns
- Hybrid semantic search (full-text + vector)
- `StructuredData` table with `data: JSONB` column

**Research Location:** `research/documentation/postgresql/` and `research/documentation/pgvector/`

---

### Qdrant

**Primary Source:** Official Qdrant Documentation

- **Overview:** https://qdrant.tech/documentation/
- **Python Client:** https://qdrant.tech/documentation/frameworks/python/
- **Collections:** https://qdrant.tech/documentation/concepts/collections/
- **Indexing:** https://qdrant.tech/documentation/concepts/indexing/
- **Points API:** https://qdrant.tech/documentation/concepts/points/

**Version:** 1.7.0 (Docker image)

**Key Usage:**
- High-performance vector similarity search
- Collection management for embeddings
- Parallel writes with Saga rollback support

**Research Location:** `research/documentation/qdrant/`

---

### Redis

**Primary Source:** Official Redis Documentation

- **Overview:** https://redis.io/docs/
- **Python Client (redis-py):** https://redis-py.readthedocs.io/
- **Data Types:** https://redis.io/docs/data-types/
- **Expiration:** https://redis.io/commands/expire/

**Version:** 7.2.3 (Docker image)

**Key Usage:**
- Cache layer for repeat queries (<100ms P90)
- Temporary storage for staging metadata
- TTL-based cache invalidation

**Research Location:** `research/documentation/redis/`

---

### OpenAI

**Primary Source:** Official OpenAI API Documentation

- **Overview:** https://platform.openai.com/docs/
- **Embeddings:** https://platform.openai.com/docs/guides/embeddings
- **Text Embedding Models:** https://platform.openai.com/docs/models/embeddings
- **Best Practices:** https://platform.openai.com/docs/guides/embeddings/best-practices

**Model Used:** `text-embedding-3-small` (1536 dimensions)

**Key Usage:**
- Generate embeddings for document chunks
- Generate embeddings for JSON field values
- Used by `generate_embeddings_activity()`

---

### Pydantic

**Primary Source:** Official Pydantic Documentation

- **Overview:** https://docs.pydantic.dev/latest/
- **Models:** https://docs.pydantic.dev/latest/concepts/models/
- **Field Validation:** https://docs.pydantic.dev/latest/concepts/fields/
- **JSON Schema:** https://docs.pydantic.dev/latest/concepts/json_schema/
- **Config:** https://docs.pydantic.dev/latest/concepts/config/

**Version:** 2.5.3

**Models Defined:**
- `StructuredData` (data, metadata, type, source_id, created_at)
- `StructuredDataMetadata` (title, description, tags, custom_fields)
- `StructuredDataType` (Enum: JSON, YAML, CSV, XML, API_RESPONSE, DATABASE_RECORD)

**Research Location:** `research/documentation/pydantic/`

---

## GitHub Repositories & SDKs

### Graphiti Core

**Repository:** https://github.com/getzep/graphiti
**Stars:** 1,500+ (verified Tier 2 source)
**Maintainer:** Zep AI (official)
**License:** Apache 2.0

**Installation:**
```bash
pip install graphiti-core==0.20.4
```

**Key Files:**
- `graphiti/client.py` - GraphitiClient implementation
- `graphiti/models.py` - Episode, Entity, Edge models
- `graphiti/llm_client.py` - LLM integration

**Documentation:** https://help.getzep.com/graphiti

---

### Temporal Python SDK

**Repository:** https://github.com/temporalio/sdk-python
**Stars:** 400+ (official SDK)
**Maintainer:** Temporal Technologies (official)
**License:** MIT

**Installation:**
```bash
pip install temporalio==1.4.0
```

**Key Modules:**
- `temporalio.workflow` - Workflow decorators and context
- `temporalio.activity` - Activity decorators and heartbeats
- `temporalio.client` - Client for starting workflows
- `temporalio.worker` - Worker for executing workflows/activities

**Documentation:** https://docs.temporal.io/dev-guide/python

---

### pgvector

**Repository:** https://github.com/pgvector/pgvector
**Stars:** 12,000+ (verified Tier 2 source)
**Maintainer:** Andrew Kane (community-maintained, widely adopted)
**License:** PostgreSQL License

**Installation:**
```bash
pip install pgvector==0.5.1
```

**Key Features:**
- Vector similarity search (L2, cosine, inner product)
- HNSW indexing for fast retrieval
- Integration with PostgreSQL JSONB

**Documentation:** https://github.com/pgvector/pgvector#pgvector

---

### Qdrant Client

**Repository:** https://github.com/qdrant/qdrant-client
**Stars:** 1,000+ (official client)
**Maintainer:** Qdrant Solutions (official)
**License:** Apache 2.0

**Installation:**
```bash
pip install qdrant-client==1.7.0
```

**Key Classes:**
- `QdrantClient` - Main client for Qdrant operations
- `PointStruct` - Data structure for vector points
- `Distance` - Distance metrics (Cosine, Euclidean, Dot)

**Documentation:** https://qdrant.tech/documentation/frameworks/python/

---

## Internal Architecture Decisions

### ADR-004: Graphiti Integration

**Location:** `research/architecture-decisions/ADR-004-graphiti-integration.md`

**Decision:** Replace regex-based EntityExtractor with Graphiti's LLM-powered extraction

**Rationale:**
- 90%+ entity extraction accuracy (vs. 60% regex)
- Bi-temporal versioning built-in
- Episode-based rollback for Saga pattern
- Community detection and pattern analysis

**Research Support:**
- Graphiti official documentation (Tier 1)
- Zep AI case studies (Tier 2)
- Neo4j graph modeling best practices (Tier 1)

**Consequences:**
- **Positive:** Higher accuracy, temporal reasoning, easier rollback
- **Negative:** OpenAI API dependency, increased latency
- **Mitigation:** Feature flag `ENABLE_GRAPHITI_EXTRACTION` for rollback

---

### ADR-006: Saga Pattern for Multi-Database Writes

**Location:** `research/architecture-decisions/ADR-006-enhanced-saga-pattern.md`

**Decision:** Implement Enhanced Saga pattern for atomic writes to 4 databases

**Rationale:**
- Distributed transactions across Neo4j, PostgreSQL, Qdrant, Redis
- Compensating transactions for rollback
- Temporal.io durable execution guarantees

**Research Support:**
- Temporal Saga Pattern guide (Tier 1)
- Microsoft Saga Pattern documentation (Tier 3)
- Microservices.io Saga pattern (Tier 3)

**Baseline Tests:** 121 tests validating all rollback scenarios

**Consequences:**
- **Positive:** Data consistency, automatic rollback, retry logic
- **Negative:** Complexity, increased latency
- **Mitigation:** Parallel writes where possible, idempotent operations

---

### TD-003: Architecture Redesign - Local Staging + Two Workflows

**Location:** `upgrades/active/temporal-implementation/TD-003-ARCHITECTURE-REDESIGN.md`

**Decision:** Replace S3 staging with local filesystem and split into two workflows

**Rationale:**
- Eliminate S3 dependency for faster iteration
- Separate workflows for documents vs. structured data
- Simpler local development without AWS credentials

**Components:**
1. **Local Staging:** `/tmp/apex-staging/` with TTL-based cleanup
2. **DocumentIngestionWorkflow:** 6 activities (stage → parse → extract → embed → write → cleanup)
3. **StructuredDataIngestionWorkflow:** 4 activities (stage → validate → write → cleanup)

**Research Support:**
- Temporal best practices for workflow composition (Tier 1)
- Filesystem staging patterns (internal analysis)
- Separation of Concerns principle (industry standard)

---

## Project Dependencies

### Core Dependencies (requirements.txt)

```python
# Workflow orchestration
temporalio==1.4.0

# Entity extraction
graphiti-core==0.20.4

# Databases
neo4j==5.15.0
psycopg2-binary==2.9.9
pgvector==0.5.1
qdrant-client==1.7.0
redis==5.0.1

# LLM & embeddings
openai==1.6.1

# Data validation
pydantic==2.5.3

# API framework
fastapi==0.109.0
uvicorn==0.25.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-mock==3.12.0

# Monitoring
prometheus-client==0.19.0
```

**Full dependency file:** `apex-memory-system/requirements.txt`

---

### Docker Infrastructure

**Docker Compose File:** `apex-memory-system/docker/docker-compose.yml`

**Services:**
- **Neo4j:** 5.15.0 (port 7474/7687)
- **PostgreSQL:** 16.1 with pgvector (port 5432)
- **Qdrant:** 1.7.0 (port 6333)
- **Redis:** 7.2.3 (port 6379)
- **Temporal Server:** 1.22.0 (port 7233)
- **Temporal UI:** 2.21.0 (port 8088)
- **Prometheus:** 2.48.0 (port 9090)
- **Grafana:** 10.2.0 (port 3001)

**Research Location:** `research/documentation/docker/`

---

## Development Context

### Current Project Status

**Project Phase:** Section 9 Complete (82% overall progress)
**Status Document:** `upgrades/active/temporal-implementation/PROJECT-STATUS-SNAPSHOT.md`

**Completed Sections:**
- ✅ Sections 1-4: Foundation (Docker, CLI, Worker, Hello World)
- ✅ Section 5: Hello World Workflow (3 tests)
- ✅ Section 6: Worker Setup (4 tests)
- ✅ Section 7: Ingestion Activities (19 tests)
- ✅ Section 8: Document Ingestion Workflow (15 tests)
- ✅ Section 9: Temporal Integration + Monitoring (27 metrics, 33-panel dashboard, 12 alerts)

**Enhanced Saga Baseline:** 121 tests passing (100% preserved)

---

### Test Organization

**Test Structure Document:** `upgrades/active/temporal-implementation/tests/STRUCTURE.md`

**Phase Tests (Section 11):**
- Phase 1: Pre-testing validation (5 critical fixes)
- Phase 2A: Integration tests (13 critical fixes, 1/6 tests passing)
- Phase 2B: Enhanced Saga baseline (121 tests)
- Phase 2C: Load tests - mocked DBs (5 tests)
- Phase 2D: Load tests - real DBs (5 tests)
- Phase 2E: Metrics validation (8 tests)
- Phase 2F: Alert validation (13 tests)

**Section Tests (Development):**
- Sections 1-8: 41 tests (all passing)

**New Tests (Graphiti + JSON):**
- Phase 1: 10 Graphiti tests (extraction + rollback)
- Phase 2: 15 JSON tests (models + database writers + Saga)
- Phase 3: 10 Staging tests (activities + manager)
- **Total:** 35 new tests + 121 baseline = 156 tests

---

### Monitoring & Observability

**Metrics:** 27 Temporal metrics across 6 layers
**Metrics File:** `apex-memory-system/src/apex_memory/monitoring/metrics.py`

**Layers:**
1. Workflow metrics (duration, failures, retries)
2. Activity metrics (per-activity latency, failures)
3. Data quality metrics (chunk count, entity count, embedding dimensions)
4. Infrastructure metrics (database write latency, Neo4j/PostgreSQL/Qdrant/Redis)
5. Business metrics (documents processed, throughput)
6. Logs (structured JSON logs with trace IDs)

**Dashboard:** 33-panel Grafana dashboard
**Dashboard File:** `apex-memory-system/monitoring/dashboards/temporal-ingestion.json`

**Alerts:** 12 critical alerts
**Alert File:** `apex-memory-system/monitoring/alerts/rules.yml`

---

### API Endpoints

**Current API:** `apex-memory-system/src/apex_memory/api/ingestion.py`

**Endpoints:**
- `POST /ingest` - Document ingestion (Temporal-integrated)
- `GET /status/{workflow_id}` - Workflow status
- `GET /health` - Health check

**New Endpoints (Graphiti + JSON):**
- `POST /ingest/json` - Structured data ingestion (StructuredDataIngestionWorkflow)
- `GET /entities/{document_uuid}` - Retrieve Graphiti entities
- `GET /staging/status` - Staging directory status

**API Documentation:** http://localhost:8000/docs (FastAPI auto-generated)

---

## Related Planning Documents

### Primary Planning Documents

1. **saga-graphiti-integration-plan.md**
   - Location: `upgrades/active/temporal-implementation/saga-graphiti-integration-plan.md`
   - Original 3-week plan for Graphiti + JSON integration
   - Graphiti episode management details
   - JSON support architecture

2. **TD-003-ARCHITECTURE-REDESIGN.md**
   - Location: `upgrades/active/temporal-implementation/TD-003-ARCHITECTURE-REDESIGN.md`
   - Full architectural redesign (local staging, two workflows)
   - 6-phase implementation over 4 weeks
   - Referenced by saga-plan as "original plan"

3. **This Integration Planning**
   - Location: `upgrades/active/temporal-implementation/graphiti-json-integration/`
   - **PLANNING.md** - Unified 4-week plan (merges saga-plan + TD-003)
   - **IMPLEMENTATION.md** - Step-by-step Tier 1 guide
   - **TESTING.md** - 35 test specifications
   - **TROUBLESHOOTING.md** - Common issues and solutions
   - **RESEARCH-REFERENCES.md** - This document

---

### Execution Roadmap

**Document:** `upgrades/active/temporal-implementation/EXECUTION-ROADMAP.md`

**Overall Timeline:** 11 sections (Sections 1-9 complete, 10-11 remaining)

**Next Steps After Graphiti + JSON:**
- Section 10: Ingestion Testing & Rollout Validation
- Section 11: Production Readiness & Documentation

---

### Section 9 Summary

**Document:** `upgrades/active/temporal-implementation/SECTION-9-COMPLETE.md`

**Key Achievements:**
- 100% Temporal integration (no legacy path)
- Complete observability (6-layer monitoring)
- Silent failure detection (zero chunks/entities alerts)
- Production-ready monitoring and alerting
- 162 tests passing (Enhanced Saga preserved: 121/121)

**Handoff Document:** `upgrades/active/temporal-implementation/HANDOFF-SECTION-9.md`

---

## Research Methodology

### Source Hierarchy Standards

All implementation decisions follow the research-first principle with source hierarchy:

**Tier 1 (Highest Priority):**
- Official documentation from service providers
- Official SDKs and API references
- Authoritative technical standards (RFCs, W3C)

**Tier 2:**
- Verified GitHub repositories (1,500+ stars minimum)
- Case studies from official vendors
- Conference talks from maintainers

**Tier 3:**
- Reputable technical blogs (Martin Fowler, Microservices.io)
- Technical standards from established organizations
- Academic papers from reputable institutions

**Research Validation:**
- Documentation must be current (<2 years old OR explicitly verified)
- GitHub examples must demonstrate the pattern being researched
- All sources must include citations with URLs
- Breaking changes and deprecations must be noted

**Research Location:** `research/documentation/`

---

## Quick Reference Links

### Essential Documentation

- **Project README:** `README.md`
- **CLAUDE.md:** `CLAUDE.md` (project instructions)
- **Upgrades README:** `upgrades/README.md`
- **Research README:** `research/README.md`
- **Test Structure:** `upgrades/active/temporal-implementation/tests/STRUCTURE.md`

### Key Code Locations

- **Graphiti Service:** `apex-memory-system/src/apex_memory/services/graphiti_service.py`
- **Temporal Activities:** `apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`
- **Temporal Workflows:** `apex-memory-system/src/apex_memory/temporal/workflows/ingestion.py`
- **Metrics:** `apex-memory-system/src/apex_memory/monitoring/metrics.py`
- **API:** `apex-memory-system/src/apex_memory/api/ingestion.py`

### Monitoring Endpoints

- **Grafana:** http://localhost:3001/d/temporal-ingestion
- **Temporal UI:** http://localhost:8088
- **Prometheus:** http://localhost:9090
- **API Docs:** http://localhost:8000/docs
- **Neo4j Browser:** http://localhost:7474

---

## Document Version

**Created:** 2025-10-19
**Author:** Claude Code (Apex Memory System Development)
**Purpose:** Complete research foundation for Graphiti + JSON integration
**Status:** Active - Reference for implementation phases

---

**End of Research References**

For questions or clarifications, refer to:
- **PLANNING.md** - Overall strategy and timeline
- **IMPLEMENTATION.md** - Step-by-step technical guide
- **TESTING.md** - Test specifications and success criteria
- **TROUBLESHOOTING.md** - Common issues and solutions
