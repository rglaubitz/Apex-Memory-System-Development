# 6-HUB SCHEMA CROSS-REFERENCE

**Date:** November 4, 2025
**Purpose:** Master reference document for complete 6-hub schema
**Status:** ✅ Complete - All 6 hubs, 39 entities, 800+ properties
**Version:** v2.0 (Production-Ready)

---

## Document Purpose

This is the **definitive reference** for the complete 6-hub schema. Use this document to:
- Look up any entity across all hubs
- Find properties and data types
- Identify cross-hub relationships
- Determine database distribution
- Navigate between related entities

**For implementation details, see:**
- Hub-specific documents: `HUB-X-*-COMPLETE.md`
- Implementation schemas: `6-HUB-IMPLEMENTATION-SCHEMAS.md`
- Validation queries: `6-HUB-SCHEMA-VALIDATION-QUERIES.md`

---

## Table of Contents

1. [Entity Master Index](#entity-master-index) - All 39 entities
2. [Property Index](#property-index) - Common properties across hubs
3. [Relationship Catalog](#relationship-catalog) - All cross-hub relationships
4. [Database Distribution Matrix](#database-distribution-matrix) - 5 databases
5. [Primary Key Index](#primary-key-index) - All entity keys
6. [Cross-Hub Navigation](#cross-hub-navigation) - How entities connect
7. [Temporal Tracking Index](#temporal-tracking-index) - Bi-temporal entities
8. [Quick Lookup Tables](#quick-lookup-tables) - Developer reference

---

## Entity Master Index

**Total: 39 entities across 6 hubs**

### Hub 1: G (Command Center) - 8 entities

| # | Entity | Properties | Primary Key | Description |
|---|--------|------------|-------------|-------------|
| 1 | G (Person) | 30 | user_id (string) | Central command entity - G's profile |
| 2 | Project | 28 | project_id (UUID) | Active initiatives (business + personal) |
| 3 | Goal | 26 | goal_id (UUID) | Objectives with measurable criteria |
| 4 | Task | 22 | task_id (UUID) | Action items linked to projects/goals |
| 5 | KnowledgeItem | 25 | knowledge_id (UUID) | Research, protocols, how-tos |
| 6 | Insight | 28 | insight_id (UUID) | Observations and AI-generated patterns |
| 7 | Asset | 22 | asset_id (UUID) | Credentials, logins (encrypted) |
| 8 | Communication | 24 | communication_id (UUID) | Important messages and conversations |

**Hub 1 Total:** 8 entities, 195 properties

---

### Hub 2: OpenHaul (Brokerage) - 8 entities

| # | Entity | Properties | Primary Key | Description |
|---|--------|------------|-------------|-------------|
| 9 | Load | 42 | load_number (string) | Freight movement - central operational entity |
| 10 | Carrier | 38 | carrier_id (string) | Trucking companies (Origin = internal carrier) |
| 11 | Location | 28 | location_id (UUID) | Pickup and delivery facilities |
| 12 | SalesOrder | 15 | sales_order_id (UUID) | Customer purchase order documents |
| 13 | RateConfirmation | 18 | rate_con_id (UUID) | Carrier booking agreements |
| 14 | BOL | 22 | bol_id (UUID) | Bill of Lading (proof of pickup) |
| 15 | POD | 20 | pod_id (UUID) | Proof of Delivery |
| 16 | Factor | 18 | factor_id (UUID) | Quick-pay factoring companies |

**Hub 2 Total:** 8 entities, 201 properties

---

### Hub 3: Origin Transport (Trucking) - 7 entities

| # | Entity | Properties | Primary Key | Description |
|---|--------|------------|-------------|-------------|
| 17 | Tractor | 35 | unit_number (string) | Trucks (18 units: #6501-6533) |
| 18 | Trailer | 25 | unit_number (string) | Trailers (dry van, reefer) |
| 19 | Driver | 28 | driver_id (string) | CDL drivers |
| 20 | FuelTransaction | 22 | fuel_transaction_id (UUID) | Individual fuel purchases |
| 21 | MaintenanceRecord | 25 | maintenance_id (UUID) | Service/repair events |
| 22 | Insurance | 20 | insurance_id (UUID) | Coverage policies (sub-entity of Tractor) |
| 23 | Load (Origin) | 35 | load_id (string) | Origin direct customer loads |

**Hub 3 Total:** 7 entities, 190 properties

---

### Hub 4: Contacts (CRM) - 7 entities

| # | Entity | Properties | Primary Key | Description |
|---|--------|------------|-------------|-------------|
| 24 | Person | 32 | person_id (UUID) | Individuals (customers, drivers, partners) |
| 25 | Company | 38 | company_id (UUID/string) | Organizations (multi-category support) |
| 26 | Contact | 18 | contact_id (UUID) | Person-Company junction with role |
| 27 | Address | 15 | address_id (UUID) | Physical addresses (shared) |
| 28 | CommunicationLog | 22 | log_id (UUID) | Emails, calls, meetings |
| 29 | Note | 12 | note_id (UUID) | Free-form notes attached to entities |
| 30 | Tag | 10 | tag_id (UUID) | Reusable tags across entities |

**Hub 4 Total:** 7 entities, 147 properties

---

### Hub 5: Financials - 8 entities

| # | Entity | Properties | Primary Key | Description |
|---|--------|------------|-------------|-------------|
| 31 | Expense | 28 | expense_id (UUID) | Money out (fuel, maintenance, carrier payments) |
| 32 | Revenue | 25 | revenue_id (UUID) | Money in (customer payments, load revenue) |
| 33 | Invoice | 24 | invoice_id (UUID) | Invoices (customer and vendor) |
| 34 | Payment | 22 | payment_id (UUID) | Payments (sent and received) |
| 35 | Loan | 26 | loan_id (UUID) | Loans (equipment, line of credit) |
| 36 | BankAccount | 18 | bank_account_id (UUID) | Bank accounts owned by entities |
| 37 | IntercompanyTransfer | 20 | transfer_id (UUID) | Capital movements between entities |
| 38 | PaymentTerm | 12 | term_id (UUID) | Reusable payment terms (Net 30, etc.) |

**Hub 5 Total:** 8 entities, 175 properties

---

### Hub 6: Corporate (Legal Infrastructure) - 7 entities

| # | Entity | Properties | Primary Key | Description |
|---|--------|------------|-------------|-------------|
| 39 | LegalEntity | 35 | entity_id (string) | Legal entities (G, Primetime, Origin, OpenHaul) |
| 40 | Ownership | 18 | ownership_id (UUID) | Ownership stakes and equity |
| 41 | License | 28 | license_id (UUID) | DOT, MC, state licenses (16 types) |
| 42 | Filing | 25 | filing_id (UUID) | Annual reports, tax returns (14 types) |
| 43 | BrandAsset | 30 | asset_id (UUID) | Logos, domains, trademarks (20 types) |
| 44 | CompanyDocument | 22 | document_id (UUID) | Operating agreements, bylaws (16 types) |
| 45 | Award | 20 | award_id (UUID) | Industry awards, certifications |

**Hub 6 Total:** 7 entities, 178 properties

---

## Entity Count Summary

| Hub | Entities | Properties | Avg Properties/Entity |
|-----|----------|------------|----------------------|
| Hub 1: G | 8 | 195 | 24.4 |
| Hub 2: OpenHaul | 8 | 201 | 25.1 |
| Hub 3: Origin | 7 | 190 | 27.1 |
| Hub 4: Contacts | 7 | 147 | 21.0 |
| Hub 5: Financials | 8 | 175 | 21.9 |
| Hub 6: Corporate | 7 | 178 | 25.4 |
| **TOTAL** | **45 entities** | **1,086 properties** | **24.1** |

**Note:** Entity count includes sub-types (e.g., Hub 3 has both OpenHaul loads and Origin loads). Unique entity types = 39.

---

## Property Index

### Common Properties Across All Hubs

**Temporal Properties (39/45 entities = 87%):**

| Property | Data Type | Purpose | Entities |
|----------|-----------|---------|----------|
| `created_at` | timestamp | When record created | All 45 entities |
| `updated_at` | timestamp | When last modified | All 45 entities |
| `valid_from` | timestamp | Business validity start | 32 entities (not financial transactions) |
| `valid_to` | timestamp (nullable) | Business validity end | 32 entities (NULL = current) |

---

**Identifier Properties:**

| Property Pattern | Data Type | Count | Examples |
|-----------------|-----------|-------|----------|
| `{entity}_id` | UUID | 37 entities | project_id, expense_id, person_id |
| `{entity}_number` | string | 4 entities | load_number, unit_number |
| `user_id` | string | 1 entity | "g_main" (unique) |
| `entity_id` | string | 1 entity | "entity_origin" (LegalEntity) |

---

**Status Properties (30 entities):**

| Property | Data Type | Entities Using | Common Values |
|----------|-----------|----------------|---------------|
| `status` | enum | 28 entities | active, completed, cancelled, etc. |
| `active_status` | boolean | 2 entities | Hub 4 Person/Company |

---

**Contact Properties (18 entities):**

| Property | Data Type | Entities | Purpose |
|----------|-----------|----------|---------|
| `email` | string | 9 entities | Email address |
| `phone` | string | 9 entities | Phone number |
| `address` | string | 12 entities | Street address |
| `city` | string | 12 entities | City |
| `state` | string | 12 entities | State |
| `zip` | string | 12 entities | ZIP code |
| `country` | string | 8 entities | Country (defaults "USA") |

---

**Financial Properties (23 entities):**

| Property | Data Type | Entities | Purpose |
|----------|-----------|----------|---------|
| `amount` | decimal | 8 entities | Transaction amounts (Hub 5) |
| `total_cost` | decimal | 5 entities | Total costs (Hub 3 maintenance, fuel) |
| `customer_rate` | decimal | 2 entities | Hub 2 Load pricing |
| `carrier_rate` | decimal | 2 entities | Hub 2 Load carrier payment |
| `price_per_gallon` | decimal | 1 entity | Hub 3 FuelTransaction |

---

**Date Properties:**

| Property Pattern | Data Type | Count | Purpose |
|-----------------|-----------|-------|---------|
| `{action}_date` | date | 45+ occurrences | Business event dates |
| `{action}_time` | time | 8 occurrences | Specific times for events |
| `expiration_date` | date | 12 entities | When something expires |

---

**Relationship Properties:**

| Property Pattern | Purpose | Count | Examples |
|-----------------|---------|-------|----------|
| `{entity}_id` | Foreign key reference | 100+ | customer_id, carrier_id, driver_id |
| `owner_id` | Ownership reference | 15 entities | Always "g_main" or entity_id |
| `related_to` | General relationships | 8 entities | Arrays of related entity IDs |

---

## Relationship Catalog

### Hub 1 (G) Relationships - Strategic Direction

**Ownership:**
```cypher
(G:Person {user_id: "g_main"})-[:OWNS {percentage: 100}]->(Primetime:LegalEntity)
(G:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)
(Primetime:LegalEntity)-[:OWNS {percentage: 100}]->(Origin:LegalEntity)
```

**Strategic Creation:**
```cypher
(G:Person)-[:CREATED]->(Project)
(G:Person)-[:OWNS]->(Project)
(G:Person)-[:SET_GOAL]->(Goal)
(G:Person)-[:TRACKS]->(Goal)
(Project)-[:HAS_TASK]->(Task)
(Goal)-[:HAS_TASK]->(Task)
```

**Knowledge Management:**
```cypher
(G:Person)-[:RESEARCHED]->(KnowledgeItem)
(KnowledgeItem)-[:SUPPORTS]->(Project)
(KnowledgeItem)-[:INFORMS]->(Goal)
(KnowledgeItem)-[:RELATED_TO]->(KnowledgeItem)
```

**Intelligence Aggregation:**
```cypher
(Insight)-[:ABOUT]->(Tractor)      // Hub 3
(Insight)-[:ABOUT]->(Load)         // Hub 2
(Insight)-[:ABOUT]->(Customer)     // Hub 4
(Insight)-[:ABOUT]->(Expense)      // Hub 5
(Insight)-[:INFORMS]->(Project)
(Insight)-[:IMPACTS]->(Goal)
```

**Measurement:**
```cypher
(Goal)-[:MEASURED_BY]->(Revenue)   // Hub 5
(Goal)-[:MEASURED_BY]->(Expense)   // Hub 5
(Goal)-[:MEASURED_BY]->(Tractor)   // Hub 3 (utilization)
(Project)-[:DRIVES]->(Load)        // Hub 2
(Project)-[:TARGETS]->(Tractor)    // Hub 3
```

---

### Hub 2 (OpenHaul) Relationships - Operational Flow

**Load Lifecycle:**
```cypher
(Load)-[:CUSTOMER]->(Customer:Company)           // Hub 4
(Load)-[:HAULED_BY]->(Carrier)                   // Hub 2/3 (could be Origin)
(Load)-[:SHIPPER]->(Shipper:Company)             // Hub 4
(Load)-[:CONSIGNEE]->(Consignee:Company)         // Hub 4
(Load)-[:PICKUP_LOCATION]->(Location)
(Load)-[:DELIVERY_LOCATION]->(Location)
```

**When Origin Hauls:**
```cypher
(Load {carrier_id: "carr_origin"})-[:HAULED_BY]->(Carrier {carrier_id: "carr_origin"})
(Load)-[:ASSIGNED_UNIT {unit_number: "6520"}]->(Tractor {unit_number: "6520"})  // Hub 3
(Carrier {carrier_id: "carr_origin"})-[:COMPANY_RECORD]->(Company {company_id: "company_origin"})  // Hub 4
```

**Documents:**
```cypher
(Load)-[:HAS_SALES_ORDER]->(SalesOrder)
(Load)-[:HAS_RATE_CON]->(RateConfirmation)
(Load)-[:HAS_BOL]->(BOL)
(Load)-[:HAS_POD]->(POD)
```

**Financial Flow:**
```cypher
(Load)-[:GENERATES]->(Revenue)     // Hub 5 (customer payment)
(Load)-[:INCURS]->(Expense)        // Hub 5 (carrier payment)
```

---

### Hub 3 (Origin) Relationships - Fleet Operations

**Ownership:**
```cypher
(Origin:LegalEntity)-[:OWNS]->(Tractor)          // Hub 6 → Hub 3
(Origin:LegalEntity)-[:OWNS]->(Trailer)
```

**Driver Assignment (Bi-Temporal):**
```cypher
(Driver)-[:ASSIGNED_TO {
    assigned_date: date,
    end_date: date (nullable),
    valid_from: timestamp,
    valid_to: timestamp (nullable)
}]->(Tractor)
```

**Fuel & Maintenance:**
```cypher
(Tractor)-[:CONSUMES]->(FuelTransaction)
(Driver)-[:PURCHASES]->(FuelTransaction)
(Tractor)-[:REQUIRES_MAINTENANCE]->(MaintenanceRecord)
(MaintenanceRecord)-[:PERFORMED_BY]->(Vendor:Company)  // Hub 4
```

**Insurance:**
```cypher
(Tractor)-[:HAS_INSURANCE]->(Insurance)
(Insurance)-[:PROVIDED_BY]->(InsuranceCompany:Company)  // Hub 4
```

**Load Hauling:**
```cypher
(Tractor)-[:HAULS]->(Load)         // Hub 2 (OpenHaul) or Hub 3 (Origin direct)
(Driver)-[:HAULS]->(Load)
```

**Financial:**
```cypher
(Tractor)-[:GENERATES_REVENUE]->(Revenue)  // Hub 5
(Tractor)-[:INCURS]->(Expense)             // Hub 5 (maintenance, fuel)
(Loan)-[:SECURES]->(Tractor)               // Hub 5
```

---

### Hub 4 (Contacts) Relationships - CRM Network

**Person-Company Junction:**
```cypher
(Person)-[:WORKS_FOR {role: "driver"}]->(Company)
(Person)-[:CONTACT_AT {role: "operations_manager"}]->(Company)
(Person)-[:OWNS]->(Company)
```

**Cross-Hub Person Links:**
```cypher
(Person)-[:DRIVER_RECORD]->(Driver)                  // Hub 3
(Person {person_id: "person_g"})-[:USER_RECORD]->(G {user_id: "g_main"})  // Hub 1
```

**Cross-Hub Company Links:**
```cypher
(Company {company_id: "company_origin"})-[:LEGAL_ENTITY]->(LegalEntity {entity_id: "entity_origin"})  // Hub 6
(Company)-[:CARRIER_RECORD]->(Carrier)               // Hub 2
(Company)-[:CUSTOMER_OF]->(Load)                     // Hub 2
```

**Address:**
```cypher
(Person)-[:HAS_ADDRESS]->(Address)
(Company)-[:HAS_ADDRESS]->(Address)
(Location)-[:HAS_ADDRESS]->(Address)  // Hub 2
```

**Communication:**
```cypher
(CommunicationLog)-[:WITH]->(Person)
(CommunicationLog)-[:REGARDING]->(Company)
(CommunicationLog)-[:ABOUT]->(Load)  // Hub 2 (discussed loads)
```

**Notes & Tags:**
```cypher
(Note)-[:ATTACHED_TO]->(Person | Company | Load | Tractor)
(Tag)-[:APPLIED_TO]->(Person | Company | Load | Tractor)
```

---

### Hub 5 (Financials) Relationships - Money Flows

**Revenue Sources:**
```cypher
(Revenue)-[:SOURCE]->(Load)              // Hub 2 (load revenue)
(Revenue)-[:RECEIVED_BY]->(LegalEntity)  // Hub 6
(Revenue)-[:RECEIVED_FROM]->(Company)    // Hub 4 (customer)
```

**Expense Targets:**
```cypher
(Expense)-[:SOURCE]->(Load)              // Hub 2 (carrier payment)
(Expense)-[:SOURCE]->(Tractor)           // Hub 3 (fuel, maintenance)
(Expense)-[:PAID_BY]->(LegalEntity)      // Hub 6
(Expense)-[:PAID_TO]->(Company)          // Hub 4 (vendor/carrier)
```

**Invoices:**
```cypher
(Invoice)-[:FOR]->(Load | Tractor | Company)
(Invoice)-[:PAID_BY]->(Payment)
(Payment)-[:FROM_ACCOUNT]->(BankAccount)
(Payment)-[:TO_COMPANY]->(Company)  // Hub 4
```

**Loans:**
```cypher
(Loan)-[:SECURES]->(Tractor)             // Hub 3 (equipment loan)
(Loan)-[:BORROWED_BY]->(LegalEntity)     // Hub 6
(Loan)-[:LENDER]->(Company)              // Hub 4 (bank)
```

**Intercompany:**
```cypher
(IntercompanyTransfer)-[:FROM]->(LegalEntity)  // Hub 6 (e.g., G)
(IntercompanyTransfer)-[:TO]->(LegalEntity)    // Hub 6 (e.g., Origin)
(IntercompanyTransfer)-[:RELATED_TO]->(Loan)   // If loan transfer
```

---

### Hub 6 (Corporate) Relationships - Legal Structure

**Ownership Chains:**
```cypher
(Person {person_id: "person_g"})-[:OWNS {percentage: 100}]->(LegalEntity {entity_id: "entity_primetime"})
(LegalEntity {entity_id: "entity_primetime"})-[:OWNS {percentage: 100}]->(LegalEntity {entity_id: "entity_origin"})
(Person {person_id: "person_g"})-[:OWNS {percentage: 50}]->(LegalEntity {entity_id: "entity_openhaul"})
(Person {person_id: "person_travis"})-[:OWNS {percentage: 50}]->(LegalEntity {entity_id: "entity_openhaul"})
```

**Licenses & Compliance:**
```cypher
(LegalEntity)-[:HOLDS_LICENSE]->(License)
(LegalEntity)-[:REQUIRES_FILING]->(Filing)
(Filing)-[:DUE_TO]->(Government:Authority)
```

**Brand Assets:**
```cypher
(LegalEntity)-[:OWNS_ASSET]->(BrandAsset)
(BrandAsset {asset_type: "domain"})-[:REGISTERED_AT]->(Registrar:Company)  // Hub 4
```

**Documents:**
```cypher
(LegalEntity)-[:HAS_DOCUMENT]->(CompanyDocument)
(LegalEntity)-[:RECEIVED_AWARD]->(Award)
```

**Cross-Hub Links:**
```cypher
(LegalEntity)-[:COMPANY_RECORD]->(Company)        // Hub 4
(LegalEntity)-[:OWNS_FLEET]->(Tractor)            // Hub 3
(LegalEntity)-[:FINANCIAL_ENTITY]->(BankAccount)  // Hub 5
```

---

## Database Distribution Matrix

### PostgreSQL - Factual Memory (PRIMARY for all entities)

**Hub 1:**
- ✅ PRIMARY: All 8 entities (G, Project, Goal, Task, KnowledgeItem, Insight, Asset, Communication)

**Hub 2:**
- ✅ PRIMARY: All 8 entities (Load, Carrier, Location, SalesOrder, RateConfirmation, BOL, POD, Factor)

**Hub 3:**
- ✅ PRIMARY: All 7 entities (Tractor, Trailer, Driver, FuelTransaction, MaintenanceRecord, Insurance, Load)

**Hub 4:**
- ✅ PRIMARY: All 7 entities (Person, Company, Contact, Address, CommunicationLog, Note, Tag)

**Hub 5:**
- ✅ PRIMARY: All 8 entities (Expense, Revenue, Invoice, Payment, Loan, BankAccount, IntercompanyTransfer, PaymentTerm)

**Hub 6:**
- ✅ PRIMARY: All 7 entities (LegalEntity, Ownership, License, Filing, BrandAsset, CompanyDocument, Award)

**PostgreSQL Total:** 45 entities (100% of schema)

---

### Neo4j - Relationship Memory (REPLICA for all entities)

**Purpose:** Graph traversal, relationship queries

**Stores:**
- Basic node properties (id, name, status)
- ALL relationships between entities
- Temporal properties on relationships (valid_from, valid_to)

**Does NOT store:**
- Complete entity details (use PostgreSQL)
- Large text fields (descriptions, notes)
- Binary data (PDFs, images)

**Example Node:**
```cypher
(:Tractor {
    unit_number: "6520",
    make: "Kenworth",
    model: "T680",
    status: "active",
    updated_at: timestamp()
})
// Complete details in PostgreSQL
```

**Neo4j Total:** 45 entities (100% as nodes), 150+ relationship types

---

### Qdrant - Semantic Memory (VECTORS for documents)

**Hub 1:**
- ✅ KnowledgeItem (research, protocols)
- ✅ Insight (semantic search)
- ✅ Communication (transcript embeddings)

**Hub 2:**
- ✅ SalesOrder (PDFs)
- ✅ RateConfirmation (PDFs)
- ✅ BOL (PDFs)
- ✅ POD (PDFs)

**Hub 3:**
- ✅ FuelTransaction (Fleetone invoices)
- ✅ MaintenanceRecord (repair receipts)
- ✅ Insurance (policy documents)

**Hub 4:**
- ✅ CommunicationLog (email content)
- ✅ Note (if long-form)
- ✅ Company (company documents)

**Hub 5:**
- ✅ Invoice (invoice PDFs)
- ✅ Loan (loan documents)

**Hub 6:**
- ✅ Filing (tax returns, annual reports)
- ✅ BrandAsset (if visual files)
- ✅ CompanyDocument (operating agreements, bylaws)

**Qdrant Total:** 17 entity types with document vectors

---

### Redis - Working Memory (CACHE for current state)

**Purpose:** Sub-100ms access to frequently-used current state

**Hub 1:**
- `focus:g_main` → current_focus (60s TTL)
- `projects:active:g_main` → active projects list (300s TTL)
- `insights:recent` → last 24h insights (86400s TTL)

**Hub 2:**
- `load:{load_number}:status` → current status (300s TTL)
- `load:active_list` → all active loads (300s TTL)
- `carrier:available` → available carriers (600s TTL)

**Hub 3:**
- `truck:{unit_number}:location` → GPS (60s TTL, synced from Samsara)
- `truck:{unit_number}:status` → current status (60s TTL)
- `truck:{unit_number}:current_driver` → driver assignment (300s TTL)
- `truck:{unit_number}:current_miles` → odometer (60s TTL)

**Hub 4:**
- `company:active` → active companies (3600s TTL)
- `person:contacts:recent` → recent contacts (3600s TTL)

**Hub 5:**
- `invoice:unpaid` → unpaid invoices list (3600s TTL)
- `account:{account_id}:balance` → current balance (300s TTL)

**Hub 6:**
- `license:expiring:30days` → licenses expiring soon (86400s TTL)
- `filing:due:current_quarter` → upcoming filings (86400s TTL)

**Redis Total:** 20+ key patterns (cache only, not primary storage)

---

### Graphiti - Temporal Memory (TIMELINE for state changes)

**Purpose:** Time-travel queries, pattern detection

**Hub 1:**
- ✅ Goal (status changes, progress over time)
- ✅ Project (lifecycle progression)
- ✅ G (focus shifts, strategic evolution)

**Hub 2:**
- ✅ Load (status lifecycle: booked → dispatched → delivered)
- ✅ Carrier (performance history, rating changes)

**Hub 3:**
- ✅ Tractor (status changes, odometer progression, value depreciation)
- ✅ Driver (assignment history)
- ✅ MaintenanceRecord (service patterns over time)

**Hub 4:**
- ✅ Person (role changes, relationship evolution)
- ✅ Company (categories changes, relationship history)
- ✅ Contact (role changes)

**Hub 5:**
- ✅ Loan (payment history, balance progression)
- ✅ IntercompanyTransfer (capital flow patterns)

**Hub 6:**
- ✅ LegalEntity (status changes)
- ✅ Ownership (ownership transfers over time)
- ✅ License (renewal history)

**Graphiti Total:** 16 entity types with temporal tracking

---

## Primary Key Index

### String Keys (Business-Readable) - 7 entities

| Entity | Primary Key | Pattern | Example | Justification |
|--------|-------------|---------|---------|---------------|
| G (Person) | user_id | "g_main" | "g_main" | Unique identifier for G |
| Load (Hub 2) | load_number | "OH-{6 digits}" | "OH-321678" | Customer-facing, on documents |
| Tractor | unit_number | "{4 digits}" | "6520" | Business-standard identifier |
| Trailer | unit_number | "T-{3 digits}" | "T-001" | Consistent with Tractor |
| Driver | driver_id | "driver_{name}" | "driver_robert" | Synced from Samsara |
| Load (Hub 3) | load_id | "LOAD_{type}_{num}" | "LOAD_ORIGIN_5678" | Distinguishes from Hub 2 |
| LegalEntity | entity_id | "entity_{name}" | "entity_origin" | Small set, human-readable |

**String Key Total:** 7 entities

---

### UUID Keys (System-Generated) - 38 entities

**All other entities use UUID v4 primary keys:**

- Hub 1: Project, Goal, Task, KnowledgeItem, Insight, Asset, Communication (7)
- Hub 2: Carrier, Location, SalesOrder, RateConfirmation, BOL, POD, Factor (7)
- Hub 3: FuelTransaction, MaintenanceRecord, Insurance (3)
- Hub 4: Person, Company (if external), Contact, Address, CommunicationLog, Note, Tag (7)
- Hub 5: All 8 entities (Expense, Revenue, Invoice, Payment, Loan, BankAccount, IntercompanyTransfer, PaymentTerm)
- Hub 6: Ownership, License, Filing, BrandAsset, CompanyDocument, Award (6)

**UUID Key Total:** 38 entities

---

### Hybrid Keys (Context-Dependent) - 2 entities

| Entity | Primary Key | When String | When UUID |
|--------|-------------|-------------|-----------|
| Carrier | carrier_id | Internal carriers ("carr_origin") | External carriers (UUID) |
| Company | company_id | Internal companies ("company_origin") | External companies (UUID) |

---

## Cross-Hub Navigation

### Starting from Hub 1 (G)

**To find G's businesses:**
```cypher
// Hub 1 → Hub 6: Ownership
MATCH (g:Person {user_id: "g_main"})-[:OWNS]->(entity:LegalEntity)
RETURN entity.legal_name, entity.entity_id
```

**To find projects impacting operations:**
```cypher
// Hub 1 → Hub 2: Project drives loads
MATCH (p:Project {project_id: "proj_018c3a8b"})-[:DRIVES]->(l:Load)
RETURN count(l) as loads_driven
```

**To measure goal progress:**
```cypher
// Hub 1 → Hub 5: Goal measured by revenue
MATCH (g:Goal {goal_id: "goal_openhaul_revenue_2025"})-[:MEASURED_BY]->(r:Revenue)
WHERE r.revenue_date >= date("2025-01-01")
RETURN sum(r.amount) as current_revenue, g.target_value
```

---

### Starting from Hub 2 (Load)

**To find who owns the load:**
```cypher
// Hub 2 → Hub 6: Load customer's legal entity
MATCH (l:Load {load_number: "OH-321678"})-[:CUSTOMER]->(c:Company)-[:LEGAL_ENTITY]->(e:LegalEntity)
RETURN e.legal_name
```

**When Origin hauls:**
```cypher
// Hub 2 → Hub 3: Load to assigned truck
MATCH (l:Load {load_number: "OH-321678", carrier_id: "carr_origin"})-[:ASSIGNED_UNIT]->(t:Tractor)
RETURN t.unit_number, t.current_driver_id
```

**To find financial impact:**
```cypher
// Hub 2 → Hub 5: Load to revenue/expense
MATCH (l:Load {load_number: "OH-321678"})
MATCH (l)-[:GENERATES]->(r:Revenue)
MATCH (l)-[:INCURS]->(e:Expense)
RETURN r.amount as revenue, e.amount as cost, (r.amount - e.amount) as margin
```

---

### Starting from Hub 3 (Tractor)

**To find who owns the truck:**
```cypher
// Hub 3 → Hub 6: Tractor to legal entity
MATCH (t:Tractor {unit_number: "6520"})<-[:OWNS]-(e:LegalEntity)
RETURN e.legal_name
```

**To find current driver:**
```cypher
// Hub 3 → Hub 4: Tractor to driver to person
MATCH (t:Tractor {unit_number: "6520"})<-[:ASSIGNED_TO {end_date: null}]-(d:Driver)-[:PERSON_RECORD]->(p:Person)
RETURN p.first_name, p.last_name, d.hire_date
```

**To find maintenance history:**
```cypher
// Hub 3: Tractor to maintenance
MATCH (t:Tractor {unit_number: "6520"})-[:REQUIRES_MAINTENANCE]->(m:MaintenanceRecord)
RETURN m.service_date, m.service_type, m.total_cost
ORDER BY m.service_date DESC
```

**To find financial burden:**
```cypher
// Hub 3 → Hub 5: Tractor to expenses
MATCH (t:Tractor {unit_number: "6520"})-[:INCURS]->(e:Expense)
WHERE e.expense_date >= date("2025-01-01")
RETURN sum(e.amount) as ytd_expenses
```

---

### Starting from Hub 4 (Company)

**To check if company is related party:**
```cypher
// Hub 4 → Hub 6: Company to legal entity
MATCH (c:Company {company_id: "company_origin"})-[:LEGAL_ENTITY]->(e:LegalEntity)
MATCH (e)<-[:OWNS]-(owner)
RETURN owner.name, e.legal_name
```

**To find all loads with this customer:**
```cypher
// Hub 4 → Hub 2: Company to loads
MATCH (c:Company {company_id: "company_sunglo"})<-[:CUSTOMER]-(l:Load)
RETURN count(l) as total_loads, sum(l.customer_rate) as total_revenue
```

**To find all contacts at company:**
```cypher
// Hub 4: Company to people
MATCH (c:Company {company_id: "company_sunglo"})<-[:WORKS_FOR]-(p:Person)
RETURN p.first_name, p.last_name, p.job_title
```

---

### Starting from Hub 5 (Revenue/Expense)

**To trace revenue to source:**
```cypher
// Hub 5 → Hub 2: Revenue to load
MATCH (r:Revenue)-[:SOURCE]->(l:Load)
WHERE r.revenue_id = "rev_001"
RETURN l.load_number, l.customer_id, l.completed_date
```

**To trace expense to source:**
```cypher
// Hub 5 → Hub 3: Expense to tractor
MATCH (e:Expense)-[:SOURCE]->(t:Tractor)
WHERE e.expense_category = "maintenance"
RETURN t.unit_number, e.amount, e.expense_date
```

**To find entity's financial position:**
```cypher
// Hub 5 → Hub 6: Entity financial summary
MATCH (e:LegalEntity {entity_id: "entity_origin"})
MATCH (e)<-[:RECEIVED_BY]-(r:Revenue)
MATCH (e)<-[:PAID_BY]-(exp:Expense)
RETURN sum(r.amount) as total_revenue, sum(exp.amount) as total_expenses
```

---

### Starting from Hub 6 (LegalEntity)

**To find everything owned:**
```cypher
// Hub 6 → Hub 3: Entity to fleet
MATCH (e:LegalEntity {entity_id: "entity_origin"})-[:OWNS]->(t:Tractor)
RETURN count(t) as fleet_size, collect(t.unit_number) as units
```

**To find ownership chain:**
```cypher
// Hub 6: Ownership hierarchy
MATCH path = (top)-[:OWNS*]->(bottom:LegalEntity {entity_id: "entity_origin"})
RETURN [node in nodes(path) | node.legal_name] as ownership_chain
```

**To find compliance status:**
```cypher
// Hub 6: Entity to licenses/filings
MATCH (e:LegalEntity {entity_id: "entity_origin"})-[:HOLDS_LICENSE]->(lic:License)
WHERE lic.expiration_date < date() + duration({days: 30})
RETURN lic.license_type, lic.expiration_date
```

---

## Temporal Tracking Index

### Entities with Bi-Temporal Tracking (32 entities)

**Pattern:** `valid_from` / `valid_to` (business reality) + `created_at` / `updated_at` (system knowledge)

**Hub 1:** All 8 entities track temporal changes
**Hub 2:** Load, Carrier track lifecycle/performance changes
**Hub 3:** Tractor, Trailer, Driver, Load track operational changes
**Hub 4:** Person, Company, Contact track relationship changes
**Hub 5:** Loan, IntercompanyTransfer track repayment/transfer patterns
**Hub 6:** LegalEntity, Ownership, License, Filing track legal changes

---

### Common Temporal Queries

**"Who was driving Unit #6520 on October 15, 2025?"**
```cypher
MATCH (d:Driver)-[a:ASSIGNED_TO]->(t:Tractor {unit_number: "6520"})
WHERE date("2025-10-15") >= date(a.valid_from)
  AND (a.valid_to IS NULL OR date("2025-10-15") <= date(a.valid_to))
RETURN d.name
```

```python
# Graphiti
graphiti.query_at_time(
    entity_type="Tractor",
    entity_id="6520",
    property="current_driver_id",
    timestamp="2025-10-15T12:00:00Z"
)
```

---

**"Show goal progress over last 6 months"**
```python
# Graphiti timeline query
graphiti.query_temporal(
    entity_type="Goal",
    entity_id="goal_openhaul_revenue_2025",
    property="progress_percentage",
    start_date="2025-05-01",
    end_date="2025-11-01"
)
# Returns: [{valid_from, valid_to, progress_percentage}, ...]
```

---

**"When did Origin's ownership change?"**
```cypher
MATCH (o:LegalEntity {entity_id: "entity_origin"})<-[owns:OWNS]-(owner)
RETURN owner.name, owns.acquisition_date, owns.valid_from, owns.valid_to
ORDER BY owns.valid_from
```

---

## Quick Lookup Tables

### Entity → Primary Key Quick Reference

| Entity | Key | Type | Example |
|--------|-----|------|---------|
| G | user_id | string | "g_main" |
| Project | project_id | UUID | "proj_018c3a8b..." |
| Goal | goal_id | UUID | "goal_oh_rev..." |
| Task | task_id | UUID | "task_001..." |
| Load (OH) | load_number | string | "OH-321678" |
| Tractor | unit_number | string | "6520" |
| Driver | driver_id | string | "driver_robert" |
| Person | person_id | UUID | "person_abc..." |
| Company | company_id | UUID/string | "company_origin" or UUID |
| Expense | expense_id | UUID | "exp_001..." |
| LegalEntity | entity_id | string | "entity_origin" |

---

### Hub → Entity Count

| Hub | Entities | String Keys | UUID Keys | Properties |
|-----|----------|-------------|-----------|------------|
| 1 | 8 | 1 | 7 | 195 |
| 2 | 8 | 1 | 7 | 201 |
| 3 | 7 | 4 | 3 | 190 |
| 4 | 7 | 0 | 7 | 147 |
| 5 | 8 | 0 | 8 | 175 |
| 6 | 7 | 1 | 6 | 178 |
| **Total** | **45** | **7** | **38** | **1,086** |

---

### Database → Entity Coverage

| Database | Entities | Purpose | Storage Type |
|----------|----------|---------|--------------|
| PostgreSQL | 45 (100%) | PRIMARY | Complete records |
| Neo4j | 45 (100%) | REPLICA | Nodes + relationships |
| Qdrant | 17 (38%) | VECTORS | Document embeddings |
| Redis | 20 patterns | CACHE | Current state (TTL) |
| Graphiti | 16 (36%) | TIMELINE | State changes over time |

---

## Implementation Checklist

**Before implementing, ensure:**

- [ ] PostgreSQL schema created for all 45 entities
- [ ] Neo4j constraints created for all primary keys
- [ ] Qdrant collections created for 17 document types
- [ ] Redis key patterns documented and TTLs configured
- [ ] Graphiti entity tracking configured for 16 entities
- [ ] Cross-database sync patterns implemented
- [ ] Validation queries passing (see 6-HUB-SCHEMA-VALIDATION-QUERIES.md)
- [ ] Sample data generated and tested
- [ ] Temporal queries validated across Neo4j + Graphiti
- [ ] Multi-category entity logic tested (Hub 4 Company)
- [ ] Intercompany transaction separation validated (Hub 5)
- [ ] Goal measurement calculations tested (Hub 1 → Hub 5)

---

**Cross-Reference Complete:** November 4, 2025
**Schema Version:** v2.0 (Production-Ready)
**Next:** Implementation Schemas (PostgreSQL DDL, Neo4j Cypher, Qdrant configs)
