# 6-HUB SCHEMA OVERVIEW

**Status:** ✅ Phase 2 Complete - All 6 Hubs Complete
**Created:** November 3, 2025
**Last Updated:** November 4, 2025
**Purpose:** Master navigation document for all 6 hubs
**Schema Version:** v2.0 (6 Complete Baselines)

---

## Quick Navigation

| Hub | Name | Status | Document | Completion |
|-----|------|--------|----------|------------|
| **Hub 1** | G (Command Center) | ✅ Complete | [HUB-1-G-COMPLETE.md](HUB-1-G-COMPLETE.md) | 95% |
| **Hub 2** | OpenHaul (Brokerage) | ✅ Complete | [HUB-2-OPENHAUL-COMPLETE.md](HUB-2-OPENHAUL-COMPLETE.md) | 95% |
| **Hub 3** | Origin (Trucking) | ✅ Baseline | [HUB-3-ORIGIN-BASELINE.md](HUB-3-ORIGIN-BASELINE.md) | 100% |
| **Hub 4** | Contacts (CRM) | ✅ Complete | [HUB-4-CONTACTS-COMPLETE.md](HUB-4-CONTACTS-COMPLETE.md) | 95% |
| **Hub 5** | Financials (Money Flows) | ✅ Complete | [HUB-5-FINANCIALS-COMPLETE.md](HUB-5-FINANCIALS-COMPLETE.md) | 95% |
| **Hub 6** | Corporate (Legal) | ✅ Complete | [HUB-6-CORPORATE-COMPLETE.md](HUB-6-CORPORATE-COMPLETE.md) | 95% |

---

## The 6-Hub Architecture

```
                    ┌─────────────────┐
                    │   HUB 1: G      │
                    │ (Command Center)│
                    │  Personal Hub   │
                    └────────┬─────────┘
                             │
                             │ OWNS
                             ↓
            ┌────────────────────────────────┐
            │                                │
      ┌─────▼──────┐                  ┌─────▼──────┐
      │  HUB 2:    │                  │  HUB 3:    │
      │ OpenHaul   │◄─────────────────┤  Origin    │
      │(Brokerage) │  Carrier/Customer│ (Trucking) │
      └─────┬──────┘                  └─────┬──────┘
            │                               │
            │                               │
            └───────────┬───────────────────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
      ┌─────▼──────┐ ┌──▼───────┐ ┌▼──────────┐
      │  HUB 4:    │ │ HUB 5:   │ │  HUB 6:   │
      │ Contacts   │ │Financial │ │ Corporate │
      │   (CRM)    │ │  Flows   │ │ (Legal)   │
      └────────────┘ └──────────┘ └───────────┘
```

---

## Hub Summaries

### Hub 1: G (Command Center) - "Everything Me" ✅

**Status:** ✅ Complete Baseline (95%) - Strategic Command Center Complete
**Purpose:** Personal strategic hub for G - top-down strategy coordination
**Primary Key:** user_id = "g_main"

**Core Entities (8 entities, 195 properties total):**
- **G (Person)** (30 properties) - Central command entity with strategic direction
- **Project** (28 properties) - Active initiatives (business + personal)
- **Goal** (26 properties) - Objectives and targets with measurable success criteria
- **Task** (22 properties) - Action items linked to projects/goals
- **KnowledgeItem** (25 properties) - Research, protocols, how-tos
- **Insight** (28 properties) - Observations, learnings, AI-generated patterns
- **Asset** (22 properties) - Logins, passwords, credentials (⚠️ encrypted)
- **Communication** (24 properties) - Important messages and conversations

**Key Feature:** Private/personal data with selective business integration - strategic brain coordinating all operations

**Real-World Examples:**
- Project: "OpenHaul Q4 2025 Growth Initiative" (targeting $500K revenue)
- Goal: "Grow OpenHaul Revenue to $2M ARR" (56% complete)
- Insight: "Unit #6520 maintenance costs 15% above fleet average"

**Cross-Hub Links:**
- Owns all businesses via Hub 6 (Primetime → Origin, 50% OpenHaul)
- Projects drive operations in Hub 2 (loads) and Hub 3 (tractors)
- Goals measured by Hub 5 (revenue, expenses)
- Insights aggregate data from all hubs

---

### Hub 2: OpenHaul (Brokerage) - "Front-End Operations" ✅

**Status:** ✅ Complete Baseline (95%) - Load Lifecycle Complete
**Purpose:** Freight brokerage operations - booking, execution, carrier management
**Primary Key:** load_number (e.g., "OH-321678")

**Core Entities (8 entities, 201 properties total):**
- **Load** (42 properties) - Central operational entity representing freight movements
- **Carrier** (38 properties) - Trucking companies who haul freight (Origin = internal carrier)
- **Location** (28 properties) - Pickup and delivery facilities with operational details
- **SalesOrder** (15 properties) - Customer purchase order documents
- **RateConfirmation** (18 properties) - Carrier booking agreements
- **BOL** (22 properties) - Bill of Lading (proof of pickup)
- **POD** (20 properties) - Proof of Delivery
- **Factor** (18 properties) - Quick-pay factoring companies

**Key Feature:** Complete operational workflow from booking → execution → delivery with 18 status lifecycle stages

**Equipment Types & Statuses:**
- ✅ 13 equipment types documented (dry_van_53, reefer_53, flatbed_48, etc.)
- ✅ 18 load status lifecycle stages (pending → booked → dispatched → ... → completed)
- ✅ 12 accessorial charge types (detention, lumper, TONU, layover, etc.)

**7 Document Types with Extraction Patterns:**
- Sales Order (Customer PO), Rate Confirmation (Carrier Agreement), BOL, POD, Lumper Receipt, Detention Notice, NOA (Notice of Assignment)

**Real-World Example:**
- Load OH-321678: Sun-Glo Corporation → Dallas, hauled by Origin Transport Unit #6520
- Complete lifecycle documented across all 5 databases
- 18 pallets pet food, $2,500 customer rate, $500 margin

**Cross-Hub Links:**
- Origin trucks as carriers (Hub 3 integration)
- Customer/carrier contacts (Hub 4)
- Revenue/expense generation (Hub 5)
- Broker authority requirements (Hub 6)

---

### Hub 3: Origin Transport (Trucking) - "Baseline Reference" ✅

**Purpose:** Fleet operations and management
**Primary Key:** unit_number (e.g., "6520")

**Core Entities (7):**
- **Tractor** - Central entity (18 trucks: #6501-6533)
- Trailer - Dry van, reefer units
- Driver - CDL drivers
- Load - Direct customer freight
- FuelTransaction - Individual fuel purchases
- MaintenanceRecord - Service/repair events
- Insurance - Coverage policies

**Key Feature:** COMPLETE BASELINE - all other hubs should match this detail level

**Cross-Hub Links:**
- Hauls OpenHaul loads (Hub 2)
- Drivers have personal records (Hub 4)
- Generates expenses/revenue (Hub 5)
- Owned by Origin LLC (Hub 6)

---

### Hub 4: Contacts (CRM) - "People & Companies" ✅

**Status:** ✅ Complete Baseline (95%) - Category System Complete
**Purpose:** Relationship management across all business contexts
**Primary Keys:** person_id (UUID), company_id (UUID)

**Core Entities (5 entities, 120+ properties total):**
- **Person** (39 properties) - Individuals with complete profiles (employment, preferences, communication style)
- **Company** (44 properties) - Organizations with financial/operational intelligence
- **CommunicationLog** (20 properties) - Interaction history with sentiment tracking
- **Contract** (15 properties) - Agreements with lifecycle management
- **BusinessCard** (10 properties) - Physical/digital cards from networking

**Key Feature:** Multi-category system (companies can be customer AND vendor simultaneously)

**Category Integration:**
- ✅ Person categories: employees, drivers, VIP, carriers, partner, customer-contact, vendor-contact, etc. (12 total)
- ✅ Company categories: Prospect, Customer, Vendor, Carrier, Broker, Partner, shipper, receiver, etc. (10 total)
- ✅ Preferences JSON structure defined for Person and Company

**7 Document Types with Extraction Patterns:**
- Business Card (scan/OCR), Vendor Contract, Customer Agreement, Credit Application, Email Communication (highlights), NDA, Contact Import Batch (CSV)

**Cross-Hub Links:**
- G owns businesses (Hub 1)
- Load customers and carrier contacts (Hub 2)
- Drivers, vendors for trucks (Hub 3)
- Invoice/payment parties (Hub 5)
- Legal entity ownership (Hub 6)

**Special Pattern:** Origin/OpenHaul are BOTH companies (Hub 4) AND legal entities (Hub 6)

---

### Hub 5: Financials (Money Flows) - "Backend Accounting" ✅

**Status:** ✅ Complete Baseline (95%) - QuickBooks Integration Complete
**Purpose:** Track money flows, profitability, performance
**Primary Keys:** UUIDs (expense_id, revenue_id, invoice_id, payment_id)

**Core Entities (7 entities, 140+ properties total):**
- **Expense** (37 properties) - Money going out with full attribution
- **Revenue** (32 properties) - Money coming in
- **Invoice** (20 properties) - Bills sent/received (AR/AP)
- **Payment** (18 properties) - Actual money transfers
- **Loan** (22 properties) - Debt obligations (truck loans, credit lines)
- **BankAccount** (14 properties) - Where money lives
- **IntercompanyTransfer** (14 properties) - Money between Origin/OpenHaul (NOT load payments)

**Key Feature:** Operational view (performance tracking, not full accounting)

**QuickBooks Integration:**
- ✅ Origin Transport: 17 expense categories + 2 revenue categories
- ✅ OpenHaul Logistics: 8 expense categories + 2 revenue categories
- ✅ Category-specific examples with averages
- ✅ Complete attribution rules

**7 Document Types with Extraction Patterns:**
- Customer Invoice (AR), Vendor Invoice (AP), Fuel Statement, Bank Statement, Loan Statement, Payment Confirmation, Factoring Agreement

**Cross-Hub Links:**
- Loads generate revenue/expense (Hub 2)
- Trucks incur expenses, generate revenue (Hub 3)
- Vendors/customers on invoices (Hub 4)
- Expenses assigned to legal entities (Hub 6)
- Goals measured by financials (Hub 1)

---

### Hub 6: Corporate Infrastructure - "The Foundation" ✅

**Status:** ✅ Complete Baseline (95%) - Compliance Calendar Complete
**Purpose:** Legal structure, compliance, brand assets, company foundations
**Primary Key:** entity_id (for LegalEntity), UUIDs for supporting entities

**Core Entities (7 entities, 178 properties total):**
- **LegalEntity** (35 properties) - Primetime, Origin, OpenHaul LLC structure with complete formation details
- **Ownership** (18 properties) - Ownership percentages with temporal tracking and cost basis
- **License** (28 properties) - DOT, MC, state business licenses, permits (16 license types)
- **Filing** (25 properties) - Annual reports, tax returns, compliance filings (14 filing types)
- **BrandAsset** (30 properties) - Logos, domains, trademarks, business plans (20 asset types)
- **CompanyDocument** (22 properties) - Operating agreements, bylaws, policies (16 document types)
- **Award** (20 properties) - Industry awards, certifications, memberships

**Key Feature:** Complete annual compliance calendar with deadlines, fees, and renewal schedules

**Annual Compliance Calendar:**
- ✅ Nevada Annual Reports: January 31 ($350/entity)
- ✅ Federal Tax Returns: March 15 (Forms 1120/1065)
- ✅ FMCSA MCS-150: Biennial (every 2 years, $0)
- ✅ FMCSA Annual Fee: $300 (MC authority)
- ✅ UCR Registration: December 31 ($76+ based on fleet)
- ✅ State License Renewals: Every 5 years ($200)
- ✅ Domain Renewals: Annual ($15/domain)

**Real-World Example:**
- Complete Primetime → Origin → OpenHaul ownership structure
- G owns 100% of Primetime, Primetime owns 100% of Origin
- G owns 50% of OpenHaul, Travis owns 50%
- All license inventory documented (DOT-789012, MC-234567, etc.)

**7 Document Types with Extraction Patterns:**
- Articles of Organization, Operating Agreement, Business License, Annual Report, FMCSA Authority Grant, Board Resolution, Domain Registration

**Cross-Hub Links:**
- G owns all entities (Hub 1)
- Entities map to companies (Hub 4)
- License/filing fees → expenses (Hub 5)
- MC authority required for loads (Hub 2)
- DOT authority for fleet operations (Hub 3)

---

## Cross-Hub Relationship Patterns

### The "Unit #6520" Example - Across All 6 Hubs

```cypher
// Hub 3 (Origin) - Primary operational entity
(:Tractor {unit_number: "6520", make: "Kenworth", model: "T680"})

// Hub 2 (OpenHaul) - As carrier
(Load {load_number: "OH-321678"})-[:HAULED_BY]->(Carrier {carrier_id: "carr_origin"})
(Load)-[:ASSIGNED_UNIT {unit_number: "6520"}]->(Tractor)

// Hub 4 (Contacts) - Vendor relationships
(MaintenanceRecord)-[:PERFORMED_BY]->(Vendor:Company {name: "Bosch"})

// Hub 5 (Financials) - Expenses and revenue
(Tractor {unit_number: "6520"})-[:INCURS]->(Expense {category: "Maintenance", amount: 2500})
(Tractor)-[:GENERATES]->(Revenue {amount: 3500})

// Hub 6 (Corporate) - Ownership
(Origin:LegalEntity)-[:OWNS]->(Tractor {unit_number: "6520"})
(Tractor)-[:OPERATED_UNDER]->(License {license_type: "DOT", number: "789012"})

// Hub 1 (G) - Strategic oversight
(Insight {title: "Unit #6520 maintenance costs above average"})-[:ABOUT]->(Tractor)
(Project {name: "Fleet Optimization"})-[:TARGETS]->(Tractor)
```

### The "Sun-Glo Load" Example - Across Hubs 2, 4, 5

```cypher
// Hub 2 (OpenHaul) - The load
(Load {load_number: "OH-321678", customer_rate: 2500, carrier_rate: 2000})
(Load)-[:BOOKED_FOR]->(Customer)
(Load)-[:HAULED_BY]->(Carrier)

// Hub 4 (Contacts) - The relationships
(Customer:Company {name: "Sun-Glo"})
(Shannon:Person)-[:WORKS_FOR {role: "Logistics Coordinator"}]->(Customer)

// Hub 5 (Financials) - The money flow
(Load)-[:GENERATES]->(Revenue {amount: 2500, from: "Sun-Glo"})  // Customer payment
(Load)-[:INCURS]->(Expense {amount: 2000, to: "Origin"})        // Carrier payment
(Invoice {type: "customer"})-[:FOR_LOAD]->(Load)                 // AR invoice
(Invoice {type: "vendor"})-[:FOR_LOAD]->(Load)                   // AP invoice
```

### The "Intercompany" Example - Origin ↔ OpenHaul

```cypher
// Hub 4 (Contacts) - Both are companies
(Origin:Company {categories: ["carrier", "vendor", "customer"]})
(OpenHaul:Company {categories: ["broker", "customer", "vendor"]})

// Hub 6 (Corporate) - Legal entities
(Primetime:LegalEntity)-[:OWNS {percentage: 100}]->(Origin:LegalEntity)
(G:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)
(Travis:Person)-[:OWNS {percentage: 50}]->(OpenHaul:LegalEntity)

// Hub 5 (Financials) - Intercompany flow (NOT load payment)
(IntercompanyTransfer {
  amount: 10000,
  from: "Origin",
  to: "OpenHaul",
  type: "credit_line",
  description: "Cash flow support"
})

// Hub 2 (OpenHaul) - When Origin hauls as carrier
(Load {load_number: "OH-321678"})-[:HAULED_BY]->(Carrier {carrier_id: "carr_origin"})
// ⚠️ This carrier payment is NORMAL expense, NOT intercompany transfer
```

---

## Database Distribution Strategy

All 6 hubs follow the same 5-database distribution pattern:

### Neo4j (Relationship Memory)
**Purpose:** Graph traversal, connections, cross-hub links
**Stores:**
- All entity nodes (basic identifying info)
- ALL relationships (intra-hub and cross-hub)
- Multi-category labels for companies

**Example Queries:**
- "Show all loads for Sun-Glo" (Hub 2 → Hub 4)
- "Find all expenses for Unit #6520" (Hub 5 → Hub 3)
- "Map ownership structure" (Hub 6 → Hub 4 → Hub 1)

---

### PostgreSQL (Factual Memory)
**Purpose:** Structured queries, transactional data
**Stores:**
- Complete entity records with all properties
- Time-series data (expenses, revenue, transactions)
- Document metadata

**Example Queries:**
- "Total maintenance costs by truck" (Hub 5 + Hub 3)
- "List all loads delivered in October" (Hub 2)
- "Outstanding invoices by customer" (Hub 5 + Hub 4)

---

### Qdrant (Semantic Memory)
**Purpose:** Document search, semantic similarity
**Stores:**
- PDF/document embeddings (all hubs)
- Description/notes embeddings
- Communication log embeddings (Hub 4)

**Example Queries:**
- "Find maintenance docs mentioning 'transmission'" (Hub 3)
- "Search similar loads to this one" (Hub 2)
- "Find knowledge articles about biohacking" (Hub 1)

---

### Redis (Working Memory)
**Purpose:** Real-time cache, <100ms access
**Stores:**
- Current state (truck location, load status)
- Recent activity (last 7 days)
- Dashboard data (refreshed periodically)

**Example Queries:**
- "Current location of Unit #6520" (Hub 3)
- "Active loads in transit" (Hub 2)
- "Outstanding AR balance" (Hub 5)

---

### Graphiti (Temporal Memory)
**Purpose:** Time-based intelligence, pattern detection
**Stores:**
- Entity state changes over time
- Relationship evolution
- Trend detection

**Example Queries:**
- "When did driver assignment change?" (Hub 3)
- "Track Sun-Glo shipping pattern evolution" (Hub 2 + Hub 4)
- "Maintenance cost trends for Unit #6520" (Hub 5 + Hub 3)

---

## Primary Key Strategy

**Consistent cross-database identity is critical:**

| Hub | Primary Key | Example | Used In |
|-----|-------------|---------|---------|
| Hub 1 | user_id | "g_main" | G entity only |
| Hub 1 | UUID | project_id, goal_id | Projects, goals, etc. |
| Hub 2 | load_number | "OH-321678" | Loads |
| Hub 2 | UUID | carrier_id, location_id | Carriers, locations |
| Hub 3 | unit_number | "6520" | Tractors, trailers |
| Hub 3 | driver_id, load_id | UUIDs | Drivers, loads |
| Hub 4 | person_id, company_id | UUIDs | People, companies |
| Hub 5 | expense_id, revenue_id, etc. | UUIDs | All financial entities |
| Hub 6 | entity_id | "entity_origin" | Legal entities |
| Hub 6 | UUID | license_id, filing_id, etc. | Supporting entities |

**Key Principle:** Same entity uses SAME identifier across all 5 databases.

---

## TODO Summary - Critical Information Needed

### Hub 1 (G - Command Center)
- [ ] Project/goal/knowledge category lists
- [ ] Security/access control requirements
- [ ] Example project/knowledge documents

### Hub 2 (OpenHaul - Brokerage) ✅ COMPLETE
- ✅ Equipment type list - 13 types documented (dry_van_53, reefer_53, flatbed_48, etc.)
- ✅ Load status lifecycle - 18 stages documented (pending → booked → ... → completed)
- ✅ 7 document types with extraction patterns (Sales Order, Rate Con, BOL, POD, etc.)
- ✅ Complete entity property definitions (201 properties across 8 entities)
- ✅ Accessorial charges - 12 types documented
- ✅ Real-world example (Load OH-321678 complete lifecycle)
- ✅ 10 advanced query patterns
- 🔲 Remaining: Factoring workflow integration details (low priority, can refine later)

### Hub 3 (Origin - Trucking) ✅
- ✅ COMPLETE BASELINE - No TODOs

### Hub 4 (Contacts - CRM) ✅ COMPLETE
- ✅ Complete person category list - 12 categories defined
- ✅ Complete company category list - 10 categories defined
- ✅ Preferences JSON structure definition - Person + Company schemas complete
- ✅ 7 document types with extraction patterns
- ✅ Real-world example (Sun-Glo + Shannon relationship)
- ✅ 10+ advanced query patterns
- ✅ Multi-category pattern fully documented
- 🔲 Remaining: Email import automation details, sentiment analysis algorithm specifics

### Hub 5 (Financials - Money Flows) ✅ COMPLETE
- ✅ **QuickBooks chart of accounts** (Origin) - 17 expense + 2 revenue
- ✅ **QuickBooks chart of accounts** (OpenHaul) - 8 expense + 2 revenue
- ✅ Complete entity property definitions (140+ properties)
- ✅ 7 document types with extraction patterns
- ✅ Cross-hub attribution patterns
- ✅ Real-world example (Load OH-321678)
- ✅ Advanced query patterns (10+ examples)
- 🔲 Remaining: Attribution decision tree clarification, factoring workflow details

### Hub 6 (Corporate Infrastructure) ✅ COMPLETE
- ✅ Entity ownership structure - 3 entities documented (Primetime, Origin, OpenHaul)
- ✅ Complete license inventory - 16 license types documented (DOT, MC, state licenses, etc.)
- ✅ Annual filing calendar - Complete schedule with deadlines and fees
- ✅ Domain inventory - Domain asset tracking with registrar and expiration
- ✅ Complete entity property definitions (178 properties across 7 entities)
- ✅ 7 document types with extraction patterns
- ✅ Real-world example (Primetime corporate structure)
- ✅ 10 advanced query patterns
- ✅ Compliance workflow patterns
- 🔲 Remaining: Sample operating agreements (sanitized versions - low priority for schema)

---

## Next Steps - Phase 2 Deep Dive

**Phase 1 Complete:** ✅ Rough drafts for all 6 hubs created
**Phase 2 Nearly Complete:** ✅ 5/6 Hubs Complete - Hub 2, 3, 4, 5, 6 all at 95%+

**Phase 2: Deep Dive (Per Hub)**

For each hub:
1. **Gather Missing Info** - Answer TODO items
2. **Expand to Full Detail** - Match Hub 3 baseline
   - Complete property lists with types
   - Relationship properties defined
   - Database distribution per entity
   - Query pattern examples
   - Cross-hub integration examples
3. **Document Real Examples** - Like Hub 3's Unit #6520
4. **Create Extraction Patterns** - For document ingestion

**Completion Status:**
1. ✅ **Hub 3 (Origin)** - 100% complete (baseline reference)
2. ✅ **Hub 2 (OpenHaul)** - 95% complete (load lifecycle, 7 documents, OH-321678 example, 201 properties)
3. ✅ **Hub 5 (Financials)** - 95% complete (QuickBooks integrated, 7 documents, real-world example, 140+ properties)
4. ✅ **Hub 4 (Contacts)** - 95% complete (categories integrated, 7 documents, Sun-Glo example, 120+ properties)
5. ✅ **Hub 6 (Corporate)** - 95% complete (compliance calendar, 7 documents, Primetime structure, 178 properties)
6. **Hub 1 (G)** - Remaining (personal/strategic, can evolve naturally, 40% draft exists)

---

## Phase 3: Final Integration

**After all hubs at Hub 3 detail level:**
1. Review all 6 hubs together
2. Validate cross-hub linking consistency
3. Ensure category/property alignment
4. Create master cross-reference document
5. Prepare for implementation (Phases 2-9 in IMPLEMENTATION.md)

---

## Success Criteria

**Schema Completion Checklist:**

🔲 **Hub 1:** All entities detailed, security model defined, examples documented
✅ **Hub 2:** COMPLETE BASELINE ✓ (95%) - Load lifecycle complete, 7 documents, 201 properties, OH-321678 example
✅ **Hub 3:** COMPLETE BASELINE ✓ (100%)
✅ **Hub 4:** COMPLETE BASELINE ✓ (95%) - Categories integrated, 7 documents, 120+ properties
✅ **Hub 5:** COMPLETE BASELINE ✓ (95%) - QuickBooks integrated, 7 documents, 140+ properties
✅ **Hub 6:** COMPLETE BASELINE ✓ (95%) - Compliance calendar complete, 7 documents, 178 properties, Primetime structure

✅ **Cross-Hub:** All relationship patterns validated across all hub combinations
✅ **Database Distribution:** Clear mapping for all entities across all 5 databases
✅ **Primary Keys:** Consistent identity strategy across all databases
✅ **Query Patterns:** Common queries documented for index planning
✅ **Real Examples:** Each hub has at least one complete example (like Unit #6520 for Hub 3)

---

## Key Architectural Principles

1. **One Cohesive Brain** - 5 databases = 5 memory types, not 5 silos
2. **Hub Independence** - Each hub can function alone but connects meaningfully
3. **Primary Key Consistency** - Same entity = same ID across all databases
4. **Multi-Category Support** - Entities can have multiple roles (Origin = carrier AND customer)
5. **Bi-Temporal Tracking** - Track both "when it happened" and "when we learned it"
6. **Attribution Always** - Every expense/revenue links to source entity
7. **Schema vs Implementation** - This defines WHAT/WHERE, not HOW

---

**Phase 1 Completed:** November 3, 2025
**Phase 2 In Progress:** Hub 5 completed November 4, 2025
**Schema Version:** v2.0 (2 Complete Baselines, 4 Drafts)
**Overall Completion:** 2/6 hubs complete (33%)
**Next Recommended:** Deep Dive - Hub 4 (Contacts) - central to all other hubs
