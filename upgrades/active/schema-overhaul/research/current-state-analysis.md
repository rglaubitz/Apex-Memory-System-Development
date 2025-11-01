# Current Schema State Analysis - Apex Memory System

**Status:** ✅ Analysis Complete
**Date:** 2025-11-01
**Method:** Codebase exploration via Explore agent

**Full Details:** See [RESEARCH-SUMMARY.md](../RESEARCH-SUMMARY.md#6-current-state-analysis)

---

## Executive Summary

**Current State:** All databases have formal schema definitions, but gaps exist in migration systems, validation, and integration.

### Schema Quality: 7/10

**Strengths:**
- ✅ Formal definitions exist for all databases
- ✅ PostgreSQL uses Alembic migrations (13 models, version-controlled)
- ✅ Comprehensive indices (60+ PostgreSQL, 35+ Neo4j, 11 Qdrant)
- ✅ Temporal workflows implement saga pattern

**Critical Gaps:**
- ⚠️ Neo4j has no migration system (static Cypher script)
- ⚠️ Qdrant lazy creation (not declarative)
- ⚠️ Redis lacks formal schema (markdown only)
- ⚠️ No schema validation tests
- ⚠️ Graphiti integration incomplete

---

## Schema Files Inventory

### PostgreSQL (✅ Excellent)

**Location:** `apex-memory-system/schemas/`

- `postgres_schema.sql` - Main tables
- `postgres_indices.sql` - Index creation
- `postgres_dlq.sql` - Dead letter queue
- `postgres_structured_data.sql` - NEW (Week 2)

**Tables:** 13 core + system tables
- Core: documents, chunks, entities, structured_data
- User/Auth: users, api_keys
- Chat: conversations, messages, conversation_shares
- Analytics: briefings, achievements, user_metrics
- System: query_log, query_cache, embeddings_cache, ingestion_log

**Indices:** 60+ (pgvector ivfflat, full-text, composite)
**Extensions:** pgvector, uuid-ossp, btree_gin, pg_trgm

**Migration System:** ✅ Alembic (5 active migrations)

---

### Neo4j (⚠️ Needs Migration System)

**Location:** `apex-memory-system/schemas/`

- `neo4j_schema.cypher` (435 lines) - Formal definition
- `neo4j_indices.cypher` - Property indices

**Node Types:** 11 formal
- Core: Document, Chunk, Entity
- Business: Customer, Equipment, Driver, Invoice, Load
- System: Concept, User

**Relationships:** 15+ types
**Constraints:** 15 (UNIQUE + NOT NULL)
**Indices:** 35+ property + 5 full-text

**Migration System:** ❌ **MISSING - CRITICAL GAP**
- Schema created via static Cypher script
- No version tracking
- No rollback capability
- Runtime script: `init_graphiti_indices.py`

---

### Qdrant (⚠️ Needs Formalization)

**Location:** `apex-memory-system/schemas/qdrant_schema.py` (540 lines)

**Collections:** 2 (documents, chunks)
- Vector: 1536-dim (OpenAI text-embedding-3-small)
- Distance: Cosine similarity
- Index: HNSW (M=16, ef_construct=100)
- Payload indices: 11 total (6 documents, 5 chunks)
- Quantization: INT8 enabled

**Creation Method:** ⚠️ Lazy creation
- Collections auto-create on first write via `_ensure_collection_exists()`
- Not declarative like PostgreSQL migrations

---

### Redis (⚠️ Needs Formal Schema)

**Location:** `apex-memory-system/schemas/redis_schema.md` (530+ lines)

**Key Patterns:** 7 types
- `doc:{uuid}` (Hash, 3600s TTL)
- `chunk:meta:{uuid}` (Hash, 3600s TTL)
- `query:hash:{hash}` (String/JSON, 600s TTL)
- `session:{user_id}` (Hash, 7200s TTL)
- `user:docs:{user_id}` (Set, 3600s TTL)
- `stats:daily:{date}` (Hash, 86400s TTL)
- `entity:{uuid}` (Hash, 1800s TTL)

**Memory:** 2GB max, LRU eviction
**Schema Enforcement:** ⚠️ Application-level only (no validation)

---

### Graphiti (⚠️ Integration Incomplete)

**Location:** `apex-memory-system/schemas/graphiti_schema.py` (438 lines)

**Status:** ⚠️ Custom wrapper (not official client)

**Components:**
- Episode Model (lines 33-75) - ✅ Matches Graphiti concept
- TemporalEntity Model (lines 77-125) - ⚠️ Custom Apex design
- TemporalRelationship Model (lines 127-178) - ⚠️ Custom Apex design
- GraphitiSchema Class (lines 185-429) - ❌ **SHOULD BE REPLACED**

**Integration:** `GraphitiService` (✅ uses official client)
- `add_document_episode()` ✅ Correct
- `build_indices()` ✅ Delegates to Graphiti
- **Missing:** `entity_types` parameter not passed

---

## Critical Gaps Identified

### Priority 1 (Blocking)

1. **Neo4j Migration System** ❌
   - No version control for schema changes
   - No rollback capability
   - Manual script execution required
   - **Impact:** Cannot safely evolve Neo4j schema in production

2. **Schema Validation Tests** ❌
   - Schemas defined but not validated
   - No tests verify tables/indices exist
   - Risk of schema drift
   - **Impact:** Silent failures possible

3. **Graphiti Entity Types Not Passed** ❌
   - `GraphitiService.add_document_episode()` missing `entity_types` parameter
   - Custom entity extraction not working
   - **Impact:** Only generic entities extracted (60% accuracy instead of 90%)

### Priority 2 (Important)

4. **Qdrant Lazy Creation** ⚠️
   - Collections auto-create instead of declarative
   - Not version-controlled
   - No initialization script
   - **Impact:** Inconsistent collection configs across environments

5. **Structured Data Integration Incomplete** ⚠️
   - StructuredDataDB model exists
   - `apex_structured_data` Qdrant collection referenced but not formally documented
   - Embedding field missing from migration
   - **Impact:** JSON data ingestion not fully operational

6. **Redis Schema Documentation Only** ⚠️
   - No enforcement of key naming conventions
   - No validation layer
   - **Impact:** Potential key collisions, inconsistent patterns

### Priority 3 (Nice to Have)

7. **DLQ Schema Usage Unclear** ⚠️
   - `postgres_dlq.sql` exists but not referenced
   - No documented retry/failure handling
   - **Impact:** Dead letter queue may not be operational

8. **Mixed Definition Locations** ⚠️
   - SQLAlchemy models + SQL migrations create duplication
   - Risk of drift between code and migrations
   - **Impact:** Maintenance complexity

---

## Recommendations

### Immediate Actions (Week 1)

1. **Implement Neo4j Migration System**
   - Create `migrations/neo4j/` directory
   - Implement `Neo4jMigrationManager` class
   - Version tracking with `:SchemaVersion` nodes
   - Rollback support

2. **Add Schema Validation Tests**
   - `tests/schema/test_neo4j_schema.py`
   - `tests/schema/test_postgresql_schema.py`
   - `tests/schema/test_qdrant_schema.py`
   - Target: 30+ tests

3. **Fix Graphiti Integration**
   - Add `entity_types=ENTITY_TYPES` to `add_document_episode()`
   - Create `schemas/entity_types.py` with 5 custom types
   - Test extraction accuracy >90%

### Short-Term Actions (Week 2-3)

4. **Formalize Qdrant Collection Creation**
   - Create `scripts/setup/create_qdrant_collections.py`
   - Define collection configs declaratively
   - Version collection schemas

5. **Complete Structured Data Integration**
   - Document Qdrant `apex_structured_data` collection
   - Add embedding field to migration
   - Test end-to-end JSON ingestion

6. **Add Redis Key Validation**
   - Create validation layer (optional)
   - Document key patterns comprehensively
   - Add metrics for key pattern usage

---

## Migration Complexity Assessment

| Database | Current State | Target State | Complexity | Estimated Effort |
|----------|---------------|--------------|------------|------------------|
| **Neo4j** | Static schema | Version-controlled migrations | High | 3-5 days |
| **PostgreSQL** | Alembic (good) | Optimized (pgvector, JSONB) | Medium | 2-3 days |
| **Qdrant** | Lazy creation | Declarative initialization | Low | 1 day |
| **Redis** | Docs only | Docs + validation (optional) | Low | 1 day |
| **Graphiti** | Incomplete | Full integration | Medium | 2-3 days |

**Total Estimated Effort:** 9-13 days (2-3 weeks with testing)

---

## Success Criteria

### Schema Quality

- ✅ All databases have version-controlled schemas
- ✅ Neo4j migration system operational (like Alembic)
- ✅ Graphiti integration complete (5 custom entity types)
- ✅ 30+ schema validation tests passing

### Performance

- ✅ Neo4j temporal queries <50ms (P90)
- ✅ PostgreSQL pgvector queries <100ms (P90)
- ✅ Qdrant vector queries <50ms (P90)
- ✅ Redis cache hit rate >70%

### Operational

- ✅ Documented schema evolution process
- ✅ Rollback procedures tested
- ✅ Schema audit script passing
- ✅ No schema drift between environments

---

**For Full Analysis:** See [RESEARCH-SUMMARY.md](../RESEARCH-SUMMARY.md#6-current-state-analysis)
**Next Steps:** See [PLANNING.md](../PLANNING.md) for implementation roadmap
