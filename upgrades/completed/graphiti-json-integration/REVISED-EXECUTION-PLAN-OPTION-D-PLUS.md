# Revised Execution Plan: Graphiti + JSON Integration (Option D+)

**Architecture Decision:** Option D+ (Hub Rigidity + Property Flexibility)
**Approved:** November 5, 2025
**Timeline:** 5 days (34 hours)
**Current Status:** 82% complete → Refactoring to unified schema

---

## Architecture Overview

### The Philosophy

**"Rigid at the hub level, flexible at the data level"**

**What Changed from Original Plan:**
- ❌ **OLD:** Separate Graphiti types (5 minimal) + Backbone types (45 full) with UUID linkage
- ✅ **NEW:** Single unified entity schemas (45 entities) with three-tier property system

### Three-Tier Property System

Every entity has three property tiers:

```
┌─────────────────────────────────────────────────────┐
│ TIER 1: CORE (Required)                             │
│ - uuid, name, hub, entity_type, created_at          │
│ - RIGID: Must exist for entity to be valid          │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ TIER 2: STRUCTURED (Optional)                       │
│ - 44 Backbone schema fields (Customer example)      │
│ - SEMI-RIGID: Optional but typed/validated          │
│ - Some have llm_extractable=True (Graphiti extracts)│
│ - Others llm_extractable=False (manual/API entry)   │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ TIER 3: DYNAMIC (Catch-all)                         │
│ - additional_properties: Dict[str, Any]             │
│ - FLEXIBLE: Anything Graphiti extracts that doesn't │
│   match schema goes here (nothing falls through!)   │
│ - extracted_fields_not_in_schema: List[str]         │
└─────────────────────────────────────────────────────┘
```

### Hub Rigidity Enforcement

**6 Hubs (RIGID - cannot add new hubs without architecture review):**
1. Hub 1: G (Command Center) - 8 entities
2. Hub 2: OpenHaul (Brokerage) - 8 entities
3. Hub 3: Origin Transport - 7 entities
4. Hub 4: Contacts/CRM - 7 entities
5. Hub 5: Financials - 8 entities
6. Hub 6: Corporate Infrastructure - 7 entities

**Entity Types (SEMI-RIGID - can add new types to existing hubs):**
- 45 defined entity types with full schemas
- Each entity assigned to exactly one hub (enforced programmatically)
- Example: `customer` → Hub 4, `invoice` → Hub 5, `truck` → Hub 3

**Properties (FLEXIBLE - can add to Tier 2 or use Tier 3):**
- Tier 2: Add new optional fields to schema as needed
- Tier 3: Extract anything → `additional_properties`
- Schema evolves based on usage patterns

---

## Revised Implementation Plan

### PHASE 1: Unified Schema Architecture (Day 1: 8 hours)

**Changed from original:** Instead of dual labels + linkage, create unified schemas

**Morning Session (4 hours)**

**Task 1.1: Create Unified Entity Base Class**
- File: `apex_memory/models/entities/base.py`
- Create `BaseEntity` with three-tier property system
- Add `llm_extractable` field metadata
- Add hub assignment validation
- Add `additional_properties` and `extracted_fields_not_in_schema`

**Task 1.2: Migrate Graphiti Custom Types to Full Backbone Schemas**
- File: `apex_memory/models/entities/customer.py` (new - 44 properties)
- File: `apex_memory/models/entities/person.py` (new - 39 properties)
- File: `apex_memory/models/entities/invoice.py` (new - 20 properties)
- File: `apex_memory/models/entities/truck.py` (new - 40 properties)
- File: `apex_memory/models/entities/load.py` (new - 45 properties)
- **Mark fields with `llm_extractable=True/False`**
- **Add Tier 3 catch-all to each**

**Afternoon Session (4 hours)**

**Task 1.3: Update Graphiti Configuration**
- File: `apex_memory/services/graphiti_service.py`
- Update to use full Backbone entity schemas
- Create `get_llm_prompt_schema()` helper (filters llm_extractable=True only)
- Configure Graphiti with 45 entity types (not just 5)

**Task 1.4: Create Smart Population Helper**
- File: `apex_memory/utils/entity_population.py`
- `populate_entity_from_extraction()` function
  - Maps extracted fields to Tier 2 (structured) if schema match
  - Moves unmatched fields to Tier 3 (additional_properties)
  - Tracks mismatches in `extracted_fields_not_in_schema`

**Task 1.5: Hub Assignment Validator**
- File: `apex_memory/utils/hub_validator.py`
- `HUB_ASSIGNMENTS` constant (45 entity types → 6 hubs)
- `validate_hub_assignment()` enforces rigid hub structure

**Deliverables:**
- ✅ BaseEntity with three-tier system
- ✅ 5 unified entity schemas (Customer, Person, Invoice, Truck, Load)
- ✅ Graphiti configured to use full schemas
- ✅ Smart population helper
- ✅ Hub validator

---

### PHASE 2: Update Extraction Pipeline (Day 2: 6 hours)

**Changed from original:** Extract to unified schema instead of minimal types

**Morning Session (3 hours)**

**Task 2.1: Update Graphiti Extraction Activity**
- File: `apex_memory/temporal/activities/ingestion.py`
- Update `extract_entities_with_graphiti_activity()`
  - Access `result.nodes` (full Graphiti Node objects)
  - Use `populate_entity_from_extraction()` for smart mapping
  - Store in unified schema format (Tier 2 + Tier 3)

**Task 2.2: Update Entity Type Mapping**
- Remove old minimal type logic
- Use hub validator for entity type → hub assignment
- Ensure all 45 entity types supported (not just 5)

**Afternoon Session (3 hours)**

**Task 2.3: Update Neo4j Writer**
- File: `apex_memory/database/neo4j_writer.py`
- Write entities with hub-based labels (`:Customer` not `:Entity`)
- Store Tier 2 properties as node properties
- Store Tier 3 (`additional_properties`) as JSON property
- Create hub-based indices

**Task 2.4: Update PostgreSQL Writer**
- File: `apex_memory/database/postgres_writer.py`
- Store full entity in `entities` table
- Add `additional_properties` JSONB column
- Add `extracted_fields_not_in_schema` TEXT[] column
- Create index on `additional_properties` for GIN queries

**Deliverables:**
- ✅ Extraction pipeline uses unified schemas
- ✅ Neo4j stores hub-based entities (`:Customer`, `:Invoice`, etc.)
- ✅ PostgreSQL stores Tier 3 catch-all
- ✅ Nothing falls through cracks

---

### PHASE 3: Fix Tests + Create Staging Infrastructure (Day 2: 4 hours)

**Mostly unchanged from original, just update expectations**

**Task 3.1: Fix Test Failures**
- Update `test_graphiti_extraction_activity.py` for unified schemas
- Expect `:Customer` labels instead of `:Entity`
- Expect `additional_properties` field in results
- Fix entity type assertions (customer not 'other')

**Task 3.2: Create Staging Infrastructure**
```bash
mkdir -p /tmp/apex-staging/{samsara,turvo,frontapp}/{pending,processed,failed}
chmod 755 /tmp/apex-staging
```

**Task 3.3: Fix Staging Tests**
- Update staging tests for unified schema format
- Ensure JSON ingestion uses same three-tier system

**Deliverables:**
- ✅ All tests passing with unified schema
- ✅ Staging infrastructure created
- ✅ Staging tests fixed

---

### PHASE 4: Schema Evolution System (Day 3: 8 hours)

**New phase - wasn't in original plan, critical for Option D+**

**Morning Session (4 hours)**

**Task 4.1: Create Schema Evolution Analyzer**
- File: `apex_memory/utils/schema_evolution.py`
- `analyze_additional_properties()` function
  - Query PostgreSQL for common fields in `additional_properties`
  - Generate usage reports (field name, usage count, example values)
  - Recommend fields for promotion to Tier 2 (>40% usage threshold)

**Task 4.2: Create Schema Migration Generator**
- File: `apex_memory/utils/schema_migration_generator.py`
- `generate_field_promotion_migration()` function
  - Takes field name + type from analyzer
  - Generates Pydantic field definition
  - Generates Alembic migration for PostgreSQL
  - Generates Neo4j migration for new property

**Afternoon Session (4 hours)**

**Task 4.3: Create Admin Dashboard Endpoint**
- File: `apex_memory/api/admin/schema_evolution.py`
- `GET /api/admin/schema/evolution` - Show unstructured fields + usage stats
- `POST /api/admin/schema/promote` - Promote field to Tier 2
- Requires authentication (admin only)

**Task 4.4: Documentation**
- Create `SCHEMA-EVOLUTION-GUIDE.md`
- Document weekly review process
- Document promotion criteria
- Document migration workflow

**Deliverables:**
- ✅ Schema evolution analyzer
- ✅ Migration generator
- ✅ Admin API endpoints
- ✅ Evolution guide

---

### PHASE 5: Workflow Separation (Day 4: 8 hours)

**Unchanged from original - Full separation approved**

**Morning Session (4 hours)**

**Task 5.1: Create Separate Document Activities**
- File: `apex_memory/temporal/activities/document_ingestion.py`
- Extract document-specific activities from shared file
- `parse_document_activity`
- `extract_document_entities_activity`
- `generate_document_embeddings_activity`
- `write_document_to_databases_activity`

**Task 5.2: Create Separate JSON Activities**
- File: `apex_memory/temporal/activities/json_ingestion.py`
- Extract JSON-specific activities from shared file
- `fetch_json_data_activity`
- `extract_json_entities_activity`
- `generate_json_embeddings_activity`
- `write_json_to_databases_activity`

**Afternoon Session (4 hours)**

**Task 5.3: Separate API Endpoints**
- File: `apex_memory/api/ingestion.py`
- `/api/v1/documents/ingest` - Document ingestion endpoint
- `/api/v1/structured-data/ingest` - JSON ingestion endpoint
- Different request models (DocumentIngestionRequest vs JSONIngestionRequest)
- Different response schemas

**Task 5.4: Configure Separate Task Queues**
- File: `apex_memory/temporal/workers/dev_worker.py`
- Register DocumentIngestionWorkflow on `apex-document-queue`
- Register StructuredDataIngestionWorkflow on `apex-json-queue`
- Update worker startup to listen to both queues

**Deliverables:**
- ✅ Separate activity modules
- ✅ Separate API endpoints
- ✅ Separate task queues
- ✅ Zero cross-contamination

---

### PHASE 6: Testing & Documentation (Day 5: 8 hours)

**Updated to include schema evolution testing**

**Morning Session (4 hours)**

**Task 6.1: Write Integration Tests**
- File: `tests/integration/test_unified_schema.py`
  - Test Tier 2 extraction (structured fields)
  - Test Tier 3 catch-all (unmatched fields)
  - Test `extracted_fields_not_in_schema` tracking
  - Test schema evolution analyzer

- File: `tests/integration/test_workflow_separation.py`
  - Test document workflow independence
  - Test JSON workflow independence
  - Test concurrent execution
  - Test queue isolation

**Task 6.2: Run Complete Test Suite**
```bash
pytest tests/ -v --ignore=tests/load/
# Target: 170+ tests passing (156 baseline + 14 new)
```

**Afternoon Session (4 hours)**

**Task 6.3: Create Comprehensive Documentation**
- Update `CLAUDE.md` with Option D+ architecture
- Update `graphiti-json-integration/README.md`
- Create `OPTION-D-PLUS-ARCHITECTURE.md` (handoff doc)
- Create `SCHEMA-EVOLUTION-GUIDE.md`
- Update API documentation (Swagger/OpenAPI)

**Task 6.4: Create Handoff Document**
- File: `HANDOFF-GRAPHITI-JSON-COMPLETE-OPTION-D-PLUS.md`
- Document implementation decisions
- Document schema evolution process
- Document query patterns
- Include examples and code snippets

**Deliverables:**
- ✅ 170+ tests passing (100% pass rate)
- ✅ All documentation updated
- ✅ Handoff document created
- ✅ Ready for production deployment

---

## Comparison: Original Plan vs Option D+

| Aspect | Original Plan | Option D+ Plan |
|--------|--------------|----------------|
| Entity schemas | 5 minimal + 45 full (50 total) | 45 unified schemas |
| Graphiti extraction | 5 types, 6-10 properties | 45 types, Tier 2 subset |
| Missing data handling | Lost (no catch-all) | Tier 3 catch-all |
| Hub enforcement | Manual (no validation) | Programmatic validator |
| Schema evolution | Manual updates | Automated analyzer + migrator |
| Integration complexity | High (UUID linkage) | Low (single schema) |
| Maintenance burden | 2 schemas to update | 1 schema to update |
| Query complexity | Joins required | Single node |
| Total effort | 30 hours | 42 hours (+12 for evolution system) |

---

## Timeline Summary

| Phase | Day | Hours | Key Changes from Original |
|-------|-----|-------|---------------------------|
| Phase 1 | Day 1 | 8h | **NEW:** Unified schemas instead of dual labels |
| Phase 2 | Day 2 | 6h | **UPDATED:** Extract to unified schema |
| Phase 3 | Day 2 | 4h | **SAME:** Fix tests + staging |
| Phase 4 | Day 3 | 8h | **NEW:** Schema evolution system (not in original) |
| Phase 5 | Day 4 | 8h | **SAME:** Workflow separation (full) |
| Phase 6 | Day 5 | 8h | **UPDATED:** Test unified schema + evolution |
| **TOTAL** | **5 days** | **42 hours** | **+12 hours vs original (worth it!)** |

---

## Critical Success Factors

**✅ Must Have:**
1. Hub validator enforces rigid 6-hub structure
2. All 45 entity types have unified schemas (not just 5)
3. `llm_extractable` flags accurate on all fields
4. Tier 3 catch-all implemented on all entities
5. Schema evolution analyzer working
6. Nothing falls through cracks (100% data capture)

**🎯 Should Have:**
1. >40% promotion threshold for Tier 3 → Tier 2
2. Weekly schema evolution review process
3. Admin dashboard for field promotion
4. Audit trail of schema changes

**💡 Nice to Have:**
1. Automated field type inference (string vs number vs date)
2. ML-based field clustering (find related unstructured fields)
3. Schema versioning system
4. Backward compatibility testing

---

## Risk Assessment

**Risk 1: Schema Rigidity vs Flexibility Balance**
- **Impact:** If too rigid, data lost; if too flexible, schema chaos
- **Mitigation:** Three-tier system balances both + evolution analyzer
- **Probability:** Low (architecture designed to prevent)

**Risk 2: Performance with 45 Entity Types**
- **Impact:** Graphiti LLM may be slower with larger schema context
- **Mitigation:** Filter to `llm_extractable=True` only (6-10 fields per type)
- **Probability:** Low (same field count as before)

**Risk 3: Migration Complexity**
- **Impact:** Existing Graphiti extractions use old minimal schema
- **Mitigation:** Migration script to populate `additional_properties`
- **Probability:** Medium (planned for Phase 3)

**Risk 4: Developer Onboarding**
- **Impact:** New developers confused by three-tier system
- **Mitigation:** Comprehensive handoff documentation (this plan + OPTION-D-PLUS-ARCHITECTURE.md)
- **Probability:** Low (well-documented)

---

## Next Steps After Approval

1. ✅ **Plan approved** (Done!)
2. 🔄 **Update TODO list** with Phase 1-6 tasks
3. 🚀 **Begin Phase 1:** Create unified BaseEntity + 5 core schemas
4. 📊 **Daily standups:** Review progress, adjust as needed

**Ready to begin Phase 1 implementation.**

---

**Document Version:** 1.0
**Created:** November 5, 2025
**Architecture:** Option D+ (Hub Rigidity + Property Flexibility)
**Status:** Approved, ready for execution
