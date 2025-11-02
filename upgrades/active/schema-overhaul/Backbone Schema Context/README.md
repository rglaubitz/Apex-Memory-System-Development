# BACKBONE SCHEMA CONTEXT

**Status:** 📝 Documentation Complete | 🚀 Ready for Implementation
**Owner:** G (Richard Glaubitz)
**Created:** November 1, 2025
**Purpose:** Foundational schema structure for Apex Memory System multi-database knowledge graph

---

## 🎯 QUICK START

**If you're new here, read in this order:**

1. **[Additional Schema Info.md](Additional%20Schema%20info.md)** ⭐ START HERE
   - Complete overview of the backbone schema
   - 6-hub architecture explanation
   - Database distribution strategy
   - Entity definitions and relationships

2. **[Example Documents.md](Examples/Example%20Documents.md)**
   - Real document examples from the business
   - Shows what Graphiti/Docling will extract
   - Unit #6520 as primary test case
   - 7 different document types with extraction hints

3. **[Example Entity Connections.md](example%20entity%20connections.md)**
   - How entities connect across all 6 hubs
   - Cypher relationship patterns
   - Temporal tracking examples
   - Complete load lifecycle walkthrough

4. **[Example Workflows.md](Examples/Example%20Workflows.md)**
   - Thought process on data flows
   - Document ingestion patterns
   - API integration strategies

5. **[IMPLEMENTATION.md](IMPLEMENTATION.md)** 🚀 NEXT STEP
   - 9-phase implementation plan
   - Detailed technical specifications
   - Timeline and deliverables

---

## 📊 PROJECT OVERVIEW

### What Is This?

The **Backbone Schema** is the core data model for Apex Memory System. It defines:

- **Entity types** (Tractor, FuelTransaction, Driver, etc.)
- **Relationships** between entities (ASSIGNED_TO, CONSUMES, etc.)
- **Database distribution** (which data goes where)
- **Temporal tracking** (how things change over time)
- **Integration patterns** (Samsara API, Graphiti extraction, etc.)

### Why Is This Critical?

Everything in Apex Memory builds on this foundation:
- ✅ Document ingestion knows what to extract
- ✅ Query router knows which database to use
- ✅ Temporal queries can track changes over time
- ✅ Multi-database writes maintain consistency

**Get this right = everything else is easy.**
**Get this wrong = constant rework and bugs.**

---

## 🏗️ ARCHITECTURE OVERVIEW

### The 6-Hub Model

```
                    ┌─────────────┐
                    │  G (Owner)  │
                    │  Command    │
                    │  Center     │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
    │OpenHaul │      │ Origin  │      │Contacts │
    │Brokerage│◄────►│Transport│      │   CRM   │
    └─────────┘      └────┬────┘      └────┬────┘
                          │                 │
                     ┌────▼────┐      ┌────▼────┐
                     │Financial│      │Corporate│
                     │  Flows  │      │  Infra  │
                     └─────────┘      └─────────┘
```

### Database Distribution

| Database | Purpose | Stores |
|----------|---------|--------|
| **Neo4j** | Relationships & Graph Queries | Core nodes, all relationships, graph traversal |
| **PostgreSQL** | Transactional Data | FuelTransactions, MaintenanceRecords, financial data |
| **Qdrant** | Document Search | PDF embeddings, semantic search |
| **Redis** | Real-Time Cache | Current location, status, driver assignments (60s TTL) |
| **Graphiti** | Temporal Intelligence | How things change over time, entity evolution |

---

## 🚀 KEY ENTITIES

### Core Assets (Hub 3: Origin Transport)

**Tractor** - The heart of everything
- **Primary Identifier:** `unit_number` (4 digits, e.g., "6520")
- **Secondary Identifier:** `vin` (17 characters)
- **Properties:** make, model, year, status, current_miles, location_gps, etc.
- **Databases:** Neo4j (node + relationships), PostgreSQL (static data), Redis (real-time), Graphiti (temporal)

**Trailer**
- unit_number, type, reefer_make, status

**Driver**
- driver_id, name, cdl_number, status, current_unit_assignment

### Operational Entities

**FuelTransaction** - Linked via unit_number
- Challenge: Fleetone invoices don't include unit_number directly
- Solution: Match via driver_name → Samsara assignment → GPS correlation

**MaintenanceRecord** - Linked via unit_number or VIN
- service_date, service_type, description, vendor_name, total_cost

**Load**
- load_id, origin, destination, revenue, status

### Financial Entities

**Invoice**
- invoice_number, amount, due_date, status

**Expense**
- amount, category, tax_deductible, related_to (unit_number)

**Loan**
- original_amount, current_balance, lender_name, interest_rate

### Relationship Entities (Hub 4: Contacts)

**Customer**
- name, credit_rating, payment_terms, status

**Vendor**
- name, vendor_type (maintenance, fuel, parts), rating

**Bank**
- name, institution_type, relationship_since

---

## 🔗 KEY RELATIONSHIPS

### Core Relationship Patterns

```cypher
// Ownership
(Origin:Company)-[:OPERATES]->(Tractor)

// Driver Assignment (Temporal - changes over time)
(Driver)-[:ASSIGNED_TO {
  assigned_date: timestamp,
  end_date: timestamp (nullable),
  valid_from: timestamp,
  valid_to: timestamp (nullable)
}]->(Tractor)

// Fuel Consumption
(Tractor)-[:CONSUMES]->(FuelTransaction)
(Driver)-[:PURCHASES]->(FuelTransaction)

// Maintenance
(Tractor)-[:REQUIRES_MAINTENANCE]->(MaintenanceRecord)
(Vendor)-[:PERFORMS]->(MaintenanceRecord)

// Load Hauling
(Tractor)-[:HAULS]->(Load)
(Driver)-[:HAULS]->(Load)

// Financial Flows
(Tractor)-[:GENERATES_REVENUE]->(Revenue)
(Tractor)-[:INCURS]->(Expense)
(Loan)-[:SECURES]->(Tractor)

// Intercompany (OpenHaul ↔ Origin)
(OpenHaul:Company)-[:TRANSACTS_WITH]->(Origin:Company)
```

---

## 📁 DOCUMENTATION STRUCTURE

```
Backbone Schema Context/
├── README.md                          # This file - navigation hub
├── Additional Schema info.md          # Primary schema documentation (547 lines)
├── example entity connections.md     # Relationship examples (805 lines)
├── IMPLEMENTATION.md                  # 9-phase implementation plan
│
├── Examples/
│   ├── Example Documents.md           # Real document samples (440 lines)
│   ├── Example Workflows.md           # Data flow thought process
│   │
│   └── Real Documents/                # Actual PDFs for testing
│       ├── EFS_Statement_2025-10-30.pdf
│       ├── 6520-repair-invoice-2025-10-15.pdf
│       ├── 6520-purchase-agreement.pdf
│       ├── 6520-insurance-policy-2025.pdf
│       ├── kenworth-t680-specs.pdf
│       └── 6520-loan-payoff-2025-09.pdf
│
└── Example Documents/                 # (Legacy - being consolidated)
```

---

## 🎯 IMPLEMENTATION STATUS

### ✅ Phase 0: Documentation (COMPLETE)
- [x] Schema design documented (Additional Schema info.md)
- [x] Entity relationships mapped (example entity connections.md)
- [x] Real document examples collected (Example Documents.md)
- [x] Example workflows documented
- [x] This README created

### 🚀 Phase 1: Schema Definition (NEXT)
- [ ] Create Graphiti entity types (Pydantic models)
- [ ] Create Neo4j schema (Cypher constraints + indexes)
- [ ] Create PostgreSQL schema (SQL tables + foreign keys)
- [ ] Create Qdrant collections
- [ ] Define Redis cache patterns

**See [IMPLEMENTATION.md](IMPLEMENTATION.md) for complete 9-phase plan.**

---

## 🔑 KEY DESIGN DECISIONS

### 1. unit_number as Primary Identifier

**Why:** More human-readable than VIN, easier to reference in conversation.

**Trade-off:** Not all documents include unit_number (especially purchase docs use VIN first).

**Solution:** Support both, with VIN as backup identifier.

### 2. Bi-Temporal Tracking

**Valid Time** (Business Reality):
- `valid_from`: When this became true in real world
- `valid_to`: When this stopped being true (null = current)

**Transaction Time** (System Knowledge):
- `created_at`: When system learned this
- `updated_at`: When last modified

**Why:** Enables "as-of" queries like "Who was driving Unit #6520 on October 15?"

### 3. Polyglot Persistence

**Why not just use one database?**

Each database excels at different tasks:
- Neo4j: Graph traversal ("Show all trucks assigned to Driver X")
- PostgreSQL: Transactions ("Total fuel cost for Unit #6520 YTD")
- Qdrant: Semantic search ("Find maintenance docs mentioning brake repair")
- Redis: Real-time cache (<100ms access to current truck locations)
- Graphiti: Temporal reasoning ("When did Unit #6520 enter maintenance status?")

### 4. Samsara as Source of Truth

For real-time operational data:
- Current location (GPS)
- Current odometer reading
- Current driver assignment
- Current status (active, maintenance)

**Sync frequency:** Every 30-60 seconds → Redis cache (60s TTL)

### 5. Graphiti for Document Extraction

**Why Graphiti?**
- LLM-powered entity extraction (90%+ accuracy with custom types)
- Automatic relationship inference
- Temporal tracking built-in
- No manual parsing rules needed

**Challenge:** Must define custom entity types (Pydantic models) for domain accuracy.

---

## 🧪 TEST CASE: Unit #6520

**Primary Test Vehicle:** G's favorite truck, oldest in fleet

**Test Data Required:**
1. ✅ Samsara API data (current state)
2. ✅ Last 2 Fleetone fuel invoices
3. ✅ Last 5 maintenance receipts
4. ✅ Purchase/loan documents
5. ✅ Insurance policy
6. ✅ Spec sheet

**Success Criteria:**
- Neo4j: Get all relationships for Unit #6520
- PostgreSQL: Total maintenance cost for Unit #6520
- Qdrant: Find maintenance docs for Unit #6520
- Redis: Current location of Unit #6520
- Graphiti: Driver assignment history for Unit #6520

---

## 📚 REFERENCE DOCUMENTS

### Internal (This Folder)

- **[Additional Schema info.md](Additional%20Schema%20info.md)** - Complete schema specification
- **[example entity connections.md](example%20entity%20connections.md)** - Relationship patterns
- **[Examples/Example Documents.md](Examples/Example%20Documents.md)** - Real document samples
- **[Examples/Example Workflows.md](Examples/Example%20Workflows.md)** - Data flow patterns
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Implementation plan

### External (Parent Folders)

- **[../RESEARCH-SUMMARY.md](../RESEARCH-SUMMARY.md)** - Research findings (20+ sources)
- **[../research/graphiti-research.md](../research/graphiti-research.md)** - Graphiti integration guide (4,000+ lines)
- **[../research/neo4j-research.md](../research/neo4j-research.md)** - Neo4j best practices (2,000+ lines)
- **[../research/postgresql-research.md](../research/postgresql-research.md)** - PostgreSQL + pgvector patterns
- **[../research/multi-db-coordination.md](../research/multi-db-coordination.md)** - Multi-DB patterns (3,800+ lines)

---

## 💡 FREQUENTLY ASKED QUESTIONS

### Q: Why so many databases?

**A:** Each database is optimized for different query patterns. Using the right tool for each job gives us:
- 10x better performance
- Simpler code (no complex workarounds)
- Easier scaling
- Better reliability

### Q: How do you keep all databases in sync?

**A:** Saga pattern with compensation logic. If any database write fails, we roll back all previous writes.

### Q: What if a fuel invoice doesn't have a unit number?

**A:** Multi-step matching:
1. Extract driver_name from invoice
2. Query Samsara: "Which unit was this driver assigned to on that date?"
3. Cross-reference transaction location + time with truck GPS data
4. Assign with confidence score (high/medium/low/manual_review)
5. Fallback to VIN if available

### Q: Can I change the schema later?

**A:** Yes, but carefully:
1. Add schema versioning to all entities
2. Create migration scripts (Alembic for PostgreSQL, custom for Neo4j)
3. Support multiple schema versions during transition
4. Never hard-delete old data (soft deletes only)

### Q: Where do I start implementing?

**A:** Read [IMPLEMENTATION.md](IMPLEMENTATION.md) - it has a detailed 9-phase plan with ~12-15 hour timeline.

---

## 🚀 NEXT STEPS

1. ✅ **Read this README** (you're here!)
2. ✅ **Review Additional Schema info.md** - Understand the complete design
3. ✅ **Review example entity connections.md** - See how it all connects
4. 🎯 **Read IMPLEMENTATION.md** - See the detailed plan
5. 🎯 **Start Phase 2** - Create Graphiti entity types (Pydantic models)

---

## 📞 QUESTIONS?

If something is unclear:
1. Check [Additional Schema info.md](Additional%20Schema%20info.md) first
2. Check [example entity connections.md](example%20entity%20connections.md) for relationship patterns
3. Check [Examples/Example Documents.md](Examples/Example%20Documents.md) for real-world examples
4. Ask G (Richard) for clarification

---

**Last Updated:** November 1, 2025
**Schema Version:** 2.0
**Status:** Documentation complete, ready for implementation

**Next Phase:** Create Graphiti entity types (see IMPLEMENTATION.md)
