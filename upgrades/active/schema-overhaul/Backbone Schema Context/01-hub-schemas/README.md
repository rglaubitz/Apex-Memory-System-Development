# 01-hub-schemas: Individual Hub Schema Definitions

**Purpose:** Detailed entity definitions for all 6 hubs in the unified memory system.

---

## Folder Structure

```
01-hub-schemas/
├── complete/          # Finalized hub schemas (95%+ complete)
│   ├── HUB-1-G-COMPLETE.md
│   ├── HUB-2-OPENHAUL-COMPLETE.md
│   ├── HUB-4-CONTACTS-COMPLETE.md
│   ├── HUB-5-FINANCIALS-COMPLETE.md
│   └── HUB-6-CORPORATE-COMPLETE.md
└── drafts/            # Draft/baseline versions (40-60% complete)
    ├── HUB-1-G-DRAFT.md
    ├── HUB-2-OPENHAUL-DRAFT.md
    ├── HUB-3-ORIGIN-BASELINE.md
    ├── HUB-4-CONTACTS-DRAFT.md
    ├── HUB-5-FINANCIALS-DRAFT.md
    └── HUB-6-CORPORATE-DRAFT.md
```

---

## Complete Hub Schemas (Use These)

### Hub 1: G (Command Center) - "Everything Me"

**File:** [complete/HUB-1-G-COMPLETE.md](complete/HUB-1-G-COMPLETE.md)

**Status:** ✅ 95% Complete

**Core Entities (8 entities, 195 properties):**
- G (Person) - Central command entity
- Project - Strategic initiatives
- Goal - Measurable objectives
- Task - Action items
- Insight - Strategic insights
- KnowledgeItem - Captured knowledge
- Asset - Financial assets
- Note - Quick notes

**Use Cases:**
- Strategic planning and goal tracking
- Project management and task coordination
- Knowledge management
- Personal asset tracking

---

### Hub 2: OpenHaul Brokerage - "The Business"

**File:** [complete/HUB-2-OPENHAUL-COMPLETE.md](complete/HUB-2-OPENHAUL-COMPLETE.md)

**Status:** ✅ 95% Complete

**Core Entities (8 entities, 201 properties):**
- Load - Freight shipments
- Carrier - Transportation providers
- Location - Pickup/delivery locations
- Document - BOLs, PODs, rate confirmations
- MarketRate - Rate intelligence
- LoadBoard - Load postings
- Quote - Customer quotes
- RateHistory - Historical pricing

**Use Cases:**
- Freight brokerage operations
- Carrier management
- Rate negotiation and intelligence
- Load tracking and dispatch

---

### Hub 3: Origin Transport - "The Fleet" (NOTE: Only baseline exists)

**File:** [drafts/HUB-3-ORIGIN-BASELINE.md](drafts/HUB-3-ORIGIN-BASELINE.md)

**Status:** ⚠️ 40% Baseline (not yet upgraded to complete)

**Core Entities (7 entities):**
- Tractor - Trucks
- Trailer - Trailers
- Driver - Drivers
- FuelTransaction - Fuel purchases
- MaintenanceRecord - Maintenance history
- Incident - Accidents/incidents
- Insurance - Insurance policies

**Use Cases:**
- Fleet management
- Driver management
- Maintenance tracking
- Fuel expense tracking

**Note:** This hub uses the baseline/draft version. Full completion planned for future phase.

---

### Hub 4: Contacts/CRM - "The Rolodex"

**File:** [complete/HUB-4-CONTACTS-COMPLETE.md](complete/HUB-4-CONTACTS-COMPLETE.md)

**Status:** ✅ 95% Complete

**Core Entities (7 entities, 147 properties):**
- Company - Business entities
- Person - Individual contacts
- Contact - Contact points
- Address - Physical addresses
- Relationship - Person-to-person relationships
- Interaction - Communication history
- Tag - Organization tags

**Key Features:**
- Multi-category companies (customer + carrier + vendor)
- Rich relationship tracking
- Complete interaction history

**Use Cases:**
- Customer relationship management
- Vendor management
- Contact organization
- Network relationship tracking

---

### Hub 5: Financials - "The Money"

**File:** [complete/HUB-5-FINANCIALS-COMPLETE.md](complete/HUB-5-FINANCIALS-COMPLETE.md)

**Status:** ✅ 95% Complete

**Core Entities (8 entities, 175 properties):**
- Expense - Operating expenses
- Revenue - Income streams
- Invoice - Billing documents
- Payment - Payment records
- BankAccount - Bank accounts
- Loan - Financing
- IntercompanyTransfer - Capital transfers
- TaxRecord - Tax filings

**Key Features:**
- Intercompany transaction tracking
- Related party flagging
- Multi-entity financial consolidation

**Use Cases:**
- Expense tracking
- Revenue management
- Accounts payable/receivable
- Financial reporting

---

### Hub 6: Corporate Infrastructure - "The Foundation"

**File:** [complete/HUB-6-CORPORATE-COMPLETE.md](complete/HUB-6-CORPORATE-COMPLETE.md)

**Status:** ✅ 95% Complete

**Core Entities (7 entities, 178 properties):**
- LegalEntity - Businesses (OpenHaul, Origin, G)
- OwnershipRecord - Ownership relationships
- License - Operating authorities
- Filing - Corporate filings
- Document - Contracts, articles, bylaws
- Insurance - Business insurance
- Compliance - Compliance tracking

**Key Features:**
- Multi-entity ownership tracking
- License expiration monitoring
- Document management

**Use Cases:**
- Corporate structure management
- Regulatory compliance
- License tracking
- Legal document storage

---

## Draft/Baseline Versions (Historical)

The `drafts/` folder contains earlier versions of hub schemas:

- **Purpose:** Historical reference, initial planning documents
- **Status:** Superseded by complete versions (except Hub 3)
- **Use:** Reference only, do not use for implementation

**Exception:** Hub 3 (Origin Transport) only has baseline version - use `drafts/HUB-3-ORIGIN-BASELINE.md` for implementation.

---

## Schema Statistics

| Hub | Entities | Properties | Avg Props/Entity | Status |
|-----|----------|------------|------------------|--------|
| Hub 1: G | 8 | 195 | 24.4 | ✅ 95% |
| Hub 2: OpenHaul | 8 | 201 | 25.1 | ✅ 95% |
| Hub 3: Origin | 7 | 190 | 27.1 | ⚠️ 40% |
| Hub 4: Contacts | 7 | 147 | 21.0 | ✅ 95% |
| Hub 5: Financials | 8 | 175 | 21.9 | ✅ 95% |
| Hub 6: Corporate | 7 | 178 | 25.4 | ✅ 95% |
| **TOTAL** | **45** | **1,086** | **24.1** | **82%** |

---

## Quick Navigation

**I want to...**
- **Implement a hub in PostgreSQL** → Use complete/*.md + [../03-implementation/6-HUB-IMPLEMENTATION-SCHEMAS.md](../03-implementation/6-HUB-IMPLEMENTATION-SCHEMAS.md)
- **Understand hub relationships** → Use [../02-phase3-validation/PHASE-3-INTEGRATION-PATTERN-VALIDATION.md](../02-phase3-validation/PHASE-3-INTEGRATION-PATTERN-VALIDATION.md)
- **Validate hub schemas** → Use [../02-phase3-validation/](../02-phase3-validation/)
- **See all entities at once** → Use [../03-implementation/6-HUB-SCHEMA-CROSS-REFERENCE.md](../03-implementation/6-HUB-SCHEMA-CROSS-REFERENCE.md)

---

## Implementation Priority

**Recommended implementation order:**

1. **Hub 6 (Corporate)** - Foundation entities (LegalEntity required by Hub 5)
2. **Hub 4 (Contacts)** - CRM foundation (Company/Person required by Hub 2, 3, 5)
3. **Hub 5 (Financials)** - Money tracking (requires Hub 6 LegalEntity)
4. **Hub 3 (Origin)** - Fleet operations (requires Hub 4 for vendors/insurance)
5. **Hub 2 (OpenHaul)** - Brokerage operations (requires Hub 4 for customers/carriers)
6. **Hub 1 (G)** - Command center (requires Hub 4 Person, Hub 5 Revenue/Expense for goals)

**Rationale:** Bottom-up dependency resolution - implement dependencies first.
