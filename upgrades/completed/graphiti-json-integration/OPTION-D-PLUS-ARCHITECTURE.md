# Option D+ Architecture: Hub Rigidity + Property Flexibility

**Handoff Documentation for Graphiti + JSON Integration**

**Purpose:** Complete context for anyone working on this system
**Audience:** Developers, architects, future team members
**Created:** November 5, 2025
**Architecture Version:** 1.0 (Option D+)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [The Problem We Solved](#the-problem-we-solved)
3. [Architecture Decision History](#architecture-decision-history)
4. [How Option D+ Works](#how-option-d-works)
5. [Implementation Guide](#implementation-guide)
6. [Code Examples](#code-examples)
7. [Query Patterns](#query-patterns)
8. [Schema Evolution Process](#schema-evolution-process)
9. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
10. [FAQs](#faqs)

---

## Executive Summary

**What is Option D+?**

A unified entity architecture that combines:
- **Hub Rigidity:** 6 fixed business hubs (cannot change without architectural review)
- **Property Flexibility:** Three-tier property system that captures everything Graphiti extracts

**Key Innovation:**

Instead of maintaining two separate entity schemas (Graphiti minimal types + Backbone full types), we use a **single unified schema** where:
1. **Tier 1 (Core):** Required fields every entity must have
2. **Tier 2 (Structured):** Optional but typed fields from Backbone schema
3. **Tier 3 (Dynamic):** Catch-all for anything Graphiti extracts that doesn't match schema

**Why This Matters:**

✅ **Nothing falls through the cracks** - All extracted data captured (Tier 2 or Tier 3)
✅ **Perfect LLM alignment** - Graphiti uses official Backbone entity definitions
✅ **Schema evolves** - Common Tier 3 fields promoted to Tier 2 automatically
✅ **Single source of truth** - One Customer schema, not two
✅ **Hub enforcement** - Rigid business boundaries prevent data chaos

---

## The Problem We Solved

### The Original Challenge

**Week 1-2 (Oct 2025):** Implemented Graphiti integration with 5 custom entity types:
- Customer (6 properties)
- Person (6 properties)
- Invoice (7 properties)
- Equipment (7 properties)
- Project (8 properties)

**Week 2-3 (Nov 2025):** Implemented Backbone Schema with 45 full entities:
- Customer (44 properties)
- Person (39 properties)
- Invoice (20 properties)
- Truck (40 properties)
- Load (45 properties)
- ... (40 more entities)

### The Alignment Problem

**Situation:** We had two separate entity systems:
```
Graphiti Layer (Temporal)          Backbone Schema (Operational)
├─ Customer (6 properties)         ├─ Customer (44 properties)
├─ Person (6 properties)           ├─ Person (39 properties)
├─ Invoice (7 properties)          ├─ Invoice (20 properties)
├─ Equipment (7 properties)        ├─ Truck (40 properties)
└─ Project (8 properties)          └─ Load (45 properties)
                                   └─ ... (40 more entities)
```

**Problems:**
1. ❌ **Duplication:** Two Customer definitions to maintain
2. ❌ **Alignment confusion:** Graphiti doesn't know what's important for extraction
3. ❌ **Data loss:** Fields Graphiti extracts but aren't in minimal schema → LOST
4. ❌ **Complex queries:** Need joins between Graphiti and Backbone entities
5. ❌ **Maintenance burden:** Update schema in two places

### What We Tried (Options A-C)

**Option A: Graphiti as Extraction Layer (Rejected)**
- Graphiti extracts minimal entity
- After extraction, create separate full Backbone entity
- Link via UUID
- **Problem:** Duplication + orphaned Graphiti nodes

**Option B: Merged Entities (Rejected)**
- Combine Graphiti + Backbone into single entity
- **Problem:** LLM can't extract 44 properties reliably

**Option C: Separate Temporal Layer (Almost...)**
- Graphiti maintains `:Entity` nodes with temporal versioning
- Backbone maintains `:Customer` nodes with full properties
- Link via UUID
- **Problem:** Still two schemas to maintain + alignment issues

### The Breakthrough (Option D+)

**User's Insight:** "We want rigidity on the top level hubs, but flexibility as data gets more granular. We don't want data to not be extracted due to not having an obvious place to put it."

**Solution:** Hub Rigidity + Property Flexibility

```
RIGID: 6 Hubs (Fixed)
  ↓ Contains
SEMI-RIGID: 45 Entity Types (Can add new types to existing hubs)
  ↓ Contains
FLEXIBLE: Properties (Three-tier system)
  ├─ Tier 1: Core (Required) - uuid, name, hub
  ├─ Tier 2: Structured (Optional) - 44 Backbone fields
  └─ Tier 3: Dynamic (Catch-all) - additional_properties
```

---

## Architecture Decision History

### Timeline of Decisions

**October 15, 2025:** Graphiti integration begins
- Created 5 custom entity types for LLM extraction
- Minimal schemas (6-8 properties each)
- Goal: 90%+ extraction accuracy vs 60% regex baseline

**October 23, 2025:** JSON support added
- StructuredData models created
- Database writers implemented
- Parallel to Graphiti extraction

**November 1, 2025:** Schema Overhaul begins
- Backbone Schema designed (45 entities, 1,086 properties)
- 6-hub structure established
- Full operational entity definitions

**November 5, 2025:** Integration challenge identified
- Recognized misalignment between Graphiti (5 minimal) and Backbone (45 full)
- Explored Options A-C
- User requirement: "Rigidity at hub level, flexibility at data level"

**November 5, 2025 (Afternoon):** Option D+ approved
- Three-tier property system designed
- Hub validator created
- Schema evolution system planned

### Why We Chose Option D+

**Decision Factors:**

1. **Single Source of Truth** (Weight: 30%)
   - Option D+: ✅ One Customer schema used by both Graphiti and Backbone
   - Options A-C: ❌ Two schemas to maintain

2. **Nothing Falls Through Cracks** (Weight: 25%)
   - Option D+: ✅ Tier 3 catch-all captures everything
   - Options A-C: ❌ Fields not in schema are lost

3. **LLM Alignment** (Weight: 20%)
   - Option D+: ✅ Graphiti sees full Backbone context (better extraction)
   - Options A-C: ⚠️ Graphiti uses minimal types (limited context)

4. **Schema Evolution** (Weight: 15%)
   - Option D+: ✅ Automated analyzer promotes common Tier 3 → Tier 2
   - Options A-C: ❌ Manual schema updates

5. **Query Simplicity** (Weight: 10%)
   - Option D+: ✅ Single node query (no joins)
   - Options A-C: ❌ Requires joins or separate queries

**Total Score:**
- Option D+: 95/100
- Option C: 68/100
- Option B: 45/100
- Option A: 38/100

---

## How Option D+ Works

### The Three-Tier Property System

Every entity in the system has three tiers of properties:

#### Tier 1: Core (Required) - The Foundation

**Purpose:** Ensure every entity has minimum viable structure

**Fields (5 required):**
```python
class BaseEntity(BaseModel):
    # Tier 1: CORE (Required)
    uuid: str                          # Unique identifier (UUID v7, time-ordered)
    name: str                          # Human-readable name
    hub: Literal["contacts", "openhaul", ...]  # Hub assignment (RIGID)
    entity_type: str                   # Type within hub (e.g., "customer", "person")
    created_at: datetime               # When entity was created
```

**Characteristics:**
- ✅ **Required** - Entity cannot be created without these
- ✅ **System-managed** - uuid, hub, created_at auto-generated
- ✅ **Immutable** - Cannot change after creation (except name)

#### Tier 2: Structured (Optional) - The Business Schema

**Purpose:** Provide typed, validated fields for known business data

**Example (Customer):**
```python
class Customer(BaseEntity):
    # Tier 2: STRUCTURED (Optional)

    # LLM-Extractable Fields (Graphiti can extract from text)
    account_status: Optional[AccountStatus] = Field(
        default=None,
        llm_extractable=True  # ← Graphiti WILL extract this
    )
    contact_email: Optional[str] = Field(llm_extractable=True)
    phone: Optional[str] = Field(llm_extractable=True)
    address: Optional[str] = Field(llm_extractable=True)

    # Manually-Entered Fields (Too complex for LLM extraction)
    credit_limit: Optional[Decimal] = Field(llm_extractable=False)
    payment_terms: Optional[str] = Field(llm_extractable=False)
    credit_rating: Optional[str] = Field(llm_extractable=False)
    # ... (37 more Backbone fields)
```

**Characteristics:**
- ⚠️ **Optional** - Fields can be NULL
- ✅ **Typed** - Validation enforced (Decimal, Enum, str, etc.)
- ✅ **Documented** - `llm_extractable` flag marks LLM-friendly fields
- ✅ **Validated** - Pydantic ensures type safety

#### Tier 3: Dynamic (Catch-all) - The Safety Net

**Purpose:** Capture anything Graphiti extracts that doesn't match Tier 2 schema

**Fields:**
```python
class Customer(BaseEntity):
    # Tier 3: DYNAMIC (Catch-all)
    additional_properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible storage for extracted data that doesn't fit schema"
    )

    extracted_fields_not_in_schema: List[str] = Field(
        default_factory=list,
        description="Audit trail - which fields went to additional_properties"
    )
```

**Example Usage:**
```python
# Graphiti extracts unexpected field
graphiti_extraction = {
    "name": "Sun-Glo Corporation",
    "contact_email": "info@sunglo.com",  # ✅ Matches Tier 2
    "preferred_carrier": "FedEx",        # ❌ Not in Tier 2 → Tier 3
    "office_hours": "Mon-Fri 8am-5pm"   # ❌ Not in Tier 2 → Tier 3
}

# Smart population
customer = populate_entity_from_extraction(Customer, graphiti_extraction)

# Result:
Customer(
    uuid="customer_sunglo_xyz",
    name="Sun-Glo Corporation",
    hub="contacts",
    entity_type="customer",
    created_at=datetime.now(),

    # Tier 2: Matched schema
    contact_email="info@sunglo.com",  # ✅

    # Tier 3: Didn't match schema
    additional_properties={
        "preferred_carrier": "FedEx",
        "office_hours": "Mon-Fri 8am-5pm"
    },
    extracted_fields_not_in_schema=[
        "preferred_carrier",
        "office_hours"
    ]
)
```

**Characteristics:**
- ✅ **Flexible** - Any JSON-serializable data
- ✅ **Queryable** - PostgreSQL GIN index on JSONB
- ✅ **Audited** - Track what went to catch-all
- ✅ **Evolvable** - Common fields → promoted to Tier 2

### Hub Rigidity Enforcement

**The 6 Hubs (RIGID - Cannot Add New Hubs):**

```python
# apex_memory/utils/hub_validator.py

HUBS = [
    "g",           # Hub 1: G (Command Center) - Personal/family
    "openhaul",    # Hub 2: OpenHaul (Brokerage) - Load brokerage
    "origin",      # Hub 3: Origin Transport - Trucking operations
    "contacts",    # Hub 4: Contacts/CRM - People and companies
    "financials",  # Hub 5: Financials - Money and accounting
    "corporate"    # Hub 6: Corporate - Legal entities and compliance
]

# Entity Type → Hub Assignment (RIGID - Enforced Programmatically)
HUB_ASSIGNMENTS = {
    # Hub 1: G (Command Center)
    "owner": "g",
    "family": "g",
    "property": "g",
    "legal_entity_trust": "g",
    "insurance_policy": "g",
    "vehicle_personal": "g",
    "investment_account": "g",
    "personal_goal": "g",

    # Hub 2: OpenHaul (Brokerage)
    "load": "openhaul",
    "customer_openhaul": "openhaul",
    "carrier": "openhaul",
    "rate": "openhaul",
    "shipment": "openhaul",
    "broker": "openhaul",
    "factor": "openhaul",
    "loadboard": "openhaul",

    # Hub 3: Origin Transport
    "truck": "origin",
    "trailer": "origin",
    "driver": "origin",
    "maintenance_record": "origin",
    "trip": "origin",
    "fuel_purchase": "origin",
    "incident": "origin",

    # Hub 4: Contacts/CRM
    "customer": "contacts",
    "person": "contacts",
    "company": "contacts",
    "communication_log": "contacts",
    "contract": "contacts",
    "business_card": "contacts",
    "opportunity": "contacts",
    "activity": "contacts",

    # Hub 5: Financials
    "expense": "financials",
    "revenue": "financials",
    "invoice": "financials",
    "payment": "financials",
    "loan": "financials",
    "bank_account": "financials",
    "intercompany_transfer": "financials",
    "budget": "financials",

    # Hub 6: Corporate
    "legal_entity_corporate": "corporate",
    "ownership_stake": "corporate",
    "corporate_document": "corporate",
    "compliance_record": "corporate",
    "tax_record": "corporate",
    "asset": "corporate",
    "liability": "corporate",
}

def validate_hub_assignment(entity_type: str, hub: str) -> None:
    """
    Enforce rigid hub assignments (prevents data chaos).

    Raises ValueError if entity_type assigned to wrong hub.
    """
    expected_hub = HUB_ASSIGNMENTS.get(entity_type)

    if expected_hub is None:
        raise ValueError(
            f"Entity type '{entity_type}' not defined in any hub. "
            f"Add to HUB_ASSIGNMENTS or use existing type."
        )

    if hub != expected_hub:
        raise ValueError(
            f"Entity type '{entity_type}' must be in hub '{expected_hub}', "
            f"not '{hub}'. Hub assignments are RIGID and enforced."
        )
```

**Why Hub Rigidity?**

✅ **Prevents data chaos** - Can't create "customer" entity in "financials" hub
✅ **Clear boundaries** - Each hub represents distinct business domain
✅ **Scalability** - Can scale each hub independently (separate databases eventually)
✅ **Governance** - Adding hub requires architectural review (major decision)

---

## Implementation Guide

### Step 1: Create a New Unified Entity

**When:** Adding a new entity type to one of the 6 hubs

**File:** `apex_memory/models/entities/<entity_name>.py`

**Template:**

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from decimal import Decimal
from datetime import date, datetime
from enum import Enum

from .base import BaseEntity

# Step 1: Define enums (if needed)
class TruckStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    RETIRED = "retired"

# Step 2: Create entity class
class Truck(BaseEntity):
    """
    Truck entity - Hub 3 (Origin Transport)

    Three-tier property system:
    - Tier 1 (Core): Inherited from BaseEntity
    - Tier 2 (Structured): 40 Backbone schema fields
    - Tier 3 (Dynamic): additional_properties catch-all
    """

    # ═══════════════════════════════════════════════════════════
    # TIER 1: CORE (Required) - Inherited from BaseEntity
    # ═══════════════════════════════════════════════════════════
    # uuid, name, hub, entity_type, created_at

    # Override hub with literal type for validation
    hub: Literal["origin"] = Field(
        default="origin",
        description="Hub assignment (RIGID - always 'origin' for Truck)"
    )

    entity_type: Literal["truck"] = Field(
        default="truck",
        description="Entity type (RIGID - always 'truck')"
    )

    # ═══════════════════════════════════════════════════════════
    # TIER 2: STRUCTURED (Optional) - Backbone Schema
    # ═══════════════════════════════════════════════════════════

    # LLM-Extractable Fields (mark with llm_extractable=True)
    unit_number: Optional[str] = Field(
        default=None,
        description="Truck unit number (e.g., '101', 'T-425')",
        llm_extractable=True  # ← LLM can extract from "Truck #101"
    )

    make: Optional[str] = Field(
        default=None,
        description="Manufacturer (e.g., 'Freightliner', 'Kenworth')",
        llm_extractable=True  # ← LLM can extract from "2019 Freightliner"
    )

    model: Optional[str] = Field(
        default=None,
        description="Model name (e.g., 'Cascadia', 'T680')",
        llm_extractable=True
    )

    year: Optional[int] = Field(
        default=None,
        description="Model year",
        llm_extractable=True
    )

    status: Optional[TruckStatus] = Field(
        default=None,
        description="Current operational status",
        llm_extractable=True  # ← LLM can extract from "Truck is in maintenance"
    )

    current_location_city: Optional[str] = Field(
        default=None,
        description="Current location (city)",
        llm_extractable=True
    )

    current_location_state: Optional[str] = Field(
        default=None,
        description="Current location (state)",
        llm_extractable=True
    )

    # Non-LLM Fields (too complex or requires manual entry)
    vin: Optional[str] = Field(
        default=None,
        description="Vehicle Identification Number (17 characters)",
        llm_extractable=False  # Too precise for LLM extraction
    )

    license_plate: Optional[str] = Field(
        default=None,
        description="License plate number",
        llm_extractable=False
    )

    odometer: Optional[int] = Field(
        default=None,
        description="Current odometer reading (miles)",
        llm_extractable=False
    )

    purchase_price: Optional[Decimal] = Field(
        default=None,
        description="Purchase price in USD",
        llm_extractable=False
    )

    # ... (30 more Backbone fields)

    # ═══════════════════════════════════════════════════════════
    # TIER 3: DYNAMIC (Catch-all) - Inherited from BaseEntity
    # ═══════════════════════════════════════════════════════════
    # additional_properties, extracted_fields_not_in_schema
```

### Step 2: Register Entity in Hub Validator

**File:** `apex_memory/utils/hub_validator.py`

```python
HUB_ASSIGNMENTS = {
    # ... existing assignments ...

    # Hub 3: Origin Transport
    "truck": "origin",  # ← Add new entity type
    "trailer": "origin",
    # ...
}
```

### Step 3: Register with Graphiti

**File:** `apex_memory/services/graphiti_service.py`

```python
from apex_memory.models.entities import Truck  # Import new entity

GRAPHITI_ENTITY_TYPES = {
    # ... existing types ...
    "Truck": Truck,  # ← Register with Graphiti
}
```

### Step 4: Create LLM Prompt Schema

**Automatic (handled by helper):**

```python
# apex_memory/utils/llm_prompt_generator.py

def get_llm_prompt_schema(entity_class: Type[BaseEntity]) -> Dict[str, Any]:
    """
    Generate LLM prompt schema from entity class.

    Returns only fields where llm_extractable=True.
    """
    llm_fields = {}

    for field_name, field_info in entity_class.model_fields.items():
        # Check if field is LLM-extractable
        json_schema_extra = field_info.json_schema_extra or {}
        if json_schema_extra.get('llm_extractable', False):
            llm_fields[field_name] = field_info

    return llm_fields

# Usage in Graphiti service
truck_llm_schema = get_llm_prompt_schema(Truck)
# Result: {unit_number, make, model, year, status, current_location_city, current_location_state}
# (7 fields out of 40 total - only what LLM can reliably extract)
```

---

## Code Examples

### Example 1: Graphiti Extracts Customer

**Scenario:** User uploads email: "Please send invoice to Sun-Glo Corporation at 123 Main St, contact John at john@sunglo.com or (555) 123-4567. Account status is active with $15,230 balance."

**Graphiti Extraction:**

```python
# 1. Graphiti LLM extraction (using full Customer schema context)
graphiti_result = await graphiti.add_document_episode(
    document_uuid="doc_email_20251105_001",
    document_title="Customer email about billing",
    document_content=email_text,
    document_type="email"
)

# 2. Graphiti extracts entities (sees full Customer schema with 44 fields)
# But LLM prompt only includes llm_extractable=True fields (6 fields)
extracted_data = {
    "name": "Sun-Glo Corporation",
    "contact_email": "john@sunglo.com",
    "phone": "(555) 123-4567",
    "address": "123 Main St",
    "account_status": "active",
    "current_ar_balance": 15230.00,

    # Also extracted (not in schema):
    "contact_person_name": "John",
    "preferred_contact_method": "email"
}

# 3. Smart population (Tier 2 matching + Tier 3 catch-all)
customer = populate_entity_from_extraction(
    entity_class=Customer,
    extracted_data=extracted_data,
    hub="contacts"
)

# 4. Result
assert customer.name == "Sun-Glo Corporation"
assert customer.contact_email == "john@sunglo.com"  # ✅ Tier 2 match
assert customer.phone == "(555) 123-4567"  # ✅ Tier 2 match
assert customer.account_status == AccountStatus.ACTIVE  # ✅ Tier 2 match
assert customer.current_ar_balance == Decimal("15230.00")  # ✅ Tier 2 match

# Tier 3: Unmatched fields
assert customer.additional_properties == {
    "contact_person_name": "John",
    "preferred_contact_method": "email"
}
assert customer.extracted_fields_not_in_schema == [
    "contact_person_name",
    "preferred_contact_method"
]

# Tier 2: Not extracted (still NULL)
assert customer.credit_limit is None  # ← Manually entered later
assert customer.payment_terms is None  # ← Manually entered later
```

### Example 2: Manual Entry Updates Tier 2

**Scenario:** Accountant manually enters credit limit and payment terms

```python
# 1. Load existing customer (created by Graphiti extraction)
customer = get_customer_by_name("Sun-Glo Corporation")

# 2. Update Tier 2 fields manually
customer.credit_limit = Decimal("50000.00")
customer.payment_terms = "NET30"
customer.credit_rating = "A"

# 3. Save (updates same entity, no duplication)
update_customer(customer)

# 4. Result: Single entity with mixed data sources
# - Graphiti extracted: name, email, phone, address, status (Tier 2)
# - Manually entered: credit_limit, payment_terms, credit_rating (Tier 2)
# - Unmatched extracted: contact_person_name, preferred_contact_method (Tier 3)
```

### Example 3: Schema Evolution (Tier 3 → Tier 2)

**Scenario:** After 3 months, "preferred_contact_method" appears in 52% of customers

```python
# 1. Run weekly schema evolution analyzer
from apex_memory.utils.schema_evolution import analyze_additional_properties

results = analyze_additional_properties(entity_type="customer")

# Results:
# [
#     ("preferred_contact_method", 234, 52%),  # 234 of 450 customers
#     ("contact_person_name", 189, 42%),
#     ("office_hours", 67, 15%),
# ]

# 2. Promotion decision (>40% usage threshold)
# "preferred_contact_method" qualifies for promotion!

# 3. Generate migration
from apex_memory.utils.schema_migration_generator import generate_field_promotion_migration

migration = generate_field_promotion_migration(
    entity_class=Customer,
    field_name="preferred_contact_method",
    field_type="str",
    default_value=None
)

# 4. Migration updates:
# - Customer model: Add preferred_contact_method to Tier 2
# - PostgreSQL: Add preferred_contact_method column
# - Neo4j: Add preferred_contact_method property
# - Data migration: Move from additional_properties to new field

# 5. After migration:
customer = get_customer_by_name("Sun-Glo Corporation")
assert customer.preferred_contact_method == "email"  # ✅ Now Tier 2!
assert "preferred_contact_method" not in customer.additional_properties  # Migrated
```

### Example 4: Query Patterns

**Query 1: Get customer with all data (Tier 2 + Tier 3)**

```cypher
MATCH (c:Customer {name: "Sun-Glo Corporation"})
RETURN
    c.uuid,
    c.name,
    c.contact_email,
    c.credit_limit,
    c.additional_properties  // Tier 3 as JSON
```

**Query 2: Find customers with specific Tier 3 property**

```sql
-- PostgreSQL
SELECT uuid, name, additional_properties->>'preferred_contact_method' as method
FROM customers
WHERE additional_properties ? 'preferred_contact_method'
  AND additional_properties->>'preferred_contact_method' = 'email';
```

**Query 3: Temporal evolution with Graphiti**

```cypher
// Get customer + Graphiti temporal facts
MATCH (c:Customer {name: "Sun-Glo Corporation"})
OPTIONAL MATCH (c)<-[:MENTIONS]-(e:Episode)
RETURN
    c,  // Current state (all Tier 2 fields)
    collect(e) as temporal_history  // Historical extractions
ORDER BY e.created_at
```

---

## Schema Evolution Process

### Weekly Review Workflow

**Every Monday:**

```bash
# Step 1: Run analyzer
python scripts/schema_evolution/weekly_review.py

# Output:
# ┌────────────────────────────┬───────┬──────┬───────────────┐
# │ Field Name                 │ Count │  %   │ Example Value │
# ├────────────────────────────┼───────┼──────┼───────────────┤
# │ preferred_contact_method   │  234  │ 52%  │ "email"       │ ← PROMOTE
# │ contact_person_name        │  189  │ 42%  │ "John Smith"  │ ← PROMOTE
# │ office_hours              │   67  │ 15%  │ "Mon-Fri 8-5" │
# │ parking_instructions      │   23  │  5%  │ "Use Lot B"   │
# │ delivery_notes            │   12  │  3%  │ "Rear dock"   │
# └────────────────────────────┴───────┴──────┴───────────────┘
```

**Step 2: Review recommendations**
- Fields >40% usage → Automatic promotion candidate
- Fields 20-40% → Manual review
- Fields <20% → Keep in Tier 3

**Step 3: Generate migration**

```bash
python scripts/schema_evolution/promote_field.py \
    --entity=customer \
    --field=preferred_contact_method \
    --type=str

# Generates:
# - Pydantic field definition
# - Alembic migration (PostgreSQL)
# - Neo4j migration (Cypher)
# - Data migration script
```

**Step 4: Review and apply**

```bash
# Review generated code
cat migrations/customer_add_preferred_contact_method.py

# Apply migration
alembic upgrade head

# Verify
pytest tests/migration/test_customer_preferred_contact_method.py
```

### Promotion Criteria

| Usage % | Action | Rationale |
|---------|--------|-----------|
| >60% | **Automatic promotion** | Used by majority, clearly important |
| 40-60% | **Promote with review** | Used by significant portion |
| 20-40% | **Monitor for 2 more weeks** | Could be temporary spike |
| <20% | **Keep in Tier 3** | Not common enough yet |

---

## Common Pitfalls & Solutions

### Pitfall 1: Forgetting llm_extractable Flag

**Problem:**
```python
# ❌ WRONG: No llm_extractable flag
contact_email: Optional[str] = Field(default=None)
```

**Impact:** Graphiti won't extract this field (not in LLM prompt schema)

**Solution:**
```python
# ✅ CORRECT: Mark as extractable
contact_email: Optional[str] = Field(
    default=None,
    llm_extractable=True  # ← Required!
)
```

### Pitfall 2: Wrong Hub Assignment

**Problem:**
```python
# ❌ WRONG: Trying to create invoice in contacts hub
invoice = Invoice(hub="contacts", ...)
```

**Impact:** Raises ValueError (hub validator enforces rigidity)

**Solution:**
```python
# ✅ CORRECT: Use correct hub from HUB_ASSIGNMENTS
invoice = Invoice(hub="financials", ...)  # invoice → financials
```

### Pitfall 3: Not Using additional_properties

**Problem:**
```python
# ❌ WRONG: Ignoring unmatched fields
extracted = {"name": "Sun-Glo", "weird_field": "value"}
customer = Customer(name=extracted["name"])  # weird_field LOST!
```

**Solution:**
```python
# ✅ CORRECT: Use smart population helper
customer = populate_entity_from_extraction(Customer, extracted)
assert customer.additional_properties["weird_field"] == "value"  # Captured!
```

### Pitfall 4: Hardcoding Entity Types

**Problem:**
```python
# ❌ WRONG: Hardcoded entity types
if entity["type"] == "customer":  # What if we add "vendor"?
    ...
```

**Solution:**
```python
# ✅ CORRECT: Use HUB_ASSIGNMENTS registry
from apex_memory.utils.hub_validator import HUB_ASSIGNMENTS

for entity_type, hub in HUB_ASSIGNMENTS.items():
    if hub == "contacts":
        # Process all contacts entities dynamically
        ...
```

---

## FAQs

### Q1: Can I add a new hub?

**A:** No (without architectural review). Hubs are RIGID by design. Adding a hub is a major architectural decision requiring:
1. Business justification (why existing 6 hubs insufficient?)
2. Clear entity scope definition
3. Database partitioning strategy
4. Migration plan for existing entities
5. Team approval

**Why rigid?** Hubs represent fundamental business boundaries. Adding casually leads to data chaos.

### Q2: Can I add a new entity type to an existing hub?

**A:** Yes! Entity types are SEMI-RIGID. Process:
1. Create entity class extending BaseEntity
2. Add to `HUB_ASSIGNMENTS` with correct hub
3. Register with Graphiti if needed
4. Add tests

**Example:** Adding "Vendor" to Hub 4 (Contacts)
```python
# 1. Create Vendor entity
class Vendor(BaseEntity):
    hub: Literal["contacts"] = "contacts"
    entity_type: Literal["vendor"] = "vendor"
    # ... Tier 2 fields ...

# 2. Register
HUB_ASSIGNMENTS["vendor"] = "contacts"

# 3. Tests
def test_vendor_in_contacts_hub():
    vendor = Vendor(name="ACME Supplies", hub="contacts")
    validate_hub_assignment("vendor", "contacts")  # ✅ Passes
```

### Q3: What if Graphiti extracts 100 unique fields?

**A:** They all go to Tier 3 (`additional_properties`). Nothing is lost. Then:
1. Weekly analyzer identifies common fields (>40% usage)
2. Promote common fields to Tier 2 (typed schema)
3. Rare fields stay in Tier 3 (flexible)

**This is by design** - Schema evolves based on real data, not predictions.

### Q4: How do I query Tier 3 properties efficiently?

**PostgreSQL (GIN index on JSONB):**
```sql
-- Create index (one-time)
CREATE INDEX idx_customers_additional_props
ON customers USING GIN (additional_properties);

-- Query with index
SELECT * FROM customers
WHERE additional_properties @> '{"preferred_contact_method": "email"}';
```

**Neo4j (property access):**
```cypher
MATCH (c:Customer)
WHERE c.additional_properties.preferred_contact_method = "email"
RETURN c
```

### Q5: Can the same field be in Tier 2 and Tier 3?

**A:** No. When a field is promoted from Tier 3 → Tier 2:
1. Migration adds field to Tier 2 schema
2. Data migration moves values from `additional_properties` to new field
3. Future extractions go to Tier 2 (not Tier 3)

**Example:**
```python
# Before promotion
customer.additional_properties = {"preferred_contact_method": "email"}

# After promotion
customer.preferred_contact_method = "email"  # Tier 2
customer.additional_properties = {}  # Moved out
```

### Q6: What about multi-category support?

**A:** Backbone Schema supports multi-category (e.g., "Origin is both customer AND vendor"). Implementation:

```python
class Company(BaseEntity):
    # Tier 2: Multi-category support
    categories: List[CompanyCategory] = Field(
        default_factory=list,
        description="Multiple categories (customer, vendor, carrier, etc.)"
    )

    # Usage
    origin = Company(
        name="Origin Transport",
        categories=["customer", "vendor", "carrier"]  # All 3!
    )
```

### Q7: How does this work with Temporal workflows?

**A:** Temporal workflows use the unified schemas:

```python
# apex_memory/temporal/workflows/ingestion.py

@workflow.defn
class DocumentIngestionWorkflow:
    async def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Step 1: Parse document
        parsed_doc = await workflow.execute_activity(
            parse_document_activity,
            params,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Step 2: Extract entities (uses unified Customer/Person/etc. schemas)
        extraction_result = await workflow.execute_activity(
            extract_entities_with_graphiti_activity,
            parsed_doc,
            start_to_close_timeout=timedelta(minutes=10)
        )

        # extraction_result contains:
        # - Tier 1: uuid, name, hub, entity_type, created_at
        # - Tier 2: Matched schema fields (contact_email, phone, etc.)
        # - Tier 3: Unmatched fields (additional_properties)

        # Step 3: Write to databases (single entity, not separate Graphiti + Backbone)
        await workflow.execute_activity(
            write_to_databases_activity,
            extraction_result,
            start_to_close_timeout=timedelta(minutes=5)
        )
```

---

## Summary

**Option D+ Architecture in One Sentence:**

"A unified entity system where **6 rigid hubs** contain **45 semi-rigid entity types**, each with **three-tier properties** (required core + optional structured + flexible catch-all) that ensures **nothing falls through the cracks** and **schema evolves from real usage**."

**Key Principles:**
1. **Hub Rigidity** - 6 hubs, cannot change without review
2. **Entity Flexibility** - Can add new types to existing hubs
3. **Property Tiers** - Required + Structured + Catch-all
4. **Nothing Lost** - Tier 3 captures all unmatched extractions
5. **Evolution** - Common Tier 3 fields promote to Tier 2 automatically

**Benefits:**
- ✅ Single source of truth (one Customer schema)
- ✅ Perfect LLM alignment (Graphiti uses official schemas)
- ✅ No data loss (Tier 3 catch-all)
- ✅ Schema evolves (automated promotion)
- ✅ Clear boundaries (hub validator)

**Next Steps:**
1. Read revised execution plan: `REVISED-EXECUTION-PLAN-OPTION-D-PLUS.md`
2. Begin Phase 1: Create BaseEntity + 5 core schemas
3. Implement smart population helper
4. Test with real Graphiti extractions

---

**Document Version:** 1.0
**Created:** November 5, 2025
**Author:** Claude Code + Richard Glaubitz
**Status:** Approved, ready for implementation
**Architecture:** Option D+ (Hub Rigidity + Property Flexibility)
