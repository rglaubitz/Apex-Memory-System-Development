# Multi-Database Schema Overhaul - Implementation Plan

**Project Duration:** 2-3 weeks (6 phases)
**Status:** 📝 Planning Complete | 🚀 Ready for Phase 2
**Last Updated:** 2025-11-01

---

## Table of Contents

1. [Project Goals](#project-goals)
2. [Phase Breakdown](#phase-breakdown)
3. [Task Checklist](#task-checklist)
4. [Timeline](#timeline)
5. [Dependencies](#dependencies)
6. [Risk Management](#risk-management)

---

## Project Goals

### Primary Objectives

1. **Complete Neo4j Redesign**
   - Implement migration system (like PostgreSQL's Alembic)
   - Coordinate with Graphiti labels (:Entity, :Episode, :Edge, :Community)
   - Define 5 custom entity types
   - Optimize indexes for temporal queries (<50ms P90)

2. **Multi-Database Coordination**
   - Standardize ID mapping (UUID v7 across all databases)
   - Implement saga pattern with compensation activities
   - Create cache strategy (TTL + event-driven invalidation)
   - Target: <200ms multi-DB writes, >70% cache hit rate

3. **Graphiti Integration**
   - Define custom entity types (Customer, Equipment, Driver, Invoice, Load)
   - Migrate existing entities to Graphiti management
   - Implement temporal query patterns
   - Target: 90%+ extraction accuracy, <50ms temporal queries

4. **Production Readiness**
   - 30+ schema validation tests
   - Integration tests for multi-DB consistency
   - Performance benchmarks passing
   - Zero-downtime migration strategy

---

## Phase Breakdown

### Phase 1: Research Documentation (Days 1-2) ✅ COMPLETE

**Goal:** Document all research findings in organized, reference-quality guides.

**Deliverables:**

- [x] Neo4j best practices guide (2,000+ lines)
  - Node/relationship naming conventions
  - Index strategies (5 types: range, text, full-text, vector, point)
  - Constraint design (unique, exists, node key)
  - Migration system design
  - Graphiti coordination patterns

- [x] PostgreSQL/pgvector patterns (2,000+ lines)
  - Table design and normalization
  - pgvector HNSW configuration (m, ef_construction)
  - JSONB integration (GIN indexes)
  - Alembic workflow
  - Zero-downtime migrations

- [x] Qdrant collection design (3,000+ lines)
  - Collection configuration (distance metrics, vector size)
  - HNSW parameters
  - Quantization strategies (scalar, binary)
  - Payload indexing
  - PostgreSQL integration patterns

- [x] Graphiti integration guide (4,000+ lines)
  - Neo4j schema requirements
  - Custom entity types mapping
  - Temporal data model (bi-temporal)
  - Episode/Entity/Edge relationships
  - Migration strategy from existing schema

- [x] Multi-DB coordination patterns (3,800+ lines)
  - Saga pattern (orchestration vs choreography)
  - ID mapping strategies (UUID v7, ULID, Snowflake)
  - Consistency guarantees
  - Cache invalidation (TTL, event-driven, versioned)
  - Schema evolution (expand-contract)

- [x] GitHub implementation examples
  - LightRAG (7.1k stars) - Multi-DB RAG patterns
  - Microsoft GraphRAG (19.1k stars) - Graph + vector coordination
  - Neo4j LLM Graph Builder (2.4k stars) - Entity extraction
  - Cognee (3.2k stars) - Memory management
  - Quivr (37.2k stars) - PGVector production patterns

- [x] Current state analysis
  - Existing schema inventory (13 PostgreSQL tables, 11 Neo4j labels)
  - Gap analysis (Neo4j migrations missing, Qdrant lazy creation)
  - Migration recommendations

**Time:** 2 days
**Status:** ✅ Complete

---

### Phase 2: Schema Redesign (Days 3-8)

**Goal:** Implement formal, version-controlled schemas for all databases.

#### 2.1 Neo4j Complete Redesign (Days 3-5)

**Critical Tasks:**

- [ ] **Design Neo4j migration system**
  - Create `migrations/neo4j/` directory structure
  - Implement `Neo4jMigrationManager` class
  - Version tracking with `:SchemaVersion` nodes
  - Rollback support (U scripts for undo)

- [ ] **Coordinate with Graphiti**
  - Document label ownership:
    - Graphiti: :Entity, :Episode, :Edge, :Community
    - Apex: :Document, :Chunk, :Concept
    - Migrate: :Customer, :Equipment, :Driver, :Invoice, :Load → Graphiti
  - Create linking strategy for existing nodes
  - Plan dual-write period

- [ ] **Define custom entity types**
  - Create `schemas/entity_types.py`
  - Define 5 Pydantic models:
    - Customer (name, status, payment_terms, credit_limit, contact_email)
    - Equipment (equipment_type, equipment_number, make, model, status)
    - Driver (name, employee_id, license_number, status)
    - Invoice (invoice_number, invoice_date, amount, status)
    - Load (load_number, pickup_location, delivery_location, status)

- [ ] **Optimize indexes**
  - Create composite temporal index: `(valid_from, invalid_at)`
  - Add full-text indexes for entity search
  - Add vector indexes for embeddings (Neo4j 5.13+)
  - Remove unused indexes (monitor with `SHOW INDEXES`)

- [ ] **Write initial migration scripts**
  - V001__initial_schema.cypher (constraints + indexes)
  - V002__graphiti_indices.cypher (temporal indexes)
  - V003__custom_entity_types.cypher (entity type properties)

**Acceptance Criteria:**
- ✅ Migration system runs V001-V003 successfully
- ✅ All Graphiti constraints/indexes exist
- ✅ Schema validation tests pass
- ✅ Performance: temporal queries <50ms

**Time:** 3 days

---

#### 2.2 PostgreSQL Schema Optimization (Days 6-7)

**Tasks:**

- [ ] **Optimize pgvector indexes**
  - Tune HNSW parameters: m=16, ef_construction=100
  - Separate vector tables from metadata tables
  - Add missing indexes for structured_data table
  - Benchmark query performance (before/after)

- [ ] **JSONB schema enhancements**
  - Create GIN indexes for JSONB columns
  - Add path-specific indexes for nested JSON
  - Document JSONB query patterns
  - Test hybrid queries (JSONB + vector)

- [ ] **Alembic migrations**
  - Add `group_id` column (multi-tenancy support)
  - Add `schema_version` tracking column
  - Add embedding fields for structured_data
  - Create composite indexes (multi-column)

- [ ] **Create schema validation script**
  - `scripts/validate_postgresql_schema.py`
  - Verify all tables exist
  - Verify all indexes exist
  - Check pgvector extension enabled

**Acceptance Criteria:**
- ✅ pgvector queries <100ms (P90)
- ✅ JSONB queries with GIN indexes <50ms
- ✅ All Alembic migrations applied successfully
- ✅ Schema validation script passes

**Time:** 2 days

---

#### 2.3 Qdrant Collection Redesign (Day 8)

**Tasks:**

- [ ] **Formalize collection creation**
  - Create `scripts/setup/create_qdrant_collections.py`
  - Define collection configs declaratively
  - Version collection schemas

- [ ] **Enable quantization**
  - Scalar quantization (4x compression, 2x speed)
  - Binary quantization for high-dimensional vectors
  - Document when to use each method

- [ ] **Add structured_data collection**
  - Create `apex_structured_data` collection
  - Configure payload indices
  - Link to PostgreSQL structured_data table

- [ ] **Optimize payload indexing**
  - Add keyword indexes for entity_type, doc_type
  - Add integer indexes for chunk_index
  - Add datetime indexes for created_at

**Acceptance Criteria:**
- ✅ Collections created declaratively (no lazy creation)
- ✅ Quantization enabled (4x memory reduction verified)
- ✅ Payload queries <20ms
- ✅ Integration with PostgreSQL validated

**Time:** 1 day

---

### Phase 3: Multi-DB Coordination (Days 9-12)

**Goal:** Implement robust multi-database coordination patterns.

#### 3.1 ID Mapping Strategy (Day 9)

**Tasks:**

- [ ] **Standardize on UUID v7**
  - Create `utils/id_generation.py`
  - Implement `generate_entity_id()` using uuid7
  - Update all entity creation to use shared function

- [ ] **Create ID mapping table**
  - PostgreSQL schema:
    ```sql
    CREATE TABLE entity_id_mapping (
        internal_id UUID PRIMARY KEY,
        neo4j_uuid UUID,
        qdrant_point_id TEXT,
        graphiti_uuid UUID,
        entity_type TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    ```
  - Add Alembic migration
  - Create insert/lookup functions

- [ ] **Update entity creation workflows**
  - Generate UUID v7 once
  - Insert into ID mapping table
  - Use same ID in Neo4j, PostgreSQL, Qdrant, Redis

**Acceptance Criteria:**
- ✅ All new entities use UUID v7
- ✅ ID mapping table tracks all entities
- ✅ Cross-database lookups work via mapping table

**Time:** 1 day

---

#### 3.2 Saga Pattern Implementation (Days 10-11)

**Tasks:**

- [ ] **Enhance existing Temporal workflows**
  - Extend `DocumentIngestionWorkflow` with saga pattern
  - Create `EntityIngestionWorkflow` for Graphiti entities
  - Add compensation activities

- [ ] **Implement compensation activities**
  - `compensate_postgresql_write(entity_id)`
  - `compensate_graphiti_write(entity_id)`
  - `compensate_qdrant_write(entity_id)`
  - `compensate_redis_cache(entity_id)`

- [ ] **Add idempotency checks**
  - Track compensation executions in Redis
  - Key pattern: `compensated:{workflow_id}:{entity_id}`
  - TTL: 24 hours

- [ ] **Test failure scenarios**
  - Simulate PostgreSQL write failure
  - Simulate Graphiti write failure
  - Simulate Qdrant write failure
  - Verify compensations executed correctly

**Acceptance Criteria:**
- ✅ Multi-DB writes complete in <200ms (P90)
- ✅ Compensation activities are idempotent
- ✅ Failure tests pass (compensations work correctly)

**Time:** 2 days

---

#### 3.3 Cache Strategy (Day 12)

**Tasks:**

- [ ] **Implement TTL-based caching**
  - Entity metadata: 1 hour TTL
  - Query results: 5 minutes TTL
  - Temporal facts: 30 minutes TTL
  - Update Redis key patterns documentation

- [ ] **Add event-driven invalidation**
  - On entity update: delete cache keys
  - On relationship change: delete related caches
  - Pattern: `entity:{uuid}`, `entity:{uuid}:relationships`

- [ ] **Implement cache warming**
  - Pre-load hot entities on startup
  - Background job for popular queries
  - Monitor cache hit rate

- [ ] **Add monitoring**
  - Track cache hit rate (target >70%)
  - Track invalidation events
  - Alert on cache stampede

**Acceptance Criteria:**
- ✅ Cache hit rate >70%
- ✅ Event-driven invalidation working
- ✅ No cache stampede under load

**Time:** 1 day

---

### Phase 4: Graphiti Integration (Days 13-15)

**Goal:** Fully integrate Graphiti for temporal knowledge graphs.

#### 4.1 Custom Entity Types (Day 13)

**Tasks:**

- [ ] **Define all 5 entity types**
  - Complete `schemas/entity_types.py`
  - Add field descriptions for LLM extraction
  - Add validation rules

- [ ] **Update GraphitiService**
  - Modify `add_document_episode()` to pass entity_types
  - Add `entity_types` parameter
  - Test with sample documents

- [ ] **Test LLM extraction**
  - Ingest sample invoices (Customer, Invoice entities)
  - Ingest sample load documents (Driver, Equipment, Load entities)
  - Verify 90%+ extraction accuracy

**Acceptance Criteria:**
- ✅ All 5 entity types defined
- ✅ GraphitiService passes entity_types correctly
- ✅ LLM extraction accuracy >90%

**Time:** 1 day

---

#### 4.2 Migration from Existing Entities (Day 14)

**Tasks:**

- [ ] **Link existing nodes**
  - Cypher script: Match Apex nodes to Graphiti nodes by name
  - Create `[:GRAPHITI_ENTITY]` relationships
  - Document linking success rate

- [ ] **Parallel ingestion**
  - Continue creating Apex entities (backward compatibility)
  - ALSO ingest to Graphiti
  - Monitor for duplicates

- [ ] **Migrate reads to Graphiti-first**
  - Update `get_customer()` to try Graphiti first
  - Fallback to legacy Apex nodes
  - Log usage patterns

- [ ] **Plan deprecation**
  - After 2 weeks, verify Graphiti has all entities
  - Create script to delete legacy Apex nodes
  - Test in staging

**Acceptance Criteria:**
- ✅ Existing entities linked to Graphiti
- ✅ Parallel ingestion working (no duplicates)
- ✅ Reads migrated to Graphiti-first

**Time:** 1 day

---

#### 4.3 Temporal Query Patterns (Day 15)

**Tasks:**

- [ ] **Implement point-in-time queries**
  - Get entity state at time T
  - Get relationship changes over time
  - Find entities that changed in date range

- [ ] **Add temporal search to API**
  - `/api/entities/{id}/history` endpoint
  - `/api/entities/{id}/state?timestamp=T` endpoint
  - `/api/search/temporal?query=...&timestamp=T` endpoint

- [ ] **Create temporal analytics**
  - Most changed entities
  - Relationship churn rate
  - Entity lifecycle analysis

- [ ] **Performance optimization**
  - Ensure composite temporal index used
  - Profile temporal queries (<50ms target)
  - Add caching for common temporal queries

**Acceptance Criteria:**
- ✅ Point-in-time queries work correctly
- ✅ Temporal API endpoints functional
- ✅ Performance: temporal queries <50ms (P90)

**Time:** 1 day

---

### Phase 5: Testing & Validation (Days 16-18)

**Goal:** Comprehensive testing to ensure production readiness.

#### 5.1 Schema Validation Tests (Day 16)

**Tasks:**

- [ ] **Neo4j schema tests**
  - `tests/schema/test_neo4j_schema.py`
  - Test all constraints exist
  - Test all indexes exist
  - Test Graphiti labels present
  - Test migration system works

- [ ] **PostgreSQL schema tests**
  - `tests/schema/test_postgresql_schema.py`
  - Test all tables exist
  - Test all indexes exist
  - Test pgvector extension enabled
  - Test Alembic migrations applied

- [ ] **Qdrant schema tests**
  - `tests/schema/test_qdrant_schema.py`
  - Test collections exist
  - Test quantization enabled
  - Test payload indexes exist

- [ ] **Schema audit script**
  - `scripts/audit/audit_schemas.py`
  - Check consistency across databases
  - Verify ID mapping integrity
  - Generate audit report

**Acceptance Criteria:**
- ✅ 30+ schema validation tests passing
- ✅ Schema audit script passes
- ✅ No schema drift detected

**Time:** 1 day

---

#### 5.2 Integration Tests (Day 17)

**Tasks:**

- [ ] **Multi-DB consistency tests**
  - Test entity exists in all databases
  - Test same UUID used everywhere
  - Test properties match across databases

- [ ] **Temporal query tests**
  - Test point-in-time queries
  - Test relationship history queries
  - Test entity lifecycle queries

- [ ] **Saga pattern tests**
  - Test successful multi-DB write
  - Test compensation on failure
  - Test idempotency

- [ ] **Cache tests**
  - Test TTL expiration
  - Test event-driven invalidation
  - Test cache hit rate >70%

**Acceptance Criteria:**
- ✅ Integration tests passing
- ✅ No data inconsistencies found
- ✅ Saga pattern working correctly

**Time:** 1 day

---

#### 5.3 Performance Benchmarks (Day 18)

**Tasks:**

- [ ] **Temporal query benchmarks**
  - Point-in-time queries: target <50ms (P90)
  - Relationship history: target <100ms (P90)
  - Multi-hop temporal traversal: target <150ms (P90)

- [ ] **Multi-DB write benchmarks**
  - Single entity ingestion: target <200ms (P90)
  - Bulk ingestion: target 10+ docs/second
  - Saga compensation: target <500ms total

- [ ] **Hybrid search benchmarks**
  - Vector search (Qdrant): target <50ms
  - Graph traversal (Neo4j): target <100ms
  - Combined hybrid: target <150ms

- [ ] **Load testing**
  - 1,000 concurrent queries
  - 100 ingestions/second
  - Monitor for bottlenecks

**Acceptance Criteria:**
- ✅ All performance targets met
- ✅ No performance regressions
- ✅ Load tests pass without errors

**Time:** 1 day

---

### Phase 6: Production Migration (Days 19-21)

**Goal:** Zero-downtime migration to new schemas.

#### 6.1 Backup & Safety (Day 19)

**Tasks:**

- [ ] **Full database backups**
  - Backup PostgreSQL (pg_dump)
  - Backup Neo4j (neo4j-admin dump)
  - Backup Qdrant snapshots
  - Store backups securely

- [ ] **Test restoration**
  - Restore PostgreSQL to staging
  - Restore Neo4j to staging
  - Restore Qdrant to staging
  - Verify data integrity

- [ ] **Create rollback plan**
  - Document rollback steps
  - Create rollback scripts
  - Test rollback in staging

**Acceptance Criteria:**
- ✅ All databases backed up
- ✅ Restoration tested successfully
- ✅ Rollback plan documented

**Time:** 1 day

---

#### 6.2 Staged Migration (Days 20-21)

**Stage 1: Apply Schema Changes (No Data Migration)**

- [ ] Run Neo4j migrations (V001-V003)
- [ ] Apply PostgreSQL Alembic migrations
- [ ] Create Qdrant collections with new configs
- [ ] Verify schema changes applied

**Stage 2: Parallel Ingestion (New + Old Schema)**

- [ ] Enable dual-write mode
- [ ] New data → new schema (Graphiti)
- [ ] Also write to old schema (backward compatibility)
- [ ] Monitor for 24 hours

**Stage 3: Migrate Existing Entities**

- [ ] Link existing Apex entities to Graphiti
- [ ] Create `[:GRAPHITI_ENTITY]` relationships
- [ ] Verify linkage success rate >95%

**Stage 4: Switch Reads to New Schema**

- [ ] Update API to read from Graphiti first
- [ ] Fallback to old schema if not found
- [ ] Monitor error rate

**Stage 5: Deprecate Old Schema**

- [ ] After 1 week validation, stop dual-writes
- [ ] Delete old Apex entity nodes
- [ ] Remove backward compatibility code

**Acceptance Criteria:**
- ✅ Zero downtime during migration
- ✅ No data loss
- ✅ All systems operational
- ✅ Performance targets maintained

**Time:** 2 days

---

## Task Checklist

### Phase 1: Research Documentation ✅
- [x] Neo4j best practices guide
- [x] PostgreSQL/pgvector patterns
- [x] Qdrant collection design
- [x] Graphiti integration guide
- [x] Multi-DB coordination patterns
- [x] GitHub implementation examples
- [x] Current state analysis

### Phase 2: Schema Redesign
#### Neo4j
- [ ] Design migration system
- [ ] Coordinate with Graphiti labels
- [ ] Define 5 custom entity types
- [ ] Optimize indexes
- [ ] Write V001-V003 migrations

#### PostgreSQL
- [ ] Optimize pgvector indexes
- [ ] JSONB enhancements
- [ ] Alembic migrations
- [ ] Schema validation script

#### Qdrant
- [ ] Formalize collection creation
- [ ] Enable quantization
- [ ] Add structured_data collection
- [ ] Optimize payload indexing

### Phase 3: Multi-DB Coordination
- [ ] Standardize UUID v7
- [ ] Create ID mapping table
- [ ] Enhance Temporal workflows with saga
- [ ] Implement compensation activities
- [ ] TTL-based caching
- [ ] Event-driven invalidation

### Phase 4: Graphiti Integration
- [ ] Define 5 custom entity types
- [ ] Update GraphitiService
- [ ] Link existing nodes
- [ ] Parallel ingestion
- [ ] Migrate reads to Graphiti-first
- [ ] Implement temporal query patterns

### Phase 5: Testing & Validation
- [ ] Schema validation tests (30+)
- [ ] Integration tests
- [ ] Temporal query tests
- [ ] Performance benchmarks
- [ ] Load testing

### Phase 6: Production Migration
- [ ] Full database backups
- [ ] Test restoration
- [ ] Stage 1: Apply schema changes
- [ ] Stage 2: Parallel ingestion
- [ ] Stage 3: Migrate existing entities
- [ ] Stage 4: Switch reads
- [ ] Stage 5: Deprecate old schema

---

## Timeline

```
Week 1: Research + Neo4j Redesign
├── Days 1-2: Research Documentation ✅
├── Days 3-5: Neo4j Complete Redesign
├── Days 6-7: PostgreSQL Optimization
└── Day 8: Qdrant Formalization

Week 2: Coordination + Graphiti
├── Days 9-12: Multi-DB Coordination
├── Days 13-15: Graphiti Integration
└── Days 16-18: Testing & Validation

Week 3: Production Migration
└── Days 19-21: Staged Rollout
```

**Total Duration:** 21 days (3 weeks)

---

## Dependencies

### Critical Path

1. **UUID v7 standardization** (Day 9) BLOCKS multi-DB coordination
2. **Neo4j migration system** (Days 3-5) BLOCKS Graphiti integration
3. **Temporal indexes** (Day 4) BLOCKS temporal query performance
4. **Custom entity types** (Day 13) BLOCKS Graphiti entity extraction
5. **Schema validation tests** (Day 16) BLOCKS production migration

### Phase Dependencies

- **Phase 2** requires Phase 1 complete (research)
- **Phase 3** requires Phase 2 complete (schemas exist)
- **Phase 4** requires Phase 2-3 complete (schemas + coordination)
- **Phase 5** requires Phase 2-4 complete (everything to test)
- **Phase 6** requires Phase 5 complete (tests passing)

---

## Risk Management

### High-Risk Areas

1. **Neo4j Migration System**
   - Risk: No built-in tool like Alembic
   - Mitigation: Custom system based on proven patterns, extensive testing

2. **Graphiti Entity Migration**
   - Risk: Existing entities may not link cleanly
   - Mitigation: Parallel ingestion period, fallback to legacy

3. **Performance Degradation**
   - Risk: New schemas slower than old
   - Mitigation: Benchmarks before/after, rollback if targets not met

4. **Data Loss During Migration**
   - Risk: Migration script errors
   - Mitigation: Full backups, staging tests, staged rollout

### Mitigation Strategies

- ✅ **Comprehensive testing** before production (30+ tests)
- ✅ **Staged rollout** with monitoring at each stage
- ✅ **Rollback procedures** tested in staging
- ✅ **Parallel ingestion** period for safety
- ✅ **Performance benchmarks** as gate before migration

---

## Success Metrics

### Quantitative

- ✅ 30+ schema validation tests passing (100%)
- ✅ Temporal queries <50ms (P90)
- ✅ Multi-DB writes <200ms (P90)
- ✅ Cache hit rate >70%
- ✅ Entity extraction accuracy >90%
- ✅ Zero data loss during migration
- ✅ Zero downtime during migration

### Qualitative

- ✅ Schemas are version-controlled and documented
- ✅ Migration system is repeatable and tested
- ✅ Team understands new schema patterns
- ✅ Operations has runbooks for maintenance

---

**Next Steps:** Begin Phase 2 - Neo4j Complete Redesign
**Command to Resume:** See [IMPLEMENTATION.md](IMPLEMENTATION.md) for step-by-step guide
