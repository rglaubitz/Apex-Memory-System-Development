# Graphiti Domain Configuration - Improvement Plan

**Project:** Graphiti Domain Configuration for Trucking/Logistics
**Created:** 2025-10-20
**Timeline:** 2-3 days (PRE-deployment)
**Priority:** IMPORTANT (blocks Phase 3 completion)
**Status:** Active

---

## Executive Summary

### Problem Statement

The Apex Memory System currently uses Graphiti with **generic/default entity extraction**. While the infrastructure is operational, it lacks **domain-specific configuration** to ensure high-quality entity extraction and relationship formation for trucking/logistics operations.

**Current State:**
- ✅ Graphiti integration functional (GPT-5 LLM extraction)
- ✅ Entity extraction working
- ❌ No domain-specific entity types defined
- ❌ No domain-specific relationship types defined
- ❌ Generic extraction prompts (not optimized for trucking/logistics)
- ❌ Risk of missing critical entities (trucks, invoices, vendors)
- ❌ Risk of incorrect relationships (invoice → truck link not formed)

**Example of Current Problem:**

```
Input Document: "Parts invoice INV-001 for Truck #1234 from ACME Parts, paid via check #5678"

Current Output (Generic Graphiti):
Entities:
  - "INV-001" (unknown type)
  - "#1234" (unknown type)
  - "ACME Parts" (unknown type)
  - "5678" (unknown type - just a number)

Relationships:
  - None or random

Problems:
  ❌ Truck #1234 not recognized as Vehicle
  ❌ INV-001 not recognized as Invoice
  ❌ ACME Parts not recognized as Vendor
  ❌ Check #5678 mixed with random numbers
  ❌ No relationship: Invoice → Truck
  ❌ No relationship: Invoice → Vendor
  ❌ No relationship: Invoice → BankTransaction
```

**Desired Output (With Domain Configuration):**

```
Entities:
  - Invoice(INV-001, type=PartsInvoice)
  - Vehicle(Truck #1234, type=Vehicle)
  - Vendor(ACME Parts, type=Vendor)
  - BankTransaction(check #5678, type=BankTransaction)

Relationships:
  - Invoice(INV-001) -[BELONGS_TO]-> Vehicle(Truck #1234)
  - Invoice(INV-001) -[SUPPLIED_BY]-> Vendor(ACME Parts)
  - Invoice(INV-001) -[PAID_BY]-> BankTransaction(check #5678)

Success:
  ✅ All entities correctly typed
  ✅ All critical relationships formed
  ✅ No false positives (random numbers ignored)
```

---

## Goals

### Primary Goal

**Configure Graphiti with trucking/logistics domain knowledge to ensure 90%+ entity extraction accuracy and correct relationship formation from day 1 of deployment.**

### Specific Objectives

1. **Define 8-10 core entity types** for trucking/logistics domain
2. **Define 6-8 core relationship types** covering critical business logic
3. **Write custom extraction prompts** guiding GPT-5 to recognize domain patterns
4. **Validate with 10 sample documents** covering common use cases
5. **Integrate with existing GraphitiService** (zero breaking changes)
6. **Document for future iteration** (enable post-deployment refinement)

### Success Metrics

**Quantitative:**
- ✅ 90%+ entity extraction accuracy (9/10 sample docs)
- ✅ 100% critical relationships formed (invoice → truck → vendor)
- ✅ Zero false positives (no random numbers as entities)
- ✅ All 10 sample documents pass validation

**Qualitative:**
- ✅ Extraction results match business logic expectations
- ✅ Neo4j graph structure enables analytics queries
- ✅ Configuration is maintainable and extensible

---

## Scope

### In Scope

**Day 1: Schema Definition**
- Research Graphiti entity extraction best practices
- Define 8-10 core entity types
- Define 6-8 core relationship types
- Write custom extraction prompts with examples
- Document schema decisions

**Day 2: Implementation**
- Create `graphiti_config.py` configuration module
- Integrate with existing `GraphitiService`
- Create 10 sample test documents
- Write Neo4j validation queries
- Test extraction with sample documents

**Day 3: Validation & Documentation**
- Run validation tests on all 10 samples
- Fix extraction issues
- Document troubleshooting guide
- Update verification workflow
- Mark Phase 3 as IMPLEMENTED (after validation passes)

### Out of Scope

**NOT in this upgrade:**
- ❌ Changing Graphiti itself (using as-is)
- ❌ LLM model changes (staying with GPT-5)
- ❌ Database schema changes (Neo4j structure unchanged)
- ❌ API changes (extraction API unchanged)
- ❌ Re-processing historical data (can be done post-deployment)
- ❌ Advanced features (pattern detection, temporal analysis)

**Can be added later (post-deployment):**
- Additional entity types (as new use cases emerge)
- Relationship refinement (based on real data)
- Custom entity resolution logic
- Performance optimization

---

## Technical Approach

### Architecture Overview

**Integration Point:**

```
Current (Generic):
extract_entities_activity()
    ↓
GraphitiService (generic)
    ↓
Graphiti(llm_model="gpt-5")  # No domain config
    ↓
Generic entity extraction
    ↓
Unknown entity types + random relationships

Proposed (Domain-Configured):
extract_entities_activity()
    ↓
GraphitiService (configured)
    ↓
get_configured_graphiti()  # NEW: Domain configuration
    ├─ Entity types: [Vehicle, Invoice, Vendor, ...]
    ├─ Relationship types: [BELONGS_TO, SUPPLIED_BY, ...]
    └─ Extraction prompt: Trucking/logistics examples
    ↓
Domain-aware entity extraction
    ↓
Typed entities + business-logic relationships
```

**Key Changes:**

1. **New Module:** `apex_memory/config/graphiti_config.py`
2. **Updated Service:** `apex_memory/services/graphiti_service.py` (use configured Graphiti)
3. **Zero Breaking Changes:** Feature flag `ENABLE_DOMAIN_CONFIGURATION=true`

---

### Entity Schema

**8-10 Core Entity Types:**

| Entity Type | Description | Examples | Pattern Recognition |
|-------------|-------------|----------|-------------------|
| **Vehicle** | Trucks, trailers, equipment | "Truck #1234", "T-567", "VEH-001" | Regex: `Truck\s*[#]?\d+`, `Trailer\s*[A-Z]-\d+` |
| **PartsInvoice** | Parts invoices, PO numbers | "INV-2025-001", "PO-456" | Regex: `INV-\d+`, `PO-\d+` |
| **Vendor** | Suppliers, parts vendors | "ACME Parts Supply", "Midwest Truck Parts" | NLP: Company names supplying parts/services |
| **BankTransaction** | Payments, checks, transactions | "Check #5678", "TXN-456789", "ACH-001" | Regex: `Check\s*[#]?\d+`, `TXN-\d+` |
| **Driver** | People assigned to vehicles | "John Smith", "DRV-001" | NLP: Person names + driver IDs |
| **Shipment** | Loads, shipments, deliveries | "SHIP-001", "LOAD-2025-10-20" | Regex: `SHIP-\d+`, `LOAD-\d+` |
| **Location** | Warehouses, delivery addresses | "Chicago Warehouse", "123 Main St" | NLP: Addresses, city names, warehouse names |
| **Customer** | Companies receiving shipments | "Acme Manufacturing Corp" | NLP: Company names (customers) |

**Additional Types (Optional for Day 1):**
- **FuelTransaction** ("Fuel purchase at Station #45")
- **MaintenanceRecord** ("Oil change at 50,000 miles")

---

### Relationship Schema

**6-8 Core Relationship Types:**

| Relationship | Source → Target | Business Logic | Example |
|--------------|----------------|----------------|---------|
| **BELONGS_TO** | Invoice → Vehicle | Links invoice to asset | INV-001 -[BELONGS_TO]-> Truck #1234 |
| **SUPPLIED_BY** | Invoice → Vendor | Links invoice to supplier | INV-001 -[SUPPLIED_BY]-> ACME Parts |
| **PAID_BY** | Invoice → BankTransaction | Links invoice to payment | INV-001 -[PAID_BY]-> Check #5678 |
| **ASSIGNED_TO** | Vehicle → Driver | Links vehicle to driver | Truck #1234 -[ASSIGNED_TO]-> John Smith |
| **DELIVERED_TO** | Shipment → Location | Links shipment to destination | SHIP-001 -[DELIVERED_TO]-> Chicago Warehouse |
| **BILLED_TO** | Invoice → Customer | Links invoice to customer | INV-001 -[BILLED_TO]-> Acme Corp |
| **LOCATED_AT** | Vehicle → Location | Current vehicle location | Truck #1234 -[LOCATED_AT]-> GPS(41.87, -87.62) |

**Additional Relationships (Optional):**
- **TRANSPORTED_BY** (Shipment → Vehicle)
- **ORIGINATED_FROM** (Shipment → Location)

---

### Extraction Prompt Template

**Custom prompt to guide GPT-5:**

```
You are analyzing trucking and logistics documents for entity extraction.

ENTITY TYPES TO EXTRACT:

1. Vehicles: Trucks, trailers, equipment
   - Patterns: "Truck #1234", "Trailer T-567", "VEH-001"
   - Extract the full identifier including prefix

2. Parts Invoices: Invoice numbers, PO numbers
   - Patterns: "INV-2025-001", "PO-456", "Invoice #789"
   - Extract the full invoice ID

3. Vendors: Companies that supply parts or services
   - Examples: "ACME Parts Supply", "Midwest Truck Parts"
   - Extract the full company name

4. Bank Transactions: Payments, checks, ACH transfers
   - Patterns: "Check #5678", "TXN-456789", "ACH-001"
   - Extract the full transaction ID

5. Drivers: People assigned to vehicles
   - Examples: "John Smith", "DRV-001"
   - Extract person names and driver IDs

6. Shipments: Loads, deliveries
   - Patterns: "SHIP-001", "LOAD-2025-10-20"
   - Extract the full shipment ID

7. Locations: Warehouses, delivery addresses, GPS coordinates
   - Examples: "Chicago Warehouse", "123 Main St, Chicago IL", "GPS(41.87, -87.62)"
   - Extract full location descriptions

8. Customers: Companies receiving shipments or services
   - Examples: "Acme Manufacturing Corp", "Global Logistics Inc"
   - Extract full company names (customers)

RELATIONSHIPS TO CREATE:

1. BELONGS_TO: Link invoices to the vehicles they're for
   - Example: "Invoice INV-001 for Truck #1234" → INV-001 -[BELONGS_TO]-> Truck #1234

2. SUPPLIED_BY: Link invoices to vendors
   - Example: "Parts from ACME Parts" → Invoice -[SUPPLIED_BY]-> ACME Parts

3. PAID_BY: Link invoices to bank transactions
   - Example: "Paid via Check #5678" → Invoice -[PAID_BY]-> Check #5678

4. ASSIGNED_TO: Link vehicles to drivers
   - Example: "Truck #1234 driven by John Smith" → Truck #1234 -[ASSIGNED_TO]-> John Smith

5. DELIVERED_TO: Link shipments to destination locations
   - Example: "Shipment to Chicago Warehouse" → Shipment -[DELIVERED_TO]-> Chicago Warehouse

6. BILLED_TO: Link invoices to customers
   - Example: "Invoice for Acme Corp" → Invoice -[BILLED_TO]-> Acme Corp

7. LOCATED_AT: Link vehicles to current locations
   - Example: "Truck at GPS coordinates" → Vehicle -[LOCATED_AT]-> Location

EXTRACTION EXAMPLES:

Example 1:
Input: "Parts invoice INV-001 for Truck #1234 from ACME Parts, paid via check #5678"

Entities:
  - Invoice(INV-001, type=PartsInvoice)
  - Vehicle(Truck #1234, type=Vehicle)
  - Vendor(ACME Parts, type=Vendor)
  - BankTransaction(check #5678, type=BankTransaction)

Relationships:
  - Invoice(INV-001) -[BELONGS_TO]-> Vehicle(Truck #1234)
  - Invoice(INV-001) -[SUPPLIED_BY]-> Vendor(ACME Parts)
  - Invoice(INV-001) -[PAID_BY]-> BankTransaction(check #5678)

Example 2:
Input: "Shipment SHIP-001 for Acme Manufacturing Corp to Chicago Warehouse, transported by Truck #1234 driven by John Smith"

Entities:
  - Shipment(SHIP-001, type=Shipment)
  - Customer(Acme Manufacturing Corp, type=Customer)
  - Location(Chicago Warehouse, type=Location)
  - Vehicle(Truck #1234, type=Vehicle)
  - Driver(John Smith, type=Driver)

Relationships:
  - Shipment(SHIP-001) -[BILLED_TO]-> Customer(Acme Manufacturing Corp)
  - Shipment(SHIP-001) -[DELIVERED_TO]-> Location(Chicago Warehouse)
  - Vehicle(Truck #1234) -[ASSIGNED_TO]-> Driver(John Smith)

Example 3:
Input: "Fuel purchase TXN-789 for Truck #1234 at Station #45, Chicago IL"

Entities:
  - BankTransaction(TXN-789, type=BankTransaction)
  - Vehicle(Truck #1234, type=Vehicle)
  - Location(Station #45, Chicago IL, type=Location)

Relationships:
  - BankTransaction(TXN-789) -[BELONGS_TO]-> Vehicle(Truck #1234)
  - Vehicle(Truck #1234) -[LOCATED_AT]-> Location(Station #45, Chicago IL)

IMPORTANT RULES:

1. Extract ALL entities of the defined types, even if mentioned briefly
2. Create relationships ONLY when explicitly stated or strongly implied
3. Use the full identifier for entities (e.g., "Truck #1234" not just "1234")
4. Distinguish between vendors (suppliers) and customers (receivers)
5. Link invoices to vehicles, vendors, and payments whenever possible
6. Preserve location details (addresses, GPS coordinates, city names)
7. Ignore generic numbers that aren't transaction/vehicle/invoice IDs
8. When in doubt about entity type, default to the most specific type that fits

Now extract entities and relationships from the following document:
```

---

## Implementation Timeline

### Day 1: Schema Definition (6-8 hours)

**Morning (3-4 hours):**
- [ ] Research Graphiti entity extraction best practices
  - Read Graphiti documentation on custom entity types
  - Review examples of domain-specific configurations
  - Study LLM prompt engineering for entity extraction
  - Document findings in `research/GRAPHITI-ENTITY-EXTRACTION.md`

- [ ] Define entity types
  - List 8-10 core entity types for trucking/logistics
  - Define regex patterns for structured IDs (INV-\d+, SHIP-\d+)
  - Define NLP patterns for unstructured names (company names, person names)
  - Document in `examples/entity-types.yaml`

**Afternoon (3-4 hours):**
- [ ] Define relationship types
  - List 6-8 core relationship types
  - Map business logic to graph relationships
  - Define relationship constraints (source → target types)
  - Document in `examples/relationship-types.yaml`

- [ ] Write extraction prompt
  - Draft custom prompt with entity type definitions
  - Add 3-5 extraction examples
  - Add important rules and edge cases
  - Document in `examples/extraction-prompts.txt`

- [ ] Documentation
  - Write IMPLEMENTATION.md (step-by-step guide)
  - Write TESTING.md (validation test specs)
  - Commit Day 1 deliverables

---

### Day 2: Implementation & Integration (6-8 hours)

**Morning (3-4 hours):**
- [ ] Create configuration module
  - Create `apex_memory/config/graphiti_config.py`
  - Implement `get_configured_graphiti()` function
  - Add entity types configuration
  - Add relationship types configuration
  - Add custom extraction prompt
  - Add feature flag support

- [ ] Update GraphitiService
  - Modify `apex_memory/services/graphiti_service.py`
  - Replace generic Graphiti with configured version
  - Add backward compatibility (feature flag)
  - Test service initialization

**Afternoon (3-4 hours):**
- [ ] Create test documents
  - Create 10 sample documents:
    1. Parts invoice (simple)
    2. Parts invoice (complex - multiple trucks)
    3. Shipment document
    4. GPS event (Samsara)
    5. FrontApp message (shipment delay)
    6. Fuel transaction
    7. Maintenance record
    8. Multi-entity document (invoice + shipment + GPS)
    9. Edge case (missing information)
    10. Real-world example (complex)
  - Save in `tests/sample-documents/`

- [ ] Write validation queries
  - Create Neo4j Cypher queries to validate extraction
  - Document expected outputs for each sample
  - Save in `tests/validation-queries/` and `tests/expected-outputs/`

---

### Day 3: Validation & Documentation (6-8 hours)

**Morning (3-4 hours):**
- [ ] Run validation tests
  - Test each of 10 sample documents
  - Execute Neo4j validation queries
  - Compare actual vs expected outputs
  - Document pass/fail for each test

- [ ] Fix extraction issues
  - Identify failed extractions
  - Refine entity types (add patterns)
  - Refine relationship rules
  - Adjust extraction prompt
  - Re-test until 9/10 pass (90% target)

**Afternoon (3-4 hours):**
- [ ] Documentation
  - Write TROUBLESHOOTING.md (common issues + fixes)
  - Write RESEARCH-REFERENCES.md (Graphiti docs, papers)
  - Update Phase 3 verification
  - Create handoff document (if needed)

- [ ] Final validation
  - Run all 10 tests one final time
  - Verify 90%+ pass rate
  - Verify all critical relationships formed
  - Document final results

- [ ] Mark Phase 3 IMPLEMENTED
  - Update `deployment/verification/phase-3-structured-data-ingestion.md`
  - Move to `verified/implemented/`
  - Git commit all documentation

---

## Deliverables Checklist

### Documentation

- [ ] `IMPROVEMENT-PLAN.md` (this document)
- [ ] `IMPLEMENTATION.md` (step-by-step Tier 1 guide)
- [ ] `TESTING.md` (10 test specifications)
- [ ] `TROUBLESHOOTING.md` (common issues + solutions)
- [ ] `RESEARCH-REFERENCES.md` (Graphiti docs, entity extraction papers)

### Research Documentation

- [ ] `research/GRAPHITI-ENTITY-EXTRACTION.md` (Graphiti best practices)
- [ ] `research/DOMAIN-MODELING-BEST-PRACTICES.md` (Entity/relationship modeling)
- [ ] `research/NEO4J-RELATIONSHIP-PATTERNS.md` (Neo4j graph patterns)

### Configuration Files

- [ ] `examples/entity-types.yaml` (8-10 entity type definitions)
- [ ] `examples/relationship-types.yaml` (6-8 relationship definitions)
- [ ] `examples/extraction-prompts.txt` (Custom prompt with examples)

### Production Code

- [ ] `apex_memory/config/graphiti_config.py` (Configuration module)
- [ ] Update `apex_memory/services/graphiti_service.py` (Use configured Graphiti)
- [ ] Feature flag: `ENABLE_DOMAIN_CONFIGURATION` in settings

### Test Artifacts

- [ ] 10 sample documents in `tests/sample-documents/`
- [ ] Neo4j validation queries in `tests/validation-queries/`
- [ ] Expected outputs in `tests/expected-outputs/`
- [ ] Validation results documentation

### Verification

- [ ] All 10 tests pass (90%+ accuracy)
- [ ] All critical relationships formed
- [ ] No false positives
- [ ] Phase 3 marked IMPLEMENTED

---

## Risk Assessment

### High Risk

**Risk:** Extraction prompt doesn't generalize well to real documents
- **Mitigation:** Use 10 diverse sample documents, iterate on prompt
- **Fallback:** Start with minimal prompt, refine post-deployment

**Risk:** Entity types too rigid, miss edge cases
- **Mitigation:** Make entity types flexible (regex + NLP), support synonyms
- **Fallback:** Add catch-all "GenericEntity" type for unmatched entities

### Medium Risk

**Risk:** Integration breaks existing entity extraction
- **Mitigation:** Feature flag, backward compatibility, preserve existing tests
- **Fallback:** Can disable domain configuration if issues arise

**Risk:** 3 days not enough time for validation
- **Mitigation:** Focus on 8 core entities + 6 core relationships (minimal viable)
- **Fallback:** Ship with partial configuration, iterate post-deployment

### Low Risk

**Risk:** Neo4j performance degrades with typed entities
- **Mitigation:** Graphiti handles performance, no schema changes needed
- **Fallback:** Monitor query performance, add indexes if needed

---

## Success Criteria

### Phase 3 Verification (Final Goal)

**Phase 3 will be marked IMPLEMENTED when:**

1. ✅ Domain configuration complete (Day 1-2)
2. ✅ 90%+ extraction accuracy (9/10 sample docs pass)
3. ✅ All critical relationships formed
4. ✅ No false positives (random numbers ignored)
5. ✅ Documentation complete (IMPLEMENTATION.md, TESTING.md, etc.)
6. ✅ Integration tested (GraphitiService uses configured Graphiti)
7. ✅ Validation queries pass

**Then:**
- Move `phase-3-structured-data-ingestion.md` to `verified/implemented/`
- Phase 3 complete, ready for deployment

---

## Post-Deployment Iteration

**Week 1-2 Post-Deployment:**
- Monitor extraction quality in production
- Collect failed/incorrect extractions
- Identify missing entity types
- Identify missing relationships

**Week 3-4 Post-Deployment:**
- Refine extraction prompt based on real data
- Add new entity types (as needed)
- Add new relationship rules (as needed)
- Re-process historical data (optional)

**Continuous Improvement:**
- Monthly extraction quality reviews
- Quarterly prompt refinement
- Add new entity types as business evolves

---

## Appendix: Example Validation Test

**Sample Document 1: Parts Invoice**

```
ACME PARTS SUPPLY
Invoice: INV-2025-10-20-001
Date: October 20, 2025

Bill To: Apex Logistics LLC
Vehicle: Truck #1234

Items:
- Oil filter (Qty: 2) - $45.00
- Brake pads (Qty: 4) - $120.00
- Labor - $85.00

Total: $250.00
Paid via: Check #5678 on 10/20/2025
```

**Expected Extraction:**

```yaml
entities:
  - type: PartsInvoice
    name: INV-2025-10-20-001
    properties:
      date: "2025-10-20"
      total: 250.00

  - type: Vehicle
    name: Truck #1234

  - type: Vendor
    name: ACME Parts Supply

  - type: BankTransaction
    name: Check #5678
    properties:
      date: "2025-10-20"
      amount: 250.00

  - type: Customer
    name: Apex Logistics LLC

relationships:
  - source: INV-2025-10-20-001
    type: BELONGS_TO
    target: Truck #1234

  - source: INV-2025-10-20-001
    type: SUPPLIED_BY
    target: ACME Parts Supply

  - source: INV-2025-10-20-001
    type: PAID_BY
    target: Check #5678

  - source: INV-2025-10-20-001
    type: BILLED_TO
    target: Apex Logistics LLC
```

**Neo4j Validation Query:**

```cypher
// Verify invoice entity exists
MATCH (i:PartsInvoice {name: "INV-2025-10-20-001"})
RETURN i

// Verify all relationships
MATCH (i:PartsInvoice {name: "INV-2025-10-20-001"})-[r]->(n)
RETURN type(r), labels(n), n.name

// Expected relationships:
// BELONGS_TO, Vehicle, Truck #1234
// SUPPLIED_BY, Vendor, ACME Parts Supply
// PAID_BY, BankTransaction, Check #5678
// BILLED_TO, Customer, Apex Logistics LLC
```

**Pass Criteria:**
- ✅ All 5 entities extracted
- ✅ All 4 relationships created
- ✅ Entity types correct
- ✅ Relationship types correct

---

**Document Version:** 1.0
**Last Updated:** 2025-10-20
**Next Review:** After Day 3 validation
