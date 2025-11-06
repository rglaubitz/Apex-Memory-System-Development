# Graphiti Domain Configuration

**Status:** ✅ **50% COMPLETE** - Foundation Built in Temporal Implementation
**Priority:** Medium (Enhancement - foundation already working)
**Timeline:** 1-2 days remaining (5 more entities + validation)
**Goal:** Enhance domain-specific entity extraction for trucking/logistics (90%+ accuracy)

**Foundation Complete (Built in Temporal Implementation):**
- ✅ 5 Entity Schemas (Customer, Person, Invoice, Truck, Load)
- ✅ 177 Tier 2 properties, 67 LLM-extractable fields
- ✅ Helper module (`entity_schema_helpers.py`)
- ✅ Hub-based organization (6 rigid hubs, 45 entity types)
- ✅ Graphiti integration configured

**See:** `apex-memory-system/src/apex_memory/models/entities/` for implemented schemas

---

## Quick Start

**For implementers:**
1. Read [IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md) - Understand the problem and approach (5 min)
2. Follow [IMPLEMENTATION.md](IMPLEMENTATION.md) - Step-by-step implementation guide (2-3 days)
3. Run tests per [TESTING.md](TESTING.md) - Validate 90%+ accuracy (30 min)
4. If issues arise, check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common problems and solutions

**For reviewers:**
1. Review [IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md) - Goals and success metrics
2. Check [TESTING.md](TESTING.md) - Validation criteria and expected outputs

---

## Problem Statement

**Current State:** Graphiti uses generic entity extraction (no domain knowledge)

**Example (Current - Generic Extraction):**

```
Input Document:
"Invoice INV-2025-001 for $820.00 from ACME Auto Parts for brake pads for Truck VEH-1234. Paid via ACH transfer TX-5678."

Extracted Entities (Generic):
- Document: "Invoice"
- Organization: "ACME Auto Parts"
- Object: "Truck"
- Transaction: "ACH transfer"

Relationships (Generic):
- Document MENTIONS Organization
- Document MENTIONS Object
```

**Problem:** Entity types are random/generic. Relationships lack semantic meaning.

---

**Desired State:** Domain-configured extraction with trucking/logistics knowledge

**Example (Desired - Domain-Configured Extraction):**

```
Input Document:
"Invoice INV-2025-001 for $820.00 from ACME Auto Parts for brake pads for Truck VEH-1234. Paid via ACH transfer TX-5678."

Extracted Entities (Domain-Configured):
- PartsInvoice: "INV-2025-001" (amount: $820.00)
- Vendor: "ACME Auto Parts"
- Vehicle: "VEH-1234" (type: Truck)
- BankTransaction: "TX-5678"

Relationships (Domain-Configured):
- INV-2025-001 BELONGS_TO VEH-1234
- INV-2025-001 SUPPLIED_BY ACME Auto Parts
- INV-2025-001 PAID_BY TX-5678
```

**Benefit:** Accurate entity types, semantic relationships, queryable knowledge graph.

---

## Solution Overview

### What We're Building

**1. Domain Configuration Module** (`apex_memory.config.domain_config`)

- **10 Entity Types:** Vehicle, PartsInvoice, Vendor, BankTransaction, Driver, Shipment, Location, Customer, MaintenanceRecord, Route
- **8 Relationship Types:** BELONGS_TO, SUPPLIED_BY, PAID_BY, ASSIGNED_TO, DELIVERED_TO, BILLED_TO, LOCATED_AT, PERFORMED_ON
- **Custom Extraction Prompt:** Guide GPT-5 to recognize trucking/logistics patterns
- **Validation Framework:** Ensure 90%+ extraction accuracy

**2. Integration with Graphiti** (`apex_memory.services.graphiti_service`)

- Pass domain-specific extraction prompt to Graphiti
- Validate extracted entities/relationships
- Feature flag: `ENABLE_DOMAIN_CONFIGURED_GRAPHITI` (default: `false`)

**3. Validation Framework** (`tests/validate_extraction.py`)

- 10 sample documents (invoices, shipments, maintenance records, etc.)
- Expected outputs with 90%+ accuracy threshold
- Automated validation script

---

## Architecture

### Before (Generic Extraction)

```
Document → Graphiti (generic extraction) → Neo4j
Problem: Random entity types, missing relationships
```

### After (Domain-Configured Extraction)

```
Document → Graphiti (domain-configured) → Neo4j
Result: Accurate entity types, semantic relationships
```

### Feature Flag

```python
# Domain configuration disabled (default - safe)
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false
→ Uses generic extraction (existing behavior)

# Domain configuration enabled (opt-in)
ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true
→ Uses domain-configured extraction (new behavior)
```

**No breaking changes:** Existing workflows unaffected when feature flag disabled.

---

## Implementation Timeline

### Day 1: Schema Definition (4-6 hours)

**Deliverables:**
- ✅ Domain configuration module created (`domain_config.py`)
- ✅ 10 entity schemas defined
- ✅ 8 relationship schemas defined
- ✅ Custom extraction prompt written
- ✅ Example configurations created (YAML)

**Outcome:** Domain schema fully defined and documented.

---

### Day 2: Configuration Module & Integration (6-8 hours)

**Deliverables:**
- ✅ GraphitiService updated with domain configuration
- ✅ Extract entities activity updated
- ✅ Environment variable added (`ENABLE_DOMAIN_CONFIGURED_GRAPHITI`)
- ✅ Feature flag tested (on/off)
- ✅ Existing tests still pass (no regression)

**Outcome:** Domain configuration integrated but disabled by default (safe).

---

### Day 3: Validation & Testing (6-8 hours)

**Deliverables:**
- ✅ 10 test documents created
- ✅ 10 expected output files created
- ✅ Validation script created and runs
- ✅ 90%+ average accuracy achieved
- ✅ Neo4j queries validate domain entities exist

**Outcome:** Domain configuration validated, achieving 90%+ extraction accuracy.

---

## Success Metrics

**Minimum Requirements (Blocking Phase 3 Verification):**

1. ✅ **90%+ Extraction Accuracy** (measured across 10 test documents)
2. ✅ **All 10 Entity Types Recognized** (Vehicle, PartsInvoice, Vendor, BankTransaction, Driver, Shipment, Location, Customer, MaintenanceRecord, Route)
3. ✅ **All 8 Relationship Types Created** (BELONGS_TO, SUPPLIED_BY, PAID_BY, ASSIGNED_TO, DELIVERED_TO, BILLED_TO, LOCATED_AT, PERFORMED_ON)
4. ✅ **Feature Flag Works** (on/off toggle with safe defaults)
5. ✅ **Baseline Preserved** (all 162 existing tests still pass)
6. ✅ **Zero Breaking Changes** (generic extraction still works)

**When all criteria met:** Phase 3 verification can be marked **FULLY IMPLEMENTED**.

---

## Directory Structure

```
graphiti-domain-configuration/
├── README.md                      # This file - project overview
├── IMPROVEMENT-PLAN.md            # Problem statement, goals, approach (400+ lines)
├── IMPLEMENTATION.md              # Step-by-step implementation guide (1,800+ lines)
├── TESTING.md                     # Test specifications and validation (800+ lines)
├── TROUBLESHOOTING.md             # Common issues and solutions (500+ lines)
│
├── research/                      # Research documentation
│   ├── GRAPHITI-ENTITY-EXTRACTION.md    # Graphiti entity extraction capabilities
│   ├── DOMAIN-MODELING-BEST-PRACTICES.md # Domain modeling principles
│   └── NEO4J-RELATIONSHIP-PATTERNS.md   # Neo4j relationship best practices
│
├── tests/                         # Test artifacts
│   ├── sample-documents/          # 10 realistic test documents
│   │   ├── invoice-brake-parts.txt
│   │   ├── shipment-delivery-record.txt
│   │   ├── maintenance-oil-change.txt
│   │   └── ... (7 more documents)
│   │
│   ├── expected-outputs/          # Expected extraction results (JSON)
│   │   ├── invoice-brake-parts.json
│   │   ├── shipment-delivery-record.json
│   │   └── ... (8 more files)
│   │
│   ├── validation-queries/        # Neo4j validation queries
│   │   ├── check-entity-types.cypher
│   │   ├── check-relationships.cypher
│   │   └── invoice-to-vehicle-path.cypher
│   │
│   └── validate_extraction.py     # Automated validation script
│
├── examples/                      # Configuration examples
│   ├── entity-types.yaml          # Entity type definitions
│   ├── relationship-types.yaml    # Relationship type definitions
│   └── extraction-prompt.txt      # Custom extraction prompt
│
└── handoffs/                      # Handoff documentation (if multi-day)
    └── HANDOFF-DAY1.md            # Day 1 handoff (if needed)
```

---

## Documentation Suite

### For Implementers

**1. [IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md)** (400+ lines)
- Executive summary and problem statement
- Example: current vs desired extraction
- Goals and success metrics
- Technical approach with schemas
- 3-day implementation timeline
- Deliverables checklist

**2. [IMPLEMENTATION.md](IMPLEMENTATION.md)** (1,800+ lines)
- Step-by-step implementation guide
- **Day 1:** Schema definition (entity types, relationship types, extraction prompt)
- **Day 2:** Integration with GraphitiService and activities
- **Day 3:** Validation and testing
- Code examples and validation steps
- Rollback plan if issues arise

**3. [TESTING.md](TESTING.md)** (800+ lines)
- 10 sample documents with expected outputs
- Automated test specifications
- Manual Neo4j validation queries
- Performance benchmarks
- Success criteria and acceptance tests

**4. [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** (500+ lines)
- Common issues and solutions
- Accuracy problems (entity/relationship extraction)
- Integration issues (feature flag, GraphitiService)
- Performance issues (slow extraction, high memory)
- Neo4j query issues (entities not appearing)
- Debugging tools

### For Reviewers

**1. Review IMPROVEMENT-PLAN.md:**
- Validate problem statement is accurate
- Confirm goals align with Phase 3 requirements
- Check success metrics are measurable

**2. Review TESTING.md:**
- Verify 90%+ accuracy threshold is appropriate
- Check test coverage is comprehensive (10 documents)
- Confirm validation criteria match Phase 3 needs

---

## Key Files

### Production Code (To Be Created)

**`apex-memory-system/src/apex_memory/config/domain_config.py`** (700+ lines)
- Domain configuration module
- Entity schemas (10 types)
- Relationship schemas (8 types)
- Custom extraction prompt
- Validation function

**`apex-memory-system/src/apex_memory/services/graphiti_service.py`** (UPDATED)
- Load domain configuration if enabled
- Pass custom extraction prompt to Graphiti
- Validate extracted entities/relationships
- Feature flag support

**`apex-memory-system/src/apex_memory/temporal/activities/ingestion.py`** (UPDATED)
- Update `extract_entities_activity` to use domain config
- Log domain vs generic extraction
- Include validation results in metrics

**`apex-memory-system/.env`** (UPDATED)
- Add `ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false` (default: off)

### Test Artifacts (To Be Created)

**`tests/sample-documents/*.txt`** (10 files)
- Realistic test documents (invoices, shipments, maintenance, etc.)

**`tests/expected-outputs/*.json`** (10 files)
- Expected extraction results with validation criteria

**`tests/validate_extraction.py`**
- Automated validation script
- Calculates entity/relationship accuracy
- Reports pass/fail for each document

**`tests/validation-queries/*.cypher`** (3 files)
- Neo4j validation queries
- Check entity types exist
- Check relationship types exist
- Verify multi-hop paths

---

## Feature Flag Strategy

### Safe Defaults

**Default:** `ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false`

- Existing workflows unaffected
- Generic extraction (existing behavior)
- Zero risk of breaking changes

**Opt-In:** `ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true`

- Domain-configured extraction (new behavior)
- 90%+ extraction accuracy
- Semantic relationships in Neo4j

### Testing Strategy

**Phase 1: Feature Flag Off (Baseline Preservation)**

```bash
# Disable domain config
export ENABLE_DOMAIN_CONFIGURED_GRAPHITI=false

# Run existing tests
cd apex-memory-system
pytest tests/ --ignore=tests/load/ -v

# Expected: All 162 tests pass (no regression)
```

**Phase 2: Feature Flag On (Domain Configuration Validation)**

```bash
# Enable domain config
export ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true

# Run validation script
cd upgrades/active/graphiti-domain-configuration
python tests/validate_extraction.py

# Expected: 90%+ average accuracy, 9+ tests pass
```

**Phase 3: Deployment**

```bash
# After validation passes, enable in production
echo "ENABLE_DOMAIN_CONFIGURED_GRAPHITI=true" >> apex-memory-system/.env

# Restart services
docker-compose restart
```

---

## Dependencies

### Required Services

- **Neo4j:** Running on `localhost:7687` (for Graphiti)
- **OpenAI API:** Valid API key for GPT-5 (for LLM extraction)

### Python Dependencies

- `graphiti-core` - Temporal knowledge graph (already installed)
- `pydantic` - Data validation (already installed)
- `openai` - OpenAI API client (already installed)

**No new dependencies required.**

---

## Deployment Checklist

**Before Deployment:**

- [ ] All 3 days of implementation complete
- [ ] Domain config module created and tested
- [ ] GraphitiService integration complete
- [ ] Feature flag tested (on/off)
- [ ] 90%+ extraction accuracy achieved
- [ ] Existing 162 tests still pass
- [ ] Neo4j validation queries pass
- [ ] Rollback plan tested

**After Deployment:**

- [ ] Enable domain config in production (`.env` file)
- [ ] Monitor Grafana metrics for entity extraction
- [ ] Query Neo4j to verify domain entities exist
- [ ] Review first 100 documents for extraction quality
- [ ] Document any issues in GitHub

---

## Expected Outcomes

### Immediate (Post-Implementation)

1. **90%+ Extraction Accuracy** (vs. ~60% generic extraction)
2. **Semantic Relationships** (BELONGS_TO, SUPPLIED_BY, etc. vs. generic MENTIONS)
3. **Queryable Knowledge Graph** (Neo4j queries for "all invoices for VEH-1234")
4. **Phase 3 Verification** (Can mark Phase 3 as FULLY IMPLEMENTED)

### Medium-Term (1-2 weeks post-deployment)

1. **Better Search Results** (Query router uses accurate entity types)
2. **Improved Analytics** (Relationships enable complex queries)
3. **User Confidence** (Correct entity extraction → trust in system)

### Long-Term (1+ months post-deployment)

1. **Domain Expansion** (Add more entity types as business grows)
2. **Industry-Specific Insights** (Trucking patterns, vendor analytics)
3. **Competitive Advantage** (Better knowledge graph quality than competitors)

---

## Risks and Mitigations

### Risk 1: Accuracy Below 90%

**Mitigation:**
- Start with 10 well-crafted test documents
- Iterate on extraction prompt if accuracy low
- Add more examples to guide GPT-5
- Document issues in TROUBLESHOOTING.md

### Risk 2: Feature Flag Issues

**Mitigation:**
- Default to `false` (safe)
- Comprehensive feature flag tests
- Clear documentation in IMPLEMENTATION.md

### Risk 3: Breaking Existing Workflows

**Mitigation:**
- All changes behind feature flag
- Existing 162 tests must pass
- Rollback plan documented
- Generic extraction preserved

### Risk 4: Implementation Takes Longer Than 3 Days

**Mitigation:**
- Detailed day-by-day implementation guide
- Clear success criteria for each day
- Handoff documentation if multi-day break needed
- Can deploy partial (Day 1+2 complete, Day 3 validation post-deployment)

---

## Next Steps

### For Implementers

1. **Read IMPROVEMENT-PLAN.md** (5 min) - Understand the why
2. **Follow IMPLEMENTATION.md Day 1** (4-6 hours) - Schema definition
3. **Follow IMPLEMENTATION.md Day 2** (6-8 hours) - Integration
4. **Follow IMPLEMENTATION.md Day 3** (6-8 hours) - Validation
5. **Mark Phase 3 as IMPLEMENTED** - Update verification status

### For Reviewers

1. **Review IMPROVEMENT-PLAN.md** - Validate approach
2. **Review TESTING.md** - Confirm test coverage adequate
3. **Approve for implementation** - If satisfied with plan

---

## Support and Questions

**Documentation:**
- See [IMPROVEMENT-PLAN.md](IMPROVEMENT-PLAN.md) for problem statement and approach
- See [IMPLEMENTATION.md](IMPLEMENTATION.md) for step-by-step guide
- See [TESTING.md](TESTING.md) for validation criteria
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

**Research:**
- See `research/GRAPHITI-ENTITY-EXTRACTION.md` for Graphiti capabilities
- See `research/DOMAIN-MODELING-BEST-PRACTICES.md` for modeling principles
- See `research/NEO4J-RELATIONSHIP-PATTERNS.md` for relationship patterns

**Examples:**
- See `examples/entity-types.yaml` for entity schema examples
- See `examples/relationship-types.yaml` for relationship schema examples
- See `examples/extraction-prompt.txt` for prompt template

---

**Status:** Ready for Implementation
**Timeline:** 2-3 days
**Success Criteria:** 90%+ extraction accuracy + Phase 3 verification IMPLEMENTED
**Blocking:** Phase 3 verification (current: ON HOLD pending domain config)

Let's build this! 🚀
